"""
Service layer for workflow operations.

Handles workflow creation, retrieval, and stage assignment updates.
"""
from typing import List
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import WorkflowStage, Workflow, User
from app.modules.audit.repository import AuditRepository
from app.modules.workflows.repository import WorkflowsRepository
from app.schemas.workflow import WorkflowCreate, WorkflowStagesUpdate, WorkflowReopen, WorkflowNotesUpdate


class WorkflowService:
    """Service for workflow-related validation and orchestration."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = WorkflowsRepository(db)
        self.audit = AuditRepository(db)

    def _validate_stage_ordering(self, stages: List[WorkflowStage]) -> None:
        """
        Validate that workflow stages are uniquely ordered and sequential.

        Rules:
        - stage_order values are unique
        - stage_order starts at 1
        - stage_order is sequential with no gaps
        """
        orders = [stage.stage_order for stage in stages]
        if len(orders) != len(set(orders)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workflow stage orders must be unique"
            )

        if not orders:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workflow must include at least one stage"
            )

        min_order = min(orders)
        max_order = max(orders)
        expected_orders = set(range(1, max_order + 1))
        if min_order != 1 or set(orders) != expected_orders:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workflow stage orders must be sequential starting from 1"
            )

    def validate_stage_progression(
        self,
        stages: List[WorkflowStage],
        target_stage_order: int
    ) -> None:
        """
        Enforce stage progression: stage N+1 cannot start until stage N completes.
        """
        for stage in stages:
            if stage.stage_order < target_stage_order and stage.status != "completed":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Previous workflow stages must be completed before starting this stage"
                )

    async def _get_workflow_or_404(self, workflow_id: int) -> Workflow:
        workflow = await self.repository.get_workflow_by_id(workflow_id)
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found",
            )
        return workflow

    def _ensure_workflow_access(self, workflow: Workflow, user: User) -> None:
        if workflow.organization_id != user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Workflow does not belong to your organization",
            )

    def _ensure_mutable(self, workflow: Workflow) -> None:
        if workflow.is_locked:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workflow cannot be modified after final decision",
            )

    async def create_workflow(self, data: WorkflowCreate, user: User) -> Workflow:
        role = await self.repository.get_role_by_id(data.role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found",
            )
        if role.organization_id != user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Role does not belong to your organization",
            )

        # Validate stages
        if not data.stages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workflow must include at least one stage",
            )

        # Ensure interviewers belong to org
        interviewer_ids = [stage.interviewer_id for stage in data.stages]
        valid_interviewers = await self.repository.get_users_by_ids(interviewer_ids)
        if len(valid_interviewers) != len(set(interviewer_ids)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more interviewer IDs are invalid",
            )
        for interviewer in valid_interviewers:
            if interviewer.organization_id != user.organization_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Interviewer does not belong to your organization",
                )

        # Validate ordering
        stage_models = [WorkflowStage(stage_order=s.stage_order, interviewer_id=s.interviewer_id) for s in data.stages]
        self._validate_stage_ordering(stage_models)

        async with self.db.begin():
            candidate = await self.repository.create_candidate(
                full_name=data.candidate.full_name,
                email=data.candidate.email,
            )
            workflow = await self.repository.create_workflow(
                candidate_id=candidate.id,
                role_id=role.id,
                organization_id=user.organization_id,
                status="pending",
            )
            snapshot_data = {
                "role": {
                    "id": role.id,
                    "title": role.title,
                    "description": role.description,
                    "seniority_level": role.seniority_level,
                },
                "competencies": [
                    {
                        "id": comp.id,
                        "name": comp.name,
                        "description": comp.description,
                        "weight": comp.weight,
                    }
                    for comp in role.competencies
                ],
            }
            await self.repository.create_role_snapshot(
                workflow_id=workflow.id,
                role_id=role.id,
                data=snapshot_data,
            )
            await self.repository.create_workflow_stages(
                workflow_id=workflow.id,
                stages=data.stages,
            )
            await self.audit.create_log(
                entity_type="workflow",
                entity_id=workflow.id,
                action="create",
                actor_id=user.id,
                before_data=None,
                after_data={"status": workflow.status},
            )

        return await self.repository.get_workflow_by_id(workflow.id)

    async def get_workflow(self, workflow_id: int, user: User) -> Workflow:
        workflow = await self._get_workflow_or_404(workflow_id)
        self._ensure_workflow_access(workflow, user)
        return workflow

    async def list_workflows(self, user: User, skip: int = 0, limit: int = 100) -> List[Workflow]:
        return await self.repository.list_workflows_by_org(user.organization_id, skip=skip, limit=limit)

    async def update_workflow_stages(
        self,
        workflow_id: int,
        data: WorkflowStagesUpdate,
        user: User,
    ) -> Workflow:
        workflow = await self._get_workflow_or_404(workflow_id)
        self._ensure_workflow_access(workflow, user)
        self._ensure_mutable(workflow)

        stage_ids = [s.id for s in data.stages]
        existing_stages = await self.repository.get_stages_by_ids(stage_ids)
        if len(existing_stages) != len(stage_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more workflow stage IDs are invalid",
            )
        for stage in existing_stages:
            if stage.workflow_id != workflow.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Workflow stage does not belong to workflow",
                )

        interviewer_ids = [s.interviewer_id for s in data.stages]
        valid_interviewers = await self.repository.get_users_by_ids(interviewer_ids)
        if len(valid_interviewers) != len(set(interviewer_ids)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more interviewer IDs are invalid",
            )
        for interviewer in valid_interviewers:
            if interviewer.organization_id != user.organization_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Interviewer does not belong to your organization",
                )

        async with self.db.begin():
            await self.repository.update_workflow_stages(data.stages)
            await self.audit.create_log(
                entity_type="workflow",
                entity_id=workflow.id,
                action="update_stages",
                actor_id=user.id,
                before_data=None,
                after_data={"stage_updates": [s.model_dump() for s in data.stages]},
            )

        return await self.repository.get_workflow_by_id(workflow.id)

    async def reopen_workflow(
        self,
        workflow_id: int,
        data: WorkflowReopen,
        user: User,
    ) -> Workflow:
        workflow = await self._get_workflow_or_404(workflow_id)
        self._ensure_workflow_access(workflow, user)
        if user.role != "founder":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only founders can reopen workflows",
            )

        before = {
            "status": workflow.status,
            "is_locked": workflow.is_locked,
            "reopened_at": workflow.reopened_at,
            "reopen_reason": workflow.reopen_reason,
        }

        async with self.db.begin():
            workflow.status = "pending"
            workflow.is_locked = False
            workflow.reopened_at = datetime.utcnow()
            workflow.reopen_reason = data.reason
            await self.audit.create_log(
                entity_type="workflow",
                entity_id=workflow.id,
                action="reopen",
                actor_id=user.id,
                before_data=before,
                after_data={
                    "status": workflow.status,
                    "is_locked": workflow.is_locked,
                    "reopened_at": workflow.reopened_at.isoformat(),
                    "reopen_reason": workflow.reopen_reason,
                },
            )

        return await self.repository.get_workflow_by_id(workflow.id)

    async def update_workflow_notes(
        self,
        workflow_id: int,
        data: WorkflowNotesUpdate,
        user: User,
    ) -> Workflow:
        workflow = await self._get_workflow_or_404(workflow_id)
        self._ensure_workflow_access(workflow, user)

        before = {"notes": workflow.notes}

        async with self.db.begin():
            workflow.notes = data.notes
            await self.audit.create_log(
                entity_type="workflow",
                entity_id=workflow.id,
                action="update_notes",
                actor_id=user.id,
                before_data=before,
                after_data={"notes": workflow.notes},
            )

        return await self.repository.get_workflow_by_id(workflow.id)
