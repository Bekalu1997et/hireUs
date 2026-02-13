"""
Repository layer for candidate signals.
"""
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Evaluation, EvaluationScore, Workflow, Role


class SignalsRepository:
    """Repository for signals aggregation."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_workflow_ids_for_candidate_role(
        self,
        candidate_id: int,
        role_id: int,
    ) -> List[int]:
        result = await self.db.execute(
            select(Workflow.id).where(
                Workflow.candidate_id == candidate_id,
                Workflow.role_id == role_id,
            )
        )
        return [row[0] for row in result.all()]

    async def get_evaluations_for_workflows(self, workflow_ids: List[int]) -> List[Evaluation]:
        if not workflow_ids:
            return []
        result = await self.db.execute(
            select(Evaluation)
            .where(Evaluation.workflow_id.in_(workflow_ids))
            .options(
                selectinload(Evaluation.scores).selectinload(EvaluationScore.competency),
                selectinload(Evaluation.interviewer),
            )
            .order_by(Evaluation.submitted_at.desc())
        )
        return list(result.scalars().all())

    async def get_role_with_competencies(self, role_id: int) -> Role | None:
        result = await self.db.execute(
            select(Role)
            .where(Role.id == role_id)
            .options(selectinload(Role.competencies))
        )
        return result.scalar_one_or_none()
