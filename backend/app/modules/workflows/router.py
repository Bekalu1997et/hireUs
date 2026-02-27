"""
Router for workflows endpoints.

Provides REST API endpoints for workflow creation and management.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import User
from app.modules.auth.router import get_current_user, get_current_founder
from app.modules.workflows.service import WorkflowService
from app.schemas.workflow import (
    WorkflowCreate,
    WorkflowStagesUpdate,
    WorkflowResponse,
    WorkflowReopen,
    WorkflowNotesUpdate,
)


router = APIRouter()


@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    data: WorkflowCreate,
    current_user: User = Depends(get_current_founder),
    db: AsyncSession = Depends(get_db),
) -> WorkflowResponse:
    """
    Create a workflow for a candidate-role pairing.
    """
    service = WorkflowService(db)
    workflow = await service.create_workflow(data, current_user)
    response = WorkflowResponse.model_validate(workflow)
    response.role_snapshot = workflow.role_snapshot.data if workflow.role_snapshot else None
    return response


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WorkflowResponse:
    """
    Get a workflow by ID.
    """
    service = WorkflowService(db)
    workflow = await service.get_workflow(workflow_id, current_user)
    response = WorkflowResponse.model_validate(workflow)
    response.role_snapshot = workflow.role_snapshot.data if workflow.role_snapshot else None
    return response


@router.get("", response_model=List[WorkflowResponse])
async def list_workflows(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[WorkflowResponse]:
    """
    List workflows for the organization.
    """
    service = WorkflowService(db)
    workflows = await service.list_workflows(current_user, skip=skip, limit=min(limit, 100))
    responses = []
    for workflow in workflows:
        response = WorkflowResponse.model_validate(workflow)
        response.role_snapshot = workflow.role_snapshot.data if workflow.role_snapshot else None
        responses.append(response)
    return responses


@router.put("/{workflow_id}/stages", response_model=WorkflowResponse)
async def update_workflow_stages(
    workflow_id: int,
    data: WorkflowStagesUpdate,
    current_user: User = Depends(get_current_founder),
    db: AsyncSession = Depends(get_db),
) -> WorkflowResponse:
    """
    Update workflow stage assignments.
    """
    service = WorkflowService(db)
    workflow = await service.update_workflow_stages(workflow_id, data, current_user)
    response = WorkflowResponse.model_validate(workflow)
    response.role_snapshot = workflow.role_snapshot.data if workflow.role_snapshot else None
    return response


@router.post("/{workflow_id}/reopen", response_model=WorkflowResponse)
async def reopen_workflow(
    workflow_id: int,
    data: WorkflowReopen,
    current_user: User = Depends(get_current_founder),
    db: AsyncSession = Depends(get_db),
) -> WorkflowResponse:
    """
    Reopen a workflow after a final decision.
    """
    service = WorkflowService(db)
    workflow = await service.reopen_workflow(workflow_id, data, current_user)
    response = WorkflowResponse.model_validate(workflow)
    response.role_snapshot = workflow.role_snapshot.data if workflow.role_snapshot else None
    return response


@router.patch("/{workflow_id}/notes", response_model=WorkflowResponse)
async def update_workflow_notes(
    workflow_id: int,
    data: WorkflowNotesUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WorkflowResponse:
    """
    Update workflow notes (allowed even after decision).
    """
    service = WorkflowService(db)
    workflow = await service.update_workflow_notes(workflow_id, data, current_user)
    response = WorkflowResponse.model_validate(workflow)
    response.role_snapshot = workflow.role_snapshot.data if workflow.role_snapshot else None
    return response
