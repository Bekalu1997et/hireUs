# HireUs - AI-Powered Hiring Platform

A comprehensive hiring platform with AI-assisted interview kits, structured evaluations, and data-driven hiring decisions.

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
