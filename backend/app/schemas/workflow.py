"""
Workflow schemas for API request/response validation.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# ============== Stage Schemas ==============

class WorkflowStage(BaseModel):
    """Workflow stage schema."""
    id: str = Field(..., description="Unique stage identifier")
    name: str = Field(..., description="Stage name")
    order: int = Field(..., ge=0, description="Stage order in workflow")
    description: Optional[str] = Field(None, description="Stage description")
    color: str = Field(default="#6366f1", description="Stage color for UI")
    required_feedback_count: int = Field(default=0, ge=0, description="Number of required feedbacks before moving forward")
    interview_types: List[str] = Field(default_factory=list, description="Interview types for this stage")


class WorkflowStageCreate(BaseModel):
    """Schema for creating a stage."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    color: str = Field(default="#6366f1")
    required_feedback_count: int = Field(default=0, ge=0)
    interview_types: List[str] = Field(default_factory=list)


class WorkflowStageUpdate(BaseModel):
    """Schema for updating a stage."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = None
    required_feedback_count: Optional[int] = Field(None, ge=0)
    interview_types: Optional[List[str]] = None


# ============== Workflow Schemas ==============

class WorkflowBase(BaseModel):
    """Base workflow schema with common fields."""
    name: str
    description: Optional[str] = None
    stages: List[Dict[str, Any]] = Field(default_factory=list)


class WorkflowCreate(WorkflowBase):
    """Schema for creating a workflow."""
    organization_id: str
    is_default: bool = Field(default=False, description="Set as default workflow")


class WorkflowUpdate(BaseModel):
    """Schema for updating a workflow."""
    name: Optional[str] = None
    description: Optional[str] = None
    stages: Optional[List[Dict[str, Any]]] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class WorkflowInDB(WorkflowBase):
    """Schema for workflow stored in database."""
    id: str
    organization_id: str
    is_default: bool
    is_active: bool
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkflowResponse(WorkflowBase):
    """Workflow response schema for API responses."""
    id: str
    organization_id: str
    is_default: bool
    is_active: bool
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class WorkflowListResponse(BaseModel):
    """Paginated list of workflows."""
    items: List[WorkflowResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class WorkflowDetailResponse(WorkflowResponse):
    """Detailed workflow response with all fields."""
    candidates_count: Optional[Dict[str, int]] = None


# ============== Candidate Stage Transition Schemas ==============

class CandidateStageInfo(BaseModel):
    """Schema for candidate current stage info."""
    workflow_id: Optional[str] = None
    current_stage_id: Optional[str] = None
    current_stage_name: Optional[str] = None
    status: str = "active"


class MoveCandidateRequest(BaseModel):
    """Request schema for moving a candidate to a new stage."""
    candidate_id: str
    to_stage_id: str
    reason: Optional[str] = None
    skip_feedback_check: bool = Field(default=False, description="Skip feedback validation (admin only)")


class BulkMoveCandidateRequest(BaseModel):
    """Request schema for moving multiple candidates."""
    candidate_ids: List[str]
    to_stage_id: str
    reason: Optional[str] = None


class StageTransitionResult(BaseModel):
    """Result of a stage transition."""
    success: bool
    candidate_id: str
    from_stage: Optional[str] = None
    to_stage: str
    message: str
    blocked_reason: Optional[str] = None


class BulkStageTransitionResult(BaseModel):
    """Result of bulk stage transition."""
    success: bool
    total: int
    moved: int
    blocked: int
    results: List[StageTransitionResult]
    message: str


# ============== Interviewer Assignment Schemas ==============

class InterviewerAssignmentRequest(BaseModel):
    """Request schema for assigning an interviewer."""
    candidate_id: str
    interviewer_id: str
    interview_kit_id: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    duration_minutes: int = Field(default=60, ge=15, le=480)
    notes: Optional[str] = None


class InterviewerReassignmentRequest(BaseModel):
    """Request schema for reassigning an interviewer."""
    assignment_id: str
    new_interviewer_id: str
    reason: Optional[str] = None


class CancelAssignmentRequest(BaseModel):
    """Request schema for canceling an interview assignment."""
    assignment_id: str
    reason: Optional[str] = None


class AssignmentResponse(BaseModel):
    """Interview assignment response."""
    id: str
    candidate_id: str
    interviewer_id: str
    interviewer_name: Optional[str] = None
    interview_kit_id: Optional[str] = None
    interview_kit_title: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    duration_minutes: int
    status: str
    notes: Optional[str] = None
    feedback_required: bool
    feedback_submitted: bool = False
    created_at: datetime


class StageAssignmentsResponse(BaseModel):
    """Response for stage assignments."""
    stage_id: str
    stage_name: str
    assignments: List[AssignmentResponse]


# ============== Feedback Status Schemas ==============

class FeedbackStatusResponse(BaseModel):
    """Feedback status response for a candidate."""
    candidate_id: str
    candidate_name: str
    current_stage_id: Optional[str] = None
    current_stage_name: Optional[str] = None
    total_required_feedbacks: int
    total_submitted_feedbacks: int
    is_blocked: bool
    blocked_reason: Optional[str] = None
    assignments: List[AssignmentResponse]


class PendingFeedbackResponse(BaseModel):
    """Pending feedback response."""
    assignment_id: str
    candidate_id: str
    candidate_name: str
    stage_id: str
    stage_name: str
    interviewer_id: str
    interviewer_name: Optional[str] = None
    interview_kit_id: Optional[str] = None
    interview_kit_title: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    is_overdue: bool = False


class FeedbackCompletionStats(BaseModel):
    """Feedback completion statistics."""
    total_assignments: int
    completed: int
    pending: int
    overdue: int
    completion_rate: float


# ============== Workflow Template Schemas ==============

class DefaultWorkflowTemplate(BaseModel):
    """Default workflow template for quick creation."""
    name: str = "Standard Hiring Pipeline"
    description: str = "Standard hiring workflow with typical stages"
    stages: List[Dict[str, Any]] = Field(default_factory=list)


class WorkflowTemplateResponse(BaseModel):
    """Response for workflow template."""
    name: str
    description: str
    stages: List[WorkflowStage]
    use_template: str


# ============== Validation Schemas ==============

class CanMoveCandidateResponse(BaseModel):
    """Response for can-move-candidate validation."""
    can_move: bool
    candidate_id: str
    current_stage_id: Optional[str] = None
    required_feedbacks: int
    submitted_feedbacks: int
    missing_feedbacks: List[str] = Field(default_factory=list)
    blocked_reason: Optional[str] = None


# ============== Workflow Analytics Schemas ==============

class WorkflowStageStats(BaseModel):
    """Statistics for a workflow stage."""
    stage_id: str
    stage_name: str
    candidate_count: int
    avg_time_in_stage_hours: Optional[float] = None
    feedback_completion_rate: float


class WorkflowStatsResponse(BaseModel):
    """Workflow statistics response."""
    workflow_id: str
    total_candidates: int
    active_candidates: int
    completed_candidates: int
    rejected_candidates: int
    stage_stats: List[WorkflowStageStats]

