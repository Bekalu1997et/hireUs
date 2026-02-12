"""
AI Response Validators Module

Validates LLM responses against business rules.
"""
from typing import Dict, Any, List, Set


class LLMValidationError(Exception):
    """Exception raised when LLM response fails business rule validation."""
    pass


def validate_interview_kit(
    kit_data: Dict[str, Any],
    competency_ids: Set[int]
) -> None:
    """
    Validate interview kit against business rules.
    
    Business Rules:
    - All competencies must have at least one question
    - All question competency_ids must reference valid competencies
    - Question orders must be unique and sequential
    
    Args:
        kit_data: Parsed interview kit data
        competency_ids: Set of valid competency IDs
        
    Raises:
        LLMValidationError: If validation fails
    """
    questions = kit_data["questions"]
    
    # Check that all competencies are covered
    covered_competencies = set()
    for question in questions:
        covered_competencies.add(question["competency_id"])
    
    missing_competencies = competency_ids - covered_competencies
    if missing_competencies:
        raise LLMValidationError(
            f"Interview kit missing questions for competencies: {missing_competencies}"
        )
    
    # Check that all competency_ids are valid
    invalid_competencies = covered_competencies - competency_ids
    if invalid_competencies:
        raise LLMValidationError(
            f"Interview kit references invalid competencies: {invalid_competencies}"
        )
    
    # Check that question orders are unique
    orders = [q["order"] for q in questions]
    if len(orders) != len(set(orders)):
        raise LLMValidationError("Question orders must be unique")
    
    # Check that orders are sequential starting from 1
    expected_orders = set(range(1, len(questions) + 1))
    actual_orders = set(orders)
    if actual_orders != expected_orders:
        raise LLMValidationError(
            f"Question orders must be sequential from 1 to {len(questions)}"
        )


def validate_decision_brief(brief_data: Dict[str, str]) -> None:
    """
    Validate decision brief against business rules.
    
    Business Rules:
    - All required fields must be present and non-empty
    - Summary should be concise (< 1000 characters)
    - Recommendation should contain actionable guidance
    
    Args:
        brief_data: Parsed decision brief data
        
    Raises:
        LLMValidationError: If validation fails
    """
    # Check field lengths
    if len(brief_data["summary"]) > 1000:
        raise LLMValidationError("Summary must be less than 1000 characters")
    
    # Check that recommendation contains actionable language
    recommendation = brief_data["recommendation"].lower()
    actionable_keywords = ["recommend", "suggest", "should", "hire", "not hire", "hold"]
    if not any(keyword in recommendation for keyword in actionable_keywords):
        raise LLMValidationError(
            "Recommendation must contain actionable guidance (recommend, suggest, should, hire, etc.)"
        )
