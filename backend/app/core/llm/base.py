"""
Core LLM types and utilities for AI integration.
Shared types used across all AI modules.
"""
import enum
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field
import google.generativeai as genai

from app.core.config import settings


class LLMResponse(BaseModel):
    """Response from LLM generation."""
    content: str = Field(..., description="Generated text content")
    model: str = Field(..., description="Model used for generation")
    usage: Optional[Dict[str, Any]] = Field(None, description="Token usage information")
    finish_reason: Optional[str] = Field(None, description="Reason for completion")


class LLMClient:
    """Base class for LLM clients."""
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> LLMResponse:
        """
        Generate content using the LLM.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse with generated content
        """
        raise NotImplementedError("Subclasses must implement generate()")


class GeminiClient(LLMClient):
    """Google Gemini LLM client."""
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize Gemini client.
        
        Args:
            model_name: Name of Gemini model to use
        """
        self.model_name = model_name or settings.GEMINI_MODEL
        self._client = None
    
    def _get_client(self) -> genai.GenerativeModel:
        """Get or create Gemini client."""
        if self._client is None:
            api_key = settings.GEMINI_API_KEY
            if api_key:
                genai.configure(api_key=api_key)
            self._client = genai.GenerativeModel(self.model_name)
        return self._client
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> LLMResponse:
        """Generate content using Gemini."""
        client = self._get_client()
        
        response = client.generate_content(
            prompt,
            generation_config={
                'temperature': temperature,
                'max_output_tokens': max_tokens,
                **kwargs
            }
        )
        
        return LLMResponse(
            content=response.text,
            model=self.model_name,
            usage={'prompt_tokens': -1, 'completion_tokens': -1},  # Not available in this version
            finish_reason='stop'
        )


class InterviewType(str, enum.Enum):
    """Interview type enumeration."""
    CODING = "coding"
    SYSTEM_DESIGN = "system_design"
    PM_CASE = "pm_case"
    BEHAVIORAL = "behavioral"


# Singleton instances
_gemini_client: Optional[genai.GenerativeModel] = None


def get_gemini_client() -> genai.GenerativeModel:
    """
    Get or create the Gemini model singleton.
    
    Returns:
        Configured Gemini GenerativeModel instance
    """
    global _gemini_client
    if _gemini_client is None:
        api_key = settings.GEMINI_API_KEY
        if api_key:
            genai.configure(api_key=api_key)
        model_name = settings.GEMINI_MODEL
        _gemini_client = genai.GenerativeModel(model_name)
    return _gemini_client


def is_gemini_configured() -> bool:
    """Check if Gemini API is configured."""
    return bool(settings.GEMINI_API_KEY)

