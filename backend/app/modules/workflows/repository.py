"""
Workflow repository.
Handles database operations for workflows, candidates, and assignments.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.db.models import (
    Workflow, 
    Candidate, 
    InterviewAssignment, 
    Feedback, 
    StageHistory,
    User,
    InterviewKit
)


class WorkflowRepository:
    """Repository for workflow operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ============== Workflow CRUD ==============
    
    async def create(
        self, 
        workflow_data: Dict[str, Any], 
        user_id: Optional[str] = None
    ) -> Workflow:
        """Create a new workflow."""
        workflow = Workflow(
            **workflow_data,
            created_by=user_id
        )
        self.db.add(workflow)
        await self.db.commit()
        await self.db.refresh(workflow)
        return workflow
    
    async def get_by_id(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID."""
        result = await self.db.execute(
            select(Workflow).where(
                and_(
                    Workflow.id == workflow_id,
                    Workflow.is_active == True
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_organization(
        self, 
        organization_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Workflow], int]:
        """Get all workflows for an organization."""
        # Get total count
        count_result = await self.db.execute(
            select(func.count(Workflow.id)).where(
                and_(
                    Workflow.organization_id == organization_id,
                    Workflow.is_active == True
                )
            )
        )
        total = count_result.scalar() or 0
        
        # Get workflows
        result = await self.db.execute(
            select(Workflow)
            .where(
                and_(
                    Workflow.organization_id == organization_id,
                    Workflow.is_active == True
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(Workflow.created_at.desc())
        )
        workflows = result.scalars().all()
        
        return list(workflows), total
    
    async def get_default_workflow(self, organization_id: str) -> Optional[Workflow]:
        """Get the default workflow for an organization."""
        result = await self.db.execute(
            select(Workflow).where(
                and_(
                    Workflow.organization_id == organization_id,
                    Workflow.is_default == True,
                    Workflow.is_active == True
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def update(
        self, 
        workflow_id: str, 
        update_data: Dict[str, Any]
    ) -> Optional[Workflow]:
        """Update a workflow."""
        await self.db.execute(
            update(Workflow)
            .where(Workflow.id == workflow_id)
            .values(**update_data)
        )
        await self.db.commit()
        return await self.get_by_id(workflow_id)
    
    async def delete(self, workflow_id: str, hard_delete: bool = False) -> bool:
        """Delete a workflow."""
        if hard_delete:
            await self.db.execute(
                delete(Workflow).where(Workflow.id == workflow_id)
            )
        else:
            await self.db.execute(
                update(Workflow)
                .where(Workflow.id == workflow_id)
                .values(is_active=False)
            )
        await self.db.commit()
        return True
    
    async def set_default(
        self, 
        workflow_id: str, 
        organization_id: str
    ) -> Workflow:
        """Set a workflow as the default for an organization."""
        # Remove default from existing default workflow
        await self.db.execute(
            update(Workflow)
            .where(
                and_(
                    Workflow.organization_id == organization_id,
                    Workflow.is_default == True
                )
            )
            .values(is_default=False)
        )
        
        # Set new default
        await self.db.execute(
            update(Workflow)
            .where(Workflow.id == workflow_id)
            .values(is_default=True)
        )
        
        await self.db.commit()
        return await self.get_by_id(workflow_id)
    
    # ============== Candidate Operations ==============
    
    async def get_candidate_by_id(self, candidate_id: str) -> Optional[Candidate]:
        """Get candidate by ID with all relations."""
        result = await self.db.execute(
            select(Candidate)
            .options(
                joinedload(Candidate.role),
                joinedload(Candidate.workflow),
                joinedload(Candidate.feedbacks),
            )
            .where(Candidate.id == candidate_id)
        )
        return result.unique().scalar_one_or_none()
    
    async def get_candidates_by_workflow(
        self, 
        workflow_id: str,
        stage_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Candidate], int]:
        """Get candidates in a workflow, optionally filtered by stage."""
        # Build base condition
        conditions = [
            Candidate.workflow_id == workflow_id,
            Candidate.is_active == True
        ]
        if stage_id:
            conditions.append(Candidate.current_stage_id == stage_id)
        
        # Get total count
        count_result = await self.db.execute(
            select(func.count(Candidate.id)).where(and_(*conditions))
        )
        total = count_result.scalar() or 0
        
        # Get candidates
        result = await self.db.execute(
            select(Candidate)
            .options(
                joinedload(Candidate.role),
                joinedload(Candidate.feedbacks),
            )
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
            .order_by(Candidate.created_at.desc())
        )
        candidates = result.unique().scalars().all()
        
        return list(candidates), total
    
    async def get_candidates_by_stage(
        self, 
        workflow_id: str,
        stage_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Candidate], int]:
        """Get all candidates in a specific stage."""
        return await self.get_candidates_by_workflow(
            workflow_id=workflow_id,
            stage_id=stage_id,
            skip=skip,
            limit=limit
        )
    
    async def update_candidate_stage(
        self,
        candidate_id: str,
        new_stage_id: str,
        new_stage_name: str,
        changed_by: Optional[str] = None,
        reason: Optional[str] = None
    ) -> Optional[Candidate]:
        """Update candidate's current stage and record history."""
        # Get current candidate
        candidate = await self.get_candidate_by_id(candidate_id)
        if not candidate:
            return None
        
        old_stage_id = candidate.current_stage_id
        old_stage_name = None
        
        # Get old stage name from workflow
        if candidate.workflow and candidate.workflow.stages:
            for stage in candidate.workflow.stages:
                if stage.get("id") == old_stage_id:
                    old_stage_name = stage.get("name")
                    break
        
        # Update candidate
        await self.db.execute(
            update(Candidate)
            .where(Candidate.id == candidate_id)
            .values(
                current_stage_id=new_stage_id,
                current_stage_name=new_stage_name
            )
        )
        
        # Create stage history record
        stage_history = StageHistory(
            candidate_id=candidate_id,
            from_stage=old_stage_name,
            to_stage=new_stage_name,
            changed_by=changed_by,
            reason=reason
        )
        self.db.add(stage_history)
        await self.db.commit()
        await self.db.refresh(candidate)
        
        return candidate
    
    async def assign_candidate_to_workflow(
        self,
        candidate_id: str,
        workflow_id: str,
        initial_stage_id: str,
        initial_stage_name: str,
        changed_by: Optional[str] = None
    ) -> Optional[Candidate]:
        """Assign a candidate to a workflow at the initial stage."""
        await self.db.execute(
            update(Candidate)
            .where(Candidate.id == candidate_id)
            .values(
                workflow_id=workflow_id,
                current_stage_id=initial_stage_id,
                current_stage_name=initial_stage_name
            )
        )
        
        # Create stage history
        stage_history = StageHistory(
            candidate_id=candidate_id,
            from_stage=None,
            to_stage=initial_stage_name,
            changed_by=changed_by,
            reason="Assigned to workflow"
        )
        self.db.add(stage_history)
        await self.db.commit()
        
        return await self.get_candidate_by_id(candidate_id)
    
    async def get_candidate_feedback_status(
        self, 
        candidate_id: str
    ) -> Dict[str, Any]:
        """Get feedback status for a candidate."""
        candidate = await self.get_candidate_by_id(candidate_id)
        if not candidate:
            return {"error": "Candidate not found"}
        
        # Get assignments
        result = await self.db.execute(
            select(InterviewAssignment)
            .options(joinedload(InterviewAssignment.feedback))
            .where(InterviewAssignment.candidate_id == candidate_id)
        )
        assignments = result.unique().scalars().all()
        
        # Count required vs submitted
        required = sum(1 for a in assignments if a.feedback_required)
        submitted = sum(
            1 for a in assignments 
            if a.feedback_required and a.feedback and a.feedback.is_submitted
        )
        
        # Get stage info
        stage_id = candidate.current_stage_id
        stage_name = candidate.current_stage_name
        
        # Get stage from workflow if available
        workflow = candidate.workflow
        required_feedbacks = 0
        if workflow and workflow.stages and stage_id:
            for stage in workflow.stages:
                if stage.get("id") == stage_id:
                    required_feedbacks = stage.get("required_feedback_count", 0)
                    break
        
        return {
            "candidate_id": candidate_id,
            "candidate_name": candidate.full_name,
            "current_stage_id": stage_id,
            "current_stage_name": stage_name,
            "total_required_feedbacks": required_feedbacks,
            "total_submitted_feedbacks": submitted,
            "is_blocked": submitted < required_feedbacks,
            "blocked_reason": None if submitted >= required_feedbacks 
                else f"Missing {required_feedbacks - submitted} feedback(s)",
            "assignments": [
                {
                    "id": a.id,
                    "candidate_id": a.candidate_id,
                    "interviewer_id": a.interviewer_id,
                    "interview_kit_id": a.interview_kit_id,
                    "scheduled_at": a.scheduled_at,
                    "duration_minutes": a.duration_minutes,
                    "status": a.status,
                    "notes": a.notes,
                    "feedback_required": a.feedback_required,
                    "feedback_submitted": a.feedback is not None and a.feedback.is_submitted
                }
                for a in assignments
            ]
        }
    
    # ============== Interview Assignment Operations ==============
    
    async def create_assignment(
        self,
        assignment_data: Dict[str, Any]
    ) -> InterviewAssignment:
        """Create a new interview assignment."""
        assignment = InterviewAssignment(**assignment_data)
        self.db.add(assignment)
        await self.db.commit()
        await self.db.refresh(assignment)
        return assignment
    
    async def get_assignment_by_id(
        self, 
        assignment_id: str
    ) -> Optional[InterviewAssignment]:
        """Get assignment by ID with relations."""
        result = await self.db.execute(
            select(InterviewAssignment)
            .options(
                joinedload(InterviewAssignment.candidate),
                joinedload(InterviewAssignment.interviewer),
                joinedload(InterviewAssignment.interview_kit),
                joinedload(InterviewAssignment.feedback),
            )
            .where(InterviewAssignment.id == assignment_id)
        )
        return result.unique().scalar_one_or_none()
    
    async def get_assignments_by_candidate(
        self, 
        candidate_id: str
    ) -> List[InterviewAssignment]:
        """Get all assignments for a candidate."""
        result = await self.db.execute(
            select(InterviewAssignment)
            .options(
                joinedload(InterviewAssignment.interviewer),
                joinedload(InterviewAssignment.interview_kit),
                joinedload(InterviewAssignment.feedback),
            )
            .where(
                and_(
                    InterviewAssignment.candidate_id == candidate_id,
                    InterviewAssignment.status != "cancelled"
                )
            )
            .order_by(InterviewAssignment.scheduled_at.desc())
        )
        return list(result.unique().scalars().all())
    
    async def get_assignments_by_interviewer(
        self, 
        interviewer_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[InterviewAssignment], int]:
        """Get all assignments for an interviewer."""
        # Get total count
        count_result = await self.db.execute(
            select(func.count(InterviewAssignment.id)).where(
                and_(
                    InterviewAssignment.interviewer_id == interviewer_id,
                    InterviewAssignment.status != "cancelled"
                )
            )
        )
        total = count_result.scalar() or 0
        
        # Get assignments
        result = await self.db.execute(
            select(InterviewAssignment)
            .options(
                joinedload(InterviewAssignment.candidate),
                joinedload(InterviewAssignment.interview_kit),
                joinedload(InterviewAssignment.feedback),
            )
            .where(
                and_(
                    InterviewAssignment.interviewer_id == interviewer_id,
                    InterviewAssignment.status != "cancelled"
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(InterviewAssignment.scheduled_at.asc())
        )
        assignments = result.unique().scalars().all()
        
        return list(assignments), total
    
    async def get_pending_assignments(
        self,
        interviewer_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[InterviewAssignment], int]:
        """Get pending interview assignments."""
        conditions = [
            InterviewAssignment.status == "pending",
            InterviewAssignment.feedback_required == True,
        ]
        
        if interviewer_id:
            conditions.append(InterviewAssignment.interviewer_id == interviewer_id)
        
        # Get total count
        count_result = await self.db.execute(
            select(func.count(InterviewAssignment.id)).where(and_(*conditions))
        )
        total = count_result.scalar() or 0
        
        # Get assignments
        result = await self.db.execute(
            select(InterviewAssignment)
            .options(
                joinedload(InterviewAssignment.candidate),
                joinedload(InterviewAssignment.interviewer),
                joinedload(InterviewAssignment.interview_kit),
            )
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
            .order_by(InterviewAssignment.created_at.asc())
        )
        assignments = result.unique().scalars().all()
        
        return list(assignments), total
    
    async def update_assignment(
        self,
        assignment_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[InterviewAssignment]:
        """Update an assignment."""
        await self.db.execute(
            update(InterviewAssignment)
            .where(InterviewAssignment.id == assignment_id)
            .values(**update_data)
        )
        await self.db.commit()
        return await self.get_assignment_by_id(assignment_id)
    
    async def cancel_assignment(
        self,
        assignment_id: str,
        reason: Optional[str] = None
    ) -> Optional[InterviewAssignment]:
        """Cancel an assignment."""
        return await self.update_assignment(
            assignment_id,
            {"status": "cancelled", "notes": reason or "Cancelled"}
        )
    
    async def check_assignment_has_feedback(
        self,
        assignment_id: str
    ) -> bool:
        """Check if an assignment has submitted feedback."""
        result = await self.db.execute(
            select(Feedback)
            .where(
                and_(
                    Feedback.assignment_id == assignment_id,
                    Feedback.is_submitted == True
                )
            )
        )
        return result.scalar_one_or_none() is not None
    
    # ============== Stage History Operations ==============
    
    async def get_stage_history(
        self,
        candidate_id: str,
        limit: int = 50
    ) -> List[StageHistory]:
        """Get stage history for a candidate."""
        result = await self.db.execute(
            select(StageHistory)
            .where(StageHistory.candidate_id == candidate_id)
            .order_by(StageHistory.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    # ============== Feedback Status Queries ==============
    
    async def get_required_feedbacks_for_stage(
        self,
        workflow_id: str,
        stage_id: str
    ) -> int:
        """Get the number of required feedbacks for a stage."""
        workflow = await self.get_by_id(workflow_id)
        if not workflow or not workflow.stages:
            return 0
        
        for stage in workflow.stages:
            if stage.get("id") == stage_id:
                return stage.get("required_feedback_count", 0)
        
        return 0
    
    async def validate_candidate_can_move(
        self,
        candidate_id: str,
        target_stage_id: str
    ) -> Dict[str, Any]:
        """Check if a candidate can be moved to a target stage."""
        candidate = await self.get_candidate_by_id(candidate_id)
        if not candidate:
            return {
                "can_move": False,
                "candidate_id": candidate_id,
                "error": "Candidate not found"
            }
        
        # Get required feedbacks for current stage
        required = await self.get_required_feedbacks_for_stage(
            candidate.workflow_id,
            candidate.current_stage_id
        )
        
        # Count submitted feedbacks
        result = await self.db.execute(
            select(func.count(Feedback.id))
            .where(
                and_(
                    Feedback.candidate_id == candidate_id,
                    Feedback.is_submitted == True
                )
            )
        )
        submitted = result.scalar() or 0
        
        if submitted < required:
            # Get missing assignment details
            assignments = await self.get_assignments_by_candidate(candidate_id)
            missing = []
            for a in assignments:
                if a.feedback_required and (
                    not a.feedback or not a.feedback.is_submitted
                ):
                    missing.append({
                        "assignment_id": a.id,
                        "interviewer_id": a.interviewer_id
                    })
            
            return {
                "can_move": False,
                "candidate_id": candidate_id,
                "current_stage_id": candidate.current_stage_id,
                "required_feedbacks": required,
                "submitted_feedbacks": submitted,
                "missing_feedbacks": missing,
                "blocked_reason": f"Required feedback not submitted. {submitted}/{required} complete."
            }
        
        return {
            "can_move": True,
            "candidate_id": candidate_id,
            "current_stage_id": candidate.current_stage_id,
            "required_feedbacks": required,
            "submitted_feedbacks": submitted
        }
    
    # ============== Statistics ==============
    
    async def get_workflow_stats(
        self,
        workflow_id: str
    ) -> Dict[str, Any]:
        """Get statistics for a workflow."""
        workflow = await self.get_by_id(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}
        
        # Get candidate counts
        result = await self.db.execute(
            select(
                func.count(Candidate.id).label("total"),
                func.sum(
                    func.cast(
                        Candidate.status == "active", 
                        __import__('sqlalchemy').Integer
                    )
                ).label("active")
            ).where(
                and_(
                    Candidate.workflow_id == workflow_id,
                    Candidate.is_active == True
                )
            )
        )
        counts = result.one()
        
        # Get stage counts
        stage_stats = []
        if workflow.stages:
            for stage in workflow.stages:
                stage_id = stage.get("id")
                count_result = await self.db.execute(
                    select(func.count(Candidate.id))
                    .where(
                        and_(
                            Candidate.workflow_id == workflow_id,
                            Candidate.current_stage_id == stage_id,
                            Candidate.is_active == True
                        )
                    )
                )
                stage_count = count_result.scalar() or 0
                
                stage_stats.append({
                    "stage_id": stage_id,
                    "stage_name": stage.get("name"),
                    "candidate_count": stage_count
                })
        
        return {
            "workflow_id": workflow_id,
            "total_candidates": counts.total or 0,
            "active_candidates": counts.active or 0,
            "stage_stats": stage_stats
        }

