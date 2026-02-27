from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import get_current_active_user
from app.modules.candicates.service import CandidateService
from app.schemas.candidate import (
    CandidateCreate,
    CandidateUpdate,
    CandidateResponse,
    CandidateListResponse,
    CandidateSearchResponse,
    CandidateStats,
)
from app.schemas.user import UserResponse


router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("/", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    candidate_data: CandidateCreate,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new candidate.
    """
    service = CandidateService(db)
    try:
        candidate = await service.create_candidate(candidate_data)
        return candidate
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=CandidateListResponse)
async def get_candidates(
    organization_id: str = Query(..., description="Organization ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    role_id: Optional[str] = Query(None, description="Filter by role ID"),
    workflow_id: Optional[str] = Query(None, description="Filter by workflow ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    source: Optional[str] = Query(None, description="Filter by source"),
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all candidates for an organization with pagination and filters.
    """
    service = CandidateService(db)
    result = await service.get_candidates(
        organization_id=organization_id,
        skip=skip,
        limit=limit,
        role_id=role_id,
        workflow_id=workflow_id,
        is_active=is_active,
        source=source,
    )
    return result


@router.get("/search", response_model=CandidateSearchResponse)
async def search_candidates(
    organization_id: str = Query(..., description="Organization ID"),
    query: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Search candidates by name, email, or company.
    """
    service = CandidateService(db)
    result = await service.search_candidates(
        organization_id=organization_id,
        query=query,
        skip=skip,
        limit=limit,
    )
    return result


@router.get("/stats", response_model=CandidateStats)
async def get_candidate_stats(
    organization_id: str = Query(..., description="Organization ID"),
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get candidate statistics for an organization.
    """
    service = CandidateService(db)
    result = await service.get_candidate_stats(organization_id)
    return result


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a candidate by ID.
    """
    service = CandidateService(db)
    candidate = await service.get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    return candidate


@router.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: str,
    candidate_data: CandidateUpdate,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a candidate.
    """
    service = CandidateService(db)
    candidate = await service.update_candidate(candidate_id, candidate_data)
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    return candidate


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(
    candidate_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a candidate (soft delete).
    """
    service = CandidateService(db)
    deleted = await service.delete_candidate(candidate_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    return None


@router.post("/{candidate_id}/activate", response_model=CandidateResponse)
async def activate_candidate(
    candidate_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Activate a candidate.
    """
    service = CandidateService(db)
    candidate = await service.activate_candidate(candidate_id)
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    return candidate


@router.post("/{candidate_id}/deactivate", response_model=CandidateResponse)
async def deactivate_candidate(
    candidate_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Deactivate a candidate.
    """
    service = CandidateService(db)
    candidate = await service.deactivate_candidate(candidate_id)
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    return candidate


@router.get("/check-email/{email}")
async def check_email_exists(
    email: str,
    organization_id: str = Query(..., description="Organization ID"),
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Check if a candidate email exists in the organization.
    """
    service = CandidateService(db)
    exists = await service.check_email_exists(email, organization_id)
    return JSONResponse(content={"exists": exists})

