"""
AI schemas for Decision Brief Generator.
Structured schemas for AI-generated decision briefs.
"""
import enum
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CandidateStrengths(BaseModel):
    """Schema for candidate strengths identified from evaluations."""
    category: str = Field(..., description="Category of strength (e.g., 'Technical Skills', 'Problem Solving')")
    description: str = Field(..., description="Detailed description of the strength")
    evidence: List[str] = Field(default_factory=list, description="Evidence from evaluations supporting this strength")
    competency_scores: Dict[str, float] = Field(default_factory=dict, description="Related competency scores")


class RiskArea(BaseModel):
    """Schema for risk areas or concerns identified from evaluations."""
    category: str = Field(..., description="Category of risk (e.g., 'Experience Gap', 'Cultural Fit')")
    description: str = Field(..., description="Detailed description of the risk")
    severity: str = Field(..., description="Severity level: low, medium, high")
    mitigation: Optional[str] = Field(None, description="Suggestions for mitigating this risk")
    evidence: List[str] = Field(default_factory=list, description="Evidence from evaluations")


class SignalGap(BaseModel):
    """Schema for signal gaps - areas lacking sufficient evaluation data."""
    competency: str = Field(..., description="Competency with missing signal")
    status: str = Field(..., description="Status: 'missing', 'weak', or 'conflicting'")
    reason: str = Field(..., description="Why this gap exists")
    recommendation: str = Field(..., description="Recommendation for additional evaluation")
    confidence_impact: Optional[str] = Field(None, description="How this impacts overall confidence")


class InterviewAgreementLevel(str, enum.Enum):
    """Enumeration for interview agreement levels."""
    STRONG_AGREEMENT = "strong_agreement"
    MODERATE_AGREEMENT = "moderate_agreement"
    MIXED_OPINIONS = "mixed_opinions"
    CONFLICTING_VIEWS = "conflicting_views"


class InterviewAgreement(BaseModel):
    """Schema for interview agreement analysis."""
    level: InterviewAgreementLevel = Field(..., description="Overall agreement level")
    description: str = Field(..., description="Detailed analysis of interview agreement")
    agreements: List[str] = Field(default_factory=list, description="Areas where interviewers agree")
    disagreements: List[str] = Field(default_factory=list, description="Areas where interviewers disagree")
    confidence_score: float = Field(..., description="Confidence in this analysis (0-1)")
    evaluator_count: int = Field(..., description="Number of evaluators")


class SuggestedDecision(str, enum.Enum):
    """Enumeration for suggested hiring decisions."""
    STRONG_HIRE = "strong_hire"
    HIRE = "hire"
    NEUTRAL = "neutral"
    NO_HIRE = "no_hire"
    STRONG_NO_HIRE = "strong_no_hire"
    DEFER = "defer"


class SuggestedDecisionOutput(BaseModel):
    """Schema for suggested decision with reasoning."""
    decision: SuggestedDecision = Field(..., description="Suggested hiring decision")
    confidence: float = Field(..., description="Confidence in this decision (0-1)")
    reasoning: str = Field(..., description="Detailed reasoning for the decision")
    key_factors: List[str] = Field(default_factory=list, description="Key factors influencing the decision")
    risks_acknowledged: List[str] = Field(default_factory=list, description="Risks that were acknowledged but overruled")
    next_steps: List[str] = Field(default_factory=list, description="Recommended next steps")


class CandidateSummaryBrief(BaseModel):
    """Brief summary of the candidate."""
    name: str = Field(..., description="Candidate's full name")
    role_applied: str = Field(..., description="Role the candidate applied for")
    overall_score: float = Field(..., description="Average overall score across evaluations")
    total_evaluations: int = Field(..., description="Number of evaluations")
    recommendation_breakdown: Dict[str, int] = Field(default_factory=dict, description="Breakdown of recommendations")


class DecisionBriefOutput(BaseModel):
    """Complete AI-generated decision brief output."""
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="When the brief was generated")
    
    # Candidate overview
    candidate: CandidateSummaryBrief = Field(..., description="Candidate summary")
    
    # Core sections
    strengths: List[CandidateStrengths] = Field(default_factory=list, description="Identified strengths")
    risk_areas: List[RiskArea] = Field(default_factory=list, description="Identified risk areas")
    signal_gaps: List[SignalGap] = Field(default_factory=list, description="Detected signal gaps")
    interview_agreement: InterviewAgreement = Field(..., description="Interview agreement analysis")
    
    # Decision recommendation
    suggested_decision: SuggestedDecisionOutput = Field(..., description="AI-suggested decision with reasoning")
    
    # Metadata
    evaluation_ids: List[str] = Field(default_factory=list, description="IDs of evaluations used")
    model_used: Optional[str] = Field(None, description="AI model used for generation")
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")


class DecisionBriefInput(BaseModel):
    """Input schema for generating a decision brief."""
    candidate_id: str = Field(..., description="ID of the candidate to generate brief for")
    include_comparison: bool = Field(default=False, description="Include comparison with other candidates")
    comparison_candidate_ids: List[str] = Field(default_factory=list, description="Candidate IDs to compare against")
    focus_areas: List[str] = Field(default_factory=list, description="Specific areas to focus analysis on")
    custom_prompt: Optional[str] = Field(None, description="Custom prompt to add to the analysis")


class DecisionBriefDocument(BaseModel):
    """Schema for storing a decision brief document."""
    id: str = Field(..., description="Unique identifier")
    candidate_id: str = Field(..., description="Candidate ID this brief is for")
    organization_id: str = Field(..., description="Organization ID")
    
    # Brief content
    content: DecisionBriefOutput = Field(..., description="The decision brief content")
    
    # Metadata
    generated_by: str = Field(..., description="User ID who generated this brief")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_latest: bool = Field(default=True, description="Whether this is the latest brief for the candidate")


class SignalGapDetectionResult(BaseModel):
    """Result of signal gap detection analysis."""
    has_gaps: bool = Field(..., description="Whether signal gaps were detected")
    overall_signal_strength: str = Field(..., description="Overall signal strength: strong, moderate, weak, none")
    gaps: List[Dict[str, Any]] = Field(default_factory=list, description="Detailed gap information")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for addressing gaps")
    missing_competencies: List[str] = Field(default_factory=list, description="Competencies with no scores")
    low_confidence_areas: List[str] = Field(default_factory=list, description="Areas with low confidence")
    conflicting_areas: List[str] = Field(default_factory=list, description="Areas with conflicting scores")

