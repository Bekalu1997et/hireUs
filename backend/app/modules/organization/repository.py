from typing import Optional, List
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Organization, OrganizationMember
from app.schemas.organization import OrganizationCreate, OrganizationUpdate


class OrganizationRepository:
    """Repository for organization operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: The async database session.
        """
        self.db = db

    async def get_by_id(self, organization_id: str) -> Optional[Organization]:
        """
        Get an organization by ID.
        
        Args:
            organization_id: The ID of the organization.
            
        Returns:
            The organization if found, None otherwise.
        """
        result = await self.db.execute(
            select(Organization).where(Organization.id == organization_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Organization]:
        """
        Get an organization by name.
        
        Args:
            name: The name of the organization.
            
        Returns:
            The organization if found, None otherwise.
        """
        result = await self.db.execute(
            select(Organization).where(Organization.name == name)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        is_active: Optional[bool] = None,
    ) -> List[Organization]:
        """
        Get all organizations with optional filters.
        
        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            is_active: Filter by active status.
            
        Returns:
            List of organizations.
        """
        query = select(Organization)

        if is_active is not None:
            query = query.where(Organization.is_active == is_active)

        query = query.offset(skip).limit(limit).order_by(Organization.created_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count(self, is_active: Optional[bool] = None) -> int:
        """
        Count organizations.
        
        Args:
            is_active: Filter by active status.
            
        Returns:
            Total count of organizations.
        """
        query = select(func.count()).select_from(Organization)

        if is_active is not None:
            query = query.where(Organization.is_active == is_active)

        result = await self.db.execute(query)
        return result.scalar_one()

    async def create(self, organization_data: OrganizationCreate, owner_id: str) -> Organization:
        """
        Create a new organization.
        
        Args:
            organization_data: The organization data to create.
            owner_id: The ID of the owner user.
            
        Returns:
            The created organization.
        """
        organization = Organization(
            name=organization_data.name,
            description=organization_data.description,
            website=organization_data.website,
            logo_url=organization_data.logo_url,
            industry=organization_data.industry,
            size=organization_data.size,
            location=organization_data.location,
            owner_id=owner_id,
            settings=organization_data.settings,
        )
        
        self.db.add(organization)
        await self.db.commit()
        await self.db.refresh(organization)
        return organization

    async def update(
        self,
        organization_id: str,
        organization_data: OrganizationUpdate,
    ) -> Optional[Organization]:
        """
        Update an existing organization.
        
        Args:
            organization_id: The ID of the organization to update.
            organization_data: The updated organization data.
            
        Returns:
            The updated organization if found, None otherwise.
        """
        organization = await self.get_by_id(organization_id)
        if not organization:
            return None

        update_data = organization_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(organization, field, value)

        await self.db.commit()
        await self.db.refresh(organization)
        return organization

    async def delete(self, organization_id: str) -> bool:
        """
        Delete an organization (soft delete by setting is_active to False).
        
        Args:
            organization_id: The ID of the organization to delete.
            
        Returns:
            True if deleted, False if not found.
        """
        organization = await self.get_by_id(organization_id)
        if not organization:
            return False

        organization.is_active = False
        await self.db.commit()
        return True

    async def exists(self, organization_id: str) -> bool:
        """
        Check if an organization exists.
        
        Args:
            organization_id: The ID of the organization.
            
        Returns:
            True if exists, False otherwise.
        """
        result = await self.db.execute(
            select(Organization.id).where(Organization.id == organization_id)
        )
        return result.scalar_one_or_none() is not None

    async def is_member(self, organization_id: str, user_id: str) -> bool:
        """
        Check if a user is a member of the organization.
        
        Args:
            organization_id: The ID of the organization.
            user_id: The ID of the user.
            
        Returns:
            True if user is a member, False otherwise.
        """
        result = await self.db.execute(
            select(OrganizationMember).where(
                and_(
                    OrganizationMember.organization_id == organization_id,
                    OrganizationMember.user_id == user_id
                )
            )
        )
        return result.scalar_one_or_none() is not None

    async def get_member(self, organization_id: str, user_id: str) -> Optional[OrganizationMember]:
        """
        Get organization membership.
        
        Args:
            organization_id: The ID of the organization.
            user_id: The ID of the user.
            
        Returns:
            The membership if found, None otherwise.
        """
        result = await self.db.execute(
            select(OrganizationMember).where(
                and_(
                    OrganizationMember.organization_id == organization_id,
                    OrganizationMember.user_id == user_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_members(
        self,
        organization_id: str,
        skip: int = 0,
        limit: int = 20,
    ) -> List[OrganizationMember]:
        """
        Get all members of an organization.
        
        Args:
            organization_id: The ID of the organization.
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            
        Returns:
            List of organization members.
        """
        query = select(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id
        ).offset(skip).limit(limit).order_by(OrganizationMember.joined_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def add_member(
        self,
        organization_id: str,
        user_id: str,
        role: str = "member",
    ) -> OrganizationMember:
        """
        Add a member to an organization.
        
        Args:
            organization_id: The ID of the organization.
            user_id: The ID of the user.
            role: The role of the member.
            
        Returns:
            The created membership.
        """
        member = OrganizationMember(
            user_id=user_id,
            organization_id=organization_id,
            role=role,
        )
        
        self.db.add(member)
        await self.db.commit()
        await self.db.refresh(member)
        return member

    async def update_member_role(
        self,
        organization_id: str,
        user_id: str,
        role: str,
    ) -> Optional[OrganizationMember]:
        """
        Update a member's role.
        
        Args:
            organization_id: The ID of the organization.
            user_id: The ID of the user.
            role: The new role.
            
        Returns:
            The updated membership if found, None otherwise.
        """
        member = await self.get_member(organization_id, user_id)
        if not member:
            return None

        member.role = role
        await self.db.commit()
        await self.db.refresh(member)
        return member

    async def remove_member(
        self,
        organization_id: str,
        user_id: str,
    ) -> bool:
        """
        Remove a member from an organization.
        
        Args:
            organization_id: The ID of the organization.
            user_id: The ID of the user.
            
        Returns:
            True if removed, False if not found.
        """
        member = await self.get_member(organization_id, user_id)
        if not member:
            return False

        await self.db.delete(member)
        await self.db.commit()
        return True

    async def count_members(self, organization_id: str) -> int:
        """
        Count members of an organization.
        
        Args:
            organization_id: The ID of the organization.
            
        Returns:
            Total count of members.
        """
        result = await self.db.execute(
            select(func.count()).select_from(OrganizationMember).where(
                OrganizationMember.organization_id == organization_id
            )
        )
        return result.scalar_one()

