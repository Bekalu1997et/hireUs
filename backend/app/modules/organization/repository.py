"""
Repository layer for organization operations.

Handles database operations for organizations and users.
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Organization, User


class OrganizationRepository:
    """Repository for organization database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_organization_by_id(self, org_id: int) -> Optional[Organization]:
        result = await self.db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        return result.scalar_one_or_none()

    async def update_organization(
        self,
        organization: Organization,
        name: str | None = None,
        domain: str | None = None,
    ) -> Organization:
        if name is not None:
            organization.name = name
        if domain is not None:
            organization.domain = domain
        await self.db.flush()
        await self.db.refresh(organization)
        return organization

    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create_user(
        self,
        email: str,
        hashed_password: str,
        full_name: str,
        role: str,
        organization_id: int,
    ) -> User:
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            organization_id=organization_id,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
