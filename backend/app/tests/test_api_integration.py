"""
API Integration Tests for Authentication Endpoints.
Tests API endpoints against the test database override from conftest fixtures.
"""
import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.integration
class TestAuthAPI:
    """Test authentication API endpoints."""

    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "healthy"

    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint."""
        response = await client.get("/")
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()

    async def test_register_valid(self, client: AsyncClient):
        """Test user registration with valid data."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "TestPass123",
                "confirm_password": "TestPass123",
                "full_name": "New User"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_register_invalid_password(self, client: AsyncClient):
        """Test registration with invalid password (no uppercase)."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "user@example.com",
                "password": "testpass123",
                "confirm_password": "testpass123",
                "full_name": "Test User"
            }
        )
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
        ]

    async def test_register_password_mismatch(self, client: AsyncClient):
        """Test registration with password mismatch."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "user2@example.com",
                "password": "TestPass123",
                "confirm_password": "DifferentPass123",
                "full_name": "Test User",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_login_success(self, client: AsyncClient):
        """Test login with valid credentials."""
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "logintest@example.com",
                "password": "TestPass123",
                "confirm_password": "TestPass123",
                "full_name": "Login Test",
            },
        )

        response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "email": "logintest@example.com",
                "password": "TestPass123",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data

    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials."""
        response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "email": "nonexistent@example.com",
                "password": "WrongPass123",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_protected_endpoint_without_token(self, client: AsyncClient):
        """Test accessing protected endpoint without token."""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_protected_endpoint_with_token(self, client: AsyncClient):
        """Test accessing protected endpoint with valid token."""
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "protected@example.com",
                "password": "TestPass123",
                "confirm_password": "TestPass123",
                "full_name": "Protected User",
            },
        )
        token = register_response.json()["access_token"]

        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "protected@example.com"


@pytest.mark.integration
class TestRolesAPI:
    """Test Roles API endpoints."""

    async def test_list_roles_unauthorized(self, client: AsyncClient):
        """Test listing roles without authentication."""
        response = await client.get("/api/v1/roles/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
class TestWorkflowsAPI:
    """Test Workflows API endpoints."""

    async def test_list_workflows_unauthorized(self, client: AsyncClient):
        """Test listing workflows without authentication."""
        response = await client.get("/api/v1/workflows/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
class TestInterviewKitsAPI:
    """Test Interview Kits API endpoints."""

    async def test_list_kits_unauthorized(self, client: AsyncClient):
        """Test listing interview kits without authentication."""
        response = await client.get("/api/v1/interview-kits/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
class TestCandidatesAPI:
    """Test Candidates API endpoints."""

    async def test_list_candidates_unauthorized(self, client: AsyncClient):
        """Test listing candidates without authentication."""
        response = await client.get("/api/v1/candidates/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
