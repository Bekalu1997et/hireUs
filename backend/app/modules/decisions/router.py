"""
Decision Brief Router.
API endpoints for decision briefs.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.decisions.service import DecisionBriefService
from app.modules.decisions.ai.schema import DecisionBriefInput


router = APIRouter(prefix="/decisions", tags=["Decisions"])


@router.post("/brief/generate")
async def generate_decision_brief(
    input_data: DecisionBriefInput,
    organization_id: Optional[str] = Query(None, description="Organization ID for filtering"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a decision brief for a candidate.
    
    This endpoint analyzes all submitted evaluations for a candidate and
    generates an AI-powered decision brief including:
    - Candidate summary
    - Strengths identification
    - Risk area analysis
    - Signal gap detection
    - Interview agreement analysis
    - Suggested hiring decision
    """
    try:
        service = DecisionBriefService(db)
        
        # Use query param for org ID (in production, get from auth context)
        if not organization_id:
            raise HTTPException(
                status_code=400,
                detail="Organization ID is required"
            )
        
        # Generate brief (user_id would come from auth context)
        result = await service.generate_brief(
            input_data=input_data,
            organization_id=organization_id,
            user_id="system"  # Would be extracted from auth context
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate decision brief: {str(e)}"
        )


@router.get("/brief/{brief_id}")
async def get_decision_brief(
    brief_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific decision brief.
    
    Note: In production, briefs would be stored in a database table
    and retrieved by ID.
    """
    # For now, briefs are generated on-demand
    raise HTTPException(
        status_code=404,
        detail="Brief storage not yet implemented. Please regenerate the brief."
    )


@router.get("/candidates/{candidate_id}/briefs")
async def get_candidate_briefs(
    candidate_id: str,
    organization_id: Optional[str] = Query(None, description="Organization ID for filtering"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all briefs for a specific candidate.
    Returns brief summaries including statistics and recommendations.
    """
    try:
        service = DecisionBriefService(db)
        
        if not organization_id:
            raise HTTPException(
                status_code=400,
                detail="Organization ID is required"
            )
        
        briefs = await service.get_candidate_briefs(
            candidate_id=candidate_id,
            organization_id=organization_id
        )
        
        return {
            "candidate_id": candidate_id,
            "briefs": briefs,
            "count": len(briefs)
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve briefs: {str(e)}"
        )


@router.get("/candidates/{candidate_id}/signal-analysis")
async def get_candidate_signal_analysis(
    candidate_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get signal gap analysis for a candidate.
    
    This endpoint provides:
    - Detected signal gaps (missing evaluations)
    - Interview agreement analysis
    - Overall signal strength assessment
    """
    try:
        service = DecisionBriefService(db)
        
        analysis = await service.get_signal_gap_analysis(candidate_id)
        
        return analysis
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze signals: {str(e)}"
        )


@router.get("/candidates/{candidate_id}/statistics")
async def get_candidate_evaluation_stats(
    candidate_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get evaluation statistics for a candidate.
    
    Returns:
    - Total evaluations
    - Average scores per competency
    - Confidence scores
    - Recommendation breakdown
    """
    try:
        service = DecisionBriefService(db)
        
        stats = await service.get_brief_statistics(candidate_id)
        
        return {
            "candidate_id": candidate_id,
            "statistics": stats
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )


@router.get("/candidates")
async def get_comparable_candidates(
    organization_id: str = Query(..., description="Organization ID"),
    role_id: Optional[str] = Query(None, description="Filter by role"),
    min_evaluations: int = Query(default=1, ge=1, description="Minimum number of evaluations"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get candidates eligible for decision briefs.
    
    Returns candidates who have at least the minimum number of
    submitted evaluations.
    """
    try:
        service = DecisionBriefService(db)
        
        result = await service.get_comparable_candidates(
            organization_id=organization_id,
            role_id=role_id,
            min_evaluations=min_evaluations,
            skip=skip,
            limit=limit
        )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve candidates: {str(e)}"
        )


@router.post("/brief/bulk-generate")
async def bulk_generate_briefs(
    candidate_ids: List[str],
    organization_id: str = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate decision briefs for multiple candidates.
    
    Useful for generating briefs for all candidates in a role.
    """
    try:
        service = DecisionBriefService(db)
        
        result = await service.generate_bulk_briefs(
            candidate_ids=candidate_ids,
            organization_id=organization_id,
            user_id="system"
        )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Bulk generation failed: {str(e)}"
        )


@router.get("/summary")
async def get_decision_summary(
    organization_id: str = Query(..., description="Organization ID"),
    role_id: Optional[str] = Query(None, description="Filter by role"),
    min_evaluations: int = Query(default=1, ge=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a summary of all candidates ready for decision briefs.
    
    Returns statistics and list of candidates with sufficient evaluations.
    """
    try:
        service = DecisionBriefService(db)
        
        candidates_result = await service.get_comparable_candidates(
            organization_id=organization_id,
            role_id=role_id,
            min_evaluations=min_evaluations,
            skip=skip,
            limit=limit
        )
        
        return {
            "summary": {
                "total_candidates": candidates_result["total"],
                "role_filter": role_id,
                "min_evaluations": min_evaluations
            },
            "candidates": candidates_result["candidates"],
            "pagination": {
                "page": candidates_result["page"],
                "page_size": candidates_result["page_size"],
                "total_pages": candidates_result["total_pages"]
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve summary: {str(e)}"
        )

