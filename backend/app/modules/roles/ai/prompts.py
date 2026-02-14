"""
Role blueprint generation prompts.
Templates for AI-powered role blueprint generation.
"""


BLUEPRINT_SYSTEM_PROMPT = """You are an expert hiring manager and technical recruiter. Generate comprehensive role blueprints for technical positions."""


BLUEPRINT_USER_PROMPT = """
Generate a comprehensive role blueprint for the following position:

**Position Details:**
- Title: {title}
- Seniority: {seniority}
- Tech Stack: {stack}
- Team Context: {team_context}

Please generate a structured role blueprint with the following sections:

1. **Role Mission**: A concise 2-3 sentence mission statement describing the role's purpose and impact.

2. **Core Competencies (5-8)**: List 5-8 key competencies required for success in this role. Each competency should include:
   - Name (e.g., "System Design", "Python Development")
   - Brief description of what this competency entails
   - Weight: "must-have" or "nice-to-have"

3. **Must-Have Requirements**: Technical and experience requirements that are essential:
   - Technical skills (languages, frameworks, tools)
   - Years of experience
   - Education requirements
   - Key experiences

4. **Nice-to-Have Qualifications**: Preferred but not required:
   - Additional technical skills
   - Nice-to-have experiences
   - Certifications
   - Industry experience

5. **Interview Stages**: Suggest a logical interview flow:
   - Stage name (e.g., "Phone Screen", "Technical Interview", "System Design")
   - Duration in minutes
   - Brief description of what happens in this stage
   - Interview type (coding, system_design, behavioral, culture_fit, etc.)

Return the response as a valid JSON object matching this schema:
{{
    "mission": "Role mission statement",
    "competencies": [
        {{
            "name": "Competency name",
            "description": "Competency description",
            "weight": "must-have" | "nice-to-have"
        }}
    ],
    "must_have": {{
        "technical_skills": [],
        "years_experience": "",
        "education": "",
        "key_experiences": []
    }},
    "nice_to_have": {{
        "additional_skills": [],
        "preferred_experiences": [],
        "certifications": []
    }},
    "interview_stages": [
        {{
            "name": "Stage name",
            "duration_minutes": 60,
            "description": "Stage description",
            "interview_type": "coding" | "system_design" | "behavioral" | "culture_fit" | "other"
        }}
    ]
}}

Important:
- Return ONLY valid JSON, no markdown formatting
- Ensure the competencies are balanced between must-have and nice-to-have
- Interview stages should logically progress from screening to final round
- Consider the seniority level when setting expectations
"""


COMPETENCY_SUGGESTION_PROMPT = """
Generate 5-7 core competencies for a {seniority} {role_title} role.
Tech Stack: {stack}

{existing_competencies}

Return as JSON array:
[
    {{
        "name": "Competency name",
        "description": "Description",
        "weight": "must-have" | "nice-to-have"
    }}
]
"""

