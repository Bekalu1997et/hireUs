"""
Repository layer for decisions operations.

Handles database operations for decisions and related workflow data.
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import (
    Decision,
    Workflow,
    Role,
    Competency,
    Evaluation,
    EvaluationScore,
    User,
    Candidate,
)


class DecisionsRepository:
    """Repository for decisions database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_workflow_with_details(self, workflow_id: int) -> Optional[Workflow]:
        """
        Get a workflow with all data needed for decision generation.

        Loads:
        - candidate
        - role and competencies
        - evaluations with scores and interviewer
        - decision (if any)
        """
        result = await self.db.execute(
            select(Workflow)
            .where(Workflow.id == workflow_id)
            .options(
                selectinload(Workflow.candidate),
                selectinload(Workflow.role).selectinload(Role.competencies),
                selectinload(Workflow.evaluations)
                .selectinload(Evaluation.scores)
                .selectinload(EvaluationScore.competency),
                selectinload(Workflow.evaluations).selectinload(Evaluation.interviewer),
                selectinload(Workflow.decision),
            )
        )
        return result.scalar_one_or_none()

    async def get_decision_by_id(self, decision_id: int) -> Optional[Decision]:
        """
        Get a decision by ID.
        """
        result = await self.db.execute(
            select(Decision)
            .where(Decision.id == decision_id)
            .options(
                selectinload(Decision.decision_maker),
                selectinload(Decision.workflow),
            )
        )
        return result.scalar_one_or_none()

    async def get_decision_by_workflow(self, workflow_id: int) -> Optional[Decision]:
        """
        Get a decision by workflow ID.
        """
        result = await self.db.execute(
            select(Decision)
            .where(Decision.workflow_id == workflow_id)
            .options(
                selectinload(Decision.decision_maker),
                selectinload(Decision.workflow),
            )
        )
        return result.scalar_one_or_none()

    async def create_decision(
        self,
        workflow_id: int,
        candidate_id: int,
        role_id: int,
        decision_maker_id: int,
        outcome: str,
        summary: str,
        strengths: str,
        concerns: str,
        recommendation: str,
    ) -> Decision:
        """
        Create a decision record.
        """
        decision = Decision(
            workflow_id=workflow_id,
            candidate_id=candidate_id,
            role_id=role_id,
            decision_maker_id=decision_maker_id,
            outcome=outcome,
            summary=summary,
            strengths=strengths,
            concerns=concerns,
            recommendation=recommendation,
        )
        self.db.add(decision)
        await self.db.flush()
        await self.db.refresh(decision)
        return decision
