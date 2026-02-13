"""
Service layer for organization operations.

Handles organization management and team invitations.
"""
from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, decode_access_token, hash_password, validate_password_strength
from app.db.models import Organization, User
from app.modules.organization.repository import OrganizationRepository
from app.schemas.organization import OrganizationUpdate, InviteRequest, InviteAccept


class OrganizationService:
    """Service for organization operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = OrganizationRepository(db)

    async def get_organization(self, org_id: int, user: User) -> Organization:
        org = await self.repository.get_organization_by_id(org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )
        if org.id != user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organization does not belong to your account",
            )
        return org

    async def update_organization(
        self,
        org_id: int,
        update: OrganizationUpdate,
        user: User,
    ) -> Organization:
        org = await self.get_organization(org_id, user)
        async with self.db.begin_nested():
            org = await self.repository.update_organization(
                org,
                name=update.name,
                domain=update.domain,
            )
        return org

    async def invite_user(self, request: InviteRequest, user: User) -> dict:
        if user.role != "founder":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only founders can invite team members",
            )

        existing = await self.repository.get_user_by_email(request.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists",
            )

        token_data = {
            "invite": True,
            "email": request.email,
            "full_name": request.full_name,
            "organization_id": user.organization_id,
            "role": "interviewer",
        }
        token = create_access_token(token_data, expires_delta=timedelta(days=7))

        return {"invitation_token": token}

    async def accept_invite(self, request: InviteAccept) -> User:
        payload = decode_access_token(request.token)
        if not payload or not payload.get("invite"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired invitation token",
            )

        is_valid, error_message = validate_password_strength(request.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message,
            )

        email = payload.get("email")
        full_name = payload.get("full_name")
        organization_id = payload.get("organization_id")
        role = payload.get("role", "interviewer")

        if not all([email, full_name, organization_id]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation token missing required fields",
            )

        existing = await self.repository.get_user_by_email(email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists",
            )

        hashed_password = hash_password(request.password)
        async with self.db.begin_nested():
            user = await self.repository.create_user(
                email=email,
                hashed_password=hashed_password,
                full_name=full_name,
                role=role,
                organization_id=organization_id,
            )
        return user
