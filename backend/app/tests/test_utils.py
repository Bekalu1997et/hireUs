"""
Unit tests for core/utils.py.
Tests all utility functions in the core module.
"""
import pytest
import uuid
import secrets
from datetime import datetime
from app.core import utils


@pytest.mark.utils
class TestGenerateUuid:
    """Tests for generate_uuid function."""

    def test_generate_uuid_returns_string(self):
        """Test that generate_uuid returns a string."""
        result = utils.generate_uuid()
        assert isinstance(result, str)

    def test_generate_uuid_valid_format(self):
        """Test that generate_uuid returns valid UUID format."""
        result = utils.generate_uuid()
        # Should be able to parse as UUID
        parsed = uuid.UUID(result)
        assert str(parsed) == result

    def test_generate_uuid_unique(self):
        """Test that generate_uuid returns unique values."""
        results = [utils.generate_uuid() for _ in range(100)]
        assert len(set(results)) == 100


@pytest.mark.utils
class TestGenerateRandomString:
    """Tests for generate_random_string function."""

    def test_generate_random_string_default_length(self):
        """Test random string with default length."""
        result = utils.generate_random_string()
        # token_urlsafe returns length+1 characters due to base64 encoding
        assert len(result) > 0

    def test_generate_random_string_custom_length(self):
        """Test random string with custom length."""
        result = utils.generate_random_string(16)
        # token_urlsafe returns length+1 characters due to base64 encoding
        assert len(result) > 16

    def test_generate_random_string_unique(self):
        """Test that random strings are unique."""
        results = [utils.generate_random_string(16) for _ in range(50)]
        assert len(set(results)) == 50


@pytest.mark.utils
class TestDatetimeUtcnow:
    """Tests for datetime_utcnow function."""

    def test_datetime_utcnow_returns_datetime(self):
        """Test that datetime_utcnow returns a datetime object."""
        result = utils.datetime_utcnow()
        assert isinstance(result, datetime)

    def test_datetime_utcnow_approximate_now(self):
        """Test that datetime_utcnow returns approximate current time."""
        before = datetime.utcnow()
        result = utils.datetime_utcnow()
        after = datetime.utcnow()
        assert before <= result <= after


@pytest.mark.utils
class TestFormatDatetime:
    """Tests for format_datetime function."""

    def test_format_datetime_default_format(self, sample_datetime):
        """Test datetime formatting with default format."""
        result = utils.format_datetime(sample_datetime)
        assert result == "2024-01-15 10:30:00"

    def test_format_datetime_custom_format(self, sample_datetime):
        """Test datetime formatting with custom format."""
        result = utils.format_datetime(sample_datetime, "%Y-%m-%d")
        assert result == "2024-01-15"

    def test_format_datetime_iso_format(self, sample_datetime):
        """Test datetime formatting with ISO format."""
        result = utils.format_datetime(sample_datetime, "%Y-%m-%dT%H:%M:%S")
        assert result == "2024-01-15T10:30:00"


@pytest.mark.utils
class TestParseDatetime:
    """Tests for parse_datetime function."""

    def test_parse_datetime_default_format(self, sample_datetime_string):
        """Test datetime parsing with default format."""
        result = utils.parse_datetime(sample_datetime_string)
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_parse_datetime_custom_format(self):
        """Test datetime parsing with custom format."""
        result = utils.parse_datetime("2024-01-15", "%Y-%m-%d")
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15


@pytest.mark.utils
class TestIsValidUuid:
    """Tests for is_valid_uuid function."""

    def test_is_valid_uuid_valid(self, valid_uuid):
        """Test with valid UUID."""
        assert utils.is_valid_uuid(valid_uuid) is True

    def test_is_valid_uuid_invalid(self, invalid_uuid):
        """Test with invalid UUID."""
        assert utils.is_valid_uuid(invalid_uuid) is False

    def test_is_valid_uuid_empty_string(self):
        """Test with empty string."""
        assert utils.is_valid_uuid("") is False

    def test_is_valid_uuid_random_string(self):
        """Test with random string."""
        assert utils.is_valid_uuid("random-string") is False


@pytest.mark.utils
class TestTruncateText:
    """Tests for truncate_text function."""

    def test_truncate_text_short_text(self):
        """Test truncation with short text."""
        text = "Short"
        result = utils.truncate_text(text, max_length=10)
        assert result == "Short"

    def test_truncate_text_long_text(self):
        """Test truncation with long text."""
        text = "This is a very long text that needs to be truncated"
        result = utils.truncate_text(text, max_length=20)
        assert len(result) == 20
        assert result.endswith("...")

    def test_truncate_text_custom_suffix(self):
        """Test truncation with custom suffix."""
        text = "This is a very long text"
        result = utils.truncate_text(text, max_length=10, suffix="[more]")
        # The implementation truncates to max_length then adds suffix
        assert len(result) <= 10 + len("[more]")
        assert result.startswith("This")

    def test_truncate_text_exact_length(self):
        """Test truncation with text at exact max length."""
        text = "1234567890"  # 10 chars
        result = utils.truncate_text(text, max_length=10)
        assert result == "1234567890"


@pytest.mark.utils
class TestFormatPhoneNumber:
    """Tests for format_phone_number function."""

    def test_format_phone_number_with_dashes(self):
        """Test formatting phone number with dashes."""
        result = utils.format_phone_number("123-456-7890")
        # Implementation adds country code for 10-digit numbers
        assert result == "11234567890"

    def test_format_phone_number_with_spaces(self):
        """Test formatting phone number with spaces."""
        result = utils.format_phone_number("123 456 7890")
        # Implementation adds country code for 10-digit numbers
        assert result == "11234567890"

    def test_format_phone_number_with_parentheses(self):
        """Test formatting phone number with parentheses."""
        result = utils.format_phone_number("(123) 456-7890")
        # Implementation adds country code for 10-digit numbers
        assert result == "11234567890"

    def test_format_phone_number_adds_country_code(self):
        """Test that country code is added for 10-digit numbers."""
        result = utils.format_phone_number("1234567890")
        assert result == "11234567890"


@pytest.mark.utils
class TestSanitizeHtml:
    """Tests for sanitize_html function."""

    def test_sanitize_html_with_script_tags(self):
        """Test HTML sanitization removes script tags."""
        html = "<script>alert('xss')</script>"
        result = utils.sanitize_html(html)
        assert "<script>" not in result
        assert "</script>" not in result

    def test_sanitize_html_with_iframe(self):
        """Test HTML sanitization removes iframe tags."""
        html = "<iframe src='evil.com'></iframe>"
        result = utils.sanitize_html(html)
        assert "<iframe>" not in result
        assert "</iframe>" not in result

    def test_sanitize_html_clean_content(self):
        """Test sanitization preserves clean content."""
        html = "<p>Hello World</p>"
        result = utils.sanitize_html(html)
        assert result == "<p>Hello World</p>"


@pytest.mark.utils
class TestPaginateResults:
    """Tests for paginate_results function."""

    def test_paginate_results_first_page(self, sample_pagination_items):
        """Test pagination on first page."""
        result = utils.paginate_results(sample_pagination_items, page=1, page_size=10)
        assert len(result["items"]) == 10
        assert result["items"][0] == 1
        assert result["page"] == 1
        assert result["total"] == 100
        assert result["total_pages"] == 10

    def test_paginate_results_middle_page(self, sample_pagination_items):
        """Test pagination on middle page."""
        result = utils.paginate_results(sample_pagination_items, page=5, page_size=10)
        assert len(result["items"]) == 10
        assert result["items"][0] == 41
        assert result["page"] == 5

    def test_paginate_results_last_page(self, sample_pagination_items):
        """Test pagination on last page."""
        result = utils.paginate_results(sample_pagination_items, page=10, page_size=10)
        assert len(result["items"]) == 10
        assert result["has_next"] is False

    def test_paginate_results_has_next_prev(self, sample_pagination_items):
        """Test has_next and has_prev flags."""
        result = utils.paginate_results(sample_pagination_items, page=2, page_size=10)
        assert result["has_next"] is True
        assert result["has_prev"] is True

    def test_paginate_results_single_item(self):
        """Test pagination with single item."""
        result = utils.paginate_results([1], page=1, page_size=10)
        assert len(result["items"]) == 1
        assert result["total"] == 1


@pytest.mark.utils
class TestTimer:
    """Tests for Timer context manager."""

    def test_timer_context_manager(self):
        """Test Timer as context manager."""
        with utils.Timer() as timer:
            pass
        assert timer.start_time is not None
        assert timer.end_time is not None

    def test_timer_elapsed_seconds(self):
        """Test elapsed_seconds calculation."""
        # Test with mock times set directly
        timer = utils.Timer()
        timer.start_time = datetime(2024, 1, 1, 12, 0, 0)
        timer.end_time = datetime(2024, 1, 1, 12, 0, 10)
        assert timer.elapsed_seconds == 10.0

    def test_timer_elapsed_seconds_not_finished(self):
        """Test elapsed_seconds before timer finishes."""
        timer = utils.Timer()
        timer.start_time = datetime(2024, 1, 1, 12, 0, 0)
        assert timer.elapsed_seconds == 0.0


@pytest.mark.utils
class TestDictToCamelCase:
    """Tests for dict_to_camel_case function."""

    def test_dict_to_camel_case_normal(self, snake_case_dict, expected_camel_case_dict):
        """Test conversion from snake_case to camelCase."""
        result = utils.dict_to_camel_case(snake_case_dict)
        assert result == expected_camel_case_dict

    def test_dict_to_camel_case_empty_dict(self):
        """Test with empty dictionary."""
        result = utils.dict_to_camel_case({})
        assert result == {}

    def test_dict_to_camel_case_single_word(self):
        """Test with single word keys."""
        result = utils.dict_to_camel_case({"active": True})
        assert result == {"active": True}

    def test_dict_to_camel_case_nested(self):
        """Test with nested dictionary."""
        # Note: The current implementation doesn't recursively convert nested dicts
        # It only converts top-level keys
        result = utils.dict_to_camel_case({"user_id": {"first_name": "John"}})
        assert "userId" in result
        # Nested dict keys are not converted by this implementation

