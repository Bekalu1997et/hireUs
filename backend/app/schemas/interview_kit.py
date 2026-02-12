"""
Pydantic schemas for interview kits.
"""
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class InterviewKitGenerateRequest(BaseModel):
    """Request schema to generate an interview kit."""
    role_id: int = Field(gt=0)


class InterviewQuestionResponse(BaseModel):
    """Schema for interview question response."""
    id: int
    competency_id: int
    question_text: str
    evaluation_rubric: str
    order: int

    class Config:
        from_attributes = True


class InterviewKitResponse(BaseModel):
    """Schema for interview kit response."""
    id: int
    role_id: int
    generated_at: datetime
    llm_model: str
    questions: List[InterviewQuestionResponse]

    class Config:
        from_attributes = True
