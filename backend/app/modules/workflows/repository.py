"""
Repository layer for workflows operations.

Handles database operations for workflows, stages, and candidates.
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import (
    Workflow,
    WorkflowStage,
    Candidate,
    Role,
    User,
    RoleSnapshot,
)


class WorkflowsRepository:
    """Repository for workflows database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_role_by_id(self, role_id: int) -> Optional[Role]:
        result = await self.db.execute(
            select(Role).where(Role.id == role_id)
        )
        return result.scalar_one_or_none()

    async def get_users_by_ids(self, user_ids: List[int]) -> List[User]:
        if not user_ids:
            return []
        result = await self.db.execute(
            select(User).where(User.id.in_(set(user_ids)))
        )
        return list(result.scalars().all())

    async def create_candidate(self, full_name: str, email: str) -> Candidate:
        candidate = Candidate(full_name=full_name, email=email)
        self.db.add(candidate)
        await self.db.flush()
        await self.db.refresh(candidate)
        return candidate

    async def create_workflow(
        self,
        candidate_id: int,
        role_id: int,
        organization_id: int,
        status: str,
    ) -> Workflow:
        workflow = Workflow(
            candidate_id=candidate_id,
            role_id=role_id,
            organization_id=organization_id,
            status=status,
        )
        self.db.add(workflow)
        await self.db.flush()
        await self.db.refresh(workflow)
        return workflow

    async def create_role_snapshot(
        self,
        workflow_id: int,
        role_id: int,
        data: dict,
    ) -> RoleSnapshot:
        snapshot = RoleSnapshot(
            workflow_id=workflow_id,
            role_id=role_id,
            data=data,
        )
        self.db.add(snapshot)
        await self.db.flush()
        await self.db.refresh(snapshot)
        return snapshot

    async def create_workflow_stages(
        self,
        workflow_id: int,
        stages: List,
    ) -> None:
        for stage in stages:
            self.db.add(
                WorkflowStage(
                    workflow_id=workflow_id,
                    interviewer_id=stage.interviewer_id,
                    stage_order=stage.stage_order,
                    status="pending",
                )
            )
        await self.db.flush()

    async def get_workflow_by_id(self, workflow_id: int) -> Optional[Workflow]:
        result = await self.db.execute(
            select(Workflow)
            .where(Workflow.id == workflow_id)
            .options(
                selectinload(Workflow.candidate),
                selectinload(Workflow.stages),
                selectinload(Workflow.role_snapshot),
                selectinload(Workflow.decision),
            )
        )
        return result.scalar_one_or_none()

    async def list_workflows_by_org(
        self,
        organization_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Workflow]:
        result = await self.db.execute(
            select(Workflow)
            .where(Workflow.organization_id == organization_id)
            .options(
                selectinload(Workflow.candidate),
                selectinload(Workflow.stages),
            )
            .order_by(Workflow.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_stages_by_ids(self, stage_ids: List[int]) -> List[WorkflowStage]:
        if not stage_ids:
            return []
        result = await self.db.execute(
            select(WorkflowStage).where(WorkflowStage.id.in_(set(stage_ids)))
        )
        return list(result.scalars().all())

    async def update_workflow_stages(self, updates: List) -> None:
        stage_map = {stage.id: stage for stage in updates}
        stages = await self.get_stages_by_ids(list(stage_map.keys()))
        for stage in stages:
            update = stage_map.get(stage.id)
            stage.interviewer_id = update.interviewer_id
        await self.db.flush()
