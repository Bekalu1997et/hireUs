# HireUs - AI-Powered Hiring Platform

A comprehensive hiring platform with AI-assisted interview kits, structured evaluations, and data-driven hiring decisions.

## Business Overview

Hiring is one of the highest‑leverage decisions for early‑stage founders. Yet most teams still rely on unstructured interviews and inconsistent evaluation, creating noise, bias, and missed talent. HireUs turns hiring into a repeatable process by combining structured scorecards with AI‑assisted interview kits and decision briefs.

**Who this is for**
- Early‑stage founders and hiring leads who need consistent decision quality.
- Interviewers who want clear criteria and fair scoring.
- Teams scaling headcount without scaling bias.

**Founder benefits**
- Faster, clearer hiring decisions based on evidence.
- Reduced interviewer variance with standardized rubrics.
- Consistent role definitions across the entire hiring funnel.
- Auditability for decisions (what was scored, why, and by whom).

## Market Context

The hiring stack has shifted from resume‑first to signal‑first. Modern recruiting focuses on demonstrable skills, structured evaluation, and fairness. The rise of AI copilots in HR is accelerating this trend, but most tools stop at sourcing. HireUs targets the **post‑screening gap**: interview design, scoring consistency, and decision quality.

**Trend alignment**
- Structured interviewing is now widely adopted by high‑growth teams.
- AI assists content generation but still needs strong guardrails.
- Data‑backed hiring decisions are a competitive advantage.

## Features

- **Role Blueprint**: Role + competency definition (AI blueprint planned)
- **Interview Kit Builder**: Generate questions and rubrics automatically
- **Structured Scorecards**: Consistent evaluation across candidates
- **Workflow Pipeline**: Candidate workflows with stages and assignment
- **Decision Briefs**: AI-powered candidate comparison and recommendations
- **Signals Aggregation**: Aggregate competency scores across evaluations

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy (PostgreSQL)
- Pydantic
- JWT Authentication
- Alembic Migrations
- OpenAI + Ollama fallback (local LLM)

### Frontend
- Next.js 14 (App Router)
- TypeScript
- TailwindCSS
- Shadcn/UI

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Docker (optional)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Docker Setup
```bash
docker-compose up -d
```

## Docker Services

- `backend`: FastAPI application
- `db`: PostgreSQL 15
- `ollama`: Local LLM runtime

If you are using Docker, update `.env` to point to the container DB:
```
DATABASE_URL=postgresql+asyncpg://postgres:hireus@db:5432/hireus
```

## Project Structure

```
hireUs/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entrypoint
│   │   ├── core/                # Configs & utilities
│   │   ├── db/                  # Database layer
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── modules/             # Feature modules
│   │   │   ├── audit/            # Audit logging
│   │   │   ├── organization/     # Organization + invites
│   │   │   ├── interview_kits/   # Interview kit generation
│   │   │   ├── workflows/        # Workflow orchestration
│   │   │   ├── evaluations/      # Evaluation submission
│   │   │   ├── decisions/        # Decision generation
│   │   │   └── signals/          # Candidate signal aggregation
│   │   └── tests/               # Tests
│   ├── alembic/                 # Migrations
│   └── requirements.txt
├── frontend/
│   ├── app/                     # Next.js pages
│   ├── components/              # UI components
│   ├── hooks/                   # React hooks
│   ├── lib/                     # Utils & API client
│   └── styles/                  # Styles
├── scripts/                     # Dev scripts
├── .env                         # Environment variables
└── docker-compose.yml
```

## License

MIT
