"""
Workflow router.
Defines API endpoints for workflow operations.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.workflows.service import WorkflowService
from app.schemas.workflow import (
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowResponse,
    WorkflowListResponse,
    WorkflowDetailResponse,
    MoveCandidateRequest,
    BulkMoveCandidateRequest,
    StageTransitionResult,
    BulkStageTransitionResult,
    InterviewerAssignmentRequest,
    InterviewerReassignmentRequest,
    CancelAssignmentRequest,
    AssignmentResponse,
    StageAssignmentsResponse,
    FeedbackStatusResponse,
    PendingFeedbackResponse,
    FeedbackCompletionStats,
    CanMoveCandidateResponse,
    WorkflowStatsResponse,
    WorkflowTemplateResponse,
)
from app.core.security import get_current_active_user
from app.db.models import User


router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.post("/", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    workflow_data: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new workflow.
    """
    service = WorkflowService(db)
    return await service.create(workflow_data, user_id=current_user.id)


@router.get("/", response_model=WorkflowListResponse)
async def get_workflows(
    organization_id: Optional[str] = Query(None, description="Filter by organization"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get paginated list of workflows.
    """
    service = WorkflowService(db)
    return await service.get_all(
        organization_id=organization_id,
        skip=skip,
        limit=limit
    )


@router.get("/default", response_model=WorkflowResponse)
async def get_default_workflow(
    organization_id: Optional[str] = Query(None, description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the default workflow for an organization.
    """
    service = WorkflowService(db)
    org_id = organization_id or current_user.organizations[0].organization_id if current_user.organizations else "demo-org"
    workflow = await service.get_default(org_id)
    
    if not workflow:
        # Create default workflow
        return await service.create_default_workflow(org_id, current_user.id)
    
    return workflow


@router.post("/default", response_model=WorkflowResponse)
async def create_default_workflow(
    organization_id: Optional[str] = Query(None, description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a default workflow for an organization.
    """
    service = WorkflowService(db)
    org_id = organization_id or current_user.organizations[0].organization_id if current_user.organizations else "demo-org"
    return await service.create_default_workflow(org_id, current_user.id)


@router.get("/template", response_model=WorkflowTemplateResponse)
async def get_workflow_template():
    """
    Get a template/example for creating workflows.
    """
    service = WorkflowService.__new__(WorkflowService)
    return await service.get_workflow_template()


@router.get("/{workflow_id}", response_model=WorkflowDetailResponse)
async def get_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get workflow by ID with detailed info.
    """
    service = WorkflowService(db)
    workflow = await service.get_by_id(workflow_id)
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    return workflow


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: str,
    workflow_data: WorkflowUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a workflow.
    """
    service = WorkflowService(db)
    workflow = await service.update(workflow_id, workflow_data, current_user.id)
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    return workflow


@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    hard_delete: bool = Query(False, description="Permanently delete the workflow"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a workflow (soft delete by default).
    """
    service = WorkflowService(db)
    result = await service.delete(workflow_id, hard_delete)
    return result


@router.post("/{workflow_id}/set-default", response_model=WorkflowResponse)
async def set_default_workflow(
    workflow_id: str,
    organization_id: Optional[str] = Query(None, description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Set a workflow as the default for an organization.
    """
    service = WorkflowService(db)
    org_id = organization_id or current_user.organizations[0].organization_id if current_user.organizations else "demo-org"
    workflow = await service.set_default(workflow_id, org_id)
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    return workflow


@router.get("/{workflow_id}/stats", response_model=WorkflowStatsResponse)
async def get_workflow_stats(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get statistics for a workflow.
    """
    service = WorkflowService(db)
    stats = await service.get_workflow_stats(workflow_id)
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    return stats


# ============== Candidate Stage Transitions ==============

@router.post("/candidates/move", response_model=StageTransitionResult)
async def move_candidate(
    request: MoveCandidateRequest,
    skip_feedback_check: bool = Query(False, description="Skip feedback validation"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Move a candidate to a new stage.
    
    This endpoint validates that the candidate can be moved (required feedbacks submitted)
    before allowing the move.
    """
    service = WorkflowService(db)
    result = await service.move_candidate(
        request,
        user_id=current_user.id,
        skip_validation=skip_feedback_check
    )
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": result.message,
                "blocked_reason": result.blocked_reason
            }
        )
    
    return result


@router.post("/candidates/bulk-move", response_model=BulkStageTransitionResult)
async def bulk_move_candidates(
    request: BulkMoveCandidateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Move multiple candidates to a new stage.
    """
    service = WorkflowService(db)
    return await service.bulk_move_candidates(request, current_user.id)


@router.get("/candidates/{candidate_id}/validate-move/{target_stage_id}", response_model=CanMoveCandidateResponse)
async def validate_candidate_move(
    candidate_id: str,
    target_stage_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Check if a candidate can be moved to a target stage.
    
    Returns whether the move is allowed and why if blocked.
    """
    service = WorkflowService(db)
    return await service.validate_candidate_move(candidate_id, target_stage_id)


@router.get("/candidates/{candidate_id}/feedback-status", response_model=FeedbackStatusResponse)
async def get_candidate_feedback_status(
    candidate_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get feedback status for a candidate.
    
    Shows required vs submitted feedbacks and whether progression is blocked.
    """
    service = WorkflowService(db)
    status = await service.get_candidate_feedback_status(candidate_id)
    
    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    return status


@router.get("/candidates/{candidate_id}/stage-history")
async def get_candidate_stage_history(
    candidate_id: str,
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get stage history for a candidate.
    """
    service = WorkflowService(db)
    return await service.get_stage_history(candidate_id, limit)


# ============== Interviewer Assignment Endpoints ==============

@router.post("/assignments", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def assign_interviewer(
    request: InterviewerAssignmentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Assign an interviewer to a candidate.
    """
    service = WorkflowService(db)
    return await service.assign_interviewer(request)


@router.put("/assignments/{assignment_id}/reassign", response_model=AssignmentResponse)
async def reassign_interviewer(
    assignment_id: str,
    request: InterviewerReassignmentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Reassign an interviewer to a different person.
    """
    service = WorkflowService(db)
    
    # Update request with assignment_id
    request_data = request.model_dump()
    request_data["assignment_id"] = assignment_id
    
    result = await service.reassign_interviewer(
        InterviewerReassignmentRequest(**request_data)
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    return result


@router.post("/assignments/{assignment_id}/cancel")
async def cancel_assignment(
    assignment_id: str,
    reason: Optional[str] = Query(None, description="Reason for cancellation"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Cancel an interview assignment.
    """
    service = WorkflowService(db)
    result = await service.cancel_assignment(
        CancelAssignmentRequest(
            assignment_id=assignment_id,
            reason=reason
        )
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["error"]
        )
    
    return result


@router.get("/candidates/{candidate_id}/assignments", response_model=list[AssignmentResponse])
async def get_candidate_assignments(
    candidate_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all assignments for a candidate.
    """
    service = WorkflowService(db)
    return await service.get_assignments_for_candidate(candidate_id)


@router.get("/assignments/pending", response_model=list[PendingFeedbackResponse])
async def get_pending_assignments(
    interviewer_id: Optional[str] = Query(None, description="Filter by interviewer"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get pending interview assignments that need feedback.
    """
    service = WorkflowService(db)
    results, _ = await service.get_pending_feedbacks(
        interviewer_id=interviewer_id or current_user.id,
        skip=skip,
        limit=limit
    )
    return results


# ============== Stage Management ==============

@router.post("/{workflow_id}/stages")
async def add_stage(
    workflow_id: str,
    stage_data: dict = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Add a new stage to a workflow.
    """
    import uuid
    
    service = WorkflowService(db)
    workflow = await service.get_by_id(workflow_id)
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    # Add stage with generated ID
    stages = workflow.stages.copy() if workflow.stages else []
    new_stage = {
        "id": f"stage_{uuid.uuid4().hex[:8]}",
        "order": len(stages),
        "required_feedback_count": 0,
        "interview_types": [],
        **stage_data
    }
    stages.append(new_stage)
    
    # Update workflow
    await service.update(
        workflow_id,
        WorkflowUpdate(stages=stages)
    )
    
    return {"message": "Stage added successfully", "stage": new_stage}


@router.put("/{workflow_id}/stages/{stage_id}")
async def update_stage(
    workflow_id: str,
    stage_id: str,
    stage_data: dict = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a stage in a workflow.
    """
    service = WorkflowService(db)
    workflow = await service.get_by_id(workflow_id)
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    # Update stage
    stages = workflow.stages.copy() if workflow.stages else []
    updated_stages = []
    for stage in stages:
        if stage.get("id") == stage_id:
            updated_stages.append({**stage, **stage_data})
        else:
            updated_stages.append(stage)
    
    await service.update(
        workflow_id,
        WorkflowUpdate(stages=updated_stages)
    )
    
    return {"message": "Stage updated successfully"}


@router.delete("/{workflow_id}/stages/{stage_id}")
async def delete_stage(
    workflow_id: str,
    stage_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a stage from a workflow.
    """
    service = WorkflowService(db)
    workflow = await service.get_by_id(workflow_id)
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    # Remove stage
    stages = [s for s in (workflow.stages or []) if s.get("id") != stage_id]
    
    # Reorder remaining stages
    for i, stage in enumerate(stages):
        stage["order"] = i
    
    await service.update(
        workflow_id,
        WorkflowUpdate(stages=stages)
    )
    
    return {"message": "Stage deleted successfully"}


@router.put("/{workflow_id}/stages/reorder")
async def reorder_stages(
    workflow_id: str,
    stage_orders: list[dict] = Body(..., description="List of {id, order} objects"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Reorder stages in a workflow.
    """
    service = WorkflowService(db)
    workflow = await service.get_by_id(workflow_id)
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    # Update stage orders
    stages = workflow.stages.copy() if workflow.stages else []
    order_map = {s["id"]: s for s in stage_orders}
    
    for stage in stages:
        if stage["id"] in order_map:
            stage["order"] = order_map[stage["id"]]["order"]
    
    # Sort by order
    stages.sort(key=lambda s: s.get("order", 0))
    
    await service.update(
        workflow_id,
        WorkflowUpdate(stages=stages)
    )
    
    return {"message": "Stages reordered successfully"}

