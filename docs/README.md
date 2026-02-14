# HireUs - AI-Powered Hiring Platform

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white" alt="Next.js">
  <img src="https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript">
</p>

HireUs is a comprehensive hiring platform with AI-assisted interview kits, structured evaluations, and data-driven hiring decisions. Built for founders who want to make smarter hiring decisions through structured interviews and AI-powered insights.

## 🚀 Features

### Core Features

| Feature | Description |
|---------|-------------|
| **Role Blueprint** | AI-powered role requirement analysis with competency suggestions |
| **Interview Kit Builder** | Generate interview questions and rubrics automatically using AI |
| **Structured Scorecards** | Consistent competency-based evaluations across all candidates |
| **Workflow Board** | Kanban-style candidate pipeline with stage management |
| **Decision Briefs** | AI-powered candidate comparison and hiring recommendations |
| **Signal Gap Detection** | Automatically identify weak areas in candidate evaluations |

### Core 1: Structured Technical Interview Engine

- **Role Setup**: Define roles with AI-suggested competencies and interview stages
- **Interview Kit Generator**: Create coding, system design, PM case, and behavioral interview kits
- **Structured Scorecards**: Competency-based scoring with required evidence
- **Interview Workflow Board**: Kanban pipeline with feedback requirements

### Core 2: Hiring Intelligence for Founders

- **Candidate Comparison Dashboard**: Side-by-side competency heatmaps and score analysis
- **Decision Brief Generator**: AI-generated hiring recommendations with strengths/risks
- **Signal Gap Detection**: Identify missing evaluation signals automatically

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT-based auth with refresh tokens
- **Migrations**: Alembic
- **AI**: OpenAI GPT-4 / Google Gemini integration
- **Validation**: Pydantic v2

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: TailwindCSS with Shadcn/UI
- **State Management**: React Query (TanStack Query)
- **HTTP Client**: Axios

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Docker & Docker Compose (optional)

## 🏁 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd hireUs

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api/v1
# API Docs: http://localhost:8000/api/docs
```

### Option 2: Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Start development server
npm run dev
```

## 📁 Project Structure

```
hireUs/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── core/                # Core utilities (config, security, utils)
│   │   ├── db/                  # Database layer (models, session, base)
│   │   ├── schemas/             # Pydantic validation schemas
│   │   ├── modules/             # Feature modules
│   │   │   ├── auth/            # Authentication
│   │   │   ├── roles/           # Job roles management
│   │   │   ├── interview_kits/   # Interview kits with AI generation
│   │   │   ├── workflows/       # Candidate pipeline workflows
│   │   │   ├── evaluations/     # Structured scorecards
│   │   │   ├── comparison/      # Candidate comparison analytics
│   │   │   ├── decisions/       # AI decision briefs
│   │   │   ├── candicates/      # Candidate management
│   │   │   └── organization/    # Organization management
│   │   └── tests/              # Test suite
│   ├── alembic/                 # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── app/                    # Next.js pages (App Router)
│   │   ├── auth/              # Authentication pages
│   │   ├── roles/             # Role management pages
│   │   ├── interview-kits/    # Interview kit pages
│   │   ├── workflows/        # Workflow board pages
│   │   ├── evaluations/       # Evaluation pages
│   │   ├── comparison/        # Comparison dashboard
│   │   ├── decisions/         # Decision briefs
│   │   └── candidates/        # Candidate management
│   ├── components/            # React components
│   │   ├── forms/            # Form components
│   │   ├── ui/               # Shadcn/UI components
│   │   └── ...               # Other components
│   ├── hooks/                # React Query hooks
│   ├── lib/                  # Utilities and API client
│   └── package.json
├── docs/                      # Documentation
├── scripts/                   # Development scripts
└── docker-compose.yml
```

## 🔧 Environment Variables

### Backend (.env)

```env
# Application
APP_NAME="HireUs - AI-Powered Hiring Platform"
DEBUG=true

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/hireus
SYNC_DATABASE_URL=postgresql://user:password@localhost:5432/hireus

# JWT Authentication
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# First Superuser
FIRST_SUPERUSER_EMAIL=admin@hireus.com
FIRST_SUPERUSER_PASSWORD=admin123

# AI Configuration (OpenAI)
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4

# AI Configuration (Google Gemini)
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-pro

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## 📖 Documentation

Detailed documentation is available in the `docs/` folder:

- [Setup Guide](SETUP.md) - Detailed setup instructions
- [Architecture](ARCHITECTURE.md) - System architecture and design patterns
- [API Reference](API.md) - Complete API endpoint documentation

## 🔌 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI Schema**: http://localhost:8000/api/openapi.json

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend linting
cd frontend
npm run lint
```

## 🚢 Deployment

### Docker Production Build

```bash
# Build and start
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Production Setup

For production deployment, refer to the [Setup Guide](docs/SETUP.md#production-setup).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- Documentation: Check the `docs/` folder
- API Issues: Use `/api/docs` interactive documentation
- Report bugs: GitHub Issues

---

<p align="center">Built with ❤️ for better hiring decisions</p>

