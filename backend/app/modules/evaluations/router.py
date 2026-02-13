"""
Router for evaluations endpoints.

Provides REST API endpoints for evaluation submission and retrieval.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import User
from app.modules.auth.router import get_current_user
from app.modules.evaluations.service import EvaluationsService
from app.schemas.evaluation import (
    EvaluationCreate,
    EvaluationResponse,
    EvaluationScoreResponse,
)


router = APIRouter()


def _to_response(evaluation) -> EvaluationResponse:
    scores = [
        EvaluationScoreResponse(
            competency_id=score.competency_id,
            competency_name=score.competency.name if score.competency else "",
            score=score.score,
        )
        for score in evaluation.scores
    ]
    return EvaluationResponse(
        id=evaluation.id,
        workflow_id=evaluation.workflow_id,
        interviewer_name=evaluation.interviewer.full_name if evaluation.interviewer else "",
        notes=evaluation.notes,
        scores=scores,
        submitted_at=evaluation.submitted_at,
    )


@router.post("", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED)
async def submit_evaluation(
    evaluation_data: EvaluationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EvaluationResponse:
    """
    Submit an evaluation with competency scores.
    """
    service = EvaluationsService(db)
    evaluation = await service.submit_evaluation(evaluation_data, current_user)
    return _to_response(evaluation)


@router.get("/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation(
    evaluation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EvaluationResponse:
    """
    Get an evaluation by ID.
    """
    service = EvaluationsService(db)
    evaluation = await service.get_evaluation(evaluation_id, current_user)
    return _to_response(evaluation)


@router.get("/workflow/{workflow_id}", response_model=List[EvaluationResponse])
async def list_evaluations_for_workflow(
    workflow_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[EvaluationResponse]:
    """
    List evaluations for a workflow.
    """
    service = EvaluationsService(db)
    evaluations = await service.list_evaluations_for_workflow(workflow_id, current_user)
    return [_to_response(evaluation) for evaluation in evaluations]
