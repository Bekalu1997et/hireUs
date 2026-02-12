"""
Router for organization endpoints.

Provides REST API endpoints for organization management and invitations.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import User
from app.modules.auth.router import get_current_user, get_current_founder
from app.modules.organization.service import OrganizationService
from app.schemas.organization import (
    OrganizationUpdate,
    OrganizationResponse,
    InviteRequest,
    InviteAccept,
)
from app.schemas.auth import UserResponse


router = APIRouter()


@router.get("/organizations/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrganizationResponse:
    service = OrganizationService(db)
    org = await service.get_organization(org_id, current_user)
    return OrganizationResponse.model_validate(org)


@router.put("/organizations/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: int,
    update: OrganizationUpdate,
    current_user: User = Depends(get_current_founder),
    db: AsyncSession = Depends(get_db),
) -> OrganizationResponse:
    service = OrganizationService(db)
    org = await service.update_organization(org_id, update, current_user)
    return OrganizationResponse.model_validate(org)


@router.post("/auth/invite", status_code=status.HTTP_201_CREATED)
async def invite_user(
    request: InviteRequest,
    current_user: User = Depends(get_current_founder),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = OrganizationService(db)
    return await service.invite_user(request, current_user)


@router.post("/auth/accept-invite", response_model=UserResponse)
async def accept_invite(
    request: InviteAccept,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    service = OrganizationService(db)
    user = await service.accept_invite(request)
    return UserResponse.model_validate(user)
