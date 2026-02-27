from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import get_current_active_user
from app.modules.organization.service import OrganizationService
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationListResponse,
    OrganizationMemberResponse,
    OrganizationMemberListResponse,
    OrganizationStats,
)
from app.schemas.user import UserResponse


router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    organization_data: OrganizationCreate,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new organization.
    """
    service = OrganizationService(db)
    try:
        organization = await service.create_organization(organization_data, current_user.id)
        return organization
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=OrganizationListResponse)
async def get_organizations(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all organizations with pagination and filters.
    """
    service = OrganizationService(db)
    result = await service.get_organizations(
        skip=skip,
        limit=limit,
        is_active=is_active,
    )
    return result


@router.get("/stats", response_model=OrganizationStats)
async def get_organization_stats(
    organization_id: str = Query(..., description="Organization ID"),
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get organization statistics.
    """
    service = OrganizationService(db)
    result = await service.get_organization_stats(organization_id)
    return result


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get an organization by ID.
    """
    service = OrganizationService(db)
    organization = await service.get_organization(organization_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return organization


@router.put("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    organization_id: str,
    organization_data: OrganizationUpdate,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update an organization.
    """
    service = OrganizationService(db)
    organization = await service.update_organization(organization_id, organization_data)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return organization


@router.delete("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    organization_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete an organization (soft delete).
    """
    service = OrganizationService(db)
    deleted = await service.delete_organization(organization_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return None


# Organization Members Endpoints
@router.get("/{organization_id}/members", response_model=OrganizationMemberListResponse)
async def get_organization_members(
    organization_id: str,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get organization members.
    """
    service = OrganizationService(db)
    result = await service.get_members(
        organization_id=organization_id,
        skip=skip,
        limit=limit,
    )
    return result


@router.post("/{organization_id}/members", response_model=OrganizationMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_organization_member(
    organization_id: str,
    user_id: str = Query(..., description="User ID to add"),
    role: str = Query("member", description="Role for the member"),
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Add a member to an organization.
    """
    service = OrganizationService(db)
    try:
        member = await service.add_member(organization_id, user_id, role)
        return member
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{organization_id}/members/{user_id}", response_model=OrganizationMemberResponse)
async def update_organization_member(
    organization_id: str,
    user_id: str,
    role: str = Query(..., description="New role for the member"),
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a member's role in an organization.
    """
    service = OrganizationService(db)
    member = await service.update_member_role(organization_id, user_id, role)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    return member


@router.delete("/{organization_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_organization_member(
    organization_id: str,
    user_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Remove a member from an organization.
    """
    service = OrganizationService(db)
    removed = await service.remove_member(organization_id, user_id)
    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    return None


@router.get("/{organization_id}/members/{user_id}")
async def check_organization_membership(
    organization_id: str,
    user_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Check if a user is a member of the organization.
    """
    service = OrganizationService(db)
    is_member = await service.is_member(organization_id, user_id)
    return {"is_member": is_member}

