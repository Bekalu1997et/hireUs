# Structured Interview Platform - Backend

FastAPI backend for the Structured Technical Interview Platform.

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- pip or poetry

### Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp ../.env.example ../.env
# Edit .env with your configuration
```

4. Create databases:
```bash
# Create main database
createdb hireus

# Create test database
createdb hireus_test
```

5. Run database migrations:
```bash
alembic upgrade head
```

### Running the Application

Development server:
```bash
python -m app.main
# or
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

### Running Tests

Run all tests:
```bash
pytest
```

Run specific test types:
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Property-based tests only
pytest -m property
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

### Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

## Project Structure

```
backend/
├── alembic/              # Database migrations
├── app/
│   ├── core/            # Core configuration and utilities
│   ├── db/              # Database setup and models
│   ├── modules/         # Feature modules
│   │   ├── auth/        # Authentication
│   │   ├── roles/       # Role management
│   │   ├── interview_kits/  # Interview kit generation
│   │   ├── workflows/   # Workflow orchestration
│   │   ├── evaluations/ # Evaluation submission
│   │   └── decisions/   # Decision generation
│   ├── schemas/         # Pydantic schemas
│   ├── tests/           # Test suite
│   └── main.py          # Application entry point
└── requirements.txt     # Python dependencies
```

## Development

### Code Style

This project follows PEP 8 style guidelines. Use `black` and `isort` for formatting:

```bash
black app/
isort app/
```

### Testing Strategy

- **Unit Tests**: Test individual functions and classes
- **Property Tests**: Test universal properties using Hypothesis
- **Integration Tests**: Test end-to-end workflows

All tests should be placed in `app/tests/` with the naming convention `test_*.py`.

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
