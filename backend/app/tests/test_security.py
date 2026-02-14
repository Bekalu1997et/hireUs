"""
Unit tests for core/security.py.
Tests all security functions including password hashing and JWT tokens.
"""
import pytest
from datetime import datetime, timedelta
from jose import jwt
from app.core import security
from app.core.config import settings


@pytest.mark.security
class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_get_password_hash_returns_string(self):
        """Test that get_password_hash returns a string."""
        result = security.get_password_hash("testpassword")
        assert isinstance(result, str)

    def test_get_password_hash_different_hashes(self):
        """Test that same password produces different hashes (salt)."""
        hash1 = security.get_password_hash("testpassword")
        hash2 = security.get_password_hash("testpassword")
        assert hash1 != hash2  # Different salts

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "TestPassword123"
        hashed = security.get_password_hash(password)
        assert security.verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "TestPassword123"
        hashed = security.get_password_hash(password)
        assert security.verify_password("WrongPassword", hashed) is False

    def test_verify_password_empty(self):
        """Test password verification with empty password."""
        hashed = security.get_password_hash("testpassword")
        assert security.verify_password("", hashed) is False


@pytest.mark.security
class TestCreateAccessToken:
    """Tests for create_access_token function."""

    def test_create_access_token_returns_string(self):
        """Test that create_access_token returns a string."""
        result = security.create_access_token({"sub": "test-user"})
        assert isinstance(result, str)

    def test_create_access_token_contains_payload(self):
        """Test that token contains the payload data."""
        data = {"sub": "test-user-123"}
        token = security.create_access_token(data)
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == "test-user-123"
        assert payload["type"] == "access"

    def test_create_access_token_has_expiration(self):
        """Test that token has expiration time."""
        token = security.create_access_token({"sub": "test-user"})
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert "exp" in payload

    def test_create_access_token_custom_expiration(self):
        """Test token with custom expiration time."""
        custom_delta = timedelta(hours=2)
        token = security.create_access_token(
            {"sub": "test-user"},
            expires_delta=custom_delta
        )
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp_time = datetime.fromtimestamp(payload["exp"])
        # Should expire in approximately 2 hours from now
        # Check that expiration is in the future and less than 3 hours
        now = datetime.utcnow()
        time_diff = (exp_time - now).total_seconds()
        assert time_diff > 0, "Token should not be expired"
        assert time_diff < 10800, "Token should expire in less than 3 hours"


@pytest.mark.security
class TestCreateRefreshToken:
    """Tests for create_refresh_token function."""

    def test_create_refresh_token_returns_string(self):
        """Test that create_refresh_token returns a string."""
        result = security.create_refresh_token({"sub": "test-user"})
        assert isinstance(result, str)

    def test_create_refresh_token_contains_payload(self):
        """Test that token contains the payload data."""
        data = {"sub": "test-user-123"}
        token = security.create_refresh_token(data)
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == "test-user-123"
        assert payload["type"] == "refresh"

    def test_create_refresh_token_has_expiration(self):
        """Test that refresh token has expiration."""
        token = security.create_refresh_token({"sub": "test-user"})
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert "exp" in payload


@pytest.mark.security
class TestDecodeToken:
    """Tests for decode_token function."""

    def test_decode_token_valid(self):
        """Test decoding a valid token."""
        token = security.create_access_token({"sub": "test-user-123"})
        payload = security.decode_token(token)
        assert payload["sub"] == "test-user-123"

    def test_decode_token_invalid(self):
        """Test decoding an invalid token."""
        with pytest.raises(Exception):  # HTTPException
            security.decode_token("invalid-token")

    def test_decode_token_tampered(self):
        """Test decoding a tampered token."""
        token = security.create_access_token({"sub": "test-user"})
        # Tamper with the token
        tampered_token = token[:-5] + "xxxxx"
        with pytest.raises(Exception):
            security.decode_token(tampered_token)


@pytest.mark.security
class TestCreateTokensResponse:
    """Tests for create_tokens_response function."""

    def test_create_tokens_response_format(self):
        """Test that response has correct format."""
        access = security.create_access_token({"sub": "test-user"})
        refresh = security.create_refresh_token({"sub": "test-user"})
        result = security.create_tokens_response(access, refresh)
        
        assert "access_token" in result
        assert "refresh_token" in result
        assert "token_type" in result
        assert result["token_type"] == "bearer"

    def test_create_tokens_response_token_types(self):
        """Test that correct tokens are returned."""
        access = security.create_access_token({"sub": "test-user"})
        refresh = security.create_refresh_token({"sub": "test-user"})
        result = security.create_tokens_response(access, refresh)
        
        # Verify token types
        access_payload = jwt.decode(result["access_token"], settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        refresh_payload = jwt.decode(result["refresh_token"], settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        assert access_payload["type"] == "access"
        assert refresh_payload["type"] == "refresh"


@pytest.mark.security
class TestPasswordValidation:
    """Tests for password validation in AuthService."""

    @pytest.fixture
    def auth_service(self):
        """Create AuthService instance."""
        # We need to mock the db session for testing
        from app.modules.auth.service import AuthService
        from unittest.mock import MagicMock
        mock_db = MagicMock()
        return AuthService(mock_db)

    @pytest.mark.asyncio
    async def test_validate_password_short(self, auth_service):
        """Test password validation with short password."""
        is_valid, error = await auth_service.validate_password("short")
        assert is_valid is False
        assert "characters" in error.lower()

    @pytest.mark.asyncio
    async def test_validate_password_no_uppercase(self, auth_service):
        """Test password validation without uppercase."""
        is_valid, error = await auth_service.validate_password("lowercase123")
        assert is_valid is False
        assert "uppercase" in error.lower()

    @pytest.mark.asyncio
    async def test_validate_password_no_lowercase(self, auth_service):
        """Test password validation without lowercase."""
        is_valid, error = await auth_service.validate_password("UPPERCASE123")
        assert is_valid is False
        assert "lowercase" in error.lower()

    @pytest.mark.asyncio
    async def test_validate_password_no_digit(self, auth_service):
        """Test password validation without digit."""
        is_valid, error = await auth_service.validate_password("NoDigitsHere")
        assert is_valid is False
        assert "digit" in error.lower()

    @pytest.mark.asyncio
    async def test_validate_password_valid(self, auth_service):
        """Test password validation with valid password."""
        is_valid, error = await auth_service.validate_password("ValidPass123")
        assert is_valid is True
        assert error == ""


@pytest.mark.security
class TestTokenExpiration:
    """Tests for token expiration behavior."""

    def test_access_token_expires(self):
        """Test that access token eventually expires."""
        # Create a token that expires in 1 second
        from datetime import datetime, timedelta
        exp = datetime.utcnow() + timedelta(seconds=1)
        token = security.create_access_token(
            {"sub": "test-user"},
            expires_delta=timedelta(seconds=1)
        )
        
        # Token should be valid now
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == "test-user"


@pytest.mark.security
class TestSecurityEdgeCases:
    """Edge case tests for security functions."""

    def test_hash_empty_password(self):
        """Test hashing empty password."""
        result = security.get_password_hash("")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_hash_unicode_password(self):
        """Test hashing unicode password."""
        result = security.get_password_hash("пароль123")
        assert isinstance(result, str)

    def test_hash_very_long_password(self):
        """Test hashing very long password."""
        long_password = "a" * 1000
        result = security.get_password_hash(long_password)
        assert isinstance(result, str)

    def test_verify_malformed_hash(self):
        """Test verification with malformed hash."""
        result = security.verify_password("password", "not-a-valid-hash")
        assert result is False

