"""
Router for authentication endpoints.

Provides REST API endpoints for user registration, login, and token validation.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.auth.service import AuthService
from app.schemas.auth import UserRegister, UserLogin, Token, UserResponse
from app.db.models import User


router = APIRouter()
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Usage:
        @router.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"user_id": current_user.id}
    """
    service = AuthService(db)
    return await service.get_current_user(credentials.credentials)


async def get_current_founder(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure the current user is a founder.
    
    Usage:
        @router.post("/admin-only")
        async def admin_route(founder: User = Depends(get_current_founder)):
            return {"message": "Founder access granted"}
    """
    if current_user.role != "founder":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only founders can perform this action"
        )
    return current_user


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
) -> Token:
    """
    Register a new user and create their organization.
    
    Creates both an organization and a founder user. The founder will have
    full access to the organization.
    
    Args:
        user_data: User registration data including email, password, name, and organization details
        
    Returns:
        JWT access token for the newly created user
        
    Raises:
        400: If email already exists, domain already exists, or password is weak
        
    Example:
        POST /api/auth/register
        {
            "email": "founder@startup.com",
            "password": "StrongPass123",
            "full_name": "John Doe",
            "organization_name": "My Startup",
            "organization_domain": "mystartup.com"
        }
    """
    service = AuthService(db)
    user, token = await service.register_user(user_data)
    
    return Token(access_token=token)


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> Token:
    """
    Authenticate a user and return a JWT token.
    
    Args:
        login_data: User login credentials (email and password)
        
    Returns:
        JWT access token
        
    Raises:
        401: If credentials are invalid
        
    Example:
        POST /api/auth/login
        {
            "email": "founder@startup.com",
            "password": "StrongPass123"
        }
    """
    service = AuthService(db)
    user, token = await service.login_user(login_data)
    
    return Token(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get the current authenticated user's information.
    
    Requires a valid JWT token in the Authorization header.
    
    Args:
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        Current user's information
        
    Example:
        GET /api/auth/me
        Authorization: Bearer <token>
    """
    return UserResponse.model_validate(current_user)


@router.post("/validate-token")
async def validate_token(
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Validate a JWT token.
    
    This endpoint can be used to check if a token is still valid.
    
    Args:
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        Validation status
        
    Example:
        POST /api/auth/validate-token
        Authorization: Bearer <token>
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role
    }
