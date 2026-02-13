"""
Service layer for evaluations operations.

Handles business logic for evaluation submission and validation.
"""
from typing import List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Evaluation, Workflow, WorkflowStage, User
from app.modules.evaluations.repository import EvaluationsRepository
from app.schemas.evaluation import EvaluationCreate


class EvaluationsService:
    """Service for evaluations operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = EvaluationsRepository(db)

    async def _get_workflow_or_404(self, workflow_id: int) -> Workflow:
        workflow = await self.repository.get_workflow_with_role(workflow_id)
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found",
            )
        return workflow

    async def _get_stage_or_404(self, stage_id: int) -> WorkflowStage:
        stage = await self.repository.get_workflow_stage(stage_id)
        if not stage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow stage not found",
            )
        return stage

    def _ensure_workflow_access(self, workflow: Workflow, user: User) -> None:
        if workflow.organization_id != user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Workflow does not belong to your organization",
            )

    def _validate_scores(
        self,
        workflow: Workflow,
        scores: List[Dict[str, Any]]
    ) -> None:
        if not scores:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one score is required",
            )

        role_competency_ids = {comp.id for comp in workflow.role.competencies}
        score_competency_ids = {score["competency_id"] for score in scores}

        missing = role_competency_ids - score_competency_ids
        if missing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing scores for competencies: {missing}",
            )

        invalid = score_competency_ids - role_competency_ids
        if invalid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid competency IDs in scores: {invalid}",
            )

    async def submit_evaluation(
        self,
        evaluation_data: EvaluationCreate,
        user: User,
    ) -> Evaluation:
        workflow = await self._get_workflow_or_404(evaluation_data.workflow_id)
        stage = await self._get_stage_or_404(evaluation_data.workflow_stage_id)

        self._ensure_workflow_access(workflow, user)

        if stage.workflow_id != workflow.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workflow stage does not belong to workflow",
            )

        if stage.interviewer_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not assigned to this workflow stage",
            )

        # Enforce stage progression (previous stages must be completed)
        for wf_stage in workflow.stages:
            if wf_stage.stage_order < stage.stage_order and wf_stage.status != "completed":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Previous workflow stages must be completed before starting this stage",
                )

        self._validate_scores(workflow, [s.model_dump() for s in evaluation_data.scores])

        async with self.db.begin_nested():
            evaluation = await self.repository.create_evaluation(
                workflow_id=workflow.id,
                workflow_stage_id=stage.id,
                interviewer_id=user.id,
                notes=evaluation_data.notes,
                scores=[s.model_dump() for s in evaluation_data.scores],
            )

            # Mark stage as completed
            stage.status = "completed"

        return evaluation

    async def get_evaluation(self, evaluation_id: int, user: User) -> Evaluation:
        evaluation = await self.repository.get_evaluation_by_id(evaluation_id)
        if not evaluation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluation not found",
            )

        if evaluation.workflow.organization_id != user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Evaluation does not belong to your organization",
            )

        return evaluation

    async def list_evaluations_for_workflow(
        self,
        workflow_id: int,
        user: User,
    ) -> List[Evaluation]:
        workflow = await self._get_workflow_or_404(workflow_id)
        self._ensure_workflow_access(workflow, user)

        return await self.repository.list_evaluations_by_workflow(workflow_id)
