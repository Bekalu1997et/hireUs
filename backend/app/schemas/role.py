"""
Pydantic schemas for roles and competencies.
"""
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class CompetencyCreate(BaseModel):
    """Schema for creating a competency."""
    name: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    weight: float = Field(gt=0.0, le=1.0)


class CompetencyUpdate(BaseModel):
    """Schema for updating a competency."""
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, min_length=1)
    weight: float | None = Field(None, gt=0.0, le=1.0)


class CompetencyResponse(BaseModel):
    """Schema for competency response."""
    id: int
    name: str
    description: str
    weight: float
    
    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    """Schema for creating a role."""
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    seniority_level: str = Field(pattern="^(junior|mid|senior|staff|principal)$")
    competencies: List[CompetencyCreate] = Field(min_length=1)


class RoleUpdate(BaseModel):
    """Schema for updating a role."""
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, min_length=1)
    seniority_level: str | None = Field(None, pattern="^(junior|mid|senior|staff|principal)$")
    competencies: List[CompetencyCreate] | None = Field(None, min_length=1)


class RoleResponse(BaseModel):
    """Schema for role response."""
    id: int
    title: str
    description: str
    seniority_level: str
    organization_id: int
    competencies: List[CompetencyResponse]
    created_at: datetime
    
    class Config:
        from_attributes = True
