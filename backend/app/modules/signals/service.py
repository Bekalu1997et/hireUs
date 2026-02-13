"""
Service layer for candidate signals aggregation.
"""
from collections import defaultdict
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.modules.signals.repository import SignalsRepository
from app.schemas.signal import (
    SignalResponse,
    SignalCompetencyAggregate,
    SignalEvaluationResponse,
    SignalEvaluationScoreResponse,
)


class SignalsService:
    """Service for aggregating candidate signals."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = SignalsRepository(db)

    async def get_candidate_signals(
        self,
        candidate_id: int,
        role_id: int,
        user: User,
    ) -> SignalResponse:
        role = await self.repository.get_role_with_competencies(role_id)
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

        workflow_ids = await self.repository.get_workflow_ids_for_candidate_role(
            candidate_id,
            role_id,
        )
        evaluations = await self.repository.get_evaluations_for_workflows(workflow_ids)

        # Aggregate competency scores across evaluations
        score_buckets: dict[int, list[int]] = defaultdict(list)
        for evaluation in evaluations:
            for score in evaluation.scores:
                score_buckets[score.competency_id].append(score.score)

        competency_averages: list[SignalCompetencyAggregate] = []
        overall_weighted_score = 0.0
        for competency in role.competencies:
            scores = score_buckets.get(competency.id, [])
            avg = sum(scores) / len(scores) if scores else 0.0
            competency_averages.append(
                SignalCompetencyAggregate(
                    competency_id=competency.id,
                    competency_name=competency.name,
                    average_score=round(avg, 2),
                    weight=competency.weight,
                )
            )
            overall_weighted_score += avg * competency.weight

        evaluations_payload: list[SignalEvaluationResponse] = []
        for evaluation in evaluations:
            scores_payload = [
                SignalEvaluationScoreResponse(
                    competency_id=score.competency_id,
                    competency_name=score.competency.name,
                    score=score.score,
                )
                for score in evaluation.scores
            ]
            evaluations_payload.append(
                SignalEvaluationResponse(
                    id=evaluation.id,
                    interviewer_name=evaluation.interviewer.full_name,
                    notes=evaluation.notes,
                    submitted_at=evaluation.submitted_at,
                    scores=scores_payload,
                )
            )

        return SignalResponse(
            candidate_id=candidate_id,
            role_id=role_id,
            overall_weighted_score=round(overall_weighted_score, 2),
            competency_averages=competency_averages,
            evaluations=evaluations_payload,
        )
