"""
Pydantic schemas for candidate signals aggregation.
"""
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class SignalEvaluationScoreResponse(BaseModel):
    """Schema for a single competency score inside an evaluation."""
    competency_id: int
    competency_name: str
    score: int


class SignalEvaluationResponse(BaseModel):
    """Schema for evaluation metadata returned in signals."""
    id: int
    interviewer_name: str
    notes: str
    submitted_at: datetime
    scores: List[SignalEvaluationScoreResponse]


class SignalCompetencyAggregate(BaseModel):
    """Aggregated score for a competency across evaluations."""
    competency_id: int
    competency_name: str
    average_score: float = Field(ge=0)
    weight: float = Field(ge=0)


class SignalResponse(BaseModel):
    """Full signal response for a candidate-role pairing."""
    candidate_id: int
    role_id: int
    overall_weighted_score: float = Field(ge=0)
    competency_averages: List[SignalCompetencyAggregate]
    evaluations: List[SignalEvaluationResponse]
