"""
AI Response Parser Module

Parses and validates LLM JSON responses.
"""
import json
import re
from typing import Dict, Any, List


class LLMParseError(Exception):
    """Exception raised when LLM response cannot be parsed."""
    pass


def extract_json_from_response(response: str) -> str:
    """
    Extract JSON from LLM response, handling markdown code blocks.
    
    Args:
        response: Raw response string from LLM
        
    Returns:
        Clean JSON string
        
    Raises:
        LLMParseError: If JSON cannot be extracted
    """
    # Try to extract JSON from markdown code blocks
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
    if json_match:
        return json_match.group(1)
    
    # Try to find JSON object directly
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    if json_match:
        return json_match.group(0)
    
    # If no JSON found, assume entire response is JSON
    return response.strip()


def parse_json_safely(json_str: str) -> Dict[str, Any]:
    """
    Parse JSON string with error handling.
    
    Args:
        json_str: JSON string to parse
        
    Returns:
        Parsed JSON as dict
        
    Raises:
        LLMParseError: If JSON is malformed
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise LLMParseError(f"Failed to parse JSON: {str(e)}")


def parse_interview_kit_response(response: str) -> Dict[str, Any]:
    """
    Parse interview kit generation response.
    
    Expected structure:
    {
        "questions": [
            {
                "competency_id": int,
                "question_text": str,
                "evaluation_rubric": str,
                "order": int
            }
        ]
    }
    
    Args:
        response: Raw LLM response string
        
    Returns:
        Parsed interview kit data
        
    Raises:
        LLMParseError: If response is malformed or missing required fields
    """
    # Extract and parse JSON
    json_str = extract_json_from_response(response)
    data = parse_json_safely(json_str)
    
    # Validate structure
    if "questions" not in data:
        raise LLMParseError("Response missing 'questions' field")
    
    if not isinstance(data["questions"], list):
        raise LLMParseError("'questions' field must be a list")
    
    if len(data["questions"]) == 0:
        raise LLMParseError("'questions' list cannot be empty")
    
    # Validate each question
    for i, question in enumerate(data["questions"]):
        if not isinstance(question, dict):
            raise LLMParseError(f"Question {i} must be a dict")
        
        required_fields = ["competency_id", "question_text", "evaluation_rubric", "order"]
        for field in required_fields:
            if field not in question:
                raise LLMParseError(f"Question {i} missing required field: {field}")
        
        # Validate types
        if not isinstance(question["competency_id"], int):
            raise LLMParseError(f"Question {i} competency_id must be an integer")
        
        if not isinstance(question["question_text"], str) or not question["question_text"].strip():
            raise LLMParseError(f"Question {i} question_text must be a non-empty string")
        
        if not isinstance(question["evaluation_rubric"], str) or not question["evaluation_rubric"].strip():
            raise LLMParseError(f"Question {i} evaluation_rubric must be a non-empty string")
        
        if not isinstance(question["order"], int):
            raise LLMParseError(f"Question {i} order must be an integer")
    
    return data


def parse_decision_brief_response(response: str) -> Dict[str, str]:
    """
    Parse decision brief generation response.
    
    Expected structure:
    {
        "summary": str,
        "strengths": str,
        "concerns": str,
        "recommendation": str
    }
    
    Args:
        response: Raw LLM response string
        
    Returns:
        Parsed decision brief data
        
    Raises:
        LLMParseError: If response is malformed or missing required fields
    """
    # Extract and parse JSON
    json_str = extract_json_from_response(response)
    data = parse_json_safely(json_str)
    
    # Validate structure
    required_fields = ["summary", "strengths", "concerns", "recommendation"]
    for field in required_fields:
        if field not in data:
            raise LLMParseError(f"Response missing required field: {field}")
        
        if not isinstance(data[field], str) or not data[field].strip():
            raise LLMParseError(f"Field '{field}' must be a non-empty string")
    
    return data
