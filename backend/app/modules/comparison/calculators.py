"""
Statistical calculators for Candidate Comparison.
Provides mathematical operations for comparing candidate scores.
"""
import statistics
from typing import List, Dict, Optional, Any
from collections import defaultdict


class ComparisonCalculators:
    """
    Collection of statistical calculators for candidate comparison.
    """

    @staticmethod
    def calculate_average(scores: List[float]) -> float:
        """
        Calculate the arithmetic mean of a list of scores.
        
        Args:
            scores: List of numeric scores
            
        Returns:
            Average score (rounded to 2 decimal places)
        """
        if not scores:
            return 0.0
        return round(sum(scores) / len(scores), 2)

    @staticmethod
    def calculate_standard_deviation(scores: List[float]) -> Optional[float]:
        """
        Calculate the standard deviation of a list of scores.
        
        Args:
            scores: List of numeric scores
            
        Returns:
            Standard deviation (rounded to 2 decimal places) or None if insufficient data
        """
        if len(scores) < 2:
            return None
        try:
            return round(statistics.stdev(scores), 2)
        except statistics.StatisticsError:
            return None

    @staticmethod
    def calculate_variance(scores: List[float]) -> Optional[float]:
        """
        Calculate the variance of a list of scores.
        
        Args:
            scores: List of numeric scores
            
        Returns:
            Variance (rounded to 2 decimal places) or None if insufficient data
        """
        if len(scores) < 2:
            return None
        try:
            return round(statistics.variance(scores), 2)
        except statistics.StatisticsError:
            return None

    @staticmethod
    def calculate_min_max(scores: List[float]) -> Dict[str, float]:
        """
        Calculate minimum and maximum values.
        
        Args:
            scores: List of numeric scores
            
        Returns:
            Dictionary with 'min' and 'max' keys
        """
        if not scores:
            return {"min": 0.0, "max": 0.0}
        return {
            "min": min(scores),
            "max": max(scores)
        }

    @staticmethod
    def calculate_percentile(scores: List[float], percentile: float) -> Optional[float]:
        """
        Calculate the specified percentile of scores.
        
        Args:
            scores: List of numeric scores
            percentile: Percentile to calculate (0-100)
            
        Returns:
            Percentile value or None if insufficient data
        """
        if len(scores) < 2:
            return None
        try:
            return round(statistics.quantiles(scores, n=100)[int(percentile)], 2)
        except (statistics.StatisticsError, IndexError):
            return None

    @staticmethod
    def calculate_median(scores: List[float]) -> Optional[float]:
        """
        Calculate the median of a list of scores.
        
        Args:
            scores: List of numeric scores
            
        Returns:
            Median value or None if insufficient data
        """
        if not scores:
            return None
        try:
            return round(statistics.median(scores), 2)
        except statistics.StatisticsError:
            return None

    @staticmethod
    def calculate_mode(scores: List[float]) -> Optional[Any]:
        """
        Calculate the mode of a list of scores.
        
        Args:
            scores: List of numeric scores
            
        Returns:
            Mode value or None if insufficient data
        """
        if not scores:
            return None
        try:
            return statistics.mode(scores)
        except statistics.StatisticsError:
            return None

    @staticmethod
    def calculate_confidence_score(
        confidence_values: List[int],
        evaluation_count: int
    ) -> Dict[str, Any]:
        """
        Calculate confidence metrics for candidate evaluations.
        
        Args:
            confidence_values: List of confidence scores (1-5)
            evaluation_count: Number of evaluations
            
        Returns:
            Dictionary with confidence metrics
        """
        if not confidence_values:
            return {
                "average": 0.0,
                "variance": None,
                "is_reliable": False,
                "reliability_message": "No evaluations available"
            }

        avg_confidence = ComparisonCalculators.calculate_average(confidence_values)
        variance = ComparisonCalculators.calculate_variance(confidence_values)

        # Determine reliability based on variance and count
        is_reliable = True
        reliability_message = "Confidence is reliable"

        if evaluation_count < 2:
            is_reliable = False
            reliability_message = "Need more evaluations for reliable confidence"
        elif variance and variance > 1.5:
            is_reliable = False
            reliability_message = "High variance in interviewer confidence"
        elif avg_confidence < 3.0:
            is_reliable = False
            reliability_message = "Low average confidence"

        return {
            "average": avg_confidence,
            "variance": variance,
            "is_reliable": is_reliable,
            "reliability_message": reliability_message,
            "min": min(confidence_values),
            "max": max(confidence_values)
        }

    @staticmethod
    def calculate_overall_score(
        competency_scores: Dict[str, List[float]]
    ) -> Dict[str, Any]:
        """
        Calculate overall score metrics from competency scores.
        
        Args:
            competency_scores: Dict of competency name to list of scores
            
        Returns:
            Dictionary with overall score metrics
        """
        if not competency_scores:
            return {
                "overall_average": 0.0,
                "total_competencies": 0,
                "strongest_competency": None,
                "weakest_competency": None,
                "score_distribution": {}
            }

        # Calculate average for each competency
        competency_averages = {}
        for comp, scores in competency_scores.items():
            avg = ComparisonCalculators.calculate_average(scores)
            competency_averages[comp] = avg

        # Calculate overall average
        all_scores = []
        for scores in competency_scores.values():
            all_scores.extend(scores)
        overall_average = ComparisonCalculators.calculate_average(all_scores)

        # Find strongest and weakest competencies
        sorted_comps = sorted(
            competency_averages.items(),
            key=lambda x: x[1],
            reverse=True
        )

        strongest = sorted_comps[0][0] if sorted_comps else None
        weakest = sorted_comps[-1][0] if sorted_comps else None

        # Score distribution
        distribution = {
            "excellent": sum(1 for s in all_scores if s >= 4.5),
            "good": sum(1 for s in all_scores if 3.5 <= s < 4.5),
            "average": sum(1 for s in all_scores if 2.5 <= s < 3.5),
            "below_average": sum(1 for s in all_scores if 1.5 <= s < 2.5),
            "poor": sum(1 for s in all_scores if s < 1.5)
        }

        return {
            "overall_average": overall_average,
            "total_competencies": len(competency_scores),
            "strongest_competency": strongest,
            "weakest_competency": weakest,
            "strongest_score": competency_averages.get(strongest) if strongest else None,
            "weakest_score": competency_averages.get(weakest) if weakest else None,
            "score_distribution": distribution
        }

    @staticmethod
    def calculate_recommendation_score(
        recommendation_counts: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Calculate recommendation metrics.
        
        Args:
            recommendation_counts: Dict of recommendation type to count
            
        Returns:
            Dictionary with recommendation metrics
        """
        if not recommendation_counts:
            return {
                "dominant_recommendation": None,
                "hire_score": 0.0,
                "total_recommendations": 0
            }

        total = sum(recommendation_counts.values())

        # Calculate hire score (-1 to 1 scale)
        hire_score = 0.0
        weights = {
            "strong_hire": 1.0,
            "hire": 0.5,
            "neutral": 0.0,
            "no_hire": -0.5,
            "strong_no_hire": -1.0
        }

        for rec, count in recommendation_counts.items():
            weight = weights.get(rec, 0.0)
            hire_score += weight * count

        if total > 0:
            hire_score = round(hire_score / total, 2)

        # Find dominant recommendation
        dominant = max(recommendation_counts.items(), key=lambda x: x[1])
        dominant_rec = dominant[0] if dominant else None

        return {
            "dominant_recommendation": dominant_rec,
            "hire_score": hire_score,
            "total_recommendations": total,
            "recommendation_breakdown": recommendation_counts
        }

    @staticmethod
    def calculate_ranking_score(
        overall_average: float,
        confidence_score: float,
        hire_score: float,
        evaluation_count: int,
        weights: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Calculate a composite ranking score.
        
        Args:
            overall_average: Candidate's overall average score
            confidence_score: Average confidence of evaluators
            hire_score: Recommendation hire score (-1 to 1)
            evaluation_count: Number of evaluations
            weights: Optional custom weights for each factor
            
        Returns:
            Composite ranking score (0-100 scale)
        """
        if weights is None:
            weights = {
                "overall": 0.4,
                "confidence": 0.3,
                "hire": 0.2,
                "count": 0.1
            }

        # Normalize scores to 0-1 scale where applicable
        normalized_overall = (overall_average - 1) / 4  # 1-5 to 0-1
        normalized_confidence = (confidence_score - 1) / 4  # 1-5 to 0-1
        normalized_hire = (hire_score + 1) / 2  # -1 to 1 to 0-1
        normalized_count = min(evaluation_count / 10, 1.0)  # Cap at 10 evaluations

        # Calculate weighted score
        score = (
            weights.get("overall", 0.4) * normalized_overall +
            weights.get("confidence", 0.3) * normalized_confidence +
            weights.get("hire", 0.2) * normalized_hire +
            weights.get("count", 0.1) * normalized_count
        )

        return round(score * 100, 2)  # Convert to 0-100 scale

    @staticmethod
    def detect_signal_gaps(
        competency_scores: Dict[str, float],
        confidence_scores: List[float],
        evaluation_count: int,
        competency_threshold: float = 3.0,
        confidence_threshold: float = 3.0,
        variance_threshold: float = 1.0
    ) -> List[Dict[str, Any]]:
        """
        Detect signal gaps in candidate evaluation.
        
        Args:
            competency_scores: Dict of competency to average score
            confidence_scores: List of confidence scores
            evaluation_count: Number of evaluations
            competency_threshold: Minimum acceptable competency score
            confidence_threshold: Minimum acceptable confidence
            variance_threshold: Maximum acceptable variance
            
        Returns:
            List of signal gaps with details
        """
        gaps = []

        # Check for low competency scores
        for comp, score in competency_scores.items():
            if score < competency_threshold:
                severity = "high" if score < 2.0 else "medium" if score < 2.5 else "low"
                gaps.append({
                    "competency": comp,
                    "type": "low_score",
                    "severity": severity,
                    "description": f"Low score in {comp}: {score}/5",
                    "recommendation": f"Consider additional interview focused on {comp}"
                })

        # Check for low confidence
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            if avg_confidence < confidence_threshold:
                severity = "high" if avg_confidence < 2.0 else "medium" if avg_confidence < 2.5 else "low"
                gaps.append({
                    "competency": "overall",
                    "type": "low_confidence",
                    "severity": severity,
                    "description": f"Low interviewer confidence: {avg_confidence:.1f}/5",
                    "recommendation": "Consider gathering more evaluations or second opinions"
                })

        # Check for insufficient evaluations
        if evaluation_count < 2:
            gaps.append({
                "competency": "overall",
                "type": "insufficient_data",
                "severity": "high",
                "description": f"Only {evaluation_count} evaluation(s)",
                "recommendation": "Need at least 2 evaluations for reliable assessment"
            })

        return gaps

    @staticmethod
    def generate_heatmap_data(
        candidate_scores: Dict[str, Dict[str, float]]
    ) -> Dict[str, Any]:
        """
        Generate heatmap data for visualization.
        
        Args:
            candidate_scores: Dict of candidate_id to competency_scores
            
        Returns:
            Dictionary with heatmap data for visualization
        """
        if not candidate_scores:
            return {
                "competencies": [],
                "candidates": [],
                "data": []
            }

        # Get all competencies
        all_competencies = set()
        for scores in candidate_scores.values():
            all_competencies.update(scores.keys())

        competencies = sorted(all_competencies)
        candidates = list(candidate_scores.keys())

        # Build heatmap matrix
        data = []
        for comp in competencies:
            row = {
                "competency": comp,
                "scores": {}
            }
            for candidate_id in candidates:
                score = candidate_scores[candidate_id].get(comp, 0)
                row["scores"][candidate_id] = score
            data.append(row)

        # Calculate column averages (per candidate)
        candidate_averages = {}
        for candidate_id in candidates:
            scores = candidate_scores[candidate_id].values()
            if scores:
                avg = sum(scores) / len(scores)
                candidate_averages[candidate_id] = round(avg, 2)

        return {
            "competencies": competencies,
            "candidates": candidates,
            "data": data,
            "candidate_averages": candidate_averages
        }

    @staticmethod
    def rank_candidates(
        candidate_metrics: Dict[str, Dict[str, Any]],
        criteria: str = "overall_score"
    ) -> List[Dict[str, Any]]:
        """
        Rank candidates based on specified criteria.
        
        Args:
            candidate_metrics: Dict of candidate_id to metrics dict
            criteria: Ranking criteria (overall_score, confidence, recommendation)
            
        Returns:
            List of candidates with rank information
        """
        ranked = []

        for candidate_id, metrics in candidate_metrics.items():
            if criteria == "overall_score":
                score = metrics.get("overall_average", 0)
            elif criteria == "confidence":
                score = metrics.get("confidence_average", 0)
            elif criteria == "recommendation":
                score = metrics.get("hire_score", 0)
            else:
                score = metrics.get("overall_average", 0)

            ranked.append({
                "candidate_id": candidate_id,
                "candidate_name": metrics.get("candidate_name", "Unknown"),
                "score": score,
                "metrics": metrics
            })

        # Sort by score (descending)
        ranked.sort(key=lambda x: x["score"], reverse=True)

        # Add ranks
        for i, candidate in enumerate(ranked):
            candidate["rank"] = i + 1

        return ranked

    @staticmethod
    def calculate_agreement_level(
        evaluation_scores: Dict[str, Dict[str, float]]
    ) -> Dict[str, Any]:
        """
        Calculate how much evaluators agree on scores.
        
        Args:
            evaluation_scores: Dict of competency to scores from different evaluators
            
        Returns:
            Dictionary with agreement metrics
        """
        if not evaluation_scores:
            return {
                "overall_variance": None,
                "agreement_level": "unknown",
                "per_competency": {}
            }

        # Calculate variance per competency
        per_competency = {}
        all_variances = []

        for competency, scores in evaluation_scores.items():
            variance = ComparisonCalculators.calculate_variance(list(scores.values()))
            if variance is not None:
                per_competency[competency] = {
                    "variance": variance,
                    "evaluator_count": len(scores),
                    "scores": scores
                }
                all_variances.append(variance)

        # Calculate overall variance
        overall_variance = (
            sum(all_variances) / len(all_variances)
            if all_variances else None
        )

        # Determine agreement level
        if overall_variance is None:
            agreement = "unknown"
        elif overall_variance < 0.3:
            agreement = "high"
        elif overall_variance < 0.7:
            agreement = "moderate"
        else:
            agreement = "low"

        return {
            "overall_variance": overall_variance,
            "agreement_level": agreement,
            "per_competency": per_competency
        }

