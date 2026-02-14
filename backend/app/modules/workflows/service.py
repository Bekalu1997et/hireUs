"""
Workflow service.
Business logic for workflows, candidates, and assignments.
"""
from typing import Optional, List, Dict, Any
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.workflows.repository import WorkflowRepository
from app.schemas.workflow import (
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowResponse,
    WorkflowListResponse,
    WorkflowDetailResponse,
    MoveCandidateRequest,
    BulkMoveCandidateRequest,
    StageTransitionResult,
    BulkStageTransitionResult,
    InterviewerAssignmentRequest,
    InterviewerReassignmentRequest,
    CancelAssignmentRequest,
    AssignmentResponse,
    FeedbackStatusResponse,
    PendingFeedbackResponse,
    FeedbackCompletionStats,
    CanMoveCandidateResponse,
    WorkflowStatsResponse,
    DefaultWorkflowTemplate,
    WorkflowTemplateResponse,
)


class WorkflowService:
    """Service for workflow operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = WorkflowRepository(db)
    
    # ============== Workflow CRUD ==============
    
    async def create(
        self,
        workflow_data: WorkflowCreate,
        user_id: Optional[str] = None
    ) -> WorkflowResponse:
        """Create a new workflow."""
        workflow_dict = workflow_data.model_dump()
        
        # Generate stage IDs if not provided
        if workflow_dict.get("stages"):
            for i, stage in enumerate(workflow_dict["stages"]):
                if not stage.get("id"):
                    stage["id"] = f"stage_{uuid.uuid4().hex[:8]}"
                stage["order"] = i
        
        workflow = await self.repo.create(workflow_dict, user_id)
        
        return WorkflowResponse(
            id=workflow.id,
            organization_id=workflow.organization_id,
            name=workflow.name,
            description=workflow.description,
            stages=workflow.stages or [],
            is_default=workflow.is_default,
            is_active=workflow.is_active,
            created_by=workflow.created_by,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at
        )
    
    async def get_all(
        self,
        organization_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> WorkflowListResponse:
        """Get all workflows for an organization."""
        workflows, total = await self.repo.get_by_organization(
            organization_id or "demo-org",  # Default to demo org if not provided
            skip=skip,
            limit=limit
        )
        
        page = (skip // limit) + 1 if limit > 0 else 1
        total_pages = (total + limit - 1) // limit if limit > 0 else 1
        
        items = [
            WorkflowResponse(
                id=w.id,
                organization_id=w.organization_id,
                name=w.name,
                description=w.description,
                stages=w.stages or [],
                is_default=w.is_default,
                is_active=w.is_active,
                created_by=w.created_by,
                created_at=w.created_at,
                updated_at=w.updated_at
            )
            for w in workflows
        ]
        
        return WorkflowListResponse(
            items=items,
            total=total,
            page=page,
            page_size=limit,
            total_pages=total_pages
        )
    
    async def get_by_id(self, workflow_id: str) -> Optional[WorkflowDetailResponse]:
        """Get workflow by ID with detailed info."""
        workflow = await self.repo.get_by_id(workflow_id)
        if not workflow:
            return None
        
        # Get candidate counts per stage
        candidate_counts: Dict[str, int] = {}
        if workflow.stages:
            for stage in workflow.stages:
                stage_id = stage.get("id")
                _, count = await self.repo.get_candidates_by_stage(
                    workflow_id, stage_id or "", limit=1
                )
                candidate_counts[stage_id or ""] = count
        
        return WorkflowDetailResponse(
            id=workflow.id,
            organization_id=workflow.organization_id,
            name=workflow.name,
            description=workflow.description,
            stages=workflow.stages or [],
            is_default=workflow.is_default,
            is_active=workflow.is_active,
            created_by=workflow.created_by,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at,
            candidates_count=candidate_counts
        )
    
    async def update(
        self,
        workflow_id: str,
        update_data: WorkflowUpdate,
        user_id: Optional[str] = None
    ) -> Optional[WorkflowResponse]:
        """Update a workflow."""
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # Regenerate stage IDs if stages are being reordered
        if "stages" in update_dict:
            for i, stage in enumerate(update_dict["stages"]):
                if not stage.get("id"):
                    stage["id"] = f"stage_{uuid.uuid4().hex[:8]}"
                stage["order"] = i
        
        workflow = await self.repo.update(workflow_id, update_dict)
        if not workflow:
            return None
        
        return WorkflowResponse(
            id=workflow.id,
            organization_id=workflow.organization_id,
            name=workflow.name,
            description=workflow.description,
            stages=workflow.stages or [],
            is_default=workflow.is_default,
            is_active=workflow.is_active,
            created_by=workflow.created_by,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at
        )
    
    async def delete(
        self,
        workflow_id: str,
        hard_delete: bool = False
    ) -> Dict[str, str]:
        """Delete a workflow."""
        success = await self.repo.delete(workflow_id, hard_delete)
        return {"message": "Workflow deleted successfully" if success else "Failed to delete workflow"}
    
    async def set_default(
        self,
        workflow_id: str,
        organization_id: str
    ) -> Optional[WorkflowResponse]:
        """Set workflow as default."""
        workflow = await self.repo.set_default(workflow_id, organization_id)
        if not workflow:
            return None
        
        return WorkflowResponse(
            id=workflow.id,
            organization_id=workflow.organization_id,
            name=workflow.name,
            description=workflow.description,
            stages=workflow.stages or [],
            is_default=workflow.is_default,
            is_active=workflow.is_active,
            created_by=workflow.created_by,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at
        )
    
    async def get_default(self, organization_id: str) -> Optional[WorkflowResponse]:
        """Get the default workflow for an organization."""
        workflow = await self.repo.get_default_workflow(organization_id)
        if not workflow:
            return None
        
        return WorkflowResponse(
            id=workflow.id,
            organization_id=workflow.organization_id,
            name=workflow.name,
            description=workflow.description,
            stages=workflow.stages or [],
            is_default=workflow.is_default,
            is_active=workflow.is_active,
            created_by=workflow.created_by,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at
        )
    
    # ============== Candidate Stage Transitions ==============
    
    async def move_candidate(
        self,
        request: MoveCandidateRequest,
        user_id: Optional[str] = None,
        skip_validation: bool = False
    ) -> StageTransitionResult:
        """Move a candidate to a new stage."""
        # Validate move if not skipped
        if not skip_validation:
            validation = await self.validate_candidate_move(
                request.candidate_id,
                request.to_stage_id
            )
            
            if not validation.can_move:
                return StageTransitionResult(
                    success=False,
                    candidate_id=request.candidate_id,
                    from_stage=None,
                    to_stage=request.to_stage_id,
                    message="Cannot move candidate",
                    blocked_reason=validation.blocked_reason
                )
        
        # Get stage name
        workflow = await self.repo.get_by_id(
            (await self.repo.get_candidate_by_id(request.candidate_id)).workflow_id
        )
        stage_name = None
        if workflow and workflow.stages:
            for stage in workflow.stages:
                if stage.get("id") == request.to_stage_id:
                    stage_name = stage.get("name")
                    break
        
        if not stage_name:
            stage_name = request.to_stage_id
        
        # Move candidate
        candidate = await self.repo.update_candidate_stage(
            candidate_id=request.candidate_id,
            new_stage_id=request.to_stage_id,
            new_stage_name=stage_name,
            changed_by=user_id,
            reason=request.reason
        )
        
        if not candidate:
            return StageTransitionResult(
                success=False,
                candidate_id=request.candidate_id,
                from_stage=None,
                to_stage=request.to_stage_id,
                message="Candidate not found",
                blocked_reason="Invalid candidate ID"
            )
        
        return StageTransitionResult(
            success=True,
            candidate_id=request.candidate_id,
            from_stage=candidate.current_stage_id,
            to_stage=request.to_stage_id,
            message="Candidate moved successfully",
            blocked_reason=None
        )
    
    async def bulk_move_candidates(
        self,
        request: BulkMoveCandidateRequest,
        user_id: Optional[str] = None
    ) -> BulkStageTransitionResult:
        """Move multiple candidates to a new stage."""
        results = []
        moved = 0
        blocked = 0
        
        for candidate_id in request.candidate_ids:
            result = await self.move_candidate(
                MoveCandidateRequest(
                    candidate_id=candidate_id,
                    to_stage_id=request.to_stage_id,
                    reason=request.reason
                ),
                user_id=user_id
            )
            results.append(result)
            
            if result.success:
                moved += 1
            else:
                blocked += 1
        
        return BulkStageTransitionResult(
            success=blocked == 0,
            total=len(request.candidate_ids),
            moved=moved,
            blocked=blocked,
            results=results,
            message=f"Moved {moved}/{len(request.candidate_ids)} candidates"
        )
    
    async def validate_candidate_move(
        self,
        candidate_id: str,
        target_stage_id: str
    ) -> CanMoveCandidateResponse:
        """Check if a candidate can be moved to a target stage."""
        result = await self.repo.validate_candidate_can_move(
            candidate_id,
            target_stage_id
        )
        
        return CanMoveCandidateResponse(
            can_move=result.get("can_move", False),
            candidate_id=result.get("candidate_id", candidate_id),
            current_stage_id=result.get("current_stage_id"),
            required_feedbacks=result.get("required_feedbacks", 0),
            submitted_feedbacks=result.get("submitted_feedbacks", 0),
            missing_feedbacks=result.get("missing_feedbacks", []),
            blocked_reason=result.get("blocked_reason")
        )
    
    # ============== Interviewer Assignment ==============
    
    async def assign_interviewer(
        self,
        request: InterviewerAssignmentRequest
    ) -> AssignmentResponse:
        """Assign an interviewer to a candidate."""
        assignment = await self.repo.create_assignment({
            "candidate_id": request.candidate_id,
            "interviewer_id": request.interviewer_id,
            "interview_kit_id": request.interview_kit_id,
            "scheduled_at": request.scheduled_at,
            "duration_minutes": request.duration_minutes,
            "notes": request.notes,
            "feedback_required": True,
            "status": "pending"
        })
        
        # Get interview kit title if exists
        interview_kit_title = None
        if assignment.interview_kit:
            interview_kit_title = assignment.interview_kit.title
        
        return AssignmentResponse(
            id=assignment.id,
            candidate_id=assignment.candidate_id,
            interviewer_id=assignment.interviewer_id,
            interviewer_name=None,  # Would need to fetch user
            interview_kit_id=assignment.interview_kit_id,
            interview_kit_title=interview_kit_title,
            scheduled_at=assignment.scheduled_at,
            duration_minutes=assignment.duration_minutes,
            status=assignment.status,
            notes=assignment.notes,
            feedback_required=assignment.feedback_required,
            feedback_submitted=False,
            created_at=assignment.created_at
        )
    
    async def reassign_interviewer(
        self,
        request: InterviewerReassignmentRequest
    ) -> Optional[AssignmentResponse]:
        """Reassign an interviewer."""
        assignment = await self.repo.update_assignment(
            request.assignment_id,
            {"interviewer_id": request.new_interviewer_id}
        )
        
        if not assignment:
            return None
        
        return AssignmentResponse(
            id=assignment.id,
            candidate_id=assignment.candidate_id,
            interviewer_id=assignment.interviewer_id,
            interviewer_name=None,
            interview_kit_id=assignment.interview_kit_id,
            interview_kit_title=None,
            scheduled_at=assignment.scheduled_at,
            duration_minutes=assignment.duration_minutes,
            status=assignment.status,
            notes=assignment.notes,
            feedback_required=assignment.feedback_required,
            feedback_submitted=False,
            created_at=assignment.created_at
        )
    
    async def cancel_assignment(
        self,
        request: CancelAssignmentRequest
    ) -> Dict[str, Any]:
        """Cancel an interview assignment."""
        assignment = await self.repo.cancel_assignment(
            request.assignment_id,
            request.reason
        )
        
        if not assignment:
            return {"error": "Assignment not found"}
        
        return {
            "id": assignment.id,
            "status": "cancelled",
            "message": "Assignment cancelled successfully"
        }
    
    async def get_assignments_for_candidate(
        self,
        candidate_id: str
    ) -> List[AssignmentResponse]:
        """Get all assignments for a candidate."""
        assignments = await self.repo.get_assignments_by_candidate(candidate_id)
        
        return [
            AssignmentResponse(
                id=a.id,
                candidate_id=a.candidate_id,
                interviewer_id=a.interviewer_id,
                interviewer_name=None,
                interview_kit_id=a.interview_kit_id,
                interview_kit_title=a.interview_kit.title if a.interview_kit else None,
                scheduled_at=a.scheduled_at,
                duration_minutes=a.duration_minutes,
                status=a.status,
                notes=a.notes,
                feedback_required=a.feedback_required,
                feedback_submitted=a.feedback is not None and a.feedback.is_submitted,
                created_at=a.created_at
            )
            for a in assignments
        ]
    
    async def get_pending_feedbacks(
        self,
        interviewer_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[PendingFeedbackResponse], int]:
        """Get pending feedback requests."""
        assignments, total = await self.repo.get_pending_assignments(
            interviewer_id, skip, limit
        )
        
        results = []
        for a in assignments:
            results.append(PendingFeedbackResponse(
                assignment_id=a.id,
                candidate_id=a.candidate_id,
                candidate_name=a.candidate.full_name if a.candidate else None,
                stage_id=a.candidate.current_stage_id if a.candidate else None,
                stage_name=a.candidate.current_stage_name if a.candidate else None,
                interviewer_id=a.interviewer_id,
                interviewer_name=None,
                interview_kit_id=a.interview_kit_id,
                interview_kit_title=a.interview_kit.title if a.interview_kit else None,
                scheduled_at=a.scheduled_at,
                is_overdue=False  # Would need additional logic
            ))
        
        return results, total
    
    # ============== Feedback Status ==============
    
    async def get_candidate_feedback_status(
        self,
        candidate_id: str
    ) -> Optional[FeedbackStatusResponse]:
        """Get feedback status for a candidate."""
        status_data = await self.repo.get_candidate_feedback_status(candidate_id)
        
        if "error" in status_data:
            return None
        
        return FeedbackStatusResponse(
            candidate_id=status_data["candidate_id"],
            candidate_name=status_data["candidate_name"],
            current_stage_id=status_data.get("current_stage_id"),
            current_stage_name=status_data.get("current_stage_name"),
            total_required_feedbacks=status_data.get("total_required_feedbacks", 0),
            total_submitted_feedbacks=status_data.get("total_submitted_feedbacks", 0),
            is_blocked=status_data.get("is_blocked", False),
            blocked_reason=status_data.get("blocked_reason"),
            assignments=[
                AssignmentResponse(
                    id=a["id"],
                    candidate_id=a["candidate_id"],
                    interviewer_id=a["interviewer_id"],
                    interviewer_name=None,
                    interview_kit_id=a.get("interview_kit_id"),
                    interview_kit_title=None,
                    scheduled_at=a.get("scheduled_at"),
                    duration_minutes=a["duration_minutes"],
                    status=a["status"],
                    notes=a.get("notes"),
                    feedback_required=a["feedback_required"],
                    feedback_submitted=a.get("feedback_submitted", False),
                    created_at=None  # Would need to fetch
                )
                for a in status_data.get("assignments", [])
            ]
        )
    
    async def get_feedback_completion_stats(
        self,
        organization_id: str
    ) -> FeedbackCompletionStats:
        """Get feedback completion statistics."""
        # This would need more complex aggregation
        # Simplified for now
        return FeedbackCompletionStats(
            total_assignments=0,
            completed=0,
            pending=0,
            overdue=0,
            completion_rate=0.0
        )
    
    # ============== Stage History ==============
    
    async def get_stage_history(
        self,
        candidate_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get stage history for a candidate."""
        history = await self.repo.get_stage_history(candidate_id, limit)
        
        return [
            {
                "id": h.id,
                "candidate_id": h.candidate_id,
                "from_stage": h.from_stage,
                "to_stage": h.to_stage,
                "changed_by": h.changed_by,
                "reason": h.reason,
                "created_at": h.created_at.isoformat() if h.created_at else None
            }
            for h in history
        ]
    
    # ============== Statistics ==============
    
    async def get_workflow_stats(
        self,
        workflow_id: str
    ) -> Optional[WorkflowStatsResponse]:
        """Get statistics for a workflow."""
        stats = await self.repo.get_workflow_stats(workflow_id)
        
        if "error" in stats:
            return None
        
        return WorkflowStatsResponse(
            workflow_id=stats["workflow_id"],
            total_candidates=stats["total_candidates"],
            active_candidates=stats["active_candidates"],
            completed_candidates=stats.get("completed_candidates", 0),
            rejected_candidates=stats.get("rejected_candidates", 0),
            stage_stats=[
                {
                    "stage_id": s["stage_id"],
                    "stage_name": s["stage_name"],
                    "candidate_count": s["candidate_count"],
                    "avg_time_in_stage_hours": None,
                    "feedback_completion_rate": 1.0
                }
                for s in stats.get("stage_stats", [])
            ]
        )
    
    # ============== Templates ==============
    
    async def create_default_workflow(
        self,
        organization_id: str,
        user_id: Optional[str] = None
    ) -> WorkflowResponse:
        """Create a default workflow with standard stages."""
        default_stages = [
            {
                "id": f"stage_{uuid.uuid4().hex[:8]}",
                "name": "Applied",
                "order": 0,
                "description": "Initial application stage",
                "color": "#6366f1",
                "required_feedback_count": 0,
                "interview_types": []
            },
            {
                "id": f"stage_{uuid.uuid4().hex[:8]}",
                "name": "Screening",
                "order": 1,
                "description": "Initial screening call",
                "color": "#8b5cf6",
                "required_feedback_count": 1,
                "interview_types": ["behavioral"]
            },
            {
                "id": f"stage_{uuid.uuid4().hex[:8]}",
                "name": "Technical 1",
                "order": 2,
                "description": "First technical interview",
                "color": "#06b6d4",
                "required_feedback_count": 1,
                "interview_types": ["coding"]
            },
            {
                "id": f"stage_{uuid.uuid4().hex[:8]}",
                "name": "Technical 2",
                "order": 3,
                "description": "Second technical interview",
                "color": "#10b981",
                "required_feedback_count": 1,
                "interview_types": ["system_design"]
            },
            {
                "id": f"stage_{uuid.uuid4().hex[:8]}",
                "name": "Decision",
                "order": 4,
                "description": "Final hiring decision",
                "color": "#f59e0b",
                "required_feedback_count": 2,
                "interview_types": ["behavioral", "culture_fit"]
            }
        ]
        
        return await self.create(
            WorkflowCreate(
                organization_id=organization_id,
                name="Standard Hiring Pipeline",
                description="Default hiring workflow with standard stages",
                stages=default_stages,
                is_default=True
            ),
            user_id=user_id
        )
    
    async def get_workflow_template(self) -> WorkflowTemplateResponse:
        """Get a template for creating workflows."""
        return WorkflowTemplateResponse(
            name="Standard Hiring Pipeline",
            description="A typical 5-stage hiring workflow",
            stages=[
                {
                    "id": "applied",
                    "name": "Applied",
                    "order": 0,
                    "description": "Initial application stage",
                    "color": "#6366f1",
                    "required_feedback_count": 0,
                    "interview_types": []
                },
                {
                    "id": "screening",
                    "name": "Screening",
                    "order": 1,
                    "description": "Initial screening call",
                    "color": "#8b5cf6",
                    "required_feedback_count": 1,
                    "interview_types": ["behavioral"]
                },
                {
                    "id": "technical_1",
                    "name": "Technical 1",
                    "order": 2,
                    "description": "First technical interview",
                    "color": "#06b6d4",
                    "required_feedback_count": 1,
                    "interview_types": ["coding"]
                },
                {
                    "id": "technical_2",
                    "name": "Technical 2",
                    "order": 3,
                    "description": "Second technical interview",
                    "color": "#10b981",
                    "required_feedback_count": 1,
                    "interview_types": ["system_design"]
                },
                {
                    "id": "decision",
                    "name": "Decision",
                    "order": 4,
                    "description": "Final hiring decision",
                    "color": "#f59e0b",
                    "required_feedback_count": 2,
                    "interview_types": ["behavioral", "culture_fit"]
                }
            ],
            use_template="Use this template to quickly set up a standard hiring workflow"
        )

