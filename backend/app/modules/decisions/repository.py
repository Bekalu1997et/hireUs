"""
Decision Brief repository.
Database operations for decision briefs.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Candidate, Feedback, Role


class DecisionBriefRepository:
    """
    Repository for decision brief database operations.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_candidate_with_details(
        self,
        candidate_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get candidate with full details including role.
        """
        query = (
            select(Candidate)
            .where(Candidate.id == candidate_id)
            .options(
                selectinload(Candidate.role),
            )
        )
        result = await self.db.execute(query)
        candidate = result.scalar_one_or_none()
        
        if not candidate:
            return None
        
        return {
            "id": candidate.id,
            "full_name": candidate.full_name,
            "email": candidate.email,
            "status": candidate.status,
            "current_stage_id": candidate.current_stage_id,
            "workflow_id": candidate.workflow_id,
            "ai_summary": candidate.ai_summary,
            "role": {
                "id": candidate.role.id if candidate.role else None,
                "title": candidate.role.title if candidate.role else None,
                "mission": candidate.role.mission if candidate.role else None,
                "core_competencies": candidate.role.core_competencies if candidate.role else [],
                "must_have": candidate.role.must_have if candidate.role else [],
                "nice_to_have": candidate.role.nice_to_have if candidate.role else [],
            } if candidate.role else None
        }
    
    async def get_candidate_evaluations(
        self,
        candidate_id: str,
        submitted_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get all evaluations for a candidate.
        """
        conditions = [
            Feedback.candidate_id == candidate_id,
            Feedback.is_active == True
        ]
        
        if submitted_only:
            conditions.append(Feedback.is_submitted == True)
        
        query = (
            select(Feedback)
            .where(and_(*conditions))
            .order_by(Feedback.created_at.desc())
            .options(
                selectinload(Feedback.interviewer),
            )
        )
        result = await self.db.execute(query)
        feedbacks = list(result.scalars().all())
        
        # Convert to dict format
        evaluations = []
        for fb in feedbacks:
            evaluations.append({
                "id": fb.id,
                "candidate_id": fb.candidate_id,
                "interviewer": {
                    "id": fb.interviewer.id if fb.interviewer else None,
                    "full_name": fb.interviewer.full_name if fb.interviewer else "Unknown",
                    "email": fb.interviewer.email if fb.interviewer else None,
                },
                "scores": fb.scores or {},
                "confidence": fb.confidence,
                "strengths": fb.strengths,
                "weaknesses": fb.weaknesses,
                "summary": fb.summary,
                "recommendation": fb.recommendation,
                "evidence": fb.evidence or {},
                "created_at": fb.created_at.isoformat() if fb.created_at else None,
                "submitted_at": fb.submitted_at.isoformat() if fb.submitted_at else None,
            })
        
        return evaluations
    
    async def get_role_competencies(
        self,
        role_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get role details including competencies.
        """
        query = select(Role).where(Role.id == role_id)
        result = await self.db.execute(query)
        role = result.scalar_one_or_none()
        
        if not role:
            return None
        
        return {
            "id": role.id,
            "title": role.title,
            "mission": role.mission,
            "seniority": role.seniority,
            "tech_stack": role.tech_stack or [],
            "core_competencies": role.core_competencies or [],
            "must_have": role.must_have or [],
            "nice_to_have": role.nice_to_have or [],
            "interview_stages": role.interview_stages or [],
        }
    
    async def get_candidates_for_organization(
        self,
        organization_id: str,
        has_evaluations: bool = True,
        min_evaluations: int = 1,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get candidates for an organization with optional evaluation filter.
        """
        from sqlalchemy import func, select
        from app.db.models import Candidate
        
        conditions = [
            Candidate.organization_id == organization_id,
            Candidate.is_active == True
        ]
        
        if has_evaluations:
            # Subquery to count submitted evaluations
            eval_subquery = (
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
            conditions.append(Candidate.id.in_(select(eval_subquery.c.candidate_id)))
        
        query = (
            select(Candidate)
            .where(and_(*conditions))
            .options(
                selectinload(Candidate.role),
            )
            .offset(skip)
            .limit(limit)
            .order_by(Candidate.created_at.desc())
        )
        
        result = await self.db.execute(query)
        candidates = list(result.scalars().all())
        
        return [
            {
                "id": c.id,
                "full_name": c.full_name,
                "email": c.email,
                "status": c.status,
                "role_id": c.role_id,
                "role_title": c.role.title if c.role else None,
            }
            for c in candidates
        ]
    
    async def count_candidates_with_evaluations(
        self,
        organization_id: str,
        min_evaluations: int = 1
    ) -> int:
        """
        Count candidates with sufficient evaluations.
        """
        from sqlalchemy import func, select
        from app.db.models import Candidate
        
        # Subquery to count submitted evaluations
        eval_subquery = (
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
            select(func.count(Candidate.id))
            .select_from(Candidate)
            .join(eval_subquery, Candidate.id == eval_subquery.c.candidate_id)
            .where(
                and_(
                    Candidate.organization_id == organization_id,
                    Candidate.is_active == True
                )
            )
        )
        
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def get_evaluation_statistics(
        self,
        candidate_id: str
    ) -> Dict[str, Any]:
        """
        Get statistics from evaluations for a candidate.
        """
        evaluations = await self.get_candidate_evaluations(candidate_id)
        
        if not evaluations:
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
        
        for eval_data in evaluations:
            # Collect competency scores
            scores = eval_data.get("scores", {})
            for comp, score_data in scores.items():
                if isinstance(score_data, dict):
                    score = score_data.get("score")
                    if isinstance(score, (int, float)):
                        if comp not in all_scores:
                            all_scores[comp] = []
                        all_scores[comp].append(float(score))
                elif isinstance(score_data, (int, float)):
                    if comp not in all_scores:
                        all_scores[comp] = []
                    all_scores[comp].append(float(score_data))
            
            # Collect confidence
            confidence = eval_data.get("confidence")
            if confidence:
                confidence_scores.append(int(confidence))
            
            # Collect recommendations
            recommendation = eval_data.get("recommendation")
            if recommendation:
                recommendation_counts[recommendation] = (
                    recommendation_counts.get(recommendation, 0) + 1
                )
        
        # Calculate averages
        competency_averages = {}
        for comp, scores in all_scores.items():
            competency_averages[comp] = round(sum(scores) / len(scores), 2)
        
        # Calculate overall average
        all_score_values = []
        for scores in all_scores.values():
            all_score_values.extend(scores)
        overall_average = (
            round(sum(all_score_values) / len(all_score_values), 2)
            if all_score_values else 0
        )
        
        # Calculate average confidence
        avg_confidence = (
            round(sum(confidence_scores) / len(confidence_scores), 2)
            if confidence_scores else 0
        )
        
        return {
            "total_evaluations": len(evaluations),
            "overall_average": overall_average,
            "competency_scores": competency_averages,
            "confidence_scores": confidence_scores,
            "average_confidence": avg_confidence,
            "recommendation_counts": recommendation_counts,
            "evaluations": evaluations
        }

