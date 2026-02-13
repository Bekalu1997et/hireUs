"""
Pydantic schemas for evaluations.
"""
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class EvaluationScoreCreate(BaseModel):
    """Schema for creating a competency score."""
    competency_id: int = Field(gt=0)
    score: int = Field(ge=1, le=5)


class EvaluationCreate(BaseModel):
    """Schema for creating an evaluation."""
    workflow_id: int = Field(gt=0)
    workflow_stage_id: int = Field(gt=0)
    notes: str = Field(min_length=1)
    scores: List[EvaluationScoreCreate] = Field(min_length=1)


class EvaluationScoreResponse(BaseModel):
    """Schema for evaluation score response."""
    competency_id: int
    competency_name: str
    score: int


class EvaluationResponse(BaseModel):
    """Schema for evaluation response."""
    id: int
    workflow_id: int
    interviewer_name: str
    notes: str
    scores: List[EvaluationScoreResponse]
    submitted_at: datetime
