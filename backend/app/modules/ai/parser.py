"""
AI Response Parser Module

Parses and validates LLM JSON responses.
"""
import json
import re
from typing import Dict, Any, List, Union


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


def _repair_json(json_str: str) -> str:
    """
    Attempt to repair common JSON issues from LLMs.
    - Replace single quotes with double quotes
    - Remove trailing commas
    """
    cleaned = json_str.strip()
    if "'" in cleaned and '"' not in cleaned:
        cleaned = cleaned.replace("'", "\"")
    # Remove trailing commas before } or ]
    cleaned = re.sub(r",\s*([}\]])", r"\\1", cleaned)
    return cleaned


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
    except json.JSONDecodeError:
        try:
            repaired = _repair_json(json_str)
            return json.loads(repaired)
        except json.JSONDecodeError as e:
            raise LLMParseError(f"Failed to parse JSON: {str(e)}")


def _normalize_questions(questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize common field variants from LLM responses.
    """
    normalized: List[Dict[str, Any]] = []
    for idx, q in enumerate(questions, 1):
        if not isinstance(q, dict):
            continue
        item = dict(q)

        # Common field aliases
        if "question" in item and "question_text" not in item:
            item["question_text"] = item.pop("question")
        if "rubric" in item and "evaluation_rubric" not in item:
            item["evaluation_rubric"] = item.pop("rubric")
        if "competency" in item and "competency_id" not in item:
            item["competency_id"] = item.pop("competency")

        # Coerce types
        if "competency_id" in item and isinstance(item["competency_id"], str):
            if item["competency_id"].isdigit():
                item["competency_id"] = int(item["competency_id"])
        if "order" in item and isinstance(item["order"], str):
            if item["order"].isdigit():
                item["order"] = int(item["order"])

        # Fill missing order
        if "order" not in item:
            item["order"] = idx

        normalized.append(item)
    return normalized


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
    data: Union[Dict[str, Any], List[Any]] = parse_json_safely(json_str)

    # Accept a bare list of questions
    if isinstance(data, list):
        data = {"questions": data}

    # If no "questions", try common alternatives
    if isinstance(data, dict) and "questions" not in data:
        for key in ("items", "data", "results"):
            if key in data and isinstance(data[key], list):
                data = {"questions": data[key]}
                break

    # As a last resort, find the first list value that looks like questions
    if isinstance(data, dict) and "questions" not in data:
        for value in data.values():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                data = {"questions": value}
                break
    
    # Validate structure
    if "questions" not in data:
        raise LLMParseError("Response missing 'questions' field")
    
    if not isinstance(data["questions"], list):
        raise LLMParseError("'questions' field must be a list")
    
    if len(data["questions"]) == 0:
        raise LLMParseError("'questions' list cannot be empty")
    
    # Normalize and validate each question
    data["questions"] = _normalize_questions(data["questions"])
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
