"""
Unit tests for ComparisonCalculators.
Tests all statistical calculation methods in the comparison module.
"""
import pytest
from app.modules.comparison.calculators import ComparisonCalculators


@pytest.mark.calculations
class TestCalculateAverage:
    """Tests for calculate_average method."""

    def test_calculate_average_normal_scores(self):
        """Test average calculation with normal scores."""
        scores = [4.0, 3.5, 4.5, 3.0, 5.0]
        result = ComparisonCalculators.calculate_average(scores)
        assert result == 4.0  # (4.0 + 3.5 + 4.5 + 3.0 + 5.0) / 5 = 4.0

    def test_calculate_average_single_score(self):
        """Test average with a single score."""
        scores = [5.0]
        result = ComparisonCalculators.calculate_average(scores)
        assert result == 5.0

    def test_calculate_average_empty_list(self):
        """Test average with empty list returns 0."""
        scores = []
        result = ComparisonCalculators.calculate_average(scores)
        assert result == 0.0

    def test_calculate_average_decimal_scores(self):
        """Test average with decimal scores."""
        scores = [1.5, 2.5, 3.5]
        result = ComparisonCalculators.calculate_average(scores)
        assert result == 2.5

    def test_calculate_average_rounding(self):
        """Test average rounding to 2 decimal places."""
        scores = [1.0, 2.0, 3.0]
        result = ComparisonCalculators.calculate_average(scores)
        assert result == 2.0


@pytest.mark.calculations
class TestCalculateStandardDeviation:
    """Tests for calculate_standard_deviation method."""

    def test_calculate_std_dev_normal(self):
        """Test standard deviation with normal distribution."""
        scores = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
        result = ComparisonCalculators.calculate_standard_deviation(scores)
        assert result is not None
        assert result > 0

    def test_calculate_std_dev_single_value(self):
        """Test standard deviation with single value returns None."""
        scores = [5.0]
        result = ComparisonCalculators.calculate_standard_deviation(scores)
        assert result is None

    def test_calculate_std_dev_empty_list(self):
        """Test standard deviation with empty list returns None."""
        scores = []
        result = ComparisonCalculators.calculate_standard_deviation(scores)
        assert result is None

    def test_calculate_std_dev_identical_values(self):
        """Test standard deviation with identical values."""
        scores = [5.0, 5.0, 5.0, 5.0]
        result = ComparisonCalculators.calculate_standard_deviation(scores)
        assert result == 0.0


@pytest.mark.calculations
class TestCalculateVariance:
    """Tests for calculate_variance method."""

    def test_calculate_variance_normal(self):
        """Test variance calculation."""
        scores = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
        result = ComparisonCalculators.calculate_variance(scores)
        assert result is not None
        assert result > 0

    def test_calculate_variance_single_value(self):
        """Test variance with single value returns None."""
        scores = [5.0]
        result = ComparisonCalculators.calculate_variance(scores)
        assert result is None


@pytest.mark.calculations
class TestCalculateMinMax:
    """Tests for calculate_min_max method."""

    def test_calculate_min_max_normal(self):
        """Test min/max with normal scores."""
        scores = [3.0, 1.0, 5.0, 2.0, 4.0]
        result = ComparisonCalculators.calculate_min_max(scores)
        assert result == {"min": 1.0, "max": 5.0}

    def test_calculate_min_max_single_value(self):
        """Test min/max with single value."""
        scores = [5.0]
        result = ComparisonCalculators.calculate_min_max(scores)
        assert result == {"min": 5.0, "max": 5.0}

    def test_calculate_min_max_empty_list(self):
        """Test min/max with empty list."""
        scores = []
        result = ComparisonCalculators.calculate_min_max(scores)
        assert result == {"min": 0.0, "max": 0.0}


@pytest.mark.calculations
class TestCalculatePercentile:
    """Tests for calculate_percentile method."""

    def test_calculate_percentile_50(self):
        """Test 50th percentile (median)."""
        scores = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = ComparisonCalculators.calculate_percentile(scores, 50)
        assert result is not None

    def test_calculate_percentile_25(self):
        """Test 25th percentile."""
        scores = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = ComparisonCalculators.calculate_percentile(scores, 25)
        assert result is not None

    def test_calculate_percentile_single_value(self):
        """Test percentile with single value returns None."""
        scores = [5.0]
        result = ComparisonCalculators.calculate_percentile(scores, 50)
        assert result is None


@pytest.mark.calculations
class TestCalculateMedian:
    """Tests for calculate_median method."""

    def test_calculate_median_odd_count(self):
        """Test median with odd number of elements."""
        scores = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = ComparisonCalculators.calculate_median(scores)
        assert result == 3.0

    def test_calculate_median_even_count(self):
        """Test median with even number of elements."""
        scores = [1.0, 2.0, 3.0, 4.0]
        result = ComparisonCalculators.calculate_median(scores)
        assert result == 2.5

    def test_calculate_median_empty_list(self):
        """Test median with empty list returns None."""
        scores = []
        result = ComparisonCalculators.calculate_median(scores)
        assert result is None


@pytest.mark.calculations
class TestCalculateMode:
    """Tests for calculate_mode method."""

    def test_calculate_mode_single_mode(self):
        """Test mode with single mode."""
        scores = [1.0, 2.0, 2.0, 3.0, 4.0]
        result = ComparisonCalculators.calculate_mode(scores)
        assert result == 2.0

    def test_calculate_mode_empty_list(self):
        """Test mode with empty list returns None."""
        scores = []
        result = ComparisonCalculators.calculate_mode(scores)
        assert result is None


@pytest.mark.calculations
class TestCalculateConfidenceScore:
    """Tests for calculate_confidence_score method."""

    def test_calculate_confidence_normal(self):
        """Test confidence score with normal data."""
        confidence_values = [4, 4, 5, 4, 3]
        result = ComparisonCalculators.calculate_confidence_score(
            confidence_values, 5
        )
        assert "average" in result
        assert "variance" in result
        assert "is_reliable" in result

    def test_calculate_confidence_empty(self):
        """Test confidence score with empty data."""
        result = ComparisonCalculators.calculate_confidence_score([], 0)
        assert result["average"] == 0.0
        assert result["is_reliable"] is False

    def test_calculate_confidence_single_evaluation(self):
        """Test confidence score with single evaluation."""
        confidence_values = [4]
        result = ComparisonCalculators.calculate_confidence_score(
            confidence_values, 1
        )
        assert result["is_reliable"] is False


@pytest.mark.calculations
class TestCalculateOverallScore:
    """Tests for calculate_overall_score method."""

    def test_calculate_overall_normal(self, sample_competency_scores):
        """Test overall score with normal data."""
        result = ComparisonCalculators.calculate_overall_score(
            sample_competency_scores
        )
        assert "overall_average" in result
        assert "total_competencies" in result
        assert result["total_competencies"] == 4

    def test_calculate_overall_empty(self):
        """Test overall score with empty data."""
        result = ComparisonCalculators.calculate_overall_score({})
        assert result["overall_average"] == 0.0
        assert result["total_competencies"] == 0


@pytest.mark.calculations
class TestCalculateRecommendationScore:
    """Tests for calculate_recommendation_score method."""

    def test_calculate_recommendation_normal(
        self, sample_recommendation_counts
    ):
        """Test recommendation score with normal data."""
        result = ComparisonCalculators.calculate_recommendation_score(
            sample_recommendation_counts
        )
        assert "dominant_recommendation" in result
        assert "hire_score" in result

    def test_calculate_recommendation_empty(self):
        """Test recommendation score with empty data."""
        result = ComparisonCalculators.calculate_recommendation_score({})
        assert result["hire_score"] == 0.0


@pytest.mark.calculations
class TestCalculateRankingScore:
    """Tests for calculate_ranking_score method."""

    def test_calculate_ranking_normal(self):
        """Test ranking score with normal values."""
        result = ComparisonCalculators.calculate_ranking_score(
            overall_average=4.0,
            confidence_score=4.0,
            hire_score=0.7,
            evaluation_count=5
        )
        assert 0 <= result <= 100

    def test_calculate_ranking_low_scores(self):
        """Test ranking score with low values."""
        result = ComparisonCalculators.calculate_ranking_score(
            overall_average=1.0,
            confidence_score=1.0,
            hire_score=-1.0,
            evaluation_count=1
        )
        assert 0 <= result <= 100


@pytest.mark.calculations
class TestDetectSignalGaps:
    """Tests for detect_signal_gaps method."""

    def test_detect_signal_gaps_low_scores(self):
        """Test signal gaps detection with low competency scores."""
        competency_scores = {
            "Python": 1.5,
            "JavaScript": 4.0,
        }
        result = ComparisonCalculators.detect_signal_gaps(
            competency_scores=competency_scores,
            confidence_scores=[4.0, 4.5, 4.0],
            evaluation_count=3
        )
        assert len(result) > 0
        assert any(g["type"] == "low_score" for g in result)

    def test_detect_signal_gaps_insufficient_data(self):
        """Test signal gaps detection with insufficient evaluations."""
        result = ComparisonCalculators.detect_signal_gaps(
            competency_scores={"Python": 4.0},
            confidence_scores=[],
            evaluation_count=1
        )
        assert any(g["type"] == "insufficient_data" for g in result)


@pytest.mark.calculations
class TestGenerateHeatmapData:
    """Tests for generate_heatmap_data method."""

    def test_generate_heatmap_normal(self, sample_candidate_scores):
        """Test heatmap generation with normal data."""
        result = ComparisonCalculators.generate_heatmap_data(
            sample_candidate_scores
        )
        assert "competencies" in result
        assert "candidates" in result
        assert "data" in result
        assert len(result["candidates"]) == 3

    def test_generate_heatmap_empty(self):
        """Test heatmap generation with empty data."""
        result = ComparisonCalculators.generate_heatmap_data({})
        assert result["competencies"] == []


@pytest.mark.calculations
class TestRankCandidates:
    """Tests for rank_candidates method."""

    def test_rank_candidates_overall_score(self, sample_candidate_metrics):
        """Test ranking by overall score."""
        result = ComparisonCalculators.rank_candidates(
            sample_candidate_metrics, criteria="overall_score"
        )
        assert len(result) == 3
        assert result[0]["rank"] == 1
        assert result[0]["candidate_name"] == "Bob Johnson"  # highest score

    def test_rank_candidates_by_confidence(self, sample_candidate_metrics):
        """Test ranking by confidence."""
        result = ComparisonCalculators.rank_candidates(
            sample_candidate_metrics, criteria="confidence"
        )
        assert len(result) == 3


@pytest.mark.calculations
class TestCalculateAgreementLevel:
    """Tests for calculate_agreement_level method."""

    def test_calculate_agreement_normal(self, sample_evaluation_scores):
        """Test agreement level with normal data."""
        result = ComparisonCalculators.calculate_agreement_level(
            sample_evaluation_scores
        )
        assert "overall_variance" in result
        assert "agreement_level" in result
        assert result["agreement_level"] in ["high", "moderate", "low", "unknown"]

    def test_calculate_agreement_empty(self):
        """Test agreement level with empty data."""
        result = ComparisonCalculators.calculate_agreement_level({})
        assert result["agreement_level"] == "unknown"

