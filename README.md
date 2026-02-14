# HireUs - AI-Powered Hiring Platform

A comprehensive hiring platform with AI-assisted interview kits, structured evaluations, and data-driven hiring decisions.

## Features

- **Role Blueprint**: AI-powered role requirement analysis
- **Interview Kit Builder**: Generate questions and rubrics automatically
- **Structured Scorecards**: Consistent evaluation across candidates
- **Workflow Board**: Kanban-style candidate pipeline
- **Decision Briefs**: AI-powered candidate comparison and recommendations

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy (PostgreSQL)
- Pydantic
- JWT Authentication
- Alembic Migrations

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
# create/update backend/.env (backend loads this file explicitly)
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
# configure frontend/.env.local (see frontend/.env.local.example)
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
