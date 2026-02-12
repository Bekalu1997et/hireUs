"""
AI Prompt Templates Module

Constructs structured prompts for LLM operations.
"""
from typing import Dict, Any, List


def build_interview_kit_prompt(
    role_title: str,
    role_description: str,
    seniority_level: str,
    competencies: List[Dict[str, Any]]
) -> str:
    """
    Build prompt for interview kit generation.
    
    Args:
        role_title: Title of the role
        role_description: Description of the role
        seniority_level: Seniority level
        competencies: List of competency dicts with id, name, description, weight
        
    Returns:
        Formatted prompt string
    """
    competencies_text = "\n".join([
        f"- Competency ID {c['id']}: {c['name']} (weight: {c['weight']:.2f})\n  {c['description']}"
        for c in competencies
    ])
    
    prompt = f"""Generate a structured technical interview kit for the following role:

Role: {role_title}
Seniority Level: {seniority_level}

Description:
{role_description}

Required Competencies:
{competencies_text}

Generate interview questions that evaluate each competency. For each question, provide:
1. The competency_id it evaluates
2. The question text (should be open-ended and probe for depth)
3. An evaluation rubric (clear criteria for scoring 1-5)
4. An order number (sequential starting from 1)

Requirements:
- Generate at least one question per competency
- Questions should be appropriate for {seniority_level} level
- Questions should be technical and probe for real-world experience
- Evaluation rubrics should provide clear scoring criteria
- Order questions logically (foundational concepts first, then advanced)

Respond with JSON in this exact format:
{{
  "questions": [
    {{
      "competency_id": <int>,
      "question_text": "<string>",
      "evaluation_rubric": "<string>",
      "order": <int>
    }}
  ]
}}"""
    
    return prompt


def build_decision_brief_prompt(
    candidate_name: str,
    role_title: str,
    role_description: str,
    competencies: List[Dict[str, Any]],
    evaluations: List[Dict[str, Any]],
    aggregated_scores: Dict[str, float]
) -> str:
    """
    Build prompt for decision brief generation.
    
    Args:
        candidate_name: Name of the candidate
        role_title: Title of the role
        role_description: Description of the role
        competencies: List of competency dicts
        evaluations: List of evaluation dicts with scores and notes
        aggregated_scores: Dict mapping competency names to average scores
        
    Returns:
        Formatted prompt string
    """
    # Format competencies with weights
    competencies_text = "\n".join([
        f"- {c['name']} (weight: {c['weight']:.2f}): {c['description']}"
        for c in competencies
    ])
    
    # Format aggregated scores
    scores_text = "\n".join([
        f"- {name}: {score:.2f}/5.0"
        for name, score in aggregated_scores.items()
    ])
    
    # Format individual evaluations
    evaluations_text = ""
    for i, eval_data in enumerate(evaluations, 1):
        evaluations_text += f"\n=== Evaluation {i} by {eval_data['interviewer_name']} ===\n"
        evaluations_text += f"Submitted: {eval_data['submitted_at']}\n\n"
        evaluations_text += "Scores:\n"
        for score in eval_data['scores']:
            evaluations_text += f"- {score['competency_name']}: {score['score']}/5\n"
        evaluations_text += f"\nNotes:\n{eval_data['notes']}\n"
    
    prompt = f"""Generate a hiring decision brief for the following candidate:

Candidate: {candidate_name}
Role: {role_title}

Role Description:
{role_description}

Required Competencies:
{competencies_text}

Aggregated Scores (Average across all interviewers):
{scores_text}

Individual Evaluations:
{evaluations_text}

Based on this data, generate a comprehensive decision brief that includes:
1. Summary: A concise overview of the candidate's performance (2-3 sentences)
2. Strengths: Key areas where the candidate excelled
3. Concerns: Areas of weakness or uncertainty
4. Recommendation: Clear hiring recommendation with rationale

Consider:
- Competency weights when assessing overall fit
- Consistency or divergence across evaluations
- Whether the candidate meets the bar for {role_title}
- Specific evidence from interviewer notes

Respond with JSON in this exact format:
{{
  "summary": "<string>",
  "strengths": "<string>",
  "concerns": "<string>",
  "recommendation": "<string>"
}}"""
    
    return prompt
