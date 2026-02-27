"""
Evaluation router.
API endpoints for Structured Scorecards/Feedbacks.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import get_current_active_user
from app.db.models import User

from app.schemas.evaluation import (
    ScorecardCreate,
    ScorecardUpdate,
    ScorecardResponse,
    ScorecardListResponse,
    ScorecardValidationResult,
    FeedbackImproveRequest,
    FeedbackImproveResponse,
    CandidateScorecardsResponse,
    ScorecardSummary,
)

from app.modules.evaluations.service import EvaluationService
from app.modules.evaluations.ai.feedback_refiner import get_feedback_refiner


router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


# ============== Scorecard CRUD Endpoints ==============

@router.post("/", response_model=ScorecardResponse, status_code=status.HTTP_201_CREATED)
async def create_scorecard(
    scorecard_data: ScorecardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new scorecard/evaluation.
    
    This endpoint creates a new feedback form for a candidate interview.
    By default, the scorecard is created as a draft.
    """
    service = EvaluationService(db)
    
    try:
        scorecard = await service.create_scorecard(scorecard_data, current_user.id)
        return scorecard
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=ScorecardListResponse)
async def list_scorecards(
    organization_id: Optional[str] = Query(None, description="Filter by organization"),
    role_id: Optional[str] = Query(None, description="Filter by role"),
    candidate_id: Optional[str] = Query(None, description="Filter by candidate"),
    interviewer_id: Optional[str] = Query(None, description="Filter by interviewer"),
    is_submitted: Optional[bool] = Query(None, description="Filter by submission status"),
    is_draft: Optional[bool] = Query(None, description="Filter by draft status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all scorecards with optional filters.
    """
    service = EvaluationService(db)
    
    result = await service.list_scorecards(
        organization_id=organization_id,
        role_id=role_id,
        candidate_id=candidate_id,
        interviewer_id=interviewer_id,
        is_submitted=is_submitted,
        is_draft=is_draft,
        skip=skip,
        limit=limit
    )
    
    return result


@router.get("/my-drafts", response_model=List[ScorecardResponse])
async def get_my_drafts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all draft scorecards for the current user.
    """
    service = EvaluationService(db)
    
    return await service.get_interviewer_scorecards(
        interviewer_id=current_user.id,
        skip=skip,
        limit=limit,
        is_draft=True
    )


@router.get("/{scorecard_id}", response_model=ScorecardResponse)
async def get_scorecard(
    scorecard_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific scorecard by ID.
    """
    service = EvaluationService(db)
    scorecard = await service.get_scorecard(scorecard_id)
    
    if not scorecard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scorecard not found"
        )
    
    return scorecard


@router.put("/{scorecard_id}", response_model=ScorecardResponse)
async def update_scorecard(
    scorecard_id: str,
    scorecard_data: ScorecardUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a scorecard.
    
    Can only update scorecards that are in draft mode.
    """
    service = EvaluationService(db)
    
    # Get existing scorecard
    existing = await service.get_scorecard(scorecard_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scorecard not found"
        )
    
    # Check if already submitted
    if existing.is_submitted and not existing.is_draft:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update a submitted scorecard. Create a duplicate instead."
        )
    
    scorecard = await service.update_scorecard(scorecard_id, scorecard_data)
    
    if not scorecard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scorecard not found"
        )
    
    return scorecard


@router.delete("/{scorecard_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scorecard(
    scorecard_id: str,
    hard_delete: bool = Query(False, description="Permanently delete the scorecard"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a scorecard (soft delete by default).
    """
    service = EvaluationService(db)
    
    # Get existing scorecard
    existing = await service.get_scorecard(scorecard_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scorecard not found"
        )
    
    # Only allow owner to delete
    if existing.interviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own scorecards"
        )
    
    success = await service.delete_scorecard(scorecard_id, hard_delete)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete scorecard"
        )


# ============== Submission Endpoints ==============

@router.post("/{scorecard_id}/submit")
async def submit_scorecard(
    scorecard_id: str,
    validate_first: bool = Query(True, description="Validate before submission"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Submit a scorecard.
    
    This marks the scorecard as final and visible to others.
    If validate_first is true, checks that all required fields are filled.
    """
    service = EvaluationService(db)
    
    # Get existing scorecard
    existing = await service.get_scorecard(scorecard_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scorecard not found"
        )
    
    # Check ownership
    if existing.interviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit your own scorecards"
        )
    
    # Check if already submitted
    if existing.is_submitted and not existing.is_draft:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scorecard is already submitted"
        )
    
    result = await service.submit_scorecard(scorecard_id, validate_first)
    
    if not result["success"]:
        return {
            "success": False,
            "message": result["message"],
            "validation": result.get("validation")
        }
    
    return {
        "success": True,
        "message": "Scorecard submitted successfully",
        "submitted_at": result["scorecard"].submitted_at
    }


@router.get("/{scorecard_id}/validate", response_model=ScorecardValidationResult)
async def validate_scorecard(
    scorecard_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Validate a scorecard for submission.
    
    Returns validation status and any missing required fields.
    """
    service = EvaluationService(db)
    
    # Get existing scorecard
    existing = await service.get_scorecard(scorecard_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scorecard not found"
        )
    
    return await service.validate_for_submission(scorecard_id)


# ============== Candidate Scorecards Endpoints ==============

@router.get("/candidates/{candidate_id}", response_model=CandidateScorecardsResponse)
async def get_candidate_scorecards(
    candidate_id: str,
    submitted_only: bool = Query(True, description="Only include submitted scorecards"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all scorecards for a specific candidate.
    """
    service = EvaluationService(db)
    
    scorecards = await service.get_candidate_scorecards(
        candidate_id=candidate_id,
        submitted_only=submitted_only
    )
    
    # Build summaries
    summaries = []
    for fb in scorecards:
        # Calculate average score
        all_scores = []
        for score_data in fb.scores.values():
            if isinstance(score_data, dict) and "score" in score_data:
                all_scores.append(score_data["score"])
        
        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
        
        summaries.append(ScorecardSummary(
            id=fb.id,
            candidate_id=fb.candidate_id,
            interviewer_id=fb.interviewer_id,
            average_score=round(avg_score, 2),
            recommendation=fb.recommendation,
            is_submitted=fb.is_submitted,
            submitted_at=fb.submitted_at,
            created_at=fb.created_at
        ))
    
    # Calculate overall average
    all_avgs = [s.average_score for s in summaries]
    overall_avg = sum(all_avgs) / len(all_avgs) if all_avgs else 0
    
    return {
        "candidate_id": candidate_id,
        "scorecards": summaries,
        "total_scorecards": len(summaries),
        "average_score": round(overall_avg, 2)
    }


# ============== AI Feedback Improvement Endpoints ==============

@router.post("/{scorecard_id}/improve-feedback", response_model=FeedbackImproveResponse)
async def improve_feedback(
    scorecard_id: str,
    request: FeedbackImproveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Improve feedback clarity using AI (Ollama).
    
    This endpoint uses AI to rewrite vague feedback into clearer,
    more actionable feedback.
    """
    service = EvaluationService(db)
    
    # Get existing scorecard
    existing = await service.get_scorecard(scorecard_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scorecard not found"
        )
    
    # Check ownership
    if existing.interviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only improve your own scorecards"
        )
    
    refiner = get_feedback_refiner()
    
    result = await refiner.improve_feedback(
        strengths=existing.strengths,
        weaknesses=existing.weaknesses,
        summary=existing.summary,
        scores=existing.scores,
        target=request.target,
        context=request.context
    )
    
    return result


@router.post("/{scorecard_id}/suggest-evidence")
async def suggest_evidence(
    scorecard_id: str,
    competency: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get AI suggestions for evidence for a competency.
    """
    service = EvaluationService(db)
    
    # Get existing scorecard
    existing = await service.get_scorecard(scorecard_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scorecard not found"
        )
    
    # Check ownership
    if existing.interviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only get suggestions for your own scorecards"
        )
    
    # Get score for competency
    score_data = existing.scores.get(competency)
    score = 0
    if isinstance(score_data, dict):
        score = score_data.get("score", 0)
    
    current_evidence = ""
    if existing.evidence:
        current_evidence = existing.evidence.get(competency, "")
    
    refiner = get_feedback_refiner()
    
    result = await refiner.suggest_evidence(
        competency=competency,
        score=score,
        current_evidence=current_evidence
    )
    
    return result


@router.post("/{scorecard_id}/generate-summary")
async def generate_summary_from_scores(
    scorecard_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a summary paragraph from scores and feedback using AI.
    """
    service = EvaluationService(db)
    
    # Get existing scorecard
    existing = await service.get_scorecard(scorecard_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scorecard not found"
        )
    
    # Check ownership
    if existing.interviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only generate summaries for your own scorecards"
        )
    
    refiner = get_feedback_refiner()
    
    summary = await refiner.generate_summary_from_scores(
        scores=existing.scores,
        strengths=existing.strengths,
        weaknesses=existing.weaknesses
    )
    
    return {
        "generated_summary": summary
    }


# ============== Statistics Endpoints ==============

@router.get("/candidates/{candidate_id}/stats")
async def get_candidate_evaluation_stats(
    candidate_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get evaluation statistics for a candidate.
    """
    service = EvaluationService(db)
    
    return await service.get_evaluation_stats(candidate_id)


@router.get("/candidates/{candidate_id}/average-scores")
async def get_candidate_average_scores(
    candidate_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get average scores across all evaluations for a candidate.
    """
    service = EvaluationService(db)
    
    return await service.calculate_average_scores(candidate_id)


# ============== Assignment Endpoints ==============

@router.get("/assignments/{assignment_id}/feedback-status")
async def get_assignment_feedback_status(
    assignment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Check if feedback is required for an assignment and its status.
    """
    service = EvaluationService(db)
    
    return await service.check_assignment_feedback_required(assignment_id)
