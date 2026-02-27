"""
Core LLM types and utilities for AI integration.
Shared types used across all AI modules.
"""
import enum
from typing import Optional, Any, Dict

import httpx
from pydantic import BaseModel, Field

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
        **kwargs: Any,
    ) -> LLMResponse:
        raise NotImplementedError("Subclasses must implement generate()")


class OllamaClient(LLMClient):
    """Ollama LLM client."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> None:
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model_name = model_name or settings.OLLAMA_MODEL

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> LLMResponse:
        payload: Dict[str, Any] = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if "format" in kwargs and kwargs["format"]:
            payload["format"] = kwargs["format"]

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()

        return LLMResponse(
            content=data.get("response", ""),
            model=data.get("model", self.model_name),
            usage={
                "prompt_tokens": data.get("prompt_eval_count"),
                "completion_tokens": data.get("eval_count"),
            },
            finish_reason=data.get("done_reason", "stop"),
        )


class InterviewType(str, enum.Enum):
    """Interview type enumeration."""

    CODING = "coding"
    SYSTEM_DESIGN = "system_design"
    PM_CASE = "pm_case"
    BEHAVIORAL = "behavioral"


_ollama_client: Optional[OllamaClient] = None


def get_ollama_client() -> OllamaClient:
    """Get or create the Ollama client singleton."""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client


def is_ollama_configured() -> bool:
    """Check if Ollama settings are configured."""
    return bool(settings.OLLAMA_BASE_URL and settings.OLLAMA_MODEL)
