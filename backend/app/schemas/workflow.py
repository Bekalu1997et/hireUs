"""
Pydantic schemas for workflows and stages.
"""
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field

from app.schemas.candidate import CandidateCreate, CandidateResponse


class WorkflowStageCreate(BaseModel):
    """Schema for creating a workflow stage."""
    interviewer_id: int = Field(gt=0)
    stage_order: int = Field(gt=0)


class WorkflowCreate(BaseModel):
    """Schema for creating a workflow."""
    candidate: CandidateCreate
    role_id: int = Field(gt=0)
    stages: List[WorkflowStageCreate] = Field(min_length=1)


class WorkflowStageUpdate(BaseModel):
    """Schema for updating a workflow stage assignment."""
    id: int = Field(gt=0)
    interviewer_id: int = Field(gt=0)


class WorkflowStagesUpdate(BaseModel):
    """Schema for updating multiple workflow stage assignments."""
    stages: List[WorkflowStageUpdate] = Field(min_length=1)


class WorkflowReopen(BaseModel):
    """Schema for reopening a workflow."""
    reason: str = Field(min_length=3)


class WorkflowNotesUpdate(BaseModel):
    """Schema for updating workflow notes."""
    notes: str | None = Field(None, max_length=5000)


class WorkflowStageResponse(BaseModel):
    """Schema for workflow stage response."""
    id: int
    interviewer_id: int
    stage_order: int
    status: str

    class Config:
        from_attributes = True


class WorkflowResponse(BaseModel):
    """Schema for workflow response."""
    id: int
    candidate: CandidateResponse
    role_id: int
    organization_id: int
    status: str
    created_at: datetime
    completed_at: datetime | None
    is_locked: bool
    notes: str | None
    reopened_at: datetime | None
    reopen_reason: str | None
    stages: List[WorkflowStageResponse]
    role_snapshot: dict | None = None

    class Config:
        from_attributes = True
