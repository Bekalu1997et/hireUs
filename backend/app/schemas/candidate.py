"""
Pydantic schemas for candidates.
"""
from datetime import datetime
from pydantic import BaseModel, Field


class CandidateCreate(BaseModel):
    """Schema for creating a candidate."""
    full_name: str = Field(min_length=1, max_length=255)
    email: str = Field(min_length=3, max_length=255)


class CandidateResponse(BaseModel):
    """Schema for candidate response."""
    id: int
    full_name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True
