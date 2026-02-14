"""
Interview kit generation prompts.
Templates for AI-powered interview kit generation.
"""
from typing import Dict

from app.core.llm.schema import InterviewType


# Type-specific guidance for different interview types
KIT_TYPE_GUIDANCE: Dict[str, str] = {
    "coding": """
    - Focus on algorithmic problem-solving skills
    - Include a practical coding problem with clear requirements
    - Consider the tech stack when designing the problem
    - Include edge cases and follow-up questions
    - Rubric should evaluate: Problem Understanding, Code Quality, Algorithm Efficiency, Testing
    """,
    "system_design": """
    - Focus on architectural thinking and system design skills
    - Design a real-world system relevant to the role
    - Include scalability and trade-offs discussions
    - Rubric should evaluate: Architecture Design, Scalability, Trade-offs, Communication
    """,
    "pm_case": """
    - Focus on product thinking and problem-solving
    - Create a realistic product scenario the candidate might face
    - Include prioritization and stakeholder management aspects
    - Rubric should evaluate: Problem Analysis, Solution Quality, Prioritization, Communication
    """,
    "behavioral": """
    - Focus on soft skills and past experiences
    - Use STAR method for question framing
    - Include questions about leadership, collaboration, and conflict resolution
    - Rubric should evaluate: Communication, Leadership, Teamwork, Problem-solving Approach
    """
}


KIT_SYSTEM_PROMPT = """You are an expert technical interviewer and hiring manager. Generate comprehensive interview kits for technical positions."""


KIT_USER_PROMPT = """
Generate a comprehensive interview kit for the following:

**Role Details:**
- Title: {role_title}
- Seniority: {seniority}
- Tech Stack: {stack}
- Interview Type: {interview_type}
- Key Competencies to Evaluate: {competencies}
- Duration: {duration_minutes} minutes
- Additional Context: {additional_context}

{type_guidance}

Please generate a structured interview kit with the following sections:

1. **Title**: A clear, descriptive title for this interview kit

2. **Problem Statement**: A realistic scenario or problem for the candidate to solve. Include:
   - Background/context
   - Specific requirements or constraints
   - Expected deliverables

3. **Evaluation Rubric**: 4-6 criteria with:
   - Criterion name
   - Description of what to evaluate
   - Max score (1-5)
   - Weight (1-5)

4. **Red Flags**: 5-7 warning signs to watch for during the interview

5. **Good Answer Outline**: A structured outline of what a strong candidate should cover

6. **Questions**: 3-5 structured questions including:
   - Question text
   - Type (open-ended, coding, scenario)
   - Suggested duration
   - Difficulty level
   - Notes for interviewer

7. **Tips for Interviewer**: 2-3 practical tips for conducting this interview effectively

8. **Suggested Duration Breakdown**: How to split the {duration_minutes} minutes

Return the response as a valid JSON object matching this schema:
{{
    "title": "Interview kit title",
    "problem_statement": "Detailed problem statement...",
    "evaluation_rubric": [
        {{
            "name": "Criterion name",
            "description": "What to evaluate",
            "max_score": 5,
            "weight": 1
        }}
    ],
    "red_flags": ["Red flag 1", "Red flag 2", ...],
    "good_answer_outline": "Outline of a good answer...",
    "questions": [
        {{
            "question": "Question text",
            "type": "open-ended" | "coding" | "scenario",
            "duration_minutes": 10,
            "difficulty": "easy" | "medium" | "hard",
            "notes": "Optional notes"
        }}
    ],
    "tips_for_interviewer": "Practical tips...",
    "suggested_duration_breakdown": {{
        "introduction": 5,
        "main_problem": 30,
        "questions": 15,
        "wrap_up": 10
    }}
}}

Important:
- Return ONLY valid JSON, no markdown formatting
- Adjust difficulty based on seniority level
- Make questions realistic and relevant to the role
- Ensure the total question time fits within the {duration_minutes} minute limit
"""


def get_type_guidance(interview_type: InterviewType) -> str:
    """Get type-specific guidance for an interview type."""
    type_value = interview_type.value if hasattr(interview_type, 'value') else interview_type
    return KIT_TYPE_GUIDANCE.get(type_value, KIT_TYPE_GUIDANCE["coding"])


def build_kit_prompt(
    role_title: str,
    seniority: str,
    stack: list,
    interview_type: InterviewType,
    competencies: list,
    duration_minutes: int,
    additional_context: str | None
) -> str:
    """Build the full prompt for interview kit generation."""
    type_guidance = get_type_guidance(interview_type)
    
    competencies_text = ", ".join(competencies) if competencies else "Core technical and soft skills"
    stack_text = ", ".join(stack) if stack else "Not specified"
    context_text = additional_context or "No additional context provided"
    
    return KIT_USER_PROMPT.format(
        role_title=role_title,
        seniority=seniority,
        stack=stack_text,
        interview_type=interview_type.value if hasattr(interview_type, 'value') else interview_type,
        competencies=competencies_text,
        duration_minutes=duration_minutes,
        additional_context=context_text,
        type_guidance=type_guidance
    )

