"""
Repository layer for authentication operations.

Handles database operations for users and organizations.
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import User, Organization


class AuthRepository:
    """Repository for authentication-related database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email address.
        
        Args:
            email: User's email address
            
        Returns:
            User object if found, None otherwise
        """
        result = await self.db.execute(
            select(User)
            .where(User.email == email)
            .options(selectinload(User.organization))
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id: User's database ID
            
        Returns:
            User object if found, None otherwise
        """
        result = await self.db.execute(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.organization))
        )
        return result.scalar_one_or_none()
    
    async def get_organization_by_domain(self, domain: str) -> Optional[Organization]:
        """
        Get an organization by domain.
        
        Args:
            domain: Organization's domain
            
        Returns:
            Organization object if found, None otherwise
        """
        result = await self.db.execute(
            select(Organization).where(Organization.domain == domain)
        )
        return result.scalar_one_or_none()
    
    async def create_organization(
        self,
        name: str,
        domain: str
    ) -> Organization:
        """
        Create a new organization.
        
        Args:
            name: Organization name
            domain: Organization domain
            
        Returns:
            Created Organization object
        """
        organization = Organization(
            name=name,
            domain=domain
        )
        self.db.add(organization)
        await self.db.flush()
        await self.db.refresh(organization)
        return organization
    
    async def create_user(
        self,
        email: str,
        hashed_password: str,
        full_name: str,
        role: str,
        organization_id: int
    ) -> User:
        """
        Create a new user.
        
        Args:
            email: User's email address
            hashed_password: Hashed password
            full_name: User's full name
            role: User's role (founder or interviewer)
            organization_id: Organization ID
            
        Returns:
            Created User object
        """
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            organization_id=organization_id
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user, ["organization"])
        return user
