"""
Pydantic schemas for Candidate Comparison.
Defines request/response schemas for the comparison API endpoints.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# ============== Competency Score Schemas ==============

class CompetencyScoreData(BaseModel):
    """
    Schema for a single competency score data.
    """
    competency: str = Field(..., description="Name of the competency")
    score: float = Field(..., ge=1, le=5, description="Score from 1-5")
    evidence: Optional[str] = Field(None, description="Written evidence supporting the score")


class CompetencyComparison(BaseModel):
    """
    Schema for comparing a competency across candidates.
    """
    competency: str = Field(..., description="Name of the competency")
    scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Candidate ID to score mapping"
    )
    average: float = Field(..., description="Average score across candidates")
    std_deviation: Optional[float] = Field(
        None,
        description="Standard deviation of scores"
    )
    min_score: float = Field(..., description="Minimum score")
    max_score: float = Field(..., description="Maximum score")


# ============== Candidate Comparison Schemas ==============

class CandidateSummary(BaseModel):
    """
    Summary of a candidate for comparison.
    """
    id: str = Field(..., description="Candidate ID")
    name: str = Field(..., description="Candidate full name")
    email: str = Field(..., description="Candidate email")
    role_id: Optional[str] = Field(None, description="Applied role ID")
    role_title: Optional[str] = Field(None, description="Applied role title")
    status: str = Field(..., description="Candidate status")
    current_stage: Optional[str] = Field(None, description="Current workflow stage")

    model_config = ConfigDict(from_attributes=True)


class CandidateComparisonInput(BaseModel):
    """
    Request schema for comparing candidates.
    """
    candidate_ids: List[str] = Field(
        ...,
        min_length=2,
        max_length=10,
        description="List of candidate IDs to compare (2-10 candidates)"
    )
    include_evaluations: bool = Field(
        default=True,
        description="Whether to include evaluation details"
    )
    include_feedback_summary: bool = Field(
        default=True,
        description="Whether to include written feedback summary"
    )


class CandidateScoreSummary(BaseModel):
    """
    Score summary for a candidate in comparison.
    """
    candidate_id: str
    candidate_name: str
    
    # Overall stats
    overall_average: float = Field(..., description="Overall average score (1-5)")
    total_evaluations: int = Field(..., description="Number of submitted evaluations")
    
    # Competency scores
    competency_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Competency name to average score mapping"
    )
    
    # Confidence
    average_confidence: float = Field(..., description="Average confidence score (1-5)")
    confidence_variance: Optional[float] = Field(
        None,
        description="Variance in confidence scores"
    )
    
    # Recommendations
    recommendation_counts: Dict[str, int] = Field(
        default_factory=dict,
        description="Count of each recommendation type"
    )
    dominant_recommendation: Optional[str] = Field(
        None,
        description="Most common recommendation"
    )


class CandidateComparisonResponse(BaseModel):
    """
    Response schema for candidate comparison.
    """
    # Metadata
    compared_at: datetime = Field(default_factory=datetime.utcnow)
    candidates_compared: int = Field(..., description="Number of candidates compared")
    
    # Candidates
    candidates: List[CandidateSummary] = Field(
        default_factory=list,
        description="List of candidate summaries"
    )
    
    # Score summaries
    score_summaries: Dict[str, CandidateScoreSummary] = Field(
        default_factory=dict,
        description="Candidate ID to score summary mapping"
    )
    
    # Competency comparisons
    competency_comparisons: List[CompetencyComparison] = Field(
        default_factory=list,
        description="Comparison for each competency"
    )
    
    # Rankings
    rankings: Dict[str, Any] = Field(
        default_factory=dict,
        description="Rankings by various criteria"
    )
    
    # Feedback summary
    feedback_summary: Optional[Dict[str, str]] = Field(
        None,
        description="Aggregated feedback summary"
    )


# ============== Signal Gap Detection Schemas ==============

class SignalGap(BaseModel):
    """
    Schema for a signal gap in candidate evaluation.
    """
    competency: str = Field(..., description="Competency with signal gap")
    severity: str = Field(..., description="Severity: low, medium, high")
    description: str = Field(..., description="Description of the gap")
    recommendation: str = Field(..., description="Recommended action")


class SignalGapDetectionInput(BaseModel):
    """
    Request schema for signal gap detection.
    """
    candidate_id: str = Field(..., description="Candidate ID to analyze")
    competency_threshold: float = Field(
        default=3.0,
        ge=1,
        le=5,
        description="Minimum score threshold for competency"
    )
    confidence_threshold: float = Field(
        default=3.0,
        ge=1,
        le=5,
        description="Minimum confidence threshold"
    )
    variance_threshold: float = Field(
        default=1.0,
        ge=0,
        le=4,
        description="Maximum acceptable variance"
    )


class SignalGapDetectionResponse(BaseModel):
    """
    Response schema for signal gap detection.
    """
    candidate_id: str
    has_gaps: bool = Field(..., description="Whether any gaps were found")
    signal_gaps: List[SignalGap] = Field(
        default_factory=list,
        description="List of detected signal gaps"
    )
    overall_signal_strength: str = Field(..., description="strong, moderate, weak")
    recommendations: List[str] = Field(
        default_factory=list,
        description="Recommended actions"
    )
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


# ============== Ranking Schemas ==============

class CandidateRanking(BaseModel):
    """
    Ranking information for a candidate.
    """
    rank: int = Field(..., description="Position in ranking (1-based)")
    candidate_id: str = Field(..., description="Candidate ID")
    candidate_name: str = Field(..., description="Candidate name")
    score: float = Field(..., description="Score used for ranking")
    improvement_areas: List[str] = Field(
        default_factory=list,
        description="Areas where candidate can improve"
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="Candidate strengths"
    )


class RankingCriteria(str):
    """
    Criteria for ranking candidates.
    """
    OVERALL_SCORE = "overall_score"
    COMPETENCY_MATCH = "competency_match"
    CONFIDENCE = "confidence"
    RECOMMENDATION = "recommendation"
    EVALUATION_COUNT = "evaluation_count"


class RankingResponse(BaseModel):
    """
    Response schema for candidate rankings.
    """
    criteria: str = Field(..., description="Ranking criteria used")
    direction: str = Field(..., description="ascending or descending")
    rankings: List[CandidateRanking] = Field(
        default_factory=list,
        description="Ordered list of ranked candidates"
    )
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# ============== Batch Comparison Schemas ==============

class BatchComparisonInput(BaseModel):
    """
    Request schema for batch comparison of many candidates.
    """
    candidate_ids: List[str] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="List of candidate IDs"
    )
    max_candidates_per_comparison: int = Field(
        default=5,
        ge=2,
        le=10,
        description="Maximum candidates to show in a single comparison view"
    )
    include_heatmap: bool = Field(
        default=True,
        description="Include heatmap data"
    )


class BatchComparisonChunk(BaseModel):
    """
    A chunk of candidates for comparison.
    """
    chunk_index: int = Field(..., description="Index of this chunk (0-based)")
    candidates: List[CandidateSummary] = Field(
        default_factory=list,
        description="Candidates in this chunk"
    )
    comparison: CandidateComparisonResponse = Field(
        ...,
        description="Comparison result for this chunk"
    )


class BatchComparisonResponse(BaseModel):
    """
    Response schema for batch comparison.
    """
    total_candidates: int = Field(..., description="Total candidates requested")
    total_chunks: int = Field(..., description="Number of chunks created")
    chunks: List[BatchComparisonChunk] = Field(
        default_factory=list,
        description="Comparison chunks"
    )
    top_candidates: List[CandidateRanking] = Field(
        default_factory=list,
        description="Top 5 candidates overall"
    )
    generated_at: datetime = Field(default_factory=datetime.utcnow)

