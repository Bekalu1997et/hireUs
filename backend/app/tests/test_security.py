"""
Tests for security utilities (password hashing and JWT tokens).

Feature: structured-interview-platform
"""
import pytest
from hypothesis import given, strategies as st
from datetime import timedelta

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    create_user_token,
    validate_password_strength,
)


# Feature: structured-interview-platform, Property 7: Password Security
@pytest.mark.property
@given(password=st.text(min_size=1, max_size=100))
def test_password_never_stored_plaintext(password):
    """
    Property 7: Password Security
    
    For any user creation or password update, the stored password should
    never match the plaintext password (must be hashed and salted).
    
    Validates: Requirements 2.5
    """
    hashed = hash_password(password)
    
    # The hashed password should never equal the plaintext password
    assert hashed != password
    
    # The hashed password should be a non-empty string
    assert isinstance(hashed, str)
    assert len(hashed) > 0
    
    # The hash should start with bcrypt identifier
    assert hashed.startswith("$2b$")


@pytest.mark.property
@given(password=st.text(min_size=1, max_size=100))
def test_password_hash_verification_round_trip(password):
    """
    Property test: Password hashing and verification round trip.
    
    For any password, hashing it and then verifying should return True.
    """
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


@pytest.mark.property
@given(
    password=st.text(min_size=1, max_size=100),
    wrong_password=st.text(min_size=1, max_size=100)
)
def test_password_verification_rejects_wrong_password(password, wrong_password):
    """
    Property test: Wrong passwords should be rejected.
    
    For any two different passwords, verifying one against the hash
    of the other should return False.
    """
    # Skip if passwords happen to be the same
    if password == wrong_password:
        return
    
    hashed = hash_password(password)
    assert verify_password(wrong_password, hashed) is False


@pytest.mark.property
@given(password=st.text(min_size=1, max_size=100))
def test_password_hash_is_deterministic_per_call(password):
    """
    Property test: Each hash call produces a unique hash (due to salt).
    
    For any password, hashing it twice should produce different hashes
    (because bcrypt uses a random salt), but both should verify correctly.
    """
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    
    # Hashes should be different (due to random salt)
    assert hash1 != hash2
    
    # But both should verify the original password
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True


@pytest.mark.unit
def test_jwt_token_creation_and_decoding():
    """Test JWT token creation and decoding."""
    data = {"sub": "test@example.com", "role": "founder"}
    token = create_access_token(data)
    
    assert isinstance(token, str)
    assert len(token) > 0
    
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "test@example.com"
    assert decoded["role"] == "founder"
    assert "exp" in decoded


@pytest.mark.unit
def test_jwt_token_expiration():
    """Test JWT token expiration."""
    data = {"sub": "test@example.com"}
    
    # Create token that expires in 1 second
    token = create_access_token(data, expires_delta=timedelta(seconds=-1))
    
    # Token should be expired and return None
    decoded = decode_access_token(token)
    assert decoded is None


@pytest.mark.unit
def test_jwt_token_invalid():
    """Test that invalid JWT tokens return None."""
    invalid_token = "invalid.token.here"
    decoded = decode_access_token(invalid_token)
    assert decoded is None


@pytest.mark.unit
def test_create_user_token():
    """Test creating a user token with standard claims."""
    token = create_user_token(
        user_id=1,
        email="founder@startup.com",
        role="founder",
        organization_id=1
    )
    
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "founder@startup.com"
    assert decoded["user_id"] == 1
    assert decoded["role"] == "founder"
    assert decoded["organization_id"] == 1


@pytest.mark.unit
def test_password_strength_validation():
    """Test password strength validation."""
    # Too short
    valid, error = validate_password_strength("Short1")
    assert valid is False
    assert "8 characters" in error
    
    # No uppercase
    valid, error = validate_password_strength("lowercase123")
    assert valid is False
    assert "uppercase" in error
    
    # No lowercase
    valid, error = validate_password_strength("UPPERCASE123")
    assert valid is False
    assert "lowercase" in error
    
    # No number
    valid, error = validate_password_strength("NoNumbers")
    assert valid is False
    assert "number" in error
    
    # Valid password
    valid, error = validate_password_strength("StrongPass123")
    assert valid is True
    assert error is None


@pytest.mark.property
@given(
    user_id=st.integers(min_value=1, max_value=1000000),
    email=st.emails(),
    role=st.sampled_from(["founder", "interviewer"]),
    org_id=st.integers(min_value=1, max_value=1000000)
)
def test_user_token_round_trip(user_id, email, role, org_id):
    """
    Property test: User token creation and decoding round trip.
    
    For any valid user data, creating a token and decoding it should
    return the same data.
    """
    token = create_user_token(user_id, email, role, org_id)
    decoded = decode_access_token(token)
    
    assert decoded is not None
    assert decoded["user_id"] == user_id
    assert decoded["sub"] == email
    assert decoded["role"] == role
    assert decoded["organization_id"] == org_id
