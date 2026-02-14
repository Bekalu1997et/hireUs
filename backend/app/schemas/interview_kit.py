"""
Interview Kit schemas for API request/response validation.
"""
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# ==================== Enums ====================

class InterviewType(str, Enum):
    """Interview type enumeration."""
    CODING = "coding"
    SYSTEM_DESIGN = "system_design"
    PM_CASE = "pm_case"
    BEHAVIORAL = "behavioral"


# ==================== Base Schemas ====================

class RubricCriterion(BaseModel):
    """Rubric criterion schema for interview evaluation."""
    name: str = Field(..., description="Criterion name")
    description: str = Field(..., description="What to evaluate")
    max_score: int = Field(default=5, ge=1, le=10, description="Maximum score for this criterion")
    weight: int = Field(default=1, ge=1, le=5, description="Weight of this criterion")


class QuestionItem(BaseModel):
    """Question item schema."""
    question: str = Field(..., description="The question text")
    type: str = Field(default="open-ended", description="Question type: open-ended, coding, scenario")
    duration_minutes: int = Field(default=10, description="Suggested time for this question")
    difficulty: str = Field(default="medium", description="Difficulty level: easy, medium, hard")
    notes: Optional[str] = Field(None, description="Additional notes for interviewer")


# ==================== Request Schemas ====================

class InterviewKitCreate(BaseModel):
    """Schema for creating an interview kit."""
    organization_id: str = Field(..., description="Organization ID")
    role_id: Optional[str] = Field(None, description="Related role ID")
    title: str = Field(..., description="Kit title")
    type: str = Field(..., description="Interview type: coding, system_design, pm_case, behavioral")
    description: Optional[str] = Field(None, description="Kit description")
    problem_statement: Optional[str] = Field(None, description="Problem statement for the interview")
    evaluation_rubric: Optional[List[Dict[str, Any]]] = Field(None, description="Evaluation rubric criteria")
    red_flags: Optional[List[str]] = Field(None, description="Red flags to watch for")
    good_answer_outline: Optional[str] = Field(None, description="Outline of a good answer")
    questions: Optional[List[Dict[str, Any]]] = Field(None, description="Interview questions")
    estimated_duration_minutes: int = Field(default=60, ge=15, le=180, description="Estimated interview duration")
    tips_for_interviewer: Optional[str] = Field(None, description="Tips for the interviewer")


class InterviewKitUpdate(BaseModel):
    """Schema for updating an interview kit."""
    title: Optional[str] = Field(None, description="Kit title")
    description: Optional[str] = Field(None, description="Kit description")
    problem_statement: Optional[str] = Field(None, description="Problem statement for the interview")
    evaluation_rubric: Optional[List[Dict[str, Any]]] = Field(None, description="Evaluation rubric criteria")
    red_flags: Optional[List[str]] = Field(None, description="Red flags to watch for")
    good_answer_outline: Optional[str] = Field(None, description="Outline of a good answer")
    questions: Optional[List[Dict[str, Any]]] = Field(None, description="Interview questions")
    estimated_duration_minutes: Optional[int] = Field(None, ge=15, le=180, description="Estimated interview duration")
    tips_for_interviewer: Optional[str] = Field(None, description="Tips for the interviewer")
    is_active: Optional[bool] = Field(None, description="Whether the kit is active")


class GenerateInterviewKitRequest(BaseModel):
    """Schema for generating an interview kit using AI."""
    role_id: Optional[str] = Field(None, description="Related role ID (optional)")
    role_title: str = Field(..., description="Job title for the role")
    seniority: str = Field(..., description="Seniority level")
    stack: Optional[List[str]] = Field(default_factory=list, description="Technology stack")
    interview_type: str = Field(..., description="Type of interview: coding, system_design, pm_case, behavioral")
    competencies: Optional[List[str]] = Field(default_factory=list, description="Core competencies to evaluate")
    duration_minutes: int = Field(default=60, ge=15, le=180, description="Estimated interview duration")
    additional_context: Optional[str] = Field(None, description="Any additional context")


# ==================== Response Schemas ====================

class InterviewKitResponse(BaseModel):
    """Schema for interview kit response."""
    id: str
    organization_id: str
    role_id: Optional[str] = None
    title: str
    type: str
    description: Optional[str] = None
    problem_statement: Optional[str] = None
    evaluation_rubric: Optional[List[Dict[str, Any]]] = None
    red_flags: Optional[List[str]] = None
    good_answer_outline: Optional[str] = None
    questions: Optional[List[Dict[str, Any]]] = None
    estimated_duration_minutes: int
    version: int
    is_template: bool
    is_active: bool
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InterviewKitListResponse(BaseModel):
    """Schema for paginated interview kit list."""
    items: List[InterviewKitResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AIGeneratedInterviewKit(BaseModel):
    """Schema for AI-generated interview kit data."""
    title: str = Field(..., description="Kit title")
    problem_statement: str = Field(..., description="Problem statement for the interview")
    evaluation_rubric: List[Dict[str, Any]] = Field(..., description="Evaluation rubric criteria")
    red_flags: List[str] = Field(..., description="Red flags to watch for")
    good_answer_outline: str = Field(..., description="Outline of a good answer")
    questions: List[Dict[str, Any]] = Field(default_factory=list, description="Interview questions")
    tips_for_interviewer: Optional[str] = Field(None, description="Tips for the interviewer")
    suggested_duration_breakdown: Optional[Dict[str, int]] = Field(None, description="Suggested time breakdown")


class GenerateInterviewKitResponse(BaseModel):
    """Schema for interview kit generation response."""
    success: bool
    kit: Optional[AIGeneratedInterviewKit] = None
    error: Optional[str] = None


class CreateInterviewKitWithAIRequest(BaseModel):
    """Schema for creating an interview kit with AI-generated content."""
    organization_id: str = Field(..., description="Organization ID")
    role_id: Optional[str] = Field(None, description="Related role ID")
    role_title: str = Field(..., description="Job title for the role")
    seniority: str = Field(..., description="Seniority level")
    stack: Optional[List[str]] = Field(default_factory=list, description="Technology stack")
    interview_type: str = Field(..., description="Type of interview")
    competencies: Optional[List[str]] = Field(default_factory=list, description="Core competencies to evaluate")
    duration_minutes: int = Field(default=60, ge=15, le=180, description="Estimated interview duration")
    additional_context: Optional[str] = Field(None, description="Any additional context")


# ==================== Question Bank Schemas ====================

class QuestionBankItem(BaseModel):
    """Schema for question bank item."""
    id: str
    interview_kit_id: str
    question: str
    type: str
    duration_minutes: int
    difficulty: str
    notes: Optional[str] = None
    is_active: bool
    created_at: datetime


class QuestionBankResponse(BaseModel):
    """Schema for question bank response."""
    items: List[QuestionBankItem]
    total: int

