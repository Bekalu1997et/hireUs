"""
Interview Kit repository for database operations.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.db.models import InterviewKit


class InterviewKitRepository:
    """
    Interview Kit repository for database operations.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize with database session.
        """
        self.db = db
    
    async def get_by_id(self, kit_id: str) -> Optional[InterviewKit]:
        """
        Get interview kit by ID.
        """
        query = select(InterviewKit).where(InterviewKit.id == kit_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        organization_id: Optional[str] = None,
        role_id: Optional[str] = None,
        interview_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[InterviewKit]:
        """
        Get paginated list of interview kits.
        """
        query = select(InterviewKit)
        
        filters = []
        if organization_id:
            filters.append(InterviewKit.organization_id == organization_id)
        if role_id:
            filters.append(InterviewKit.role_id == role_id)
        if interview_type:
            filters.append(InterviewKit.type == interview_type)
        if is_active is not None:
            filters.append(InterviewKit.is_active == is_active)
        if search:
            search_term = f"%{search}%"
            filters.append(
                or_(
                    InterviewKit.title.ilike(search_term),
                    InterviewKit.description.ilike(search_term)
                )
            )
        
        if filters:
            query = query.where(and_(*filters))
        
        query = query.offset(skip).limit(limit).order_by(InterviewKit.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count(
        self,
        organization_id: Optional[str] = None,
        role_id: Optional[str] = None,
        interview_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> int:
        """
        Count interview kits matching filters.
        """
        query = select(InterviewKit)
        
        filters = []
        if organization_id:
            filters.append(InterviewKit.organization_id == organization_id)
        if role_id:
            filters.append(InterviewKit.role_id == role_id)
        if interview_type:
            filters.append(InterviewKit.type == interview_type)
        if is_active is not None:
            filters.append(InterviewKit.is_active == is_active)
        if search:
            search_term = f"%{search}%"
            filters.append(
                or_(
                    InterviewKit.title.ilike(search_term),
                    InterviewKit.description.ilike(search_term)
                )
            )
        
        if filters:
            query = query.where(and_(*filters))
        
        result = await self.db.execute(query)
        return len(result.scalars().all())
    
    async def create(self, kit: InterviewKit) -> InterviewKit:
        """
        Create a new interview kit.
        """
        self.db.add(kit)
        await self.db.commit()
        await self.db.refresh(kit)
        return kit
    
    async def update(self, kit: InterviewKit) -> InterviewKit:
        """
        Update an existing interview kit.
        """
        await self.db.commit()
        await self.db.refresh(kit)
        return kit
    
    async def delete(self, kit: InterviewKit) -> None:
        """
        Delete an interview kit.
        """
        await self.db.delete(kit)
        await self.db.commit()
    
    async def get_by_organization(
        self,
        organization_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[InterviewKit]:
        """
        Get all interview kits for an organization.
        """
        return await self.get_all(
            organization_id=organization_id,
            skip=skip,
            limit=limit
        )
    
    async def get_by_role(
        self,
        role_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[InterviewKit]:
        """
        Get all interview kits for a role.
        """
        return await self.get_all(
            role_id=role_id,
            skip=skip,
            limit=limit
        )
    
    async def get_by_type(
        self,
        interview_type: str,
        organization_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[InterviewKit]:
        """
        Get all interview kits of a specific type.
        """
        return await self.get_all(
            organization_id=organization_id,
            interview_type=interview_type,
            skip=skip,
            limit=limit
        )

