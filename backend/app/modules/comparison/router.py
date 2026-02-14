"""
Comparison router.
API endpoints for candidate comparison.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.comparison.schemas import (
    CandidateComparisonInput,
    CandidateComparisonResponse,
    SignalGapDetectionInput,
    SignalGapDetectionResponse,
    RankingCriteria,
    RankingResponse,
    BatchComparisonInput,
    BatchComparisonResponse,
)
from app.modules.comparison.service import ComparisonService


router = APIRouter(prefix="/comparison", tags=["Comparison"])


@router.post("/compare", response_model=CandidateComparisonResponse)
async def compare_candidates(
    comparison_input: CandidateComparisonInput,
    db: AsyncSession = Depends(get_db)
):
    """
    Compare multiple candidates side by side.
    
    Provides:
    - Side-by-side competency scores
    - Average scores and standard deviations
    - Confidence metrics
    - Rankings
    - Aggregated feedback summary
    """
    try:
        service = ComparisonService(db)
        result = await service.compare_candidates(comparison_input)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@router.post("/signal-gaps", response_model=SignalGapDetectionResponse)
async def detect_signal_gaps(
    gap_input: SignalGapDetectionInput,
    db: AsyncSession = Depends(get_db)
):
    """
    Detect signal gaps in candidate evaluation.
    
    Identifies:
    - Competencies with low scores
    - Low confidence from evaluators
    - Insufficient evaluation data
    
    Returns recommendations for additional interviews or evaluation.
    """
    try:
        service = ComparisonService(db)
        result = await service.detect_signal_gaps(gap_input)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signal gap detection failed: {str(e)}")


@router.get("/rank", response_model=RankingResponse)
async def rank_candidates(
    candidate_ids: List[str] = Query(..., min_length=2, max_length=50),
    criteria: str = Query(default=RankingCriteria.OVERALL_SCORE),
    db: AsyncSession = Depends(get_db)
):
    """
    Rank candidates based on specified criteria.
    
    Criteria options:
    - overall_score: Average of all competency scores
    - confidence: Average evaluator confidence
    - recommendation: Hiring recommendation score
    - evaluation_count: Number of evaluations
    """
    try:
        # Validate criteria
        valid_criteria = [
            RankingCriteria.OVERALL_SCORE,
            RankingCriteria.CONFIDENCE,
            RankingCriteria.RECOMMENDATION,
            RankingCriteria.EVALUATION_COUNT
        ]
        
        if criteria not in valid_criteria:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid criteria. Must be one of: {valid_criteria}"
            )

        service = ComparisonService(db)
        result = await service.rank_candidates(candidate_ids, criteria)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ranking failed: {str(e)}")


@router.post("/batch", response_model=BatchComparisonResponse)
async def batch_compare(
    batch_input: BatchComparisonInput,
    db: AsyncSession = Depends(get_db)
):
    """
    Compare many candidates in batches.
    
    Useful for comparing all candidates in a role.
    Returns:
    - Chunked comparisons
    - Top 5 candidates overall
    - Heatmap data for visualization
    """
    try:
        service = ComparisonService(db)
        result = await service.batch_compare(batch_input)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch comparison failed: {str(e)}")


@router.get("/heatmap")
async def get_heatmap_data(
    candidate_ids: List[str] = Query(..., min_length=2, max_length=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Get heatmap data for candidate scores.
    
    Returns data structure suitable for heatmap visualization:
    - List of competencies
    - List of candidates
    - Score matrix
    """
    try:
        service = ComparisonService(db)
        result = await service.get_heatmap_data(candidate_ids)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Heatmap generation failed: {str(e)}")


@router.get("/summary/{candidate_id}")
async def get_candidate_comparison_summary(
    candidate_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a summary for a single candidate in comparison context.
    
    Returns evaluation statistics and feedback for the candidate.
    """
    try:
        service = ComparisonService(db)
        result = await service.get_candidate_comparison_summary(candidate_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary retrieval failed: {str(e)}")


@router.get("/role/{role_id}/candidates")
async def get_comparable_candidates(
    role_id: str,
    min_evaluations: int = Query(default=1, ge=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get candidates for a role that have evaluations.
    
    Returns list of candidates eligible for comparison.
    """
    try:
        from app.modules.comparison.repository import ComparisonRepository
        
        repository = ComparisonRepository(db)
        candidates = await repository.get_candidates_with_evaluations(
            role_id=role_id,
            min_evaluations=min_evaluations,
            skip=skip,
            limit=limit
        )

        return {
            "candidates": [
                {
                    "id": c.id,
                    "name": c.full_name,
                    "email": c.email,
                    "status": c.status,
                    "role_title": c.role.title if c.role else None
                }
                for c in candidates
            ],
            "count": len(candidates)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get candidates: {str(e)}")


@router.get("/role/{role_id}/comparison")
async def compare_role_candidates(
    role_id: str,
    status_filter: Optional[List[str]] = Query(default=None),
    db: AsyncSession = Depends(get_db)
):
    """
    Compare all candidates for a specific role.
    
    Convenience endpoint that finds all candidates with evaluations
    and performs comparison.
    """
    try:
        from app.modules.comparison.repository import ComparisonRepository
        
        repository = ComparisonRepository(db)
        
        # Get candidates with evaluations
        candidates = await repository.get_candidates_with_evaluations(
            role_id=role_id,
            min_evaluations=1
        )

        if len(candidates) < 2:
            return {
                "message": "At least 2 candidates with evaluations are needed for comparison",
                "candidates_found": len(candidates),
                "comparison_available": False
            }

        candidate_ids = [c.id for c in candidates]

        # Perform comparison
        service = ComparisonService(db)
        comparison_input = CandidateComparisonInput(
            candidate_ids=candidate_ids,
            include_evaluations=True,
            include_feedback_summary=True
        )
        
        result = await service.compare_candidates(comparison_input)

        return {
            "comparison_available": True,
            "comparison": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@router.get("/workflow/{workflow_id}/stage/{stage_id}/candidates")
async def get_stage_candidates_for_comparison(
    workflow_id: str,
    stage_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get candidates at a workflow stage for comparison.
    
    Returns candidates at a specific stage that have evaluations.
    """
    try:
        from app.modules.comparison.repository import ComparisonRepository
        
        repository = ComparisonRepository(db)
        
        candidates = await repository.get_candidates_for_workflow_stage(
            workflow_id=workflow_id,
            stage_id=stage_id,
            has_evaluations=True
        )

        return {
            "stage_id": stage_id,
            "candidates": [
                {
                    "id": c.id,
                    "name": c.full_name,
                    "email": c.email,
                    "status": c.status
                }
                for c in candidates
            ],
            "count": len(candidates)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get candidates: {str(e)}")

