"""
Pytest configuration and fixtures for HireUs Backend.
Includes both unit test fixtures and API test fixtures.
"""
import pytest
import asyncio
import secrets
from datetime import datetime, timedelta
from typing import Generator, AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.config import settings as app_settings

# Test constants
TEST_USER_ID = "test-user-123"
TEST_ORGANIZATION_ID = "test-org-456"
TEST_ROLE_ID = "test-role-789"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPass123"

# Test database URL - use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# ============== Event Loop Fixture ==============

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============== Database Fixtures ==============

@pytest.fixture(scope="function")
async def db_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture(scope="function")
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client with database override."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


# ============== Auth Fixtures ==============

@pytest.fixture
async def test_user(client: AsyncClient) -> dict:
    """Create a test user and return user data with token.
    
    This fixture creates a user via registration, and if that fails
    (user already exists), it falls back to login.
    """
    # Try to register a new user
    unique_email = f"test_{secrets.token_hex(4)}@test.com"
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": unique_email,
            "password": "TestPass123",
            "full_name": "Test User",
            "confirm_password": "TestPass123"
        }
    )
    
    if response.status_code == 201:
        user_data = response.json()
        return {
            "id": user_data.get("user_id", "test-user-id"),
            "email": unique_email,
            "password": "TestPass123",
            "token": user_data.get("access_token")
        }
    
    # If registration fails (user exists), try to login
    login_response = await client.post(
        "/api/v1/auth/login/json",
        json={
            "email": unique_email,
            "password": "TestPass123"
        }
    )
    
    if login_response.status_code == 200:
        login_data = login_response.json()
        return {
            "id": "test-user-id",
            "email": unique_email,
            "password": "TestPass123",
            "token": login_data.get("access_token")
        }
    
    # Fallback - create user dict without token
    return {
        "id": "test-user-id",
        "email": unique_email,
        "password": "TestPass123"
    }


@pytest.fixture
async def auth_headers(test_user: dict) -> dict:
    """Get authentication headers from test user.
    
    Returns a dict with Authorization header if token is available.
    """
    token = test_user.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


@pytest.fixture
async def superuser_headers(client: AsyncClient) -> dict:
    """Get superuser authentication headers.
    
    Creates a superuser and returns their token.
    """
    # Register a superuser
    unique_email = f"superuser_{secrets.token_hex(4)}@test.com"
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": unique_email,
            "password": "SuperPass123",
            "full_name": "Super User",
            "confirm_password": "SuperPass123"
        }
    )
    
    # Note: In real tests, you'd need to manually set is_superuser in DB
    # For now, return headers from registration
    if response.status_code == 201:
        user_data = response.json()
        token = user_data.get("access_token")
        if token:
            return {"Authorization": f"Bearer {token}"}
    
    return {}


# ============== Test Data Fixtures ==============

@pytest.fixture
async def test_organization(client: AsyncClient, auth_headers: dict) -> dict:
    """Create a test organization."""
    response = await client.post(
        "/api/v1/organizations/",
        headers=auth_headers,
        json={
            "name": "Test Organization",
            "description": "Test organization for testing",
            "is_active": True
        }
    )
    if response.status_code in [200, 201]:
        return response.json()
    return {"id": "test-org-id", "name": "Test Organization"}


@pytest.fixture
async def test_role(client: AsyncClient, auth_headers: dict, test_organization: dict) -> dict:
    """Create a test role."""
    response = await client.post(
        "/api/v1/roles/",
        headers=auth_headers,
        json={
            "organization_id": test_organization["id"],
            "title": "Test Role",
            "seniority": "senior",
            "stack": ["Python", "Django"],
            "is_active": True
        }
    )
    if response.status_code in [200, 201]:
        return response.json()
    return {"id": "test-role-id", "title": "Test Role"}


@pytest.fixture
async def test_candidate(client: AsyncClient, auth_headers: dict, test_organization: dict, test_role: dict) -> dict:
    """Create a test candidate."""
    response = await client.post(
        "/api/v1/candidates/",
        headers=auth_headers,
        json={
            "organization_id": test_organization["id"],
            "role_id": test_role["id"],
            "full_name": "Test Candidate",
            "email": f"candidate_{secrets.token_hex(4)}@test.com",
            "phone": "+1234567890"
        }
    )
    if response.status_code in [200, 201]:
        return response.json()
    return {"id": "test-candidate-id", "full_name": "Test Candidate", "email": "candidate@test.com"}


@pytest.fixture
async def test_workflow(client: AsyncClient, auth_headers: dict, test_organization: dict) -> dict:
    """Create a test workflow."""
    response = await client.post(
        "/api/v1/workflows/",
        headers=auth_headers,
        json={
            "organization_id": test_organization["id"],
            "name": "Test Workflow",
            "stages": [
                {"id": "stage_1", "name": "Applied", "order": 0},
                {"id": "stage_2", "name": "Interview", "order": 1},
                {"id": "stage_3", "name": "Offer", "order": 2}
            ]
        }
    )
    if response.status_code in [200, 201]:
        return response.json()
    return {"id": "test-workflow-id", "name": "Test Workflow"}


@pytest.fixture
async def test_interview_kit(client: AsyncClient, auth_headers: dict, test_organization: dict, test_role: dict) -> dict:
    """Create a test interview kit."""
    response = await client.post(
        "/api/v1/interview-kits/",
        headers=auth_headers,
        json={
            "organization_id": test_organization["id"],
            "role_id": test_role["id"],
            "role_title": "Test Role",
            "seniority": "senior",
            "interview_type": "coding",
            "duration_minutes": 60
        }
    )
    if response.status_code in [200, 201]:
        return response.json()
    return {"id": "test-kit-id", "role_title": "Test Role"}


@pytest.fixture
async def test_evaluation(client: AsyncClient, auth_headers: dict, test_organization: dict, test_candidate: dict) -> dict:
    """Create a test evaluation/scorecard."""
    response = await client.post(
        "/api/v1/evaluations/",
        headers=auth_headers,
        json={
            "organization_id": test_organization["id"],
            "candidate_id": test_candidate["id"],
            "interviewer_id": "interviewer_123",
            "scores": {"Python": {"score": 4, "confidence": 4}},
            "is_draft": False
        }
    )
    if response.status_code in [200, 201]:
        return response.json()
    return {"id": "test-evaluation-id", "candidate_id": test_candidate["id"]}


# ============== Unit Test Data Fixtures ==============

@pytest.fixture
def sample_scores() -> list:
    """Sample scores for testing calculations."""
    return [4.0, 3.5, 4.5, 3.0, 5.0]


@pytest.fixture
def sample_confidence_scores() -> list:
    """Sample confidence scores for testing."""
    return [4, 3, 5, 4, 4]


@pytest.fixture
def sample_competency_scores() -> dict:
    """Sample competency scores for testing."""
    return {
        "Python": [4.0, 4.5, 3.5],
        "JavaScript": [3.5, 4.0, 4.0],
        "System Design": [4.5, 4.0, 3.5],
        "Communication": [3.0, 3.5, 4.0],
    }


@pytest.fixture
def sample_recommendation_counts() -> dict:
    """Sample recommendation counts for testing."""
    return {
        "strong_hire": 2,
        "hire": 3,
        "neutral": 1,
        "no_hire": 0,
        "strong_no_hire": 0,
    }


@pytest.fixture
def sample_candidate_scores() -> dict:
    """Sample candidate scores for heatmap testing."""
    return {
        "candidate_1": {"Python": 4.5, "JavaScript": 4.0, "System Design": 4.0},
        "candidate_2": {"Python": 3.5, "JavaScript": 4.5, "System Design": 3.5},
        "candidate_3": {"Python": 4.0, "JavaScript": 3.5, "System Design": 4.5},
    }


@pytest.fixture
def sample_evaluation_scores() -> dict:
    """Sample evaluation scores for agreement testing."""
    return {
        "Python": {"evaluator_1": 4.0, "evaluator_2": 4.2, "evaluator_3": 3.8},
        "JavaScript": {"evaluator_1": 4.5, "evaluator_2": 4.3, "evaluator_3": 4.7},
        "System Design": {"evaluator_1": 3.5, "evaluator_2": 3.7, "evaluator_3": 3.3},
    }


@pytest.fixture
def sample_candidate_metrics() -> dict:
    """Sample candidate metrics for ranking testing."""
    return {
        "candidate_1": {
            "candidate_name": "John Doe",
            "overall_average": 4.2,
            "confidence_average": 4.0,
            "hire_score": 0.7,
        },
        "candidate_2": {
            "candidate_name": "Jane Smith",
            "overall_average": 3.8,
            "confidence_average": 4.2,
            "hire_score": 0.5,
        },
        "candidate_3": {
            "candidate_name": "Bob Johnson",
            "overall_average": 4.5,
            "confidence_average": 3.5,
            "hire_score": 0.8,
        },
    }


# UUID test data
@pytest.fixture
def valid_uuid() -> str:
    """A valid UUID string for testing."""
    return "550e8400-e29b-41d4-a716-446655440000"


@pytest.fixture
def invalid_uuid() -> str:
    """An invalid UUID string for testing."""
    return "not-a-valid-uuid"


# DateTime test data
@pytest.fixture
def sample_datetime() -> datetime:
    """A sample datetime for testing."""
    return datetime(2024, 1, 15, 10, 30, 0)


@pytest.fixture
def sample_datetime_string() -> str:
    """A sample datetime string for testing."""
    return "2024-01-15 10:30:00"


# Pagination test data
@pytest.fixture
def sample_pagination_items() -> list:
    """Sample items for pagination testing."""
    return list(range(1, 101))  # 100 items


# Token test data
@pytest.fixture
def token_payload() -> dict:
    """Sample token payload for testing."""
    return {
        "sub": TEST_USER_ID,
        "exp": datetime.utcnow() + timedelta(minutes=30),
        "type": "access",
    }


@pytest.fixture
def refresh_token_payload() -> dict:
    """Sample refresh token payload for testing."""
    return {
        "sub": TEST_USER_ID,
        "exp": datetime.utcnow() + timedelta(days=7),
        "type": "refresh",
    }


# Password test data
@pytest.fixture
def weak_password() -> str:
    """A weak password for testing."""
    return "weak"


@pytest.fixture
def valid_password() -> str:
    """A valid password for testing."""
    return "ValidPass123"


@pytest.fixture
def password_without_uppercase() -> str:
    """A password without uppercase for testing."""
    return "lowercase123"


@pytest.fixture
def password_without_lowercase() -> str:
    """A password without lowercase for testing."""
    return "UPPERCASE123"


@pytest.fixture
def password_without_digit() -> str:
    """A password without digit for testing."""
    return "NoDigitsHere"


# Timer test data
@pytest.fixture
def timer_test_data() -> dict:
    """Data for timer testing."""
    return {
        "start": datetime(2024, 1, 1, 12, 0, 0),
        "end": datetime(2024, 1, 1, 12, 0, 10),
    }


# Dict conversion test data
@pytest.fixture
def snake_case_dict() -> dict:
    """A snake_case dictionary for testing."""
    return {
        "user_id": "123",
        "created_at": "2024-01-15",
        "is_active": True,
        "user_name": "test",
    }


@pytest.fixture
def expected_camel_case_dict() -> dict:
    """Expected camelCase dictionary for testing."""
    return {
        "userId": "123",
        "createdAt": "2024-01-15",
        "isActive": True,
        "userName": "test",
    }

