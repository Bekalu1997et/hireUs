"""
Evaluation service.
Business logic for scorecards/feedbacks.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Feedback, Candidate, User, InterviewAssignment
from app.schemas.evaluation import (
    ScorecardCreate,
    ScorecardUpdate,
    ScorecardValidationResult,
)
from app.modules.evaluations.repository import EvaluationRepository


class EvaluationService:
    """
    Service for managing scorecards/feedbacks.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = EvaluationRepository(db)
    
    async def create_scorecard(
        self,
        scorecard_data: ScorecardCreate,
        user_id: str
    ) -> Feedback:
        """
        Create a new scorecard/feedback.
        """
        # Validate candidate exists
        from app.db.models import Candidate
        query = select(Candidate).where(Candidate.id == scorecard_data.candidate_id)
        from sqlalchemy import select
        result = await self.db.execute(query)
        candidate = result.scalar_one_or_none()
        
        if not candidate:
            raise ValueError(f"Candidate with ID {scorecard_data.candidate_id} not found")
        
        return await self.repository.create(scorecard_data, user_id)
    
    async def get_scorecard(self, scorecard_id: str) -> Optional[Feedback]:
        """
        Get a scorecard by ID.
        """
        return await self.repository.get_by_id(scorecard_id)
    
    async def get_candidate_scorecards(
        self,
        candidate_id: str,
        skip: int = 0,
        limit: int = 100,
        submitted_only: bool = False
    ) -> List[Feedback]:
        """
        Get all scorecards for a candidate.
        """
        return await self.repository.get_by_candidate_id(
            candidate_id, skip, limit, submitted_only
        )
    
    async def get_interviewer_scorecards(
        self,
        interviewer_id: str,
        skip: int = 0,
        limit: int = 100,
        is_draft: Optional[bool] = None
    ) -> List[Feedback]:
        """
        Get all scorecards by an interviewer.
        """
        return await self.repository.get_by_interviewer_id(
            interviewer_id, skip, limit, is_draft
        )
    
    async def get_assignment_scorecard(self, assignment_id: str) -> Optional[Feedback]:
        """
        Get the scorecard for a specific assignment.
        """
        return await self.repository.get_by_assignment_id(assignment_id)
    
    async def list_scorecards(
        self,
        organization_id: Optional[str] = None,
        role_id: Optional[str] = None,
        candidate_id: Optional[str] = None,
        interviewer_id: Optional[str] = None,
        is_submitted: Optional[bool] = None,
        is_draft: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        List scorecards with filters.
        Returns dict with items and pagination info.
        """
        scorecards = await self.repository.list_all(
            organization_id=organization_id,
            role_id=role_id,
            candidate_id=candidate_id,
            interviewer_id=interviewer_id,
            is_submitted=is_submitted,
            is_draft=is_draft,
            skip=skip,
            limit=limit
        )
        
        total = await self.repository.count(
            organization_id=organization_id,
            is_submitted=is_submitted,
            is_draft=is_draft
        )
        
        return {
            "items": scorecards,
            "total": total,
            "page": skip // limit + 1 if limit > 0 else 1,
            "page_size": limit,
            "total_pages": (total + limit - 1) // limit if limit > 0 else 1
        }
    
    async def update_scorecard(
        self,
        scorecard_id: str,
        scorecard_data: ScorecardUpdate
    ) -> Optional[Feedback]:
        """
        Update a scorecard.
        """
        return await self.repository.update(scorecard_id, scorecard_data)
    
    async def submit_scorecard(
        self,
        scorecard_id: str,
        validate_first: bool = True
    ) -> Dict[str, Any]:
        """
        Submit a scorecard.
        
        If validate_first is True, validates the scorecard before submission.
        Returns validation result along with the submitted scorecard.
        """
        if validate_first:
            validation = await self.validate_for_submission(scorecard_id)
            
            if not validation.is_valid:
                return {
                    "success": False,
                    "message": "Scorecard cannot be submitted",
                    "validation": validation
                }
        
        scorecard = await self.repository.submit(scorecard_id)
        
        if not scorecard:
            return {
                "success": False,
                "message": "Scorecard not found"
            }
        
        return {
            "success": True,
            "message": "Scorecard submitted successfully",
            "scorecard": scorecard
        }
    
    async def validate_for_submission(
        self,
        scorecard_id: str
    ) -> ScorecardValidationResult:
        """
        Validate a scorecard for submission.
        
        Checks:
        - All required competencies have scores
        - Evidence is provided for each competency
        - Confidence level is set
        - Required text fields are not empty
        """
        scorecard = await self.repository.get_by_id(scorecard_id)
        
        if not scorecard:
            return ScorecardValidationResult(
                is_valid=False,
                messages=["Scorecard not found"]
            )
        
        missing_competencies = []
        missing_evidence = []
        messages = []
        
        # Check if scores exist
        if not scorecard.scores or len(scorecard.scores) == 0:
            missing_competencies.append("No competencies scored")
            messages.append("At least one competency must be scored")
        
        # Check each competency for score and evidence
        for competency, score_data in scorecard.scores.items():
            if isinstance(score_data, dict):
                if not score_data.get("score"):
                    missing_competencies.append(competency)
                
                # Check evidence
                evidence = scorecard.get("evidence") or scorecard.evidence.get(competency) if scorecard.evidence else None
                if not evidence:
                    missing_evidence.append(competency)
            else:
                # Legacy format: score is direct value
                if not score_data:
                    missing_competencies.append(competency)
        
        # Check confidence
        if not scorecard.confidence:
            messages.append("Confidence level is required")
        
        # Check recommendation
        if not scorecard.recommendation:
            messages.append("Recommendation is required")
        
        # Check summary
        if not scorecard.summary:
            messages.append("Summary is recommended before submission")
        
        is_valid = len(missing_competencies) == 0 and len(missing_evidence) == 0
        low_confidence_warning = scorecard.confidence and scorecard.confidence < 3
        
        if low_confidence_warning:
            messages.append("Warning: Confidence level is below 3")
        
        return ScorecardValidationResult(
            is_valid=is_valid,
            missing_competencies=missing_competencies,
            missing_evidence=missing_evidence,
            low_confidence_warning=low_confidence_warning,
            messages=messages
        )
    
    async def delete_scorecard(
        self,
        scorecard_id: str,
        hard_delete: bool = False
    ) -> bool:
        """
        Delete a scorecard.
        """
        return await self.repository.delete(scorecard_id, hard_delete)
    
    async def duplicate_scorecard(
        self,
        scorecard_id: str,
        new_interviewer_id: str
    ) -> Optional[Feedback]:
        """
        Duplicate a scorecard for another interviewer.
        """
        original = await self.repository.get_by_id(scorecard_id)
        
        if not original:
            return None
        
        # Create a new scorecard based on the original
        duplicate_data = ScorecardCreate(
            candidate_id=original.candidate_id,
            assignment_id=None,  # New assignment needed
            scores={},
            confidence=3,  # Reset confidence
            is_draft=True  # Always start as draft
        )
        
        return await self.repository.create(duplicate_data, new_interviewer_id)
    
    async def get_evaluation_stats(
        self,
        candidate_id: str
    ) -> Dict[str, Any]:
        """
        Get evaluation statistics for a candidate.
        """
        return await self.repository.get_evaluation_stats(candidate_id)
    
    async def check_assignment_feedback_required(
        self,
        assignment_id: str
    ) -> Dict[str, Any]:
        """
        Check if feedback is required for an assignment and if it's been submitted.
        """
        assignment = await self._get_assignment(assignment_id)
        
        if not assignment:
            return {
                "exists": False,
                "feedback_required": False,
                "feedback_submitted": False,
                "message": "Assignment not found"
            }
        
        existing_feedback = await self.repository.get_by_assignment_id(assignment_id)
        
        return {
            "exists": True,
            "feedback_required": assignment.feedback_required,
            "feedback_submitted": existing_feedback is not None and existing_feedback.is_submitted,
            "feedback_id": existing_feedback.id if existing_feedback else None,
            "message": (
                "Feedback already submitted" 
                if existing_feedback and existing_feedback.is_submitted 
                else "Feedback pending" if assignment.feedback_required 
                else "Feedback not required"
            )
        }
    
    async def _get_assignment(self, assignment_id: str) -> Optional[InterviewAssignment]:
        """
        Get an assignment by ID.
        """
        from sqlalchemy import select
        from app.db.models import InterviewAssignment
        
        query = select(InterviewAssignment).where(
            InterviewAssignment.id == assignment_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def calculate_average_scores(
        self,
        candidate_id: str
    ) -> Dict[str, float]:
        """
        Calculate average scores across all evaluations for a candidate.
        """
        feedbacks = await self.repository.get_by_candidate_id(
            candidate_id, submitted_only=True
        )
        
        if not feedbacks:
            return {}
        
        competency_totals: Dict[str, tuple] = {}
        
        for fb in feedbacks:
            for comp, score_data in fb.scores.items():
                if isinstance(score_data, dict) and "score" in score_data:
                    score = score_data["score"]
                    if comp not in competency_totals:
                        competency_totals[comp] = (0, 0)  # (total, count)
                    total, count = competency_totals[comp]
                    competency_totals[comp] = (total + score, count + 1)
        
        return {
            comp: total / count if count > 0 else 0
            for comp, (total, count) in competency_totals.items()
        }

