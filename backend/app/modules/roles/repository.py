"""
Repository layer for roles and competencies operations.

Handles database operations for roles and their associated competencies.
"""
from typing import Optional, List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Role, Competency


class RolesRepository:
    """Repository for roles and competencies database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_role(
        self,
        title: str,
        description: str,
        seniority_level: str,
        organization_id: int,
        competencies_data: List[dict]
    ) -> Role:
        """
        Create a new role with competencies in a transaction.
        
        Args:
            title: Role title
            description: Role description
            seniority_level: Seniority level (junior, mid, senior, staff, principal)
            organization_id: Organization ID
            competencies_data: List of competency dictionaries with name, description, weight
            
        Returns:
            Created Role object with competencies
        """
        # Create role
        role = Role(
            title=title,
            description=description,
            seniority_level=seniority_level,
            organization_id=organization_id
        )
        self.db.add(role)
        await self.db.flush()
        
        # Create competencies
        for comp_data in competencies_data:
            competency = Competency(
                name=comp_data["name"],
                description=comp_data["description"],
                weight=comp_data["weight"],
                role_id=role.id
            )
            self.db.add(competency)
        
        await self.db.flush()
        await self.db.refresh(role, ["competencies"])
        
        return role
    
    async def get_role_by_id(self, role_id: int) -> Optional[Role]:
        """
        Get a role by ID with its competencies.
        
        Args:
            role_id: Role ID
            
        Returns:
            Role object if found, None otherwise
        """
        result = await self.db.execute(
            select(Role)
            .where(Role.id == role_id)
            .options(selectinload(Role.competencies))
        )
        return result.scalar_one_or_none()
    
    async def list_roles_by_organization(
        self,
        organization_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Role]:
        """
        List all roles for an organization.
        
        Args:
            organization_id: Organization ID
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of Role objects
        """
        result = await self.db.execute(
            select(Role)
            .where(Role.organization_id == organization_id)
            .options(selectinload(Role.competencies))
            .offset(skip)
            .limit(limit)
            .order_by(Role.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def update_role(
        self,
        role_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        seniority_level: Optional[str] = None,
        competencies_data: Optional[List[dict]] = None
    ) -> Optional[Role]:
        """
        Update a role and optionally replace its competencies.
        
        Args:
            role_id: Role ID
            title: New title (optional)
            description: New description (optional)
            seniority_level: New seniority level (optional)
            competencies_data: New competencies list (optional, replaces all existing)
            
        Returns:
            Updated Role object if found, None otherwise
        """
        role = await self.get_role_by_id(role_id)
        if not role:
            return None
        
        # Update role fields
        if title is not None:
            role.title = title
        if description is not None:
            role.description = description
        if seniority_level is not None:
            role.seniority_level = seniority_level
        
        # Replace competencies if provided
        if competencies_data is not None:
            # Delete existing competencies
            await self.db.execute(
                delete(Competency).where(Competency.role_id == role_id)
            )
            await self.db.flush()
            
            # Create new competencies
            for comp_data in competencies_data:
                competency = Competency(
                    name=comp_data["name"],
                    description=comp_data["description"],
                    weight=comp_data["weight"],
                    role_id=role.id
                )
                self.db.add(competency)
        
        await self.db.flush()
        await self.db.refresh(role, ["competencies"])
        
        return role
    
    async def delete_role(self, role_id: int) -> bool:
        """
        Delete a role and its competencies (cascade).
        
        Args:
            role_id: Role ID
            
        Returns:
            True if role was deleted, False if not found
        """
        role = await self.get_role_by_id(role_id)
        if not role:
            return False
        
        await self.db.delete(role)
        await self.db.flush()
        
        return True
    
    async def get_competencies_by_role(self, role_id: int) -> List[Competency]:
        """
        Get all competencies for a role.
        
        Args:
            role_id: Role ID
            
        Returns:
            List of Competency objects
        """
        result = await self.db.execute(
            select(Competency)
            .where(Competency.role_id == role_id)
            .order_by(Competency.id)
        )
        return list(result.scalars().all())
