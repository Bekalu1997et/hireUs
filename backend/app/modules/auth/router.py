"""
Authentication router.
Defines API endpoints for authentication operations.
"""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm

from app.db.session import AsyncSession, get_db
from app.modules.auth.service import AuthService
from app.modules.auth.repository import UserRepository
from app.schemas.token import (
    Token,
    LoginRequest,
    RegisterRequest,
    RefreshTokenRequest,
    ChangePasswordRequest,
    UserUpdate,
    UserResponse,
    Message,
    UserListResponse,
    HealthCheck,
)
from app.core.security import (
    get_current_user,
    get_current_active_user,
    get_current_superuser,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    register_data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.
    """
    service = AuthService(db)
    return await service.register(register_data)


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email and password.
    Returns access and refresh tokens.
    """
    service = AuthService(db)
    login_data = LoginRequest(email=form_data.username, password=form_data.password)
    return await service.login(login_data)


@router.post("/login/json", response_model=Token)
async def login_json(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with JSON body.
    Alternative to form-based login.
    """
    service = AuthService(db)
    return await service.login(login_data)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    """
    service = AuthService(db)
    return await service.refresh_token(refresh_data.refresh_token)


@router.post("/change-password", response_model=Message)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change password for authenticated user.
    """
    service = AuthService(db)
    await service.change_password(current_user.id, password_data)
    return Message(message="Password changed successfully")


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user = Depends(get_current_active_user)
):
    """
    Get current authenticated user profile.
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_me(
    user_data: UserUpdate,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user profile.
    """
    service = AuthService(db)
    return await service.update_user(current_user.id, user_data)


@router.get("/users", response_model=UserListResponse)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: bool = Query(None),
    current_user = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated list of users.
    Only accessible by superusers.
    """
    service = AuthService(db)
    users = await service.get_users(skip=skip, limit=limit, is_active=is_active)
    total = await service.count_users(is_active=is_active)
    
    return UserListResponse(
        items=[UserResponse.model_validate(user) for user in users],
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        total_pages=(total + limit - 1) // limit
    )


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user by ID.
    """
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(user)


@router.delete("/users/{user_id}", response_model=Message)
async def deactivate_user(
    user_id: str,
    current_user = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate a user.
    Only accessible by superusers.
    """
    service = AuthService(db)
    await service.deactivate_user(user_id)
    return Message(message="User deactivated successfully")


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Health check endpoint.
    """
    return HealthCheck(
        status="healthy",
        database="connected",
        version="1.0.0"
    )

