"""
Authentication service.
Handles business logic for authentication operations.
"""
from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.token import (
    Token,
    LoginRequest,
    RegisterRequest,
    ChangePasswordRequest,
)
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    create_tokens_response,
)
from app.core.config import settings


class AuthService:
    """
    Authentication service.
    Handles business logic for authentication.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize with database session.
        """
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def register(self, register_data: RegisterRequest) -> Token:
        """
        Register a new user.
        """
        # Check if passwords match
        if register_data.password != register_data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match"
            )
        
        # Check if email already exists
        existing_user = await self.user_repo.get_by_email(register_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user = await self.user_repo.create(register_data)
        
        # Create tokens
        access_token = create_access_token(data={"sub": user.id})
        refresh_token = create_refresh_token(data={"sub": user.id})
        
        # Create response
        return create_tokens_response(access_token, refresh_token)
    
    async def login(self, login_data: LoginRequest) -> Token:
        """
        Authenticate user and return tokens.
        """
        # Authenticate user
        user = await self.user_repo.authenticate(
            login_data.email, 
            login_data.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Update last login
        await self.user_repo.update_last_login(user.id)
        
        # Create tokens
        access_token = create_access_token(data={"sub": user.id})
        refresh_token = create_refresh_token(data={"sub": user.id})
        
        return create_tokens_response(access_token, refresh_token)
    
    async def refresh_token(self, refresh_token: str) -> Token:
        """
        Refresh access token using refresh token.
        """
        from jose import jwt, JWTError
        
        try:
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create new tokens
        new_access_token = create_access_token(data={"sub": user_id})
        new_refresh_token = create_refresh_token(data={"sub": user_id})
        
        return create_tokens_response(new_access_token, new_refresh_token)
    
    async def change_password(
        self, 
        user_id: str, 
        password_data: ChangePasswordRequest
    ) -> bool:
        """
        Change user password.
        """
        # Get user
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(password_data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Check new passwords match
        if password_data.new_password != password_data.confirm_new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New passwords do not match"
            )
        
        # Update password
        new_hashed_password = get_password_hash(password_data.new_password)
        await self.user_repo.update_password(user_id, new_hashed_password)
        
        return True
    
    async def validate_password(self, password: str) -> tuple[bool, str]:
        """
        Validate password strength.
        Returns (is_valid, error_message).
        """
        if len(password) < settings.PASSWORD_MIN_LENGTH:
            return False, f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters"
        
        # Check for uppercase
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        # Check for lowercase
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        # Check for digit
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        
        return True, ""
    
    async def get_user_by_id(self, user_id: str):
        """
        Get user by ID.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    
    async def update_user(self, user_id: str, user_data: UserUpdate):
        """
        Update user profile.
        """
        user = await self.user_repo.update(user_id, user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    
    async def deactivate_user(self, user_id: str):
        """
        Deactivate user account.
        """
        user = await self.user_repo.deactivate(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    
    async def get_users(
        self, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None
    ):
        """
        Get paginated list of users.
        """
        return await self.user_repo.get_all(skip, limit, is_active)
    
    async def count_users(self, is_active: Optional[bool] = None) -> int:
        """
        Count total users.
        """
        return await self.user_repo.count(is_active)

