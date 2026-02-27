"""
AI Client Module

Handles OpenAI API integration with retry logic, timeout, and error handling.
"""
import asyncio
from typing import Dict, Any, List
import httpx
from openai import AsyncOpenAI, APIError, RateLimitError, APITimeoutError
from app.core.config import settings

from app.modules.ai.prompts import build_decision_brief_prompt
from app.modules.ai.prompts import build_interview_kit_prompt


class AIClient:
    """Client for OpenAI API with retry logic and error handling."""
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize AI client.
        
        Args:
            api_key: OpenAI API key (defaults to settings)
            model: Model to use (defaults to settings)
        """
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_model
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None
        self.timeout = 180.0  # 30 second timeout
        self.max_retries = 3
        self.retry_delays = [1.0, 2.0, 4.0]  # Exponential backoff
        self.ollama_enabled = settings.ollama_enabled
        self.ollama_base_url = settings.ollama_base_url.rstrip("/")
        self.ollama_model = settings.ollama_model
        self.ollama_timeout = settings.ollama_timeout_seconds
    
    async def _call_openai_with_retry(
        self, 
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> str:
        """
        Call OpenAI API with exponential backoff retry logic.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            
        Returns:
            Response content as string
            
        Raises:
            APIError: If all retries fail
            APITimeoutError: If request times out
        """
        last_error = None
        
        if not self.client:
            raise APIError("OpenAI client is not configured")

        for attempt in range(self.max_retries):
            try:
                response = await asyncio.wait_for(
                    self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=temperature,
                        response_format={"type": "json_object"}
                    ),
                    timeout=self.timeout
                )
                return response.choices[0].message.content
            
            except asyncio.TimeoutError as e:
                # asyncio.wait_for timeout - retry with backoff
                last_error = e
                if attempt < self.max_retries - 1:
                    delay = self.retry_delays[attempt]
                    await asyncio.sleep(delay)
                    continue
                raise

            except RateLimitError as e:
                # Handle rate limiting with backoff
                last_error = e
                if attempt < self.max_retries - 1:
                    delay = self.retry_delays[attempt]
                    await asyncio.sleep(delay)
                    continue
                raise
            
            except APITimeoutError as e:
                # Timeout - retry with backoff
                last_error = e
                if attempt < self.max_retries - 1:
                    delay = self.retry_delays[attempt]
                    await asyncio.sleep(delay)
                    continue
                raise
            
            except APIError as e:
                # Other API errors - retry with backoff
                last_error = e
                if attempt < self.max_retries - 1:
                    delay = self.retry_delays[attempt]
                    await asyncio.sleep(delay)
                    continue
                raise
        
        # If we get here, all retries failed
        if last_error:
            raise last_error
        raise APIError("All retry attempts failed")

    async def _call_with_retry(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> str:
        """
        Backwards-compatible wrapper for OpenAI-only retry logic.
        """
        return await self._call_openai_with_retry(messages, temperature=temperature)

    async def _call_ollama(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> str:
        """
        Call Ollama local LLM API.

        Returns:
            Response content as string
        """
        if not self.ollama_enabled:
            raise APIError("Ollama fallback is disabled")

        payload = {
            "model": self.ollama_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }

        last_error: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.ollama_timeout) as client:
                    response = await client.post(
                        f"{self.ollama_base_url}/api/chat",
                        json=payload
                    )
                    response.raise_for_status()
                    data = response.json()
                break
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    delay = self.retry_delays[attempt]
                    await asyncio.sleep(delay)
                    continue
                raise

        message = data.get("message", {})
        content = message.get("content")
        if not isinstance(content, str):
            raise APIError("Ollama response missing message content")
        return content

    async def _call_with_fallback(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> str:
        """
        Call OpenAI first; if it fails, fall back to Ollama.
        """
        if not self.api_key:
            return await self._call_ollama(messages, temperature=temperature)

        try:
            return await self._call_openai_with_retry(messages, temperature=temperature)
        except Exception:
            return await self._call_ollama(messages, temperature=temperature)
    
    async def generate_interview_kit(
        self,
        role_title: str,
        role_description: str,
        seniority_level: str,
        competencies: List[Dict[str, Any]]
    ) -> str:
        """
        Generate interview questions for role competencies.
        
        Args:
            role_title: Title of the role
            role_description: Description of the role
            seniority_level: Seniority level (junior, mid, senior, etc.)
            competencies: List of competency dicts with id, name, description, weight
            
        Returns:
            Raw JSON string response from LLM
            
        Raises:
            APIError: If API call fails after retries
        """
        
        
        prompt = build_interview_kit_prompt(
            role_title=role_title,
            role_description=role_description,
            seniority_level=seniority_level,
            competencies=competencies
        )
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert technical interviewer who creates structured interview questions. Always respond with valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        return await self._call_with_fallback(messages, temperature=0.7)
    
    async def generate_decision_brief(
        self,
        candidate_name: str,
        role_title: str,
        role_description: str,
        competencies: List[Dict[str, Any]],
        evaluations: List[Dict[str, Any]],
        aggregated_scores: Dict[str, float]
    ) -> str:
        """
        Generate hiring decision brief from evaluations.
        
        Args:
            candidate_name: Name of the candidate
            role_title: Title of the role
            role_description: Description of the role
            competencies: List of competency dicts
            evaluations: List of evaluation dicts with scores and notes
            aggregated_scores: Dict mapping competency names to average scores
            
        Returns:
            Raw JSON string response from LLM
            
        Raises:
            APIError: If API call fails after retries
        """
        
        
        prompt = build_decision_brief_prompt(
            candidate_name=candidate_name,
            role_title=role_title,
            role_description=role_description,
            competencies=competencies,
            evaluations=evaluations,
            aggregated_scores=aggregated_scores
        )
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert hiring manager who synthesizes interview feedback into clear decision briefs. Always respond with valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        return await self._call_with_fallback(messages, temperature=0.5)
