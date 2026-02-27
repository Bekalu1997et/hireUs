"""
Interview Kit AI schemas for kit generation.
Pydantic models for interview kit input/output.
"""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

from app.core.llm.schema import InterviewType


class RubricCriterion(BaseModel):
    """Rubric criterion schema for interview evaluation."""
    name: str = Field(..., description="Criterion name")
    description: str = Field(..., description="What to evaluate")
    max_score: int = Field(default=5, ge=1, le=10, description="Maximum score for this criterion")
    weight: int = Field(default=1, ge=1, le=5, description="Weight of this criterion")


class QuestionItem(BaseModel):
    """Question item schema for interview kits."""
    question: str = Field(..., description="The question text")
    type: str = Field(default="open-ended", description="Question type: open-ended, coding, scenario")
    duration_minutes: int = Field(default=10, description="Suggested time for this question")
    difficulty: str = Field(default="medium", description="Difficulty level: easy, medium, hard")
    notes: Optional[str] = Field(None, description="Additional notes for interviewer")


class InterviewKitInput(BaseModel):
    """Input schema for interview kit generation."""
    role_title: str = Field(..., description="Job title for the role")
    seniority: str = Field(..., description="Seniority level")
    stack: Optional[List[str]] = Field(default_factory=list, description="Technology stack")
    interview_type: InterviewType = Field(..., description="Type of interview")
    competencies: Optional[List[str]] = Field(default_factory=list, description="Core competencies to evaluate")
    duration_minutes: int = Field(default=60, ge=15, le=180, description="Estimated interview duration")
    additional_context: Optional[str] = Field(None, description="Any additional context")


class InterviewKitOutput(BaseModel):
    """Output schema for interview kit generation."""
    title: str = Field(..., description="Kit title")
    problem_statement: str = Field(..., description="Problem statement for the interview")
    evaluation_rubric: List[RubricCriterion] = Field(..., description="Evaluation rubric criteria")
    red_flags: List[str] = Field(..., description="Red flags to watch for")
    good_answer_outline: str = Field(..., description="Outline of a good answer")
    questions: List[QuestionItem] = Field(default_factory=list, description="Interview questions")
    tips_for_interviewer: Optional[str] = Field(None, description="Tips for the interviewer")
    suggested_duration_breakdown: Optional[Dict[str, int]] = Field(None, description="Suggested time breakdown")

