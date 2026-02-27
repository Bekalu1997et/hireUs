"""
Service layer for candidate signal aggregation.
"""
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.modules.signals.repository import SignalsRepository
from app.schemas.signal import SignalResponse, SignalScore, SignalEvaluation


class SignalsService:
    """Service for signals aggregation."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = SignalsRepository(db)

    async def get_signals(self, candidate_id: int, role_id: int, user: User) -> SignalResponse:
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

        totals: dict[str, float] = {}
        counts: dict[str, int] = {}
        for evaluation in evaluations:
            for score in evaluation.scores:
                name = score.competency.name
                totals[name] = totals.get(name, 0.0) + float(score.score)
                counts[name] = counts.get(name, 0) + 1

        competency_scores = []
        for comp in role.competencies:
            if comp.name in totals and counts.get(comp.name):
                avg = totals[comp.name] / counts[comp.name]
                competency_scores.append(
                    SignalScore(competency_name=comp.name, average_score=avg)
                )

        overall_weighted_score = None
        if competency_scores:
            weight_map = {c.name: c.weight for c in role.competencies}
            overall_weighted_score = 0.0
            for cs in competency_scores:
                overall_weighted_score += cs.average_score * weight_map.get(cs.competency_name, 0.0)

        evaluations_payload = []
        for evaluation in evaluations:
            evaluations_payload.append(
                SignalEvaluation(
                    interviewer_name=evaluation.interviewer.full_name if evaluation.interviewer else "",
                    submitted_at=evaluation.submitted_at,
                    notes=evaluation.notes,
                    scores=[
                        {"competency_name": s.competency.name, "score": s.score}
                        for s in evaluation.scores
                    ],
                )
            )

        return SignalResponse(
            candidate_id=candidate_id,
            role_id=role_id,
            competency_scores=competency_scores,
            overall_weighted_score=overall_weighted_score,
            evaluations=evaluations_payload,
        )
