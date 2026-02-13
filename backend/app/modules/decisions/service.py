"""
Service layer for decisions operations.

Handles decision brief generation and final decision recording.
"""
from datetime import datetime
from typing import Dict, Any, List

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Workflow, User
from app.modules.decisions.repository import DecisionsRepository
from app.modules.audit.repository import AuditRepository
from app.modules.ai.client import AIClient
from app.modules.ai.parser import parse_decision_brief_response, LLMParseError
from app.modules.ai.validators import validate_decision_brief, LLMValidationError
from app.schemas.decision import DecisionCreate, DecisionBriefResponse


class DecisionsService:
    """Service for decisions operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = DecisionsRepository(db)
        self.ai_client = AIClient()
        self.audit = AuditRepository(db)

    async def _get_workflow_or_404(self, workflow_id: int) -> Workflow:
        workflow = await self.repository.get_workflow_with_details(workflow_id)
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

    def _ensure_no_final_decision(self, workflow: Workflow) -> None:
        if workflow.decision is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Final decision already recorded for this workflow",
            )

    def _build_evaluation_payload(self, workflow: Workflow) -> List[Dict[str, Any]]:
        evaluations_payload = []
        for evaluation in workflow.evaluations:
            scores_payload = [
                {
                    "competency_name": score.competency.name,
                    "score": score.score,
                }
                for score in evaluation.scores
            ]
            evaluations_payload.append(
                {
                    "interviewer_name": evaluation.interviewer.full_name
                    if evaluation.interviewer
                    else f"User {evaluation.interviewer_id}",
                    "submitted_at": evaluation.submitted_at.isoformat(),
                    "notes": evaluation.notes,
                    "scores": scores_payload,
                }
            )
        return evaluations_payload

    def _calculate_aggregated_scores(self, workflow: Workflow) -> Dict[str, float]:
        totals: Dict[str, float] = {}
        counts: Dict[str, int] = {}

        for evaluation in workflow.evaluations:
            for score in evaluation.scores:
                name = score.competency.name
                totals[name] = totals.get(name, 0.0) + float(score.score)
                counts[name] = counts.get(name, 0) + 1

        aggregated_scores = {}
        for name, total in totals.items():
            aggregated_scores[name] = total / counts[name]

        return aggregated_scores

    async def generate_decision_brief(
        self,
        workflow_id: int,
        user: User,
    ) -> DecisionBriefResponse:
        """
        Generate a decision brief using AI.
        """
        workflow = await self._get_workflow_or_404(workflow_id)
        self._ensure_workflow_access(workflow, user)
        self._ensure_no_final_decision(workflow)

        if not workflow.evaluations:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No evaluations found for workflow",
            )

        competencies = [
            {
                "id": comp.id,
                "name": comp.name,
                "description": comp.description,
                "weight": comp.weight,
            }
            for comp in workflow.role.competencies
        ]

        evaluations_payload = self._build_evaluation_payload(workflow)
        aggregated_scores = self._calculate_aggregated_scores(workflow)

        try:
            raw_response = await self.ai_client.generate_decision_brief(
                candidate_name=workflow.candidate.full_name,
                role_title=workflow.role.title,
                role_description=workflow.role.description,
                competencies=competencies,
                evaluations=evaluations_payload,
                aggregated_scores=aggregated_scores,
            )
            parsed = parse_decision_brief_response(raw_response)
            validate_decision_brief(parsed)
        except (LLMParseError, LLMValidationError) as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            )
        except Exception as exc:
            print("LLM invocation failed (decision brief):", repr(exc))
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LLM invocation failed; please retry",
            )

        return DecisionBriefResponse(**parsed)

    async def record_decision(
        self,
        decision_data: DecisionCreate,
        user: User,
    ):
        """
        Record a final decision and mark workflow completed.
        """
        workflow = await self._get_workflow_or_404(decision_data.workflow_id)
        self._ensure_workflow_access(workflow, user)
        self._ensure_no_final_decision(workflow)

        async with self.db.begin_nested():
            decision = await self.repository.create_decision(
                workflow_id=workflow.id,
                candidate_id=workflow.candidate_id,
                role_id=workflow.role_id,
                decision_maker_id=user.id,
                outcome=decision_data.outcome,
                summary=decision_data.summary,
                strengths=decision_data.strengths,
                concerns=decision_data.concerns,
                recommendation=decision_data.recommendation,
            )

            workflow.status = "completed"
            workflow.completed_at = datetime.utcnow()
            workflow.is_locked = True

            await self.audit.create_log(
                entity_type="decision",
                entity_id=decision.id,
                action="create",
                actor_id=user.id,
                before_data=None,
                after_data={
                    "workflow_id": workflow.id,
                    "outcome": decision.outcome,
                },
            )

        return decision

    async def get_decision(self, decision_id: int, user: User):
        decision = await self.repository.get_decision_by_id(decision_id)
        if not decision:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Decision not found",
            )

        if decision.workflow.organization_id != user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Decision does not belong to your organization",
            )

        return decision

    async def get_decision_for_workflow(self, workflow_id: int, user: User):
        workflow = await self._get_workflow_or_404(workflow_id)
        self._ensure_workflow_access(workflow, user)

        decision = await self.repository.get_decision_by_workflow(workflow_id)
        if not decision:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Decision not found for workflow",
            )
        return decision
