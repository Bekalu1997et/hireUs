"""
Comparison repository.
Database operations for candidate comparisons.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Feedback, Candidate, User, Role
from app.modules.comparison.schemas import (
    CandidateComparisonInput,
    CandidateSummary,
    CandidateScoreSummary,
)


class ComparisonRepository:
    """
    Repository for comparison database operations.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_candidates_by_ids(
        self,
        candidate_ids: List[str]
    ) -> List[Candidate]:
        """
        Get multiple candidates by their IDs.
        """
        query = (
            select(Candidate)
            .where(Candidate.id.in_(candidate_ids))
            .options(
                selectinload(Candidate.role),
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_candidate_summary(
        self,
        candidate: Candidate
    ) -> Dict[str, Any]:
        """
        Get a summary of a candidate.
        """
        return {
            "id": candidate.id,
            "name": candidate.full_name,
            "email": candidate.email,
            "role_id": candidate.role_id,
            "role_title": candidate.role.title if candidate.role else None,
            "status": candidate.status,
            "current_stage": candidate.current_stage_id
        }

    async def get_evaluations_for_candidates(
        self,
        candidate_ids: List[str],
        submitted_only: bool = True
    ) -> Dict[str, List[Feedback]]:
        """
        Get all evaluations for multiple candidates.
        """
        conditions = [
            Feedback.candidate_id.in_(candidate_ids),
            Feedback.is_active == True
        ]
        
        if submitted_only:
            conditions.append(Feedback.is_submitted == True)

        query = (
            select(Feedback)
            .where(and_(*conditions))
            .options(
                selectinload(Feedback.candidate),
                selectinload(Feedback.interviewer),
            )
        )
        result = await self.db.execute(query)
        feedbacks = list(result.scalars().all())

        # Group by candidate ID
        by_candidate: Dict[str, List[Feedback]] = {}
        for fb in feedbacks:
            if fb.candidate_id not in by_candidate:
                by_candidate[fb.candidate_id] = []
            by_candidate[fb.candidate_id].append(fb)

        return by_candidate

    async def get_all_candidates_for_role(
        self,
        role_id: str,
        status_filter: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Candidate]:
        """
        Get all candidates for a specific role.
        """
        conditions = [Candidate.role_id == role_id]

        if status_filter:
            conditions.append(Candidate.status.in_(status_filter))

        query = (
            select(Candidate)
            .where(and_(*conditions))
            .options(
                selectinload(Candidate.role),
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_all_candidates_for_organization(
        self,
        organization_id: str,
        status_filter: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Candidate]:
        """
        Get all candidates for an organization.
        """
        conditions = [Candidate.organization_id == organization_id]

        if status_filter:
            conditions.append(Candidate.status.in_(status_filter))

        query = (
            select(Candidate)
            .where(and_(*conditions))
            .options(
                selectinload(Candidate.role),
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_candidates_with_evaluations(
        self,
        role_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        min_evaluations: int = 1,
        skip: int = 0,
        limit: int = 100
    ) -> List[Candidate]:
        """
        Get candidates that have at least a minimum number of evaluations.
        """
        from sqlalchemy import func

        conditions = [Candidate.is_active == True]

        if role_id:
            conditions.append(Candidate.role_id == role_id)
        if organization_id:
            conditions.append(Candidate.organization_id == organization_id)

        # Subquery to count evaluations per candidate
        subquery = (
            select(
                Feedback.candidate_id,
                func.count(Feedback.id).label("eval_count")
            )
            .where(
                and_(
                    Feedback.is_active == True,
                    Feedback.is_submitted == True
                )
            )
            .group_by(Feedback.candidate_id)
            .having(func.count(Feedback.id) >= min_evaluations)
            .subquery()
        )

        query = (
            select(Candidate)
            .join(subquery, Candidate.id == subquery.c.candidate_id)
            .where(and_(*conditions))
            .options(
                selectinload(Candidate.role),
            )
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_evaluation_stats_for_candidate(
        self,
        candidate_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed evaluation statistics for a candidate.
        """
        feedbacks = await self.get_evaluations_for_candidates([candidate_id])
        candidate_feedbacks = feedbacks.get(candidate_id, [])

        if not candidate_feedbacks:
            return {
                "total_evaluations": 0,
                "overall_average": 0,
                "competency_scores": {},
                "confidence_scores": [],
                "recommendation_counts": {}
            }

        # Collect all scores
        all_scores: Dict[str, List[float]] = {}
        confidence_scores: List[int] = []
        recommendation_counts: Dict[str, int] = {}

        for fb in candidate_feedbacks:
            # Collect competency scores
            if fb.scores:
                for comp, score_data in fb.scores.items():
                    if isinstance(score_data, dict) and "score" in score_data:
                        if comp not in all_scores:
                            all_scores[comp] = []
                        all_scores[comp].append(score_data["score"])
                    elif isinstance(score_data, (int, float)):
                        if comp not in all_scores:
                            all_scores[comp] = []
                        all_scores[comp].append(float(score_data))

            # Collect confidence
            if fb.confidence:
                confidence_scores.append(fb.confidence)

            # Collect recommendations
            if fb.recommendation:
                recommendation_counts[fb.recommendation] = (
                    recommendation_counts.get(fb.recommendation, 0) + 1
                )

        # Calculate averages
        competency_averages = {}
        for comp, scores in all_scores.items():
            competency_averages[comp] = sum(scores) / len(scores)

        # Calculate overall average
        all_score_values = []
        for scores in all_scores.values():
            all_score_values.extend(scores)
        overall_average = (
            sum(all_score_values) / len(all_score_values)
            if all_score_values else 0
        )

        return {
            "total_evaluations": len(candidate_feedbacks),
            "overall_average": round(overall_average, 2),
            "competency_scores": competency_averages,
            "confidence_scores": confidence_scores,
            "recommendation_counts": recommendation_counts,
            "feedbacks": candidate_feedbacks
        }

    async def get_feedback_summary_for_candidate(
        self,
        candidate_id: str
    ) -> Dict[str, Any]:
        """
        Get aggregated feedback summary for a candidate.
        """
        feedbacks = await self.get_evaluations_for_candidates([candidate_id])
        candidate_feedbacks = feedbacks.get(candidate_id, [])

        if not candidate_feedbacks:
            return {
                "strengths": [],
                "weaknesses": [],
                "summaries": [],
                "overall_themes": []
            }

        # Collect all written feedback
        strengths: List[str] = []
        weaknesses: List[str] = []
        summaries: List[str] = []

        for fb in candidate_feedbacks:
            if fb.strengths:
                strengths.append(fb.strengths)
            if fb.weaknesses:
                weaknesses.append(fb.weaknesses)
            if fb.summary:
                summaries.append(fb.summary)

        # Calculate theme overlap (simple version)
        overall_themes = []
        if strengths:
            overall_themes.append(f"Mentioned strengths in {len(strengths)} evaluations")
        if weaknesses:
            overall_themes.append(f"Identified areas for improvement in {len(weaknesses)} evaluations")

        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "summaries": summaries,
            "overall_themes": overall_themes,
            "total_feedback_count": len(candidate_feedbacks)
        }

    async def count_candidates_for_comparison(
        self,
        role_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        has_evaluations: bool = True
    ) -> int:
        """
        Count candidates available for comparison.
        """
        from sqlalchemy import func

        conditions = [Candidate.is_active == True]

        if role_id:
            conditions.append(Candidate.role_id == role_id)
        if organization_id:
            conditions.append(Candidate.organization_id == organization_id)

        if has_evaluations:
            # Subquery to find candidates with evaluations
            subquery = (
                select(Feedback.candidate_id)
                .where(
                    and_(
                        Feedback.is_active == True,
                        Feedback.is_submitted == True
                    )
                )
                .distinct()
                .subquery()
            )
            conditions.append(Candidate.id.in_(subquery))

        query = select(func.count(Candidate.id)).where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def get_candidates_for_workflow_stage(
        self,
        workflow_id: str,
        stage_id: str,
        has_evaluations: bool = True
    ) -> List[Candidate]:
        """
        Get candidates at a specific workflow stage.
        """
        conditions = [
            Candidate.workflow_id == workflow_id,
            Candidate.current_stage_id == stage_id,
            Candidate.is_active == True
        ]

        if has_evaluations:
            from sqlalchemy import exists
            from sqlalchemy import select

            eval_subquery = (
                select(Feedback.id)
                .where(
                    and_(
                        Feedback.candidate_id == Candidate.id,
                        Feedback.is_active == True,
                        Feedback.is_submitted == True
                    )
                )
                .exists()
            )
            conditions.append(eval_subquery)

        query = (
            select(Candidate)
            .where(and_(*conditions))
            .options(
                selectinload(Candidate.role),
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

