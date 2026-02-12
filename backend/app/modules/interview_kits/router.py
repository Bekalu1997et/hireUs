"""
Router for interview kits endpoints.

Provides REST API endpoints for interview kit generation and retrieval.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import User
from app.modules.auth.router import get_current_founder, get_current_user
from app.modules.interview_kits.service import InterviewKitsService
from app.schemas.interview_kit import (
    InterviewKitGenerateRequest,
    InterviewKitResponse,
)


router = APIRouter()


@router.post("/generate", response_model=InterviewKitResponse, status_code=status.HTTP_201_CREATED)
async def generate_interview_kit(
    request: InterviewKitGenerateRequest,
    current_user: User = Depends(get_current_founder),
    db: AsyncSession = Depends(get_db),
) -> InterviewKitResponse:
    """
    Generate an interview kit for a role using AI.
    """
    service = InterviewKitsService(db)
    kit = await service.generate_interview_kit(request, current_user)
    return InterviewKitResponse.model_validate(kit)


@router.get("/{kit_id}", response_model=InterviewKitResponse)
async def get_interview_kit(
    kit_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InterviewKitResponse:
    """
    Get an interview kit by ID.
    """
    service = InterviewKitsService(db)
    kit = await service.get_interview_kit(kit_id, current_user)
    return InterviewKitResponse.model_validate(kit)


@router.get("/role/{role_id}", response_model=List[InterviewKitResponse])
async def list_interview_kits_for_role(
    role_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[InterviewKitResponse]:
    """
    List interview kits for a role.
    """
    service = InterviewKitsService(db)
    kits = await service.list_interview_kits_for_role(role_id, current_user)
    return [InterviewKitResponse.model_validate(kit) for kit in kits]
