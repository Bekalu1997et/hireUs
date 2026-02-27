"""
Pydantic schemas for candidate signal aggregation.
"""
from datetime import datetime
from typing import List
from pydantic import BaseModel


class SignalScore(BaseModel):
    competency_name: str
    average_score: float


class SignalEvaluation(BaseModel):
    interviewer_name: str
    submitted_at: datetime
    notes: str
    scores: list[dict]


class SignalResponse(BaseModel):
    candidate_id: int
    role_id: int
    competency_scores: List[SignalScore]
    overall_weighted_score: float | None
    evaluations: List[SignalEvaluation]
