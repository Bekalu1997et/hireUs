"""
Role AI schemas for blueprint generation.
Pydantic models for role blueprint input/output.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.core.llm.schema import InterviewType


class Competency(BaseModel):
    """Competency schema for role blueprints."""
    name: str = Field(..., description="Competency name")
    description: str = Field(..., description="Competency description")
    weight: str = Field(default="must-have", description="Weight: must-have or nice-to-have")


class InterviewStage(BaseModel):
    """Interview stage schema for role blueprints."""
    name: str = Field(..., description="Stage name")
    duration_minutes: int = Field(default=60, ge=15, le=180, description="Duration in minutes")
    description: str = Field(..., description="Stage description")
    interview_type: str = Field(..., description="Interview type: coding, system_design, behavioral, etc.")


class RoleBlueprintInput(BaseModel):
    """Input schema for role blueprint generation."""
    title: str = Field(..., description="Job title")
    seniority: str = Field(..., description="Seniority level (Junior, Mid, Senior, Lead, etc.)")
    stack: List[str] = Field(default_factory=list, description="Technology stack")
    team_context: Optional[str] = Field(None, description="Additional team context")


class RoleBlueprintOutput(BaseModel):
    """Output schema for role blueprint generation."""
    mission: str = Field(..., description="Role mission statement")
    competencies: List[Competency] = Field(..., description="Core competencies")
    must_have: Dict[str, Any] = Field(default_factory=dict, description="Must-have requirements")
    nice_to_have: Dict[str, Any] = Field(default_factory=dict, description="Nice-to-have qualifications")
    interview_stages: List[InterviewStage] = Field(..., description="Suggested interview stages")

