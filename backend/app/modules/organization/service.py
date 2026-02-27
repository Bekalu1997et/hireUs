from typing import Optional, List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.organization.repository import OrganizationRepository
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationListResponse,
    OrganizationMemberResponse,
    OrganizationMemberListResponse,
    OrganizationStats,
)


class OrganizationService:
    """Service for organization operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize the service with a database session.
        
        Args:
            db: The async database session.
        """
        self.db = db
        self.repository = OrganizationRepository(db)

    async def create_organization(
        self, 
        organization_data: OrganizationCreate, 
        owner_id: str
    ) -> OrganizationResponse:
        """
        Create a new organization.
        
        Args:
            organization_data: The organization data to create.
            owner_id: The ID of the owner user.
            
        Returns:
            The created organization.
        """
        # Check if organization name already exists
        exists = await self.repository.get_by_name(organization_data.name)
        if exists:
            raise ValueError("Organization with this name already exists")

        organization = await self.repository.create(organization_data, owner_id)
        
        # Add owner as a member with "owner" role
        await self.repository.add_member(
            organization_id=organization.id,
            user_id=owner_id,
            role="owner"
        )
        
        return OrganizationResponse.model_validate(organization)

    async def get_organization(self, organization_id: str) -> Optional[OrganizationResponse]:
        """
        Get an organization by ID.
        
        Args:
            organization_id: The ID of the organization.
            
        Returns:
            The organization if found, None otherwise.
        """
        organization = await self.repository.get_by_id(organization_id)
        if not organization:
            return None
        return OrganizationResponse.model_validate(organization)

    async def get_organizations(
        self,
        skip: int = 0,
        limit: int = 20,
        is_active: Optional[bool] = None,
    ) -> OrganizationListResponse:
        """
        Get organizations with pagination and filters.
        
        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            is_active: Filter by active status.
            
        Returns:
            List of organizations with pagination info.
        """
        organizations = await self.repository.get_all(
            skip=skip,
            limit=limit,
            is_active=is_active,
        )
        
        total = await self.repository.count(is_active=is_active)

        return OrganizationListResponse(
            organizations=[OrganizationResponse.model_validate(o) for o in organizations],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def update_organization(
        self,
        organization_id: str,
        organization_data: OrganizationUpdate,
    ) -> Optional[OrganizationResponse]:
        """
        Update an organization.
        
        Args:
            organization_id: The ID of the organization to update.
            organization_data: The updated organization data.
            
        Returns:
            The updated organization if found, None otherwise.
        """
        organization = await self.repository.update(organization_id, organization_data)
        if not organization:
            return None
        return OrganizationResponse.model_validate(organization)

    async def delete_organization(self, organization_id: str) -> bool:
        """
        Delete an organization (soft delete).
        
        Args:
            organization_id: The ID of the organization to delete.
            
        Returns:
            True if deleted, False if not found.
        """
        return await self.repository.delete(organization_id)

    async def get_organization_stats(self, organization_id: str) -> OrganizationStats:
        """
        Get organization statistics.
        
        Args:
            organization_id: The ID of the organization.
            
        Returns:
            Organization statistics.
        """
        # For now, return basic stats - this could be expanded
        members_count = await self.repository.count_members(organization_id)
        
        return OrganizationStats(
            total_users=members_count,
            active_users=members_count,
            total_roles=0,
            active_roles=0,
            total_candidates=0,
            active_candidates=0,
            total_workflows=0,
        )

    async def add_member(
        self,
        organization_id: str,
        user_id: str,
        role: str = "member",
    ) -> OrganizationMemberResponse:
        """
        Add a member to an organization.
        
        Args:
            organization_id: The ID of the organization.
            user_id: The ID of the user.
            role: The role of the member.
            
        Returns:
            The created membership.
        """
        # Check if already a member
        is_member = await self.repository.is_member(organization_id, user_id)
        if is_member:
            raise ValueError("User is already a member of this organization")

        member = await self.repository.add_member(organization_id, user_id, role)
        return OrganizationMemberResponse.model_validate(member)

    async def get_members(
        self,
        organization_id: str,
        skip: int = 0,
        limit: int = 20,
    ) -> OrganizationMemberListResponse:
        """
        Get organization members.
        
        Args:
            organization_id: The ID of the organization.
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            
        Returns:
            List of members with pagination info.
        """
        members = await self.repository.get_members(
            organization_id=organization_id,
            skip=skip,
            limit=limit,
        )
        
        total = await self.repository.count_members(organization_id)

        return OrganizationMemberListResponse(
            members=[OrganizationMemberResponse.model_validate(m) for m in members],
            total=total,
        )

    async def update_member_role(
        self,
        organization_id: str,
        user_id: str,
        role: str,
    ) -> Optional[OrganizationMemberResponse]:
        """
        Update a member's role.
        
        Args:
            organization_id: The ID of the organization.
            user_id: The ID of the user.
            role: The new role.
            
        Returns:
            The updated membership if found, None otherwise.
        """
        member = await self.repository.update_member_role(organization_id, user_id, role)
        if not member:
            return None
        return OrganizationMemberResponse.model_validate(member)

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
        return await self.repository.remove_member(organization_id, user_id)

    async def is_member(
        self,
        organization_id: str,
        user_id: str,
    ) -> bool:
        """
        Check if a user is a member of the organization.
        
        Args:
            organization_id: The ID of the organization.
            user_id: The ID of the user.
            
        Returns:
            True if user is a member, False otherwise.
        """
        return await self.repository.is_member(organization_id, user_id)

