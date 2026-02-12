"""
Tests for AI module.

Includes property tests and unit tests for LLM integration.
"""
import pytest
import json
import asyncio
from hypothesis import given, strategies as st
from unittest.mock import AsyncMock, patch, MagicMock
from openai import APIError, RateLimitError, APITimeoutError

from app.modules.ai.client import AIClient
from app.modules.ai.parser import (
    LLMParseError,
    extract_json_from_response,
    parse_json_safely,
    parse_interview_kit_response,
    parse_decision_brief_response
)
from app.modules.ai.validators import (
    LLMValidationError,
    validate_interview_kit,
    validate_decision_brief
)


# ============================================================================
# Property Tests
# ============================================================================

# Feature: structured-interview-platform, Property 28: LLM Response Parsing
@given(
    competency_ids=st.lists(st.integers(min_value=1, max_value=100), min_size=1, max_size=5, unique=True),
    question_texts=st.lists(st.text(min_size=10, max_size=200), min_size=1, max_size=10),
    rubrics=st.lists(st.text(min_size=10, max_size=200), min_size=1, max_size=10)
)
def test_property_llm_response_parsing_interview_kit(competency_ids, question_texts, rubrics):
    """
    Property 28: LLM Response Parsing
    
    For any valid LLM response structure, parsing the response should 
    successfully extract all required fields into structured data formats.
    
    Validates: Requirements 12.3
    """
    # Generate valid interview kit response
    questions = []
    for i, (comp_id, text, rubric) in enumerate(zip(competency_ids, question_texts, rubrics), 1):
        questions.append({
            "competency_id": comp_id,
            "question_text": text,
            "evaluation_rubric": rubric,
            "order": i
        })
    
    response_data = {"questions": questions}
    
    # Test with plain JSON
    response_json = json.dumps(response_data)
    parsed = parse_interview_kit_response(response_json)
    assert parsed == response_data
    assert len(parsed["questions"]) == len(questions)
    
    # Test with markdown code block
    response_markdown = f"```json\n{response_json}\n```"
    parsed = parse_interview_kit_response(response_markdown)
    assert parsed == response_data
    
    # Test with extra text
    response_with_text = f"Here's the interview kit:\n```json\n{response_json}\n```\nHope this helps!"
    parsed = parse_interview_kit_response(response_with_text)
    assert parsed == response_data


@given(
    summary=st.text(min_size=10, max_size=500),
    strengths=st.text(min_size=10, max_size=500),
    concerns=st.text(min_size=10, max_size=500),
    recommendation=st.text(min_size=10, max_size=500)
)
def test_property_llm_response_parsing_decision_brief(summary, strengths, concerns, recommendation):
    """
    Property 28: LLM Response Parsing
    
    For any valid decision brief structure, parsing should extract all fields.
    
    Validates: Requirements 12.3
    """
    response_data = {
        "summary": summary,
        "strengths": strengths,
        "concerns": concerns,
        "recommendation": recommendation
    }
    
    # Test with plain JSON
    response_json = json.dumps(response_data)
    parsed = parse_decision_brief_response(response_json)
    assert parsed == response_data
    
    # Test with markdown code block
    response_markdown = f"```json\n{response_json}\n```"
    parsed = parse_decision_brief_response(response_markdown)
    assert parsed == response_data


# ============================================================================
# Unit Tests - Parser
# ============================================================================

def test_extract_json_from_markdown():
    """Test JSON extraction from markdown code blocks."""
    json_data = '{"key": "value"}'
    
    # Plain JSON
    assert extract_json_from_response(json_data) == json_data
    
    # Markdown with json tag
    markdown = f"```json\n{json_data}\n```"
    assert extract_json_from_response(markdown) == json_data
    
    # Markdown without tag
    markdown = f"```\n{json_data}\n```"
    assert extract_json_from_response(markdown) == json_data
    
    # With surrounding text
    text = f"Here's the data:\n```json\n{json_data}\n```\nDone!"
    assert extract_json_from_response(text) == json_data


def test_parse_json_safely_valid():
    """Test safe JSON parsing with valid input."""
    json_str = '{"key": "value", "number": 42}'
    result = parse_json_safely(json_str)
    assert result == {"key": "value", "number": 42}


def test_parse_json_safely_invalid():
    """Test safe JSON parsing with invalid input."""
    with pytest.raises(LLMParseError, match="Failed to parse JSON"):
        parse_json_safely("{invalid json}")


def test_parse_interview_kit_missing_questions():
    """Test interview kit parsing with missing questions field."""
    response = '{"data": []}'
    with pytest.raises(LLMParseError, match="missing 'questions' field"):
        parse_interview_kit_response(response)


def test_parse_interview_kit_empty_questions():
    """Test interview kit parsing with empty questions list."""
    response = '{"questions": []}'
    with pytest.raises(LLMParseError, match="cannot be empty"):
        parse_interview_kit_response(response)


def test_parse_interview_kit_missing_field():
    """Test interview kit parsing with missing required field."""
    response = json.dumps({
        "questions": [
            {
                "competency_id": 1,
                "question_text": "What is your experience?",
                # Missing evaluation_rubric and order
            }
        ]
    })
    with pytest.raises(LLMParseError, match="missing required field"):
        parse_interview_kit_response(response)


def test_parse_interview_kit_invalid_types():
    """Test interview kit parsing with invalid field types."""
    # Invalid competency_id type
    response = json.dumps({
        "questions": [
            {
                "competency_id": "not_an_int",
                "question_text": "Question",
                "evaluation_rubric": "Rubric",
                "order": 1
            }
        ]
    })
    with pytest.raises(LLMParseError, match="must be an integer"):
        parse_interview_kit_response(response)


def test_parse_decision_brief_missing_field():
    """Test decision brief parsing with missing field."""
    response = json.dumps({
        "summary": "Good candidate",
        "strengths": "Strong technical skills"
        # Missing concerns and recommendation
    })
    with pytest.raises(LLMParseError, match="missing required field"):
        parse_decision_brief_response(response)


def test_parse_decision_brief_empty_field():
    """Test decision brief parsing with empty field."""
    response = json.dumps({
        "summary": "Good candidate",
        "strengths": "Strong technical skills",
        "concerns": "",  # Empty string
        "recommendation": "Hire"
    })
    with pytest.raises(LLMParseError, match="must be a non-empty string"):
        parse_decision_brief_response(response)


# ============================================================================
# Unit Tests - Validators
# ============================================================================

def test_validate_interview_kit_success():
    """Test interview kit validation with valid data."""
    kit_data = {
        "questions": [
            {"competency_id": 1, "question_text": "Q1", "evaluation_rubric": "R1", "order": 1},
            {"competency_id": 2, "question_text": "Q2", "evaluation_rubric": "R2", "order": 2}
        ]
    }
    competency_ids = {1, 2}
    
    # Should not raise
    validate_interview_kit(kit_data, competency_ids)


def test_validate_interview_kit_missing_competency():
    """Test interview kit validation with missing competency coverage."""
    kit_data = {
        "questions": [
            {"competency_id": 1, "question_text": "Q1", "evaluation_rubric": "R1", "order": 1}
        ]
    }
    competency_ids = {1, 2, 3}  # Missing questions for 2 and 3
    
    with pytest.raises(LLMValidationError, match="missing questions for competencies"):
        validate_interview_kit(kit_data, competency_ids)


def test_validate_interview_kit_invalid_competency():
    """Test interview kit validation with invalid competency reference."""
    kit_data = {
        "questions": [
            {"competency_id": 1, "question_text": "Q1", "evaluation_rubric": "R1", "order": 1},
            {"competency_id": 2, "question_text": "Q2", "evaluation_rubric": "R2", "order": 2},
            {"competency_id": 99, "question_text": "Q3", "evaluation_rubric": "R3", "order": 3}
        ]
    }
    competency_ids = {1, 2}  # 99 is invalid
    
    with pytest.raises(LLMValidationError, match="invalid competencies"):
        validate_interview_kit(kit_data, competency_ids)


def test_validate_interview_kit_duplicate_orders():
    """Test interview kit validation with duplicate orders."""
    kit_data = {
        "questions": [
            {"competency_id": 1, "question_text": "Q1", "evaluation_rubric": "R1", "order": 1},
            {"competency_id": 2, "question_text": "Q2", "evaluation_rubric": "R2", "order": 1}
        ]
    }
    competency_ids = {1, 2}
    
    with pytest.raises(LLMValidationError, match="orders must be unique"):
        validate_interview_kit(kit_data, competency_ids)


def test_validate_interview_kit_non_sequential_orders():
    """Test interview kit validation with non-sequential orders."""
    kit_data = {
        "questions": [
            {"competency_id": 1, "question_text": "Q1", "evaluation_rubric": "R1", "order": 1},
            {"competency_id": 2, "question_text": "Q2", "evaluation_rubric": "R2", "order": 3}
        ]
    }
    competency_ids = {1, 2}
    
    with pytest.raises(LLMValidationError, match="must be sequential"):
        validate_interview_kit(kit_data, competency_ids)


def test_validate_decision_brief_success():
    """Test decision brief validation with valid data."""
    brief_data = {
        "summary": "Strong candidate with good technical skills",
        "strengths": "Excellent problem solving",
        "concerns": "Limited experience with distributed systems",
        "recommendation": "I recommend hiring this candidate"
    }
    
    # Should not raise
    validate_decision_brief(brief_data)


def test_validate_decision_brief_too_long():
    """Test decision brief validation with summary too long."""
    brief_data = {
        "summary": "x" * 1001,  # Too long
        "strengths": "Good",
        "concerns": "None",
        "recommendation": "Hire"
    }
    
    with pytest.raises(LLMValidationError, match="less than 1000 characters"):
        validate_decision_brief(brief_data)


def test_validate_decision_brief_no_actionable_language():
    """Test decision brief validation without actionable recommendation."""
    brief_data = {
        "summary": "Candidate performed well",
        "strengths": "Good technical skills",
        "concerns": "Some gaps",
        "recommendation": "The candidate did okay"  # No actionable language
    }
    
    with pytest.raises(LLMValidationError, match="actionable guidance"):
        validate_decision_brief(brief_data)


# ============================================================================
# Unit Tests - Client Error Handling
# ============================================================================

@pytest.mark.asyncio
async def test_client_retry_on_rate_limit():
    """
    Test retry logic on rate limit errors.
    
    Validates: Requirements 4.5, 8.5, 12.5
    """
    client = AIClient(api_key="test-key")
    
    # Mock the OpenAI client to raise RateLimitError twice, then succeed
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"questions": []}'
    
    # Create a proper mock request object
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_http_response = MagicMock()
    mock_http_response.request = mock_request
    
    call_count = 0
    async def mock_create(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count <= 2:
            raise RateLimitError("Rate limit exceeded", response=mock_http_response, body=None)
        return mock_response
    
    with patch.object(client.client.chat.completions, 'create', side_effect=mock_create):
        result = await client._call_with_retry([{"role": "user", "content": "test"}])
        assert result == '{"questions": []}'
        assert call_count == 3  # Failed twice, succeeded on third


@pytest.mark.asyncio
async def test_client_retry_on_timeout():
    """
    Test retry logic on timeout errors.
    
    Validates: Requirements 4.5, 8.5, 12.5
    """
    client = AIClient(api_key="test-key")
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"questions": []}'
    
    call_count = 0
    async def mock_create(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise APITimeoutError("Request timed out")
        return mock_response
    
    with patch.object(client.client.chat.completions, 'create', side_effect=mock_create):
        result = await client._call_with_retry([{"role": "user", "content": "test"}])
        assert result == '{"questions": []}'
        assert call_count == 2  # Failed once, succeeded on second


@pytest.mark.asyncio
async def test_client_retry_on_asyncio_timeout():
    """
    Test retry logic when asyncio.wait_for raises TimeoutError.
    """
    client = AIClient(api_key="test-key")
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"questions": []}'
    
    call_count = 0
    
    async def mock_wait_for(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count <= 2:
            raise asyncio.TimeoutError()
        return mock_response
    
    with patch("app.modules.ai.client.asyncio.wait_for", side_effect=mock_wait_for):
        result = await client._call_with_retry([{"role": "user", "content": "test"}])
        assert result == '{"questions": []}'
        assert call_count == 3  # Failed twice, succeeded on third


@pytest.mark.asyncio
async def test_client_max_retries_exceeded():
    """
    Test that client raises error after max retries.
    
    Validates: Requirements 4.5, 8.5, 12.5
    """
    client = AIClient(api_key="test-key")
    
    # Create a proper mock request object
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_http_response = MagicMock()
    mock_http_response.request = mock_request
    
    async def mock_create(*args, **kwargs):
        raise RateLimitError("Rate limit exceeded", response=mock_http_response, body=None)
    
    with patch.object(client.client.chat.completions, 'create', side_effect=mock_create):
        with pytest.raises(RateLimitError):
            await client._call_with_retry([{"role": "user", "content": "test"}])


@pytest.mark.asyncio
async def test_client_timeout_enforcement():
    """
    Test that client enforces 30-second timeout.
    
    Validates: Requirements 4.5, 8.5, 12.5
    """
    client = AIClient(api_key="test-key")

    call_count = 0

    async def mock_wait_for(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        raise asyncio.TimeoutError()

    with patch("app.modules.ai.client.asyncio.wait_for", side_effect=mock_wait_for):
        with pytest.raises(asyncio.TimeoutError):
            await client._call_with_retry([{"role": "user", "content": "test"}])

    assert call_count == client.max_retries


@pytest.mark.asyncio
async def test_generate_interview_kit_integration():
    """Test interview kit generation end-to-end."""
    client = AIClient(api_key="test-key")
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "questions": [
            {
                "competency_id": 1,
                "question_text": "Describe your experience with Python",
                "evaluation_rubric": "1-2: Basic knowledge, 3-4: Intermediate, 5: Expert",
                "order": 1
            }
        ]
    })
    
    async def mock_create(*args, **kwargs):
        return mock_response
    
    with patch.object(client.client.chat.completions, 'create', side_effect=mock_create):
        result = await client.generate_interview_kit(
            role_title="Senior Backend Engineer",
            role_description="Build scalable APIs",
            seniority_level="senior",
            competencies=[
                {"id": 1, "name": "Python", "description": "Python programming", "weight": 1.0}
            ]
        )
        
        # Should return raw JSON string
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert "questions" in parsed


@pytest.mark.asyncio
async def test_generate_decision_brief_integration():
    """Test decision brief generation end-to-end."""
    client = AIClient(api_key="test-key")
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "summary": "Strong candidate",
        "strengths": "Excellent technical skills",
        "concerns": "Limited leadership experience",
        "recommendation": "Recommend hiring"
    })
    
    async def mock_create(*args, **kwargs):
        return mock_response
    
    with patch.object(client.client.chat.completions, 'create', side_effect=mock_create):
        result = await client.generate_decision_brief(
            candidate_name="John Doe",
            role_title="Senior Backend Engineer",
            role_description="Build scalable APIs",
            competencies=[],
            evaluations=[],
            aggregated_scores={}
        )
        
        # Should return raw JSON string
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert "summary" in parsed
        assert "recommendation" in parsed
