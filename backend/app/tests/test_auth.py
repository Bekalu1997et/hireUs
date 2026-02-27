"""
Tests for authentication service.

Feature: structured-interview-platform
"""
import pytest
from hypothesis import given, strategies as st
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.service import AuthService
from app.schemas.auth import UserRegister, UserLogin
from app.core.security import hash_password, decode_access_token


# Hypothesis strategies for generating valid test data
valid_email = st.emails()
valid_password = st.text(min_size=8, max_size=50).filter(
    lambda p: any(c.isupper() for c in p) and 
              any(c.islower() for c in p) and 
              any(c.isdigit() for c in p)
)
valid_name = st.text(min_size=1, max_size=255, alphabet=st.characters(blacklist_categories=('Cc', 'Cs')))
valid_domain = st.text(min_size=1, max_size=255, alphabet=st.characters(whitelist_categories=('Ll', 'Nd'), min_codepoint=97, max_codepoint=122))


# Feature: structured-interview-platform, Property 4: Authentication Correctness
@pytest.mark.property
@pytest.mark.asyncio
@given(
    email=valid_email,
    password=valid_password,
    full_name=valid_name,
    org_name=valid_name,
    org_domain=valid_domain
)
async def test_authentication_correctness_valid_credentials(
    db_session: AsyncSession,
    email: str,
    password: str,
    full_name: str,
    org_name: str,
    org_domain: str
):
    """
    Property 4: Authentication Correctness
    
    For any authentication attempt, valid credentials should result in a JWT
    token being issued, and invalid credentials should result in authentication
    rejection with an error.
    
    This test verifies the positive case: valid credentials issue a token.
    
    Validates: Requirements 2.1, 2.2
    """
    service = AuthService(db_session)
    
    # Register user
    user_data = UserRegister(
        email=email,
        password=password,
        full_name=full_name,
        organization_name=org_name,
        organization_domain=org_domain
    )
    
    user, register_token = await service.register_user(user_data)
    
    # Verify registration created user and token
    assert user is not None
    assert user.email == email
    assert register_token is not None
    
    # Verify token is valid
    decoded = decode_access_token(register_token)
    assert decoded is not None
    assert decoded["sub"] == email
    assert decoded["user_id"] == user.id
    
    # Now test login with valid credentials
    login_data = UserLogin(email=email, password=password)
    login_user, login_token = await service.login_user(login_data)
    
    # Verify login succeeded and returned token
    assert login_user is not None
    assert login_user.id == user.id
    assert login_token is not None
    
    # Verify login token is valid
    decoded_login = decode_access_token(login_token)
    assert decoded_login is not None
    assert decoded_login["sub"] == email
    assert decoded_login["user_id"] == user.id


@pytest.mark.property
@pytest.mark.asyncio
@given(
    email=valid_email,
    password=valid_password,
    wrong_password=valid_password,
    full_name=valid_name,
    org_name=valid_name,
    org_domain=valid_domain
)
async def test_authentication_correctness_invalid_credentials(
    db_session: AsyncSession,
    email: str,
    password: str,
    wrong_password: str,
    full_name: str,
    org_name: str,
    org_domain: str
):
    """
    Property 4: Authentication Correctness (negative case)
    
    For any authentication attempt with invalid credentials, the system
    should reject authentication and return an error.
    
    Validates: Requirements 2.1, 2.2
    """
    # Skip if passwords happen to be the same
    if password == wrong_password:
        return
    
    service = AuthService(db_session)
    
    # Register user
    user_data = UserRegister(
        email=email,
        password=password,
        full_name=full_name,
        organization_name=org_name,
        organization_domain=org_domain
    )
    
    await service.register_user(user_data)
    
    # Try to login with wrong password
    login_data = UserLogin(email=email, password=wrong_password)
    
    with pytest.raises(HTTPException) as exc_info:
        await service.login_user(login_data)
    
    # Verify authentication was rejected
    assert exc_info.value.status_code == 401
    assert "Incorrect email or password" in str(exc_info.value.detail)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_register_user_creates_organization_and_founder(db_session: AsyncSession):
    """Test that user registration creates both organization and founder user."""
    service = AuthService(db_session)
    
    user_data = UserRegister(
        email="founder@startup.com",
        password="StrongPass123",
        full_name="John Founder",
        organization_name="My Startup",
        organization_domain="mystartup.com"
    )
    
    user, token = await service.register_user(user_data)
    
    # Verify user was created
    assert user.id is not None
    assert user.email == "founder@startup.com"
    assert user.full_name == "John Founder"
    assert user.role == "founder"
    
    # Verify organization was created
    assert user.organization is not None
    assert user.organization.name == "My Startup"
    assert user.organization.domain == "mystartup.com"
    
    # Verify token was issued
    assert token is not None
    decoded = decode_access_token(token)
    assert decoded["user_id"] == user.id
    assert decoded["role"] == "founder"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_register_user_rejects_duplicate_email(db_session: AsyncSession):
    """Test that registration rejects duplicate email addresses."""
    service = AuthService(db_session)
    
    user_data = UserRegister(
        email="duplicate@example.com",
        password="StrongPass123",
        full_name="First User",
        organization_name="First Org",
        organization_domain="first.com"
    )
    
    # First registration should succeed
    await service.register_user(user_data)
    
    # Second registration with same email should fail
    user_data2 = UserRegister(
        email="duplicate@example.com",
        password="DifferentPass123",
        full_name="Second User",
        organization_name="Second Org",
        organization_domain="second.com"
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await service.register_user(user_data2)
    
    assert exc_info.value.status_code == 400
    assert "Email already registered" in str(exc_info.value.detail)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_register_user_rejects_duplicate_domain(db_session: AsyncSession):
    """Test that registration rejects duplicate organization domains."""
    service = AuthService(db_session)
    
    user_data = UserRegister(
        email="user1@example.com",
        password="StrongPass123",
        full_name="First User",
        organization_name="First Org",
        organization_domain="duplicate.com"
    )
    
    # First registration should succeed
    await service.register_user(user_data)
    
    # Second registration with same domain should fail
    user_data2 = UserRegister(
        email="user2@example.com",
        password="StrongPass123",
        full_name="Second User",
        organization_name="Second Org",
        organization_domain="duplicate.com"
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await service.register_user(user_data2)
    
    assert exc_info.value.status_code == 400
    assert "Organization domain already exists" in str(exc_info.value.detail)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_register_user_rejects_weak_password(db_session: AsyncSession):
    """Test that registration rejects weak passwords."""
    service = AuthService(db_session)
    
    user_data = UserRegister(
        email="user@example.com",
        password="weak",  # Too short, no uppercase, no number
        full_name="Test User",
        organization_name="Test Org",
        organization_domain="test.com"
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await service.register_user(user_data)
    
    assert exc_info.value.status_code == 400


@pytest.mark.unit
@pytest.mark.asyncio
async def test_login_user_with_valid_credentials(db_session: AsyncSession):
    """Test login with valid credentials."""
    service = AuthService(db_session)
    
    # Register user
    register_data = UserRegister(
        email="login@example.com",
        password="StrongPass123",
        full_name="Login User",
        organization_name="Login Org",
        organization_domain="login.com"
    )
    user, _ = await service.register_user(register_data)
    
    # Login with valid credentials
    login_data = UserLogin(email="login@example.com", password="StrongPass123")
    login_user, token = await service.login_user(login_data)
    
    assert login_user.id == user.id
    assert token is not None
    
    decoded = decode_access_token(token)
    assert decoded["user_id"] == user.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_login_user_with_invalid_email(db_session: AsyncSession):
    """Test login with non-existent email."""
    service = AuthService(db_session)
    
    login_data = UserLogin(email="nonexistent@example.com", password="AnyPass123")
    
    with pytest.raises(HTTPException) as exc_info:
        await service.login_user(login_data)
    
    assert exc_info.value.status_code == 401


@pytest.mark.unit
@pytest.mark.asyncio
async def test_login_user_with_invalid_password(db_session: AsyncSession):
    """Test login with incorrect password."""
    service = AuthService(db_session)
    
    # Register user
    register_data = UserRegister(
        email="user@example.com",
        password="CorrectPass123",
        full_name="Test User",
        organization_name="Test Org",
        organization_domain="test.com"
    )
    await service.register_user(register_data)
    
    # Try to login with wrong password
    login_data = UserLogin(email="user@example.com", password="WrongPass123")
    
    with pytest.raises(HTTPException) as exc_info:
        await service.login_user(login_data)
    
    assert exc_info.value.status_code == 401


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_current_user_with_valid_token(db_session: AsyncSession):
    """Test getting current user with valid token."""
    service = AuthService(db_session)
    
    # Register user
    register_data = UserRegister(
        email="current@example.com",
        password="StrongPass123",
        full_name="Current User",
        organization_name="Current Org",
        organization_domain="current.com"
    )
    user, token = await service.register_user(register_data)
    
    # Get current user from token
    current_user = await service.get_current_user(token)
    
    assert current_user.id == user.id
    assert current_user.email == user.email


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_current_user_with_invalid_token(db_session: AsyncSession):
    """Test getting current user with invalid token."""
    service = AuthService(db_session)
    
    with pytest.raises(HTTPException) as exc_info:
        await service.get_current_user("invalid.token.here")
    
    assert exc_info.value.status_code == 401



# Feature: structured-interview-platform, Property 5: Role-Based Access Control Enforcement
@pytest.mark.property
@pytest.mark.asyncio
@given(
    founder_email=valid_email,
    interviewer_email=valid_email,
    password=valid_password,
    founder_name=valid_name,
    interviewer_name=valid_name,
    org_name=valid_name,
    org_domain=valid_domain
)
async def test_role_based_access_control_enforcement(
    db_session: AsyncSession,
    founder_email: str,
    interviewer_email: str,
    password: str,
    founder_name: str,
    interviewer_name: str,
    org_name: str,
    org_domain: str
):
    """
    Property 5: Role-Based Access Control Enforcement
    
    For any protected endpoint and any user, access should be granted if and
    only if the user's role has permission for that endpoint.
    
    This test verifies that founders have founder access and interviewers
    do not have founder access.
    
    Validates: Requirements 2.3
    """
    # Skip if emails are the same
    if founder_email == interviewer_email:
        return
    
    service = AuthService(db_session)
    
    # Create founder
    founder_data = UserRegister(
        email=founder_email,
        password=password,
        full_name=founder_name,
        organization_name=org_name,
        organization_domain=org_domain
    )
    founder, _ = await service.register_user(founder_data)
    
    # Create interviewer (manually, as we don't have invite system yet)
    from app.modules.auth.repository import AuthRepository
    from app.core.security import hash_password
    
    repo = AuthRepository(db_session)
    interviewer = await repo.create_user(
        email=interviewer_email,
        hashed_password=hash_password(password),
        full_name=interviewer_name,
        role="interviewer",
        organization_id=founder.organization_id
    )
    await db_session.commit()
    
    # Test founder role validation
    # Founder should pass founder validation
    try:
        service.validate_user_role(founder, "founder")
        founder_has_founder_access = True
    except HTTPException:
        founder_has_founder_access = False
    
    assert founder_has_founder_access is True
    
    # Interviewer should NOT pass founder validation
    try:
        service.validate_user_role(interviewer, "founder")
        interviewer_has_founder_access = True
    except HTTPException:
        interviewer_has_founder_access = False
    
    assert interviewer_has_founder_access is False
    
    # Interviewer should pass interviewer validation
    try:
        service.validate_user_role(interviewer, "interviewer")
        interviewer_has_interviewer_access = True
    except HTTPException:
        interviewer_has_interviewer_access = False
    
    assert interviewer_has_interviewer_access is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_user_role_founder(db_session: AsyncSession):
    """Test role validation for founder role."""
    service = AuthService(db_session)
    
    # Create founder
    user_data = UserRegister(
        email="founder@example.com",
        password="StrongPass123",
        full_name="Founder User",
        organization_name="Test Org",
        organization_domain="test.com"
    )
    user, _ = await service.register_user(user_data)
    
    # Founder should pass founder validation
    service.validate_user_role(user, "founder")  # Should not raise
    
    # Founder should fail interviewer validation
    with pytest.raises(HTTPException) as exc_info:
        service.validate_user_role(user, "interviewer")
    
    assert exc_info.value.status_code == 403


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_user_organization(db_session: AsyncSession):
    """Test organization validation."""
    service = AuthService(db_session)
    
    # Create user
    user_data = UserRegister(
        email="user@example.com",
        password="StrongPass123",
        full_name="Test User",
        organization_name="Test Org",
        organization_domain="test.com"
    )
    user, _ = await service.register_user(user_data)
    
    # User should pass validation for their own organization
    service.validate_user_organization(user, user.organization_id)  # Should not raise
    
    # User should fail validation for different organization
    with pytest.raises(HTTPException) as exc_info:
        service.validate_user_organization(user, 99999)
    
    assert exc_info.value.status_code == 403
    assert "does not have access" in str(exc_info.value.detail)


@pytest.mark.property
@pytest.mark.asyncio
@given(
    email1=valid_email,
    email2=valid_email,
    password=valid_password,
    name1=valid_name,
    name2=valid_name,
    org1_name=valid_name,
    org2_name=valid_name,
    org1_domain=valid_domain,
    org2_domain=valid_domain
)
async def test_organization_isolation(
    db_session: AsyncSession,
    email1: str,
    email2: str,
    password: str,
    name1: str,
    name2: str,
    org1_name: str,
    org2_name: str,
    org1_domain: str,
    org2_domain: str
):
    """
    Property test: Users from different organizations should be isolated.
    
    For any two users from different organizations, one user should not
    have access to the other's organization.
    """
    # Skip if emails or domains are the same
    if email1 == email2 or org1_domain == org2_domain:
        return
    
    service = AuthService(db_session)
    
    # Create first user and organization
    user1_data = UserRegister(
        email=email1,
        password=password,
        full_name=name1,
        organization_name=org1_name,
        organization_domain=org1_domain
    )
    user1, _ = await service.register_user(user1_data)
    
    # Create second user and organization
    user2_data = UserRegister(
        email=email2,
        password=password,
        full_name=name2,
        organization_name=org2_name,
        organization_domain=org2_domain
    )
    user2, _ = await service.register_user(user2_data)
    
    # Verify users are in different organizations
    assert user1.organization_id != user2.organization_id
    
    # User1 should not have access to User2's organization
    try:
        service.validate_user_organization(user1, user2.organization_id)
        user1_has_access_to_org2 = True
    except HTTPException:
        user1_has_access_to_org2 = False
    
    assert user1_has_access_to_org2 is False
    
    # User2 should not have access to User1's organization
    try:
        service.validate_user_organization(user2, user1.organization_id)
        user2_has_access_to_org1 = True
    except HTTPException:
        user2_has_access_to_org1 = False
    
    assert user2_has_access_to_org1 is False
