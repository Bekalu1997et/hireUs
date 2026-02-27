# HireUs Architecture Guide

This document describes the system architecture, design patterns, and implementation details of the HireUs platform.

## Table of Contents

- [System Overview](#system-overview)
- [Architecture Diagram](#architecture-diagram)
- [Backend Architecture](#backend-architecture)
  - [Project Structure](#project-structure)
  - [Module Design](#module-design)
  - [Database Layer](#database-layer)
  - [API Layer](#api-layer)
- [Frontend Architecture](#frontend-architecture)
  - [Project Structure](#project-structure-1)
  - [State Management](#state-management)
  - [Component Architecture](#component-architecture)
- [AI Integration](#ai-integration)
- [Authentication & Authorization](#authentication--authorization)
- [Data Models](#data-models)

---

## System Overview

HireUs follows a **client-server architecture** with:

- **Backend**: FastAPI REST API handling business logic, database operations, and AI integrations
- **Frontend**: Next.js SPA providing user interface
- **Database**: PostgreSQL for persistent storage
- **AI Services**: Ollama for local AI features

### Core Design Principles

1. **Modular Architecture**: Feature modules are self-contained
2. **API-First Design**: Clear RESTful API contracts
3. **Type Safety**: Full TypeScript/Python typing
4. **Separation of Concerns**: Clear boundaries between layers

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │
│  │  Next   │  │  React   │  │ Tailwind │  │  TanStack      │  │
│  │   App   │──│ Components│──│   CSS    │──│    Query       │  │
│  │ Router  │  │          │  │          │  │                │  │
│  └────┬────┘  └──────────┘  └──────────┘  └───────┬────────┘  │
│       │                                           │            │
│       └──────────────────┬────────────────────────┘            │
│                          │                                      │
│                    ┌─────▼─────┐                                │
│                    │  Axios    │                                │
│                    │   Client  │                                │
│                    └─────┬─────┘                                │
└──────────────────────────┼──────────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │   REST API   │
                    │  /api/v1/*   │
                    └──────┬──────┘
                           │
┌──────────────────────────┼──────────────────────────────────────┐
│                     BACKEND                                      │
│  ┌───────────────────────▼────────────────────────────────┐     │
│  │                   FastAPI Application                   │     │
│  │  ┌────────────┐  ┌────────────┐  ┌─────────────────┐  │     │
│  │  │   Auth    │  │   Roles    │  │ Interview Kits  │  │     │
│  │  └────────────┘  └────────────┘  └─────────────────┘  │     │
│  │  ┌────────────┐  ┌────────────┐  ┌─────────────────┐  │     │
│  │  │ Workflows  │  │Evaluations │  │   Decisions    │  │     │
│  │  └────────────┘  └────────────┘  └─────────────────┘  │     │
│  └────────────────────────────────────────────────────────┘     │
│                          │                                      │
│  ┌───────────────────────▼────────────────────────────────┐     │
│  │              Service Layer (Business Logic)            │     │
│  └────────────────────────────────────────────────────────┘     │
│                          │                                      │
│  ┌───────────────────────▼────────────────────────────────┐     │
│  │              Repository Layer (Data Access)            │     │
│  └────────────────────────────────────────────────────────┘     │
│                          │                                      │
│  ┌───────────────────────▼────────────────────────────────┐     │
│  │              SQLAlchemy ORM + AsyncPG                  │     │
│  └────────────────────────────────────────────────────────┘     │
└──────────────────────────┼──────────────────────────────────────┘
                           │
              ┌────────────▼────────────┐
              │      PostgreSQL          │
              │     Database             │
              └──────────────────────────┘

        ┌───────────────┐
        │     AI        │
        │  Services     │
        │ ┌───────────┐ │
        │ │  Ollama   │ │
        │ └───────────┘ │
        └───────────────┘
```

---

## Backend Architecture

### Project Structure

```
backend/
├── app/
│   ├── main.py                 # Application entry point
│   ├── core/                   # Core utilities
│   │   ├── config.py           # Settings management
│   │   ├── security.py         # Password hashing, JWT
│   │   ├── utils.py            # Helper functions
│   │   └── llm/               # AI/LLM integrations
│   │       ├── base.py
│   │       └── schema.py
│   ├── db/                     # Database layer
│   │   ├── base.py             # SQLAlchemy base
│   │   ├── models.py           # Database models
│   │   └── session.py          # DB session management
│   ├── schemas/                # Pydantic schemas
│   │   ├── user.py
│   │   ├── role.py
│   │   └── ...
│   └── modules/                # Feature modules
│       ├── auth/              # Authentication
│       ├── roles/             # Role management
│       ├── interview_kits/    # Interview kits
│       ├── workflows/         # Pipeline workflows
│       ├── evaluations/        # Scorecards
│       ├── comparison/         # Candidate comparison
│       ├── decisions/         # Decision briefs
│       ├── candicates/        # Candidates
│       └── organization/       # Organizations
├── alembic/                   # Database migrations
└── requirements.txt
```

### Module Design

Each feature module follows a consistent structure:

```
module_name/
├── __init__.py
├── router.py          # API endpoints
├── service.py         # Business logic
├── repository.py      # Data access
└── ai/               # AI-specific code (if needed)
    ├── prompts.py
    ├── schema.py
    └── generator.py
```

### Layer Responsibilities

| Layer | Responsibility | Example Operations |
|-------|----------------|-------------------|
| **Router** | HTTP handling, request validation | `@app.get()`, `@app.post()` |
| **Service** | Business logic, orchestration | `create_role()`, `generate_brief()` |
| **Repository** | Database operations | `get_by_id()`, `create()`, `update()` |

### Database Layer

#### Session Management

```python
# app/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession)
```

#### Base Model

```python
# app/db/base.py
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

### API Layer

#### Router Example

```python
# app/modules/roles/router.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.role import RoleCreate, RoleResponse
from app.modules.roles.service import RoleService

router = APIRouter(prefix="/roles", tags=["Roles"])

@router.post("/", response_model=RoleResponse)
async def create_role(role: RoleCreate):
    service = RoleService()
    return await service.create(role)
```

---

## Frontend Architecture

### Project Structure

```
frontend/
├── app/                      # Next.js App Router pages
│   ├── layout.tsx           # Root layout
│   ├── page.tsx            # Home page
│   ├── auth/               # Authentication pages
│   ├── roles/              # Role management
│   ├── interview-kits/     # Interview kits
│   ├── workflows/          # Workflow board
│   ├── evaluations/        # Evaluations
│   ├── comparison/         # Comparison dashboard
│   ├── decisions/          # Decision briefs
│   └── candidates/         # Candidates
├── components/
│   ├── forms/             # Form components
│   ├── ui/                # Shadcn/UI components
│   └── ...
├── hooks/                  # React Query hooks
├── lib/                    # Utilities
│   ├── api.ts             # API client
│   └── utils.ts           # Helper functions
└── package.json
```

### State Management

#### React Query (TanStack Query)

The frontend uses React Query for server state management:

```typescript
// hooks/use-roles.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { roleApi } from '@/lib/api';

export function useRoles(params?: GetRolesParams) {
  return useQuery({
    queryKey: ['roles', params],
    queryFn: () => roleApi.getAll(params),
  });
}

export function useCreateRole() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: roleApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] });
    },
  });
}
```

### Component Architecture

#### Page Components

Pages are located in `app/` directory and use Next.js App Router:

```typescript
// app/roles/page.tsx
'use client';

import { useRoles } from '@/hooks/use-roles';
import { RoleCard } from '@/components/role-card';

export default function RolesPage() {
  const { data: roles, isLoading } = useRoles();

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      {roles?.map(role => (
        <RoleCard key={role.id} role={role} />
      ))}
    </div>
  );
}
```

#### Form Components

Forms use controlled components with validation:

```typescript
// components/forms/role-form.tsx
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

export function RoleForm() {
  const form = useForm({
    resolver: zodResolver(roleSchema),
  });

  const onSubmit = (data: RoleFormData) => {
    // Handle submission
  };

  return <form onSubmit={form.handleSubmit(onSubmit)}>{/* fields */}</form>;
}
```

---

## AI Integration

### LLM Base Class

```python
# app/core/llm/base.py
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class LLMBase(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        pass
    
    @abstractmethod
    async def generate_json(self, prompt: str, schema: Dict, **kwargs) -> Dict[str, Any]:
        pass
```

### AI Modules

| Module | Purpose |
|--------|---------|
| `roles/ai/` | Generate role blueprints and competencies |
| `interview_kits/ai/` | Generate interview questions and rubrics |
| `evaluations/ai/` | Improve feedback clarity |
| `decisions/ai/` | Generate decision briefs |

---

## Authentication & Authorization

### JWT Authentication Flow

```
┌─────────┐                           ┌─────────┐
│ Client  │                           │ Server  │
└────┬────┘                           └────┬────┘
     │                                      │
     │  1. POST /auth/login                 │
     │  {email, password}                  │
     │ ──────────────────────────────────► │
     │                                      │
     │  2. Validate credentials             │
     │     Generate tokens                  │
     │                                      │
     │  3. Response                         │
     │  {access_token, refresh_token}     │
     │ ◄────────────────────────────────── │
     │                                      │
     │  4. Subsequent requests              │
     │  Authorization: Bearer {token}      │
     │ ──────────────────────────────────► │
     │                                      │
```

### User Roles

| Role | Description |
|------|-------------|
| `SUPERADMIN` | Full system access |
| `ADMIN` | Organization admin |
| `RECRUITER` | Manage hiring process |
| `INTERVIEWER` | Conduct interviews |
| `HIRING_MANAGER` | Make hiring decisions |
| `CANDIDATE` | Job applicant |

---

## Data Models

### Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────────┐       ┌─────────────┐
│  User       │       │ Organization    │       │   Role      │
├─────────────┤       ├─────────────────┤       ├─────────────┤
│ id          │       │ id              │       │ id          │
│ email       │◄──────│ members ────────►│◄──────│ organization│
│ full_name   │       │ roles           │       │ title       │
│ role        │       │ candidates      │       │ seniority   │
│ password    │       │ workflows       │       │ competencies│
└─────────────┘       └────────┬────────┘       └──────┬──────┘
                               │                       │
                               │                       │
                    ┌──────────▼──────────┐  ┌─────────▼─────────┐
                    │    Candidate       │  │  InterviewKit    │
                    ├────────────────────┤  ├──────────────────┤
                    │ id                  │  │ id                │
                    │ organization       │  │ role              │
                    │ role               │  │ type              │
                    │ workflow           │  │ questions         │
                    │ current_stage      │  │ rubric            │
                    └─────────┬──────────┘  └──────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
   ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐
   │  Workflow   │    │ Interview   │    │  Feedback   │
   ├─────────────┤    │Assignment   │    ├─────────────┤
   │ id          │    │ id          │    │ id          │
   │ name        │    │ candidate   │    │ candidate   │
   │ stages      │    │ interviewer │    │ scores      │
   │             │    │ kit         │    │ summary     │
   └─────────────┘    └─────────────┘    └─────────────┘
```

### Model Summary

| Model | Description | Key Fields |
|-------|-------------|-------------|
| `User` | Authentication | email, password, role |
| `Organization` | Multi-tenant | name, members, settings |
| `Role` | Job positions | title, competencies, stages |
| `Candidate` | Applicants | name, email, status, workflow |
| `InterviewKit` | Interview content | questions, rubric, type |
| `Workflow` | Pipeline | stages, candidates |
| `Feedback` | Evaluations | scores, recommendation |

---

## API Design Patterns

### Response Format

```json
{
  "data": { ... },
  "message": "Success"
}
```

### Error Handling

```json
{
  "detail": "Error message",
  "code": "ERROR_CODE"
}
```

### Pagination

```json
{
  "data": [...],
  "total": 100,
  "skip": 0,
  "limit": 20
}
```

---

## Next Steps

- Review the [API Reference](API.md) for detailed endpoint documentation
- Explore the codebase to understand implementation details
- Check [Setup Guide](SETUP.md) for development environment configuration
