"""
Core LLM types and utilities for AI integration.
Shared types used across all AI modules.
"""
import enum
from typing import Optional
import google.generativeai as genai
from pydantic import Field

from app.core.config import settings


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

