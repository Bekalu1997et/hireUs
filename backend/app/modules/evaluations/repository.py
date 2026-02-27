"""
Repository layer for evaluations operations.

Handles database operations for evaluations and scores.
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import (
    Evaluation,
    EvaluationScore,
    Workflow,
    WorkflowStage,
    Role,
    Competency,
    User,
)


class EvaluationsRepository:
    """Repository for evaluations database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_workflow_with_role(self, workflow_id: int) -> Optional[Workflow]:
        """
        Get a workflow with role and competencies.
        """
        result = await self.db.execute(
            select(Workflow)
            .where(Workflow.id == workflow_id)
            .options(
                selectinload(Workflow.role).selectinload(Role.competencies),
                selectinload(Workflow.stages),
            )
        )
        return result.scalar_one_or_none()

    async def get_workflow_stage(self, stage_id: int) -> Optional[WorkflowStage]:
        """
        Get a workflow stage by ID.
        """
        result = await self.db.execute(
            select(WorkflowStage)
            .where(WorkflowStage.id == stage_id)
        )
        return result.scalar_one_or_none()

    async def create_evaluation(
        self,
        workflow_id: int,
        workflow_stage_id: int,
        interviewer_id: int,
        notes: str,
        scores: List[dict],
    ) -> Evaluation:
        """
        Create evaluation and associated scores.
        """
        evaluation = Evaluation(
            workflow_id=workflow_id,
            workflow_stage_id=workflow_stage_id,
            interviewer_id=interviewer_id,
            notes=notes,
        )
        self.db.add(evaluation)
        await self.db.flush()

        for score_data in scores:
            score = EvaluationScore(
                evaluation_id=evaluation.id,
                competency_id=score_data["competency_id"],
                score=score_data["score"],
            )
            self.db.add(score)

        await self.db.flush()
        await self.db.refresh(evaluation, ["scores"])
        return evaluation

    async def get_evaluation_by_id(self, evaluation_id: int) -> Optional[Evaluation]:
        """
        Get evaluation by ID with scores and competency metadata.
        """
        result = await self.db.execute(
            select(Evaluation)
            .where(Evaluation.id == evaluation_id)
            .options(
                selectinload(Evaluation.scores).selectinload(EvaluationScore.competency),
                selectinload(Evaluation.interviewer),
                selectinload(Evaluation.workflow),
            )
        )
        return result.scalar_one_or_none()

    async def list_evaluations_by_workflow(
        self,
        workflow_id: int
    ) -> List[Evaluation]:
        """
        List evaluations for a workflow with scores and interviewer.
        """
        result = await self.db.execute(
            select(Evaluation)
            .where(Evaluation.workflow_id == workflow_id)
            .options(
                selectinload(Evaluation.scores).selectinload(EvaluationScore.competency),
                selectinload(Evaluation.interviewer),
            )
            .order_by(Evaluation.submitted_at.desc())
        )
        return list(result.scalars().all())
