"""
Pydantic schemas for decisions.
"""
from datetime import datetime
from pydantic import BaseModel, Field


class DecisionBriefRequest(BaseModel):
    """Request schema for generating a decision brief."""
    workflow_id: int = Field(gt=0)


class DecisionBriefResponse(BaseModel):
    """Response schema for AI-generated decision briefs."""
    summary: str
    strengths: str
    concerns: str
    recommendation: str


class DecisionCreate(BaseModel):
    """Schema for recording a final decision."""
    workflow_id: int = Field(gt=0)
    outcome: str = Field(pattern="^(hire|no-hire|hold)$")
    summary: str = Field(min_length=1)
    strengths: str = Field(min_length=1)
    concerns: str = Field(min_length=1)
    recommendation: str = Field(min_length=1)


class DecisionResponse(BaseModel):
    """Schema for decision response."""
    id: int
    workflow_id: int
    candidate_id: int
    role_id: int
    decision_maker_id: int
    outcome: str
    summary: str
    strengths: str
    concerns: str
    recommendation: str
    decided_at: datetime

    class Config:
        from_attributes = True
