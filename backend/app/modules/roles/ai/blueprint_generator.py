"""
Blueprint Generator for role AI module.
Handles AI-powered role blueprint generation using Ollama.
"""
import json
from typing import List, Optional

from app.core.llm.schema import get_ollama_client, is_ollama_configured
from app.modules.roles.ai.schema import (
    RoleBlueprintInput,
    RoleBlueprintOutput,
    Competency,
    InterviewStage,
)
from app.modules.roles.ai.prompts import (
    BLUEPRINT_USER_PROMPT,
    COMPETENCY_SUGGESTION_PROMPT,
)


class BlueprintGenerator:
    """
    Generator for role blueprints using Ollama.
    """
    
    def __init__(self):
        """Initialize the blueprint generator."""
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
    
    def _build_prompt(self, role_input: RoleBlueprintInput) -> str:
        """Build the prompt for role blueprint generation."""
        return BLUEPRINT_USER_PROMPT.format(
            title=role_input.title,
            seniority=role_input.seniority,
            stack=', '.join(role_input.stack) if role_input.stack else 'Not specified',
            team_context=role_input.team_context or 'No additional context provided'
        )
    
    async def generate(
        self,
        role_input: RoleBlueprintInput,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> RoleBlueprintOutput:
        """
        Generate a role blueprint using Ollama.
        
        Args:
            role_input: The role details for blueprint generation
            temperature: Controls randomness (0.0-1.0)
            max_tokens: Maximum response tokens
            
        Returns:
            RoleBlueprintOutput with generated blueprint data
        """
        if not self.is_configured():
            raise ValueError("Ollama is not configured. Set OLLAMA_BASE_URL and OLLAMA_MODEL in environment.")
        
        try:
            prompt = self._build_prompt(role_input)
            
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
            
            # Validate and create output
            blueprint = RoleBlueprintOutput(
                mission=data.get("mission", ""),
                competencies=[
                    Competency(**comp) for comp in data.get("competencies", [])
                ],
                must_have=data.get("must_have", {}),
                nice_to_have=data.get("nice_to_have", {}),
                interview_stages=[
                    InterviewStage(**stage) for stage in data.get("interview_stages", [])
                ]
            )
            
            return blueprint
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse Ollama response as JSON: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Ollama API error: {str(e)}")
    
    async def generate_competency_suggestions(
        self,
        role_title: str,
        seniority: str,
        stack: List[str],
        existing_competencies: Optional[List[str]] = None
    ) -> List[Competency]:
        """
        Generate competency suggestions for a role.
        Useful for enhancing existing role definitions.
        """
        existing_text = ""
        if existing_competencies:
            existing_text = f"Existing competencies to enhance: {', '.join(existing_competencies)}"
        
        prompt = COMPETENCY_SUGGESTION_PROMPT.format(
            seniority=seniority,
            role_title=role_title,
            stack=', '.join(stack) if stack else 'Not specified',
            existing_competencies=existing_text
        )
        
        try:
            response = await self.client.generate(
                prompt=prompt,
                temperature=0.7,
                max_tokens=1000,
                format="json",
            )
            
            response_text = response.content
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            data = json.loads(response_text.strip())
            return [Competency(**comp) for comp in data]
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate competency suggestions: {str(e)}")


# Singleton instance
_blueprint_generator: Optional[BlueprintGenerator] = None


def get_blueprint_generator() -> BlueprintGenerator:
    """Get or create the BlueprintGenerator singleton."""
    global _blueprint_generator
    if _blueprint_generator is None:
        _blueprint_generator = BlueprintGenerator()
    return _blueprint_generator
