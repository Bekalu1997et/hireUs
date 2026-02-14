"""
User repository for database operations.
Handles all user-related database queries.
"""
from typing import List, Optional
from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class UserRepository:
    """
    Repository for user database operations.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize with database session.
        """
        self.db = db
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        """
        query = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.organizations))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        """
        query = select(User).where(User.email == email.lower())
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        is_active: Optional[bool] = None
    ) -> List[User]:
        """
        Get all users with pagination.
        """
        query = select(User)
        
        if is_active is not None:
            query = query.where(User.is_active == is_active)
        
        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count(self, is_active: Optional[bool] = None) -> int:
        """
        Count total users.
        """
        query = select(User)
        
        if is_active is not None:
            query = query.where(User.is_active == is_active)
        
        result = await self.db.execute(query)
        return len(result.scalars().all())
    
    async def create(self, user_data: UserCreate) -> User:
        """
        Create a new user.
        """
        # Create user object
        user = User(
            email=user_data.email.lower(),
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password),
        )
        
        # Add to session and commit
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def update(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """
        Update user information.
        """
        user = await self.get_by_id(user_id)
        
        if not user:
            return None
        
        # Update fields
        update_data = user_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def update_password(
        self, 
        user_id: str, 
        new_hashed_password: str
    ) -> Optional[User]:
        """
        Update user password.
        """
        user = await self.get_by_id(user_id)
        
        if not user:
            return None
        
        user.hashed_password = new_hashed_password
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password.
        """
        user = await self.get_by_email(email)
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        return user
    
    async def update_last_login(self, user_id: str) -> None:
        """
        Update user's last login timestamp.
        """
        from datetime import datetime
        
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_login=datetime.utcnow())
        )
        await self.db.commit()
    
    async def deactivate(self, user_id: str) -> Optional[User]:
        """
        Deactivate a user.
        """
        user = await self.get_by_id(user_id)
        
        if not user:
            return None
        
        user.is_active = False
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def activate(self, user_id: str) -> Optional[User]:
        """
        Activate a user.
        """
        user = await self.get_by_id(user_id)
        
        if not user:
            return None
        
        user.is_active = True
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def delete(self, user_id: str) -> bool:
        """
        Delete a user.
        """
        user = await self.get_by_id(user_id)
        
        if not user:
            return False
        
        await self.db.delete(user)
        await self.db.commit()
        
        return True
    
    async def exists(self, user_id: str) -> bool:
        """
        Check if user exists.
        """
        user = await self.get_by_id(user_id)
        return user is not None
    
    async def exists_by_email(self, email: str) -> bool:
        """
        Check if user exists by email.
        """
        user = await self.get_by_email(email)
        return user is not None
