"""
Comparison service.
Business logic for candidate comparison.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Feedback, Candidate
from app.modules.comparison.schemas import (
    CandidateComparisonInput,
    CandidateComparisonResponse,
    CandidateSummary,
    CandidateScoreSummary,
    CompetencyComparison,
    SignalGapDetectionInput,
    SignalGapDetectionResponse,
    SignalGap,
    RankingCriteria,
    RankingResponse,
    CandidateRanking,
    BatchComparisonInput,
    BatchComparisonResponse,
    BatchComparisonChunk,
)
from app.modules.comparison.repository import ComparisonRepository
from app.modules.comparison.calculators import ComparisonCalculators


class ComparisonService:
    """
    Service for candidate comparison operations.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ComparisonRepository(db)
        self.calculators = ComparisonCalculators

    async def compare_candidates(
        self,
        comparison_input: CandidateComparisonInput
    ) -> CandidateComparisonResponse:
        """
        Compare multiple candidates side by side.
        """
        candidate_ids = comparison_input.candidate_ids
        
        # Validate input
        if len(candidate_ids) < 2:
            raise ValueError("At least 2 candidates are required for comparison")
        if len(candidate_ids) > 10:
            raise ValueError("Maximum 10 candidates can be compared at once")

        # Fetch candidates
        candidates = await self.repository.get_candidates_by_ids(candidate_ids)
        
        if not candidates:
            raise ValueError("No valid candidates found")

        # Build candidate summaries
        candidate_summaries = []
        for candidate in candidates:
            summary = await self.repository.get_candidate_summary(candidate)
            candidate_summaries.append(CandidateSummary(**summary))

        # Fetch evaluations
        evaluations = await self.repository.get_evaluations_for_candidates(
            candidate_ids,
            submitted_only=True
        )

        # Build score summaries
        score_summaries: Dict[str, CandidateScoreSummary] = {}
        all_competencies: Dict[str, Dict[str, float]] = {}

        for candidate in candidates:
            candidate_id = candidate.id
            candidate_feedbacks = evaluations.get(candidate_id, [])

            # Get evaluation stats
            stats = await self.repository.get_evaluation_stats_for_candidate(candidate_id)
            
            # Collect competency scores
            competency_scores = stats.get("competency_scores", {})
            confidence_scores = stats.get("confidence_scores", [])
            recommendation_counts = stats.get("recommendation_counts", {})

            # Calculate metrics
            overall_average = stats.get("overall_average", 0)
            avg_confidence = (
                sum(confidence_scores) / len(confidence_scores)
                if confidence_scores else 0
            )
            confidence_variance = self.calculators.calculate_variance(confidence_scores) if confidence_scores else None

            # Get dominant recommendation
            dominant_rec = (
                max(recommendation_counts.items(), key=lambda x: x[1])[0]
                if recommendation_counts else None
            )

            score_summary = CandidateScoreSummary(
                candidate_id=candidate_id,
                candidate_name=candidate.full_name,
                overall_average=overall_average,
                total_evaluations=stats.get("total_evaluations", 0),
                competency_scores=competency_scores,
                average_confidence=round(avg_confidence, 2),
                confidence_variance=confidence_variance,
                recommendation_counts=recommendation_counts,
                dominant_recommendation=dominant_rec
            )
            score_summaries[candidate_id] = score_summary

            # Track all competencies for comparison
            for comp, score in competency_scores.items():
                if comp not in all_competencies:
                    all_competencies[comp] = {}
                all_competencies[comp][candidate_id] = score

        # Build competency comparisons
        competency_comparisons = []
        for comp, scores in all_competencies.items():
            if len(scores) >= 2:
                score_values = list(scores.values())
                comparison = CompetencyComparison(
                    competency=comp,
                    scores=scores,
                    average=self.calculators.calculate_average(score_values),
                    std_deviation=self.calculators.calculate_standard_deviation(score_values),
                    min_score=min(score_values),
                    max_score=max(score_values)
                )
                competency_comparisons.append(comparison)

        # Calculate rankings
        rankings = self._calculate_rankings(score_summaries)

        # Get feedback summary if requested
        feedback_summary = None
        if comparison_input.include_feedback_summary:
            feedback_summary = await self._get_aggregated_feedback(
                candidate_ids,
                evaluations
            )

        return CandidateComparisonResponse(
            compared_at=datetime.now(timezone.utc),
            candidates_compared=len(candidates),
            candidates=candidate_summaries,
            score_summaries=score_summaries,
            competency_comparisons=competency_comparisons,
            rankings=rankings,
            feedback_summary=feedback_summary
        )

    async def detect_signal_gaps(
        self,
        gap_input: SignalGapDetectionInput
    ) -> SignalGapDetectionResponse:
        """
        Detect signal gaps in candidate evaluation.
        """
        candidate_id = gap_input.candidate_id

        # Get evaluation stats
        stats = await self.repository.get_evaluation_stats_for_candidate(candidate_id)

        competency_scores = stats.get("competency_scores", {})
        confidence_scores = stats.get("confidence_scores", [])
        evaluation_count = stats.get("total_evaluations", 0)

        # Detect gaps using calculators
        gaps = self.calculators.detect_signal_gaps(
            competency_scores=competency_scores,
            confidence_scores=confidence_scores,
            evaluation_count=evaluation_count,
            competency_threshold=gap_input.competency_threshold,
            confidence_threshold=gap_input.confidence_threshold,
            variance_threshold=gap_input.variance_threshold
        )

        # Build SignalGap objects
        signal_gaps = [
            SignalGap(
                competency=g["competency"],
                severity=g["severity"],
                description=g["description"],
                recommendation=g["recommendation"]
            )
            for g in gaps
        ]

        # Determine overall signal strength
        if evaluation_count == 0:
            signal_strength = "none"
        elif len(signal_gaps) == 0:
            signal_strength = "strong"
        elif any(g["severity"] == "high" for g in gaps):
            signal_strength = "weak"
        elif any(g["severity"] == "medium" for g in gaps):
            signal_strength = "moderate"
        else:
            signal_strength = "strong"

        # Generate recommendations
        recommendations = []
        if evaluation_count < 2:
            recommendations.append("Gather at least 2 evaluations for reliable assessment")
        for gap in signal_gaps:
            if gap.severity == "high":
                recommendations.append(gap.recommendation)

        return SignalGapDetectionResponse(
            candidate_id=candidate_id,
            has_gaps=len(signal_gaps) > 0,
            signal_gaps=signal_gaps,
            overall_signal_strength=signal_strength,
            recommendations=recommendations,
            analyzed_at=datetime.utcnow()
        )

    async def rank_candidates(
        self,
        candidate_ids: List[str],
        criteria: str = RankingCriteria.OVERALL_SCORE
    ) -> RankingResponse:
        """
        Rank candidates based on specified criteria.
        """
        if len(candidate_ids) < 2:
            raise ValueError("At least 2 candidates are required for ranking")

        # Get evaluation stats for all candidates
        candidate_metrics: Dict[str, Dict[str, Any]] = {}

        for candidate_id in candidate_ids:
            stats = await self.repository.get_evaluation_stats_for_candidate(candidate_id)
            confidence_scores = stats.get("confidence_scores", [])
            recommendation_counts = stats.get("recommendation_counts", {})

            avg_confidence = (
                sum(confidence_scores) / len(confidence_scores)
                if confidence_scores else 0
            )

            # Calculate hire score
            hire_score = 0.0
            weights = {
                "strong_hire": 1.0,
                "hire": 0.5,
                "neutral": 0.0,
                "no_hire": -0.5,
                "strong_no_hire": -1.0
            }
            total_count = sum(recommendation_counts.values())
            if total_count > 0:
                for rec, count in recommendation_counts.items():
                    weight = weights.get(rec, 0.0)
                    hire_score += weight * count
                hire_score = round(hire_score / total_count, 2)

            candidate_metrics[candidate_id] = {
                "candidate_name": stats.get("candidate_name", "Unknown"),
                "overall_average": stats.get("overall_average", 0),
                "confidence_average": round(avg_confidence, 2),
                "hire_score": hire_score,
                "evaluation_count": stats.get("total_evaluations", 0),
                "competency_scores": stats.get("competency_scores", {})
            }

        # Calculate rankings
        ranked = self.calculators.rank_candidates(candidate_metrics, criteria)

        # Build ranking response
        rankings = []
        for item in ranked:
            metrics = item.get("metrics", {})
            
            # Identify strengths and weaknesses
            strengths = []
            weaknesses = []
            
            if metrics.get("overall_average", 0) >= 4.0:
                strengths.append("High overall score")
            elif metrics.get("overall_average", 0) < 3.0:
                weaknesses.append("Below average overall score")
                
            if metrics.get("confidence_average", 0) >= 4.0:
                strengths.append("High evaluator confidence")
            elif metrics.get("confidence_average", 0) < 3.0:
                weaknesses.append("Low evaluator confidence")
                
            if metrics.get("hire_score", 0) > 0.3:
                strengths.append("Positive hiring recommendation trend")
            elif metrics.get("hire_score", 0) < -0.3:
                weaknesses.append("Negative hiring recommendation trend")

            rankings.append(CandidateRanking(
                rank=item["rank"],
                candidate_id=item["candidate_id"],
                candidate_name=item["candidate_name"],
                score=item["score"],
                strengths=strengths,
                improvement_areas=weaknesses
            ))

        return RankingResponse(
            criteria=criteria,
            direction="descending",
            rankings=rankings,
            generated_at=datetime.utcnow()
        )

    async def batch_compare(
        self,
        batch_input: BatchComparisonInput
    ) -> BatchComparisonResponse:
        """
        Handle batch comparison of many candidates.
        """
        candidate_ids = batch_input.candidate_ids
        max_per_comparison = batch_input.max_candidates_per_comparison
        include_heatmap = batch_input.include_heatmap

        if len(candidate_ids) == 0:
            raise ValueError("At least one candidate is required")
        if max_per_comparison < 2:
            raise ValueError("Maximum candidates per comparison must be at least 2")

        # Calculate chunks
        total_chunks = (len(candidate_ids) + max_per_comparison - 1) // max_per_comparison
        chunks: List[BatchComparisonChunk] = []

        for i in range(total_chunks):
            chunk_candidate_ids = candidate_ids[
                i * max_per_comparison : (i + 1) * max_per_comparison
            ]

            if len(chunk_candidate_ids) < 2:
                continue

            comparison_input = CandidateComparisonInput(
                candidate_ids=chunk_candidate_ids,
                include_heatmap=include_heatmap
            )

            comparison = await self.compare_candidates(comparison_input)

            # Get candidates for this chunk
            candidates = await self.repository.get_candidates_by_ids(chunk_candidate_ids)
            candidate_summaries = [
                CandidateSummary(**await self.repository.get_candidate_summary(c))
                for c in candidates
            ]

            chunks.append(BatchComparisonChunk(
                chunk_index=i,
                candidates=candidate_summaries,
                comparison=comparison
            ))

        # Get top candidates overall
        top_candidates_response = await self.rank_candidates(
            candidate_ids,
            RankingCriteria.OVERALL_SCORE
        )
        top_candidates = top_candidates_response.rankings[:5]

        return BatchComparisonResponse(
            total_candidates=len(candidate_ids),
            total_chunks=total_chunks,
            chunks=chunks,
            top_candidates=top_candidates,
            generated_at=datetime.utcnow()
        )

    async def get_heatmap_data(
        self,
        candidate_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Get heatmap data for candidate scores.
        """
        if len(candidate_ids) < 2:
            raise ValueError("At least 2 candidates are required for heatmap")

        # Collect scores for each candidate
        candidate_scores: Dict[str, Dict[str, float]] = {}

        for candidate_id in candidate_ids:
            stats = await self.repository.get_evaluation_stats_for_candidate(candidate_id)
            candidate_scores[candidate_id] = stats.get("competency_scores", {})

        return self.calculators.generate_heatmap_data(candidate_scores)

    async def get_candidate_comparison_summary(
        self,
        candidate_id: str
    ) -> Dict[str, Any]:
        """
        Get a summary for a single candidate in comparison context.
        """
        # Get candidate
        candidates = await self.repository.get_candidates_by_ids([candidate_id])
        if not candidates:
            raise ValueError(f"Candidate {candidate_id} not found")

        candidate = candidates[0]

        # Get stats
        stats = await self.repository.get_evaluation_stats_for_candidate(candidate_id)
        feedback = await self.repository.get_feedback_summary_for_candidate(candidate_id)

        # Get heatmap data
        heatmap = await self.get_heatmap_data([candidate_id])

        return {
            "candidate": await self.repository.get_candidate_summary(candidate),
            "statistics": stats,
            "feedback": feedback,
            "heatmap": heatmap
        }

    def _calculate_rankings(
        self,
        score_summaries: Dict[str, CandidateScoreSummary]
    ) -> Dict[str, Any]:
        """
        Calculate various rankings from score summaries.
        """
        rankings = {
            "by_overall_score": [],
            "by_confidence": [],
            "by_recommendation": [],
            "by_evaluation_count": []
        }

        # Convert to list for sorting
        candidates = list(score_summaries.values())

        # Sort by overall score
        by_score = sorted(
            candidates,
            key=lambda x: x.overall_average,
            reverse=True
        )
        rankings["by_overall_score"] = [
            {
                "rank": i + 1,
                "candidate_id": c.candidate_id,
                "candidate_name": c.candidate_name,
                "score": c.overall_average
            }
            for i, c in enumerate(by_score)
        ]

        # Sort by confidence
        by_confidence = sorted(
            candidates,
            key=lambda x: x.average_confidence,
            reverse=True
        )
        rankings["by_confidence"] = [
            {
                "rank": i + 1,
                "candidate_id": c.candidate_id,
                "candidate_name": c.candidate_name,
                "score": c.average_confidence
            }
            for i, c in enumerate(by_confidence)
        ]

        # Sort by evaluation count
        by_count = sorted(
            candidates,
            key=lambda x: x.total_evaluations,
            reverse=True
        )
        rankings["by_evaluation_count"] = [
            {
                "rank": i + 1,
                "candidate_id": c.candidate_id,
                "candidate_name": c.candidate_name,
                "score": c.total_evaluations
            }
            for i, c in enumerate(by_count)
        ]

        return rankings

    async def _get_aggregated_feedback(
        self,
        candidate_ids: List[str],
        evaluations: Dict[str, List[Feedback]]
    ) -> Dict[str, str]:
        """
        Get aggregated feedback summary.
        """
        all_strengths: List[str] = []
        all_weaknesses: List[str] = []
        all_summaries: List[str] = []

        for candidate_id in candidate_ids:
            candidate_feedbacks = evaluations.get(candidate_id, [])
            for fb in candidate_feedbacks:
                if fb.strengths:
                    all_strengths.append(fb.strengths)
                if fb.weaknesses:
                    all_weaknesses.append(fb.weaknesses)
                if fb.summary:
                    all_summaries.append(fb.summary)

        # Create simple summary
        summary_parts = []

        if all_strengths:
            summary_parts.append(f"Strengths identified in {len(all_strengths)} evaluations")

        if all_weaknesses:
            summary_parts.append(f"Areas for improvement noted in {len(all_weaknesses)} evaluations")

        if all_summaries:
            summary_parts.append(f"Overall feedback provided in {len(all_summaries)} evaluations")

        return {
            "overall": "; ".join(summary_parts) if summary_parts else "No feedback available",
            "strengths_count": str(len(all_strengths)),
            "weaknesses_count": str(len(all_weaknesses)),
            "summaries_count": str(len(all_summaries))
        }

