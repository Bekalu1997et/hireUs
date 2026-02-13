"""
Router for decisions endpoints.

Provides REST API endpoints for decision brief generation and final decisions.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import User
from app.modules.auth.router import get_current_founder
from app.modules.decisions.service import DecisionsService
from app.schemas.decision import (
    DecisionBriefRequest,
    DecisionBriefResponse,
    DecisionCreate,
    DecisionResponse,
)


router = APIRouter()


@router.post("/generate-brief", response_model=DecisionBriefResponse)
async def generate_decision_brief(
    request: DecisionBriefRequest,
    current_user: User = Depends(get_current_founder),
    db: AsyncSession = Depends(get_db),
) -> DecisionBriefResponse:
    """
    Generate an AI decision brief for a workflow.
    """
    service = DecisionsService(db)
    return await service.generate_decision_brief(request.workflow_id, current_user)


@router.post("", response_model=DecisionResponse, status_code=status.HTTP_201_CREATED)
async def record_decision(
    decision_data: DecisionCreate,
    current_user: User = Depends(get_current_founder),
    db: AsyncSession = Depends(get_db),
) -> DecisionResponse:
    """
    Record a final hiring decision.
    """
    service = DecisionsService(db)
    decision = await service.record_decision(decision_data, current_user)
    return DecisionResponse.model_validate(decision)


@router.get("/{decision_id}", response_model=DecisionResponse)
async def get_decision(
    decision_id: int,
    current_user: User = Depends(get_current_founder),
    db: AsyncSession = Depends(get_db),
) -> DecisionResponse:
    """
    Get a decision by ID.
    """
    service = DecisionsService(db)
    decision = await service.get_decision(decision_id, current_user)
    return DecisionResponse.model_validate(decision)


@router.get("/workflow/{workflow_id}", response_model=DecisionResponse)
async def get_decision_for_workflow(
    workflow_id: int,
    current_user: User = Depends(get_current_founder),
    db: AsyncSession = Depends(get_db),
) -> DecisionResponse:
    """
    Get the decision for a workflow.
    """
    service = DecisionsService(db)
    decision = await service.get_decision_for_workflow(workflow_id, current_user)
    return DecisionResponse.model_validate(decision)
