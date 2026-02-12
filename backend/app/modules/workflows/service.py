"""
Service layer for workflow operations.

Provides validation helpers for stage ordering and progression.
"""
from typing import List
from fastapi import HTTPException, status

from app.db.models import WorkflowStage


class WorkflowService:
    """Service for workflow-related validation and orchestration."""

    def validate_stage_ordering(self, stages: List[WorkflowStage]) -> None:
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
