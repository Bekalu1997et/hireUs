"""
Pydantic schemas for Structured Scorecards/Evaluations.
Defines request/response schemas for the evaluation/scorecard API endpoints.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# ============== Competency Score Schemas ==============

class CompetencyScore(BaseModel):
    """
    Schema for a single competency score.
    """
    competency: str = Field(..., description="Name of the competency")
    score: int = Field(..., ge=1, le=5, description="Score from 1-5")
    evidence: Optional[str] = Field(None, description="Written evidence supporting the score")
    notes: Optional[str] = Field(None, description="Additional notes")


class CompetencyScoreUpdate(BaseModel):
    """
    Schema for updating a competency score.
    """
    score: int = Field(..., ge=1, le=5)
    evidence: Optional[str] = None
    notes: Optional[str] = None


# ============== Scorecard Schemas ==============

class ScorecardCreate(BaseModel):
    """
    Schema for creating a new scorecard/evaluation.
    """
    candidate_id: str = Field(..., description="ID of the candidate being evaluated")
    assignment_id: Optional[str] = Field(None, description="ID of the interview assignment")
    
    # Competency scores
    scores: Dict[str, CompetencyScore] = Field(
        default_factory=dict, 
        description="Dictionary of competency scores"
    )
    
    # Confidence level (1-5)
    confidence: int = Field(default=3, ge=1, le=5, description="Interviewer confidence level")
    
    # Written feedback
    strengths: Optional[str] = Field(None, description="Candidate strengths observed")
    weaknesses: Optional[str] = Field(None, description="Areas for improvement")
    summary: Optional[str] = Field(None, description="Overall summary of the interview")
    recommendation: str = Field(
        default="neutral", 
        description="Hiring recommendation"
    )
    
    # Metadata
    is_draft: bool = Field(default=True, description="Whether this is a draft or submitted")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "candidate_id": "uuid-candidate-id",
            "assignment_id": "uuid-assignment-id",
            "scores": {
                "System Design": {
                    "competency": "System Design",
                    "score": 4,
                    "evidence": "Candidate designed a scalable microservices architecture with proper service discovery and load balancing."
                },
                "Communication": {
                    "competency": "Communication",
                    "score": 3,
                    "evidence": "Clear explanations but sometimes missed opportunities to clarify requirements."
                }
            },
            "confidence": 4,
            "strengths": "Strong system design skills, good understanding of distributed systems.",
            "weaknesses": "Could improve on requirement gathering and clarification.",
            "summary": "Overall strong performance with good technical foundation.",
            "recommendation": "neutral",
            "is_draft": True
        }
    })


class ScorecardUpdate(BaseModel):
    """
    Schema for updating an existing scorecard.
    """
    scores: Optional[Dict[str, CompetencyScoreUpdate]] = Field(
        None, 
        description="Dictionary of competency scores"
    )
    confidence: Optional[int] = Field(None, ge=1, le=5)
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    summary: Optional[str] = None
    recommendation: Optional[str] = None
    is_draft: Optional[bool] = None


class ScorecardSubmit(BaseModel):
    """
    Schema for submitting a scorecard.
    Validates that all required fields are present before submission.
    """
    pass


class ScorecardResponse(BaseModel):
    """
    Schema for a scorecard response.
    """
    id: str
    candidate_id: str
    interviewer_id: str
    assignment_id: Optional[str] = None
    
    # Scores
    scores: Dict[str, Any] = Field(default_factory=dict)
    confidence: int
    
    # Written feedback
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    summary: Optional[str] = None
    recommendation: str
    
    # Evidence
    evidence: Dict[str, str] = Field(default_factory=dict)
    
    # AI
    ai_suggestions: Optional[str] = None
    
    # Status
    is_draft: bool
    is_submitted: bool
    submitted_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ScorecardListResponse(BaseModel):
    """
    Schema for paginated list of scorecards.
    """
    items: List[ScorecardResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============== AI Feedback Improvement Schemas ==============

class FeedbackImproveRequest(BaseModel):
    """
    Request schema for AI feedback improvement.
    """
    target: str = Field(
        ..., 
        description="What to improve: strengths, weaknesses, summary, or all"
    )
    context: Optional[str] = Field(
        None, 
        description="Additional context for the AI"
    )


class FeedbackImproveResponse(BaseModel):
    """
    Response schema for AI feedback improvement.
    """
    success: bool
    improved_text: Optional[str] = None
    suggestions: Optional[List[str]] = None
    error: Optional[str] = None


class FeedbackSuggestion(BaseModel):
    """
    Individual feedback suggestion from AI.
    """
    field: str = Field(..., description="Field being improved (strengths, weaknesses, summary)")
    original: str = Field(..., description="Original text")
    improved: str = Field(..., description="AI-improved text")
    explanation: Optional[str] = Field(None, description="Why this improvement is suggested")


# ============== Scorecard Summary Schemas ==============

class ScorecardSummary(BaseModel):
    """
    Summary of a scorecard for quick viewing.
    """
    id: str
    candidate_id: str
    candidate_name: Optional[str] = None
    interviewer_id: str
    average_score: float
    recommendation: str
    is_submitted: bool
    submitted_at: Optional[datetime] = None
    created_at: datetime


class CandidateScorecardsResponse(BaseModel):
    """
    Response for all scorecards of a candidate.
    """
    candidate_id: str
    candidate_name: Optional[str] = None
    scorecards: List[ScorecardSummary]
    total_scorecards: int
    average_score: float


# ============== Validation Schemas ==============

class ScorecardValidationResult(BaseModel):
    """
    Result of validating a scorecard before submission.
    """
    is_valid: bool
    missing_competencies: List[str] = Field(default_factory=list)
    missing_evidence: List[str] = Field(default_factory=list)
    low_confidence_warning: bool = False
    messages: List[str] = Field(default_factory=list)

