"""
Repository layer for interview kits operations.

Handles database operations for interview kits and questions.
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import InterviewKit, InterviewQuestion, Role, Competency


class InterviewKitsRepository:
    """Repository for interview kits database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_role_with_competencies(self, role_id: int) -> Optional[Role]:
        """
        Get a role with its competencies.
        """
        result = await self.db.execute(
            select(Role)
            .where(Role.id == role_id)
            .options(selectinload(Role.competencies))
        )
        return result.scalar_one_or_none()

    async def create_interview_kit(
        self,
        role_id: int,
        llm_model: str,
        questions: List[dict],
    ) -> InterviewKit:
        """
        Create an interview kit and its questions.
        """
        kit = InterviewKit(role_id=role_id, llm_model=llm_model)
        self.db.add(kit)
        await self.db.flush()

        for question in questions:
            self.db.add(
                InterviewQuestion(
                    interview_kit_id=kit.id,
                    competency_id=question["competency_id"],
                    question_text=question["question_text"],
                    evaluation_rubric=question["evaluation_rubric"],
                    order=question["order"],
                )
            )

        await self.db.flush()
        await self.db.refresh(kit, ["questions"])
        return kit

    async def get_interview_kit_by_id(self, kit_id: int) -> Optional[InterviewKit]:
        """
        Get interview kit by ID with questions.
        """
        result = await self.db.execute(
            select(InterviewKit)
            .where(InterviewKit.id == kit_id)
            .options(selectinload(InterviewKit.questions))
        )
        return result.scalar_one_or_none()

    async def list_interview_kits_by_role(self, role_id: int) -> List[InterviewKit]:
        """
        List interview kits for a role.
        """
        result = await self.db.execute(
            select(InterviewKit)
            .where(InterviewKit.role_id == role_id)
            .options(selectinload(InterviewKit.questions))
            .order_by(InterviewKit.generated_at.desc())
        )
        return list(result.scalars().all())
