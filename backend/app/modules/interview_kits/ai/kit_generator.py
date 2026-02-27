"""
Kit Generator for interview kit AI module.
Handles AI-powered interview kit generation using Ollama.
"""
import json
from typing import Optional

from app.core.llm.schema import get_ollama_client, is_ollama_configured, InterviewType
from app.modules.interview_kits.ai.schema import (
    InterviewKitInput,
    InterviewKitOutput,
    RubricCriterion,
    QuestionItem,
)
from app.modules.interview_kits.ai.prompts import build_kit_prompt


class KitGenerator:
    """
    Generator for interview kits using Ollama.
    """
    
    def __init__(self):
        """Initialize the kit generator."""
        self._model = None
    
    @property
    def client(self):
        """Lazy load the Ollama client."""
        if self._model is None:
            self._model = get_ollama_client()
        return self._model
    
    def is_configured(self) -> bool:
        """Check if Ollama is configured."""
        return is_ollama_configured()
    
    async def generate(
        self,
        kit_input: InterviewKitInput,
        temperature: float = 0.7,
        max_tokens: int = 3000
    ) -> InterviewKitOutput:
        """
        Generate an interview kit using Ollama.
        
        Args:
            kit_input: The interview kit details for generation
            temperature: Controls randomness (0.0-1.0)
            max_tokens: Maximum response tokens
            
        Returns:
            InterviewKitOutput with generated interview kit data
        """
        if not self.is_configured():
            raise ValueError("Ollama is not configured. Set OLLAMA_BASE_URL and OLLAMA_MODEL in environment.")
        
        try:
            prompt = build_kit_prompt(
                role_title=kit_input.role_title,
                seniority=kit_input.seniority,
                stack=kit_input.stack or [],
                interview_type=kit_input.interview_type,
                competencies=kit_input.competencies or [],
                duration_minutes=kit_input.duration_minutes,
                additional_context=kit_input.additional_context
            )
            
            response = await self.client.generate(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                format="json",
            )
            
            # Parse response
            response_text = response.content
            
            # Handle potential markdown code block wrapping
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            # Parse JSON
            data = json.loads(response_text.strip())
            
            # Determine interview type value for default title
            interview_type_value = (
                kit_input.interview_type.value 
                if hasattr(kit_input.interview_type, 'value') 
                else kit_input.interview_type
            )
            
            # Validate and create output
            kit = InterviewKitOutput(
                title=data.get("title", f"{kit_input.role_title} - {interview_type_value} Interview"),
                problem_statement=data.get("problem_statement", ""),
                evaluation_rubric=[
                    RubricCriterion(**criterion) for criterion in data.get("evaluation_rubric", [])
                ],
                red_flags=data.get("red_flags", []),
                good_answer_outline=data.get("good_answer_outline", ""),
                questions=[
                    QuestionItem(**q) for q in data.get("questions", [])
                ],
                tips_for_interviewer=data.get("tips_for_interviewer"),
                suggested_duration_breakdown=data.get("suggested_duration_breakdown")
            )
            
            return kit
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse Ollama response as JSON: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Ollama API error: {str(e)}")


# Singleton instance
_kit_generator: Optional[KitGenerator] = None


def get_kit_generator() -> KitGenerator:
    """Get or create the KitGenerator singleton."""
    global _kit_generator
    if _kit_generator is None:
        _kit_generator = KitGenerator()
    return _kit_generator
