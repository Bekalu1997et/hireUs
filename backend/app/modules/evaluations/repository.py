"""
Evaluation repository.
Database operations for scorecards/feedbacks.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Feedback, User, Candidate
from app.schemas.evaluation import (
    ScorecardCreate,
    ScorecardUpdate,
)


class EvaluationRepository:
    """
    Repository for feedback/scorecard database operations.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, feedback_id: str) -> Optional[Feedback]:
        """
        Get a feedback/scorecard by ID.
        """
        query = (
            select(Feedback)
            .where(Feedback.id == feedback_id)
            .options(
                selectinload(Feedback.candidate),
                selectinload(Feedback.interviewer),
                selectinload(Feedback.assignment),
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_candidate_id(
        self, 
        candidate_id: str,
        skip: int = 0,
        limit: int = 100,
        submitted_only: bool = False
    ) -> List[Feedback]:
        """
        Get all feedbacks for a candidate.
        """
        conditions = [Feedback.candidate_id == candidate_id]
        if submitted_only:
            conditions.append(Feedback.is_submitted == True)
        
        query = (
            select(Feedback)
            .where(and_(*conditions))
            .order_by(Feedback.created_at.desc())
            .offset(skip)
            .limit(limit)
            .options(
                selectinload(Feedback.interviewer),
                selectinload(Feedback.assignment),
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_interviewer_id(
        self,
        interviewer_id: str,
        skip: int = 0,
        limit: int = 100,
        is_draft: Optional[bool] = None
    ) -> List[Feedback]:
        """
        Get all feedbacks by an interviewer.
        """
        conditions = [Feedback.interviewer_id == interviewer_id]
        if is_draft is not None:
            conditions.append(Feedback.is_draft == is_draft)
        
        query = (
            select(Feedback)
            .where(and_(*conditions))
            .order_by(Feedback.created_at.desc())
            .offset(skip)
            .limit(limit)
            .options(selectinload(Feedback.candidate))
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_assignment_id(self, assignment_id: str) -> Optional[Feedback]:
        """
        Get feedback for a specific interview assignment.
        """
        query = (
            select(Feedback)
            .where(Feedback.assignment_id == assignment_id)
            .options(
                selectinload(Feedback.candidate),
                selectinload(Feedback.interviewer),
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def exists_for_assignment(self, assignment_id: str) -> bool:
        """
        Check if a feedback already exists for an assignment.
        """
        query = (
            select(Feedback.id)
            .where(
                and_(
                    Feedback.assignment_id == assignment_id,
                    Feedback.is_submitted == True
                )
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def list_all(
        self,
        organization_id: Optional[str] = None,
        role_id: Optional[str] = None,
        candidate_id: Optional[str] = None,
        interviewer_id: Optional[str] = None,
        is_submitted: Optional[bool] = None,
        is_draft: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Feedback]:
        """
        List feedbacks with various filters.
        """
        conditions = []
        
        if organization_id:
            # Filter through candidate relationship
            conditions.append(Candidate.organization_id == organization_id)
        
        if role_id:
            conditions.append(Candidate.role_id == role_id)
        
        if candidate_id:
            conditions.append(Feedback.candidate_id == candidate_id)
        
        if interviewer_id:
            conditions.append(Feedback.interviewer_id == interviewer_id)
        
        if is_submitted is not None:
            conditions.append(Feedback.is_submitted == is_submitted)
        
        if is_draft is not None:
            conditions.append(Feedback.is_draft == is_draft)
        
        # Build query with joins
        query = (
            select(Feedback)
            .join(Candidate, Feedback.candidate_id == Candidate.id)
            .where(and_(*conditions) if conditions else True)
            .order_by(Feedback.created_at.desc())
            .offset(skip)
            .limit(limit)
            .options(
                selectinload(Feedback.candidate),
                selectinload(Feedback.interviewer),
                selectinload(Feedback.assignment),
            )
        )
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count(
        self,
        organization_id: Optional[str] = None,
        is_submitted: Optional[bool] = None,
        is_draft: Optional[bool] = None
    ) -> int:
        """
        Count feedbacks with filters.
        """
        from sqlalchemy import func, select
        from app.db.models import Candidate
        
        conditions = []
        
        if organization_id:
            conditions.append(Candidate.organization_id == organization_id)
        
        if is_submitted is not None:
            conditions.append(Feedback.is_submitted == is_submitted)
        
        if is_draft is not None:
            conditions.append(Feedback.is_draft == is_draft)
        
        query = (
            select(func.count(Feedback.id))
            .join(Candidate, Feedback.candidate_id == Candidate.id)
            .where(and_(*conditions) if conditions else True)
        )
        
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def create(
        self,
        scorecard_data: ScorecardCreate,
        interviewer_id: str
    ) -> Feedback:
        """
        Create a new feedback/scorecard.
        """
        # Convert scores to dict format
        scores_dict = {}
        evidence_dict = {}
        
        for key, score in scorecard_data.scores.items():
            scores_dict[key] = {
                "competency": score.competency,
                "score": score.score,
                "notes": score.notes
            }
            if score.evidence:
                evidence_dict[key] = score.evidence
        
        feedback = Feedback(
            candidate_id=scorecard_data.candidate_id,
            interviewer_id=interviewer_id,
            assignment_id=scorecard_data.assignment_id,
            scores=scores_dict,
            evidence=evidence_dict,
            confidence=scorecard_data.confidence,
            strengths=scorecard_data.strengths,
            weaknesses=scorecard_data.weaknesses,
            summary=scorecard_data.summary,
            recommendation=scorecard_data.recommendation,
            is_draft=scorecard_data.is_draft,
            is_submitted=not scorecard_data.is_draft,
        )
        
        self.db.add(feedback)
        await self.db.commit()
        await self.db.refresh(feedback)
        
        return feedback
    
    async def update(
        self,
        feedback_id: str,
        scorecard_data: ScorecardUpdate
    ) -> Optional[Feedback]:
        """
        Update an existing feedback/scorecard.
        """
        feedback = await self.get_by_id(feedback_id)
        if not feedback:
            return None
        
        update_data = scorecard_data.model_dump(exclude_unset=True)
        
        # Handle scores specially
        if "scores" in update_data and update_data["scores"]:
            scores_dict = {}
            evidence_dict = feedback.evidence or {}
            
            for key, score in update_data["scores"].items():
                scores_dict[key] = {
                    "competency": key,
                    "score": score.score,
                    "notes": score.notes
                }
                if score.evidence:
                    evidence_dict[key] = score.evidence
            
            update_data["scores"] = scores_dict
            update_data["evidence"] = evidence_dict
        
        for field, value in update_data.items():
            setattr(feedback, field, value)
        
        await self.db.commit()
        await self.db.refresh(feedback)
        
        return feedback
    
    async def submit(self, feedback_id: str) -> Optional[Feedback]:
        """
        Submit a feedback/scorecard.
        """
        from datetime import datetime, timezone
        
        feedback = await self.get_by_id(feedback_id)
        if not feedback:
            return None
        
        feedback.is_draft = False
        feedback.is_submitted = True
        feedback.submitted_at = datetime.now(timezone.utc)
        
        await self.db.commit()
        await self.db.refresh(feedback)
        
        return feedback
    
    async def delete(self, feedback_id: str, hard_delete: bool = False) -> bool:
        """
        Delete a feedback/scorecard.
        """
        feedback = await self.get_by_id(feedback_id)
        if not feedback:
            return False
        
        if hard_delete:
            await self.db.delete(feedback)
        else:
            feedback.is_active = False
            await self.db.delete(feedback)
        
        await self.db.commit()
        return True
    
    async def update_ai_suggestions(
        self,
        feedback_id: str,
        ai_suggestions: str
    ) -> Optional[Feedback]:
        """
        Update AI suggestions for a feedback.
        """
        feedback = await self.get_by_id(feedback_id)
        if not feedback:
            return None
        
        feedback.ai_suggestions = ai_suggestions
        
        await self.db.commit()
        await self.db.refresh(feedback)
        
        return feedback
    
    async def get_evaluation_stats(
        self,
        candidate_id: str
    ) -> Dict[str, Any]:
        """
        Get evaluation statistics for a candidate.
        """
        from sqlalchemy import func
        from sqlalchemy import select
        
        feedbacks = await self.get_by_candidate_id(candidate_id, submitted_only=True)
        
        if not feedbacks:
            return {
                "total_evaluations": 0,
                "average_score": 0,
                "recommendation_breakdown": {},
                "competency_scores": {}
            }
        
        # Calculate average score
        all_scores = []
        for fb in feedbacks:
            for comp, score_data in fb.scores.items():
                if isinstance(score_data, dict) and "score" in score_data:
                    all_scores.append(score_data["score"])
        
        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
        
        # Recommendation breakdown
        rec_breakdown = {}
        for fb in feedbacks:
            rec = fb.recommendation
            rec_breakdown[rec] = rec_breakdown.get(rec, 0) + 1
        
        # Competency scores
        competency_scores = {}
        for fb in feedbacks:
            for comp, score_data in fb.scores.items():
                if isinstance(score_data, dict) and "score" in score_data:
                    if comp not in competency_scores:
                        competency_scores[comp] = []
                    competency_scores[comp].append(score_data["score"])
        
        # Average per competency
        avg_competency_scores = {}
        for comp, scores in competency_scores.items():
            avg_competency_scores[comp] = sum(scores) / len(scores)
        
        return {
            "total_evaluations": len(feedbacks),
            "average_score": round(avg_score, 2),
            "recommendation_breakdown": rec_breakdown,
            "competency_scores": avg_competency_scores,
        }
