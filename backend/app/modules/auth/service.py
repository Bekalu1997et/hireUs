"""
Service layer for authentication operations.

Handles business logic for user registration, login, and token validation.
"""
from typing import Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    hash_password,
    verify_password,
    create_user_token,
    decode_access_token,
    validate_password_strength,
)
from app.modules.auth.repository import AuthRepository
from app.db.models import User
from app.schemas.auth import UserRegister, UserLogin, Token, TokenData


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = AuthRepository(db)
    
    async def register_user(self, user_data: UserRegister) -> Tuple[User, str]:
        """
        Register a new user and create their organization.
        
        This creates both an organization and a founder user in a transaction.
        
        Args:
            user_data: User registration data
            
        Returns:
            Tuple of (created User, JWT token)
            
        Raises:
            HTTPException: If email already exists, domain already exists,
                          or password is weak
        """
        # Validate password strength
        is_valid, error_message = validate_password_strength(user_data.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )

        async with self.db.begin_nested():
            # Check if user already exists
            existing_user = await self.repository.get_user_by_email(user_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

            # Check if organization domain already exists
            existing_org = await self.repository.get_organization_by_domain(
                user_data.organization_domain
            )
            if existing_org:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Organization domain already exists"
                )

            # Create organization
            organization = await self.repository.create_organization(
                name=user_data.organization_name,
                domain=user_data.organization_domain
            )

            # Hash password
            hashed_password = hash_password(user_data.password)

            # Create user as founder
            user = await self.repository.create_user(
                email=user_data.email,
                hashed_password=hashed_password,
                full_name=user_data.full_name,
                role="founder",
                organization_id=organization.id
            )

        # Create token after successful transaction
        token = create_user_token(
            user_id=user.id,
            email=user.email,
            role=user.role,
            organization_id=user.organization_id
        )

        return user, token
    
    async def login_user(self, login_data: UserLogin) -> Tuple[User, str]:
        """
        Authenticate a user and return a JWT token.
        
        Args:
            login_data: User login credentials
            
        Returns:
            Tuple of (authenticated User, JWT token)
            
        Raises:
            HTTPException: If credentials are invalid
        """
        # Get user by email
        user = await self.repository.get_user_by_email(login_data.email)
        
        # Verify user exists and password is correct
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create token
        token = create_user_token(
            user_id=user.id,
            email=user.email,
            role=user.role,
            organization_id=user.organization_id
        )
        
        return user, token
    
    async def get_current_user(self, token: str) -> User:
        """
        Get the current user from a JWT token.
        
        Args:
            token: JWT access token
            
        Returns:
            Current User object
            
        Raises:
            HTTPException: If token is invalid or user not found
        """
        # Decode token
        payload = decode_access_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract user ID
        user_id: Optional[int] = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = await self.repository.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    
    def validate_user_role(self, user: User, required_role: str) -> None:
        """
        Validate that a user has the required role.
        
        Args:
            user: User to validate
            required_role: Required role (founder or interviewer)
            
        Raises:
            HTTPException: If user doesn't have the required role
        """
        if user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User must be a {required_role} to perform this action"
            )
    
    def validate_user_organization(self, user: User, organization_id: int) -> None:
        """
        Validate that a user belongs to the specified organization.
        
        Args:
            user: User to validate
            organization_id: Required organization ID
            
        Raises:
            HTTPException: If user doesn't belong to the organization
        """
        if user.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have access to this organization"
            )
