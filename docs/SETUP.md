# HireUs Setup Guide

This guide provides detailed instructions for setting up the HireUs platform for development and production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Development Setup](#development-setup)
- [Docker Setup](#docker-setup)
- [Database Setup](#database-setup)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [Production Setup](#production-setup)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.11+ | Backend runtime |
| Node.js | 18+ | Frontend runtime |
| PostgreSQL | 15+ | Primary database |
| Git | Latest | Version control |

### Optional Software

| Software | Purpose |
|----------|---------|
| Docker | Containerization |
| Redis | Caching and sessions |
| pgAdmin | Database management |

---

## Development Setup

### Backend Setup

#### 1. Clone and Navigate

```bash
git clone <repository-url>
cd hireUs
```

#### 2. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Activate on Linux/Mac
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Application
APP_NAME="HireUs - AI-Powered Hiring Platform"
DEBUG=true

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/hireus
SYNC_DATABASE_URL=postgresql://user:password@localhost:5432/hireus

# JWT Authentication
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# First Superuser (change password in production!)
FIRST_SUPERUSER_EMAIL=admin@hireus.com
FIRST_SUPERUSER_PASSWORD=admin123

# AI Configuration (Optional - for AI features)
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-pro

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

#### 5. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE hireus;

# Create user (optional)
CREATE USER hireus_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE hireus TO hireus_user;
```

#### 6. Run Migrations

```bash
alembic upgrade head
```

#### 7. Start Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000/api/v1
- Swagger Docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

---

### Frontend Setup

#### 1. Navigate to Frontend

```bash
cd frontend
```

#### 2. Install Dependencies

```bash
npm install
```

#### 3. Configure Environment Variables

Create a `.env.local` file in the `frontend` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

#### 4. Start Development Server

```bash
npm run dev
```

The frontend will be available at http://localhost:3000

---

## Docker Setup

### Quick Start with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Services Overview

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | Next.js application |
| Backend | 8000 | FastAPI application |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache (optional) |

### Docker Commands

```bash
# Build images
docker-compose build

# Start with specific service
docker-compose up -d postgres

# View container status
docker-compose ps

# Access container shell
docker-compose exec backend bash
docker-compose exec postgres psql -U postgres
```

---

## Database Setup

### Initial Setup

```bash
# Run migrations
alembic upgrade head

# Create initial data (optional)
alembic upgrade head + seed_data
```

### Database Migrations

```bash
# Generate a new migration
alembic revision --autogenerate -m "description"

# Run specific migration
alembic upgrade <revision_id>

# Rollback one migration
alembic downgrade -1

# Rollback all migrations
alembic downgrade base
```

### Database Models

The application uses the following main models:
- **User**: Authentication and authorization
- **Organization**: Multi-tenant support
- **Role**: Job positions
- **Candidate**: Job applicants
- **InterviewKit**: Interview questions and rubrics
- **Workflow**: Pipeline stages
- **Feedback**: Interview evaluations

---

## Environment Configuration

### Backend Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `APP_NAME` | No | "HireUs" | Application name |
| `DEBUG` | No | false | Debug mode |
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `SECRET_KEY` | Yes | - | JWT signing key |
| `ALGORITHM` | No | HS256 | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | 30 | Token expiration |
| `FIRST_SUPERUSER_EMAIL` | No | admin@hireus.com | Initial admin email |
| `FIRST_SUPERUSER_PASSWORD` | No | admin123 | Initial admin password |
| `OPENAI_API_KEY` | No | - | OpenAI API key |
| `GEMINI_API_KEY` | No | - | Google Gemini API key |
| `CORS_ORIGINS` | No | localhost:3000 | Allowed origins |

### Frontend Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | http://localhost:8000/api/v1 | Backend API URL |

---

## Running the Application

### Development Mode

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Production Mode

#### Backend

```bash
cd backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Frontend

```bash
cd frontend
npm run build
npm start
```

---

## Production Setup

### Security Checklist

- [ ] Change all default passwords
- [ ] Use strong `SECRET_KEY`
- [ ] Enable HTTPS/SSL
- [ ] Configure proper CORS origins
- [ ] Set up proper database credentials
- [ ] Configure Redis for sessions (optional)
- [ ] Set up monitoring and logging

### Using with Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### Environment Variables for Production

```env
# Backend
APP_NAME="HireUs - AI-Powered Hiring Platform"
DEBUG=false
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/hireus
SECRET_KEY=<generate-strong-secret-key>
CORS_ORIGINS=https://yourdomain.com

# Optional: Redis
REDIS_URL=redis://cache:6379/0
```

---

## Troubleshooting

### Common Issues

#### Database Connection Errors

```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Test connection
psql -h localhost -U postgres -d hireus
```

#### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
```

#### Frontend Build Errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Next.js cache
rm -rf .next
npm run dev
```

#### Port Already in Use

```bash
# Find process using port
lsof -i :8000  # Backend
lsof -i :3000  # Frontend

# Kill process
kill -9 <PID>
```

### Getting Help

- Check API docs at http://localhost:8000/api/docs
- Review logs in the console
- Open an issue on GitHub

---

## Next Steps

After setup, see:
- [Architecture Guide](ARCHITECTURE.md) - Understanding the system design
- [API Reference](API.md) - Complete API documentation

