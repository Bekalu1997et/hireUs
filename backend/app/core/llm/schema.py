"""
Shared LLM schema utilities used across AI modules.
"""
from app.core.llm.base import InterviewType, get_ollama_client, is_ollama_configured

__all__ = ["InterviewType", "get_ollama_client", "is_ollama_configured"]
