"""
Feedback Refiner for evaluations AI module.
Handles AI-powered feedback improvement using Ollama.
"""
import json
from typing import Optional, Dict, Any, List

from app.core.llm.schema import get_ollama_client, is_ollama_configured
from app.schemas.evaluation import (
    FeedbackImproveRequest,
    FeedbackImproveResponse,
    FeedbackSuggestion,
)


class FeedbackRefiner:
    """
    Refiner for interview feedback using Ollama.
    Provides AI assistance to improve feedback clarity and quality.
    """
    
    def __init__(self):
        """Initialize the feedback refiner."""
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
    
    async def improve_feedback(
        self,
        strengths: Optional[str] = None,
        weaknesses: Optional[str] = None,
        summary: Optional[str] = None,
        scores: Optional[Dict[str, Any]] = None,
        target: str = "all",
        context: Optional[str] = None
    ) -> FeedbackImproveResponse:
        """
        Improve feedback text using AI.
        
        Args:
            strengths: Current strengths text
            weaknesses: Current weaknesses text
            summary: Current summary text
            scores: Dictionary of competency scores
            target: What to improve - "strengths", "weaknesses", "summary", or "all"
            context: Additional context for the AI
            
        Returns:
            FeedbackImproveResponse with improved text(s)
        """
        if not self.is_configured():
            return FeedbackImproveResponse(
                success=False,
                error="Ollama is not configured. Set OLLAMA_BASE_URL and OLLAMA_MODEL in environment."
            )
        
        try:
            # Build the prompt based on target
            prompt = self._build_improvement_prompt(
                strengths=strengths,
                weaknesses=weaknesses,
                summary=summary,
                scores=scores,
                target=target,
                context=context
            )
            
            response = await self.client.generate(
                prompt=prompt,
                temperature=0.3,
                max_tokens=2000,
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
            
            if target == "all":
                return FeedbackImproveResponse(
                    success=True,
                    improved_text=data.get("improved_summary", ""),
                    suggestions=[
                        FeedbackSuggestion(
                            field="strengths",
                            original=strengths or "",
                            improved=data.get("improved_strengths", ""),
                            explanation=data.get("strengths_explanation", "")
                        ),
                        FeedbackSuggestion(
                            field="weaknesses",
                            original=weaknesses or "",
                            improved=data.get("improved_weaknesses", ""),
                            explanation=data.get("weaknesses_explanation", "")
                        ),
                        FeedbackSuggestion(
                            field="summary",
                            original=summary or "",
                            improved=data.get("improved_summary", ""),
                            explanation=data.get("summary_explanation", "")
                        )
                    ] if data.get("improved_strengths") else None
                )
            else:
                field_map = {
                    "strengths": "improved_strengths",
                    "weaknesses": "improved_weaknesses", 
                    "summary": "improved_summary"
                }
                improved_field = field_map.get(target, "improved_text")
                
                return FeedbackImproveResponse(
                    success=True,
                    improved_text=data.get(improved_field, ""),
                    suggestions=[
                        FeedbackSuggestion(
                            field=target,
                            original=strengths or weaknesses or summary or "",
                            improved=data.get(improved_field, ""),
                            explanation=data.get(f"{target}_explanation", "")
                        )
                    ]
                )
                
        except json.JSONDecodeError as e:
            return FeedbackImproveResponse(
                success=False,
                error=f"Failed to parse AI response: {str(e)}"
            )
        except Exception as e:
            return FeedbackImproveResponse(
                success=False,
                error=f"AI processing error: {str(e)}"
            )
    
    async def suggest_evidence(
        self,
        competency: str,
        score: int,
        current_evidence: Optional[str] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Suggest evidence for a competency based on the score.
        
        Args:
            competency: Name of the competency
            score: Score given (1-5)
            current_evidence: Any existing evidence
            context: Additional context
            
        Returns:
            Dict with suggested evidence
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "Ollama is not configured"
            }
        
        try:
            prompt = self._build_evidence_prompt(
                competency=competency,
                score=score,
                current_evidence=current_evidence,
                context=context
            )
            
            response = await self.client.generate(
                prompt=prompt,
                temperature=0.3,
                max_tokens=500,
                format="json",
            )
            
            response_text = response.content
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            data = json.loads(response_text.strip())
            
            return {
                "success": True,
                "suggested_evidence": data.get("suggested_evidence", ""),
                "what_to_look_for": data.get("what_to_look_for", []),
                "red_flags": data.get("red_flags", []),
                "positive_signs": data.get("positive_signs", [])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_summary_from_scores(
        self,
        scores: Dict[str, Any],
        strengths: Optional[str] = None,
        weaknesses: Optional[str] = None
    ) -> str:
        """
        Generate a summary paragraph based on scores and feedback.
        
        Args:
            scores: Dictionary of competency scores
            strengths: Optional strengths text
            weaknesses: Optional weaknesses text
            
        Returns:
            Generated summary string
        """
        if not self.is_configured():
            return ""
        
        try:
            # Build scores summary
            scores_summary = []
            for comp, score_data in scores.items():
                if isinstance(score_data, dict):
                    score = score_data.get("score", 0)
                    scores_summary.append(f"- {comp}: {score}/5")
                else:
                    scores_summary.append(f"- {comp}: {score_data}/5")
            
            prompt = f"""
You are an expert hiring manager helping to write interview feedback summaries.

Given the following interview evaluation data, write a concise 2-3 paragraph summary that:
1. Highlights the candidate's overall performance
2. Mentions key strengths observed
3. Notes areas for improvement
4. Provides a balanced overall impression

Scores:
{chr(10).join(scores_summary)}

Strengths noted: {strengths or "None provided"}
Weaknesses noted: {weaknesses or "None provided"}

Write a professional, constructive summary suitable for a hiring decision:
""".strip()
            
            response = await self.client.generate(
                prompt=prompt,
                temperature=0.4,
                max_tokens=500,
            )
            
            return response.content.strip()
            
        except Exception as e:
            return ""
    
    def _build_improvement_prompt(
        self,
        strengths: Optional[str],
        weaknesses: Optional[str],
        summary: Optional[str],
        scores: Optional[Dict[str, Any]],
        target: str,
        context: Optional[str]
    ) -> str:
        """Build the prompt for feedback improvement."""
        
        # Build scores info
        scores_info = ""
        if scores:
            scores_list = []
            for comp, score_data in scores.items():
                if isinstance(score_data, dict):
                    score = score_data.get("score", "?")
                    scores_list.append(f"- {comp}: {score}/5")
                else:
                    scores_list.append(f"- {comp}: {score_data}/5")
            scores_info = f"\n\nCompetency Scores:\n{chr(10).join(scores_list)}"
        
        target_map = {
            "strengths": f"""
Current strengths feedback: {strengths or '(empty)'}

Improve this feedback to be:
- More specific with examples
- Actionable for hiring managers
- Professional and constructive

Return JSON with:
- "improved_strengths": The improved text
- "strengths_explanation": Brief explanation of changes
""",
            "weaknesses": f"""
Current weaknesses feedback: {weaknesses or '(empty)'}

Improve this feedback to be:
- Constructive and actionable
- Specific about skill gaps
- Professional and fair
- Focused on development opportunities

Return JSON with:
- "improved_weaknesses": The improved text
- "weaknesses_explanation": Brief explanation of changes
""",
            "summary": f"""
Current summary: {summary or '(empty)'}{scores_info}

Improve this summary to:
- Be concise (2-3 paragraphs)
- Balance strengths and areas for improvement
- Be suitable for hiring decisions
- Include specific competency highlights

Return JSON with:
- "improved_summary": The improved summary
- "summary_explanation": Brief explanation of changes
""",
            "all": f"""
Current feedback:
- Strengths: {strengths or '(empty)'}
- Weaknesses: {weaknesses or '(empty)'}
- Summary: {summary or '(empty)'}{scores_info}

Improve ALL sections to be:
- More specific with concrete examples
- Actionable for hiring committees
- Professional and constructive
- Balanced and fair

Return JSON with:
- "improved_strengths": The improved strengths
- "strengths_explanation": Brief explanation
- "improved_weaknesses": The improved weaknesses  
- "weaknesses_explanation": Brief explanation
- "improved_summary": The improved summary
- "summary_explanation": Brief explanation
"""
        }
        
        prompt = f"""You are an expert hiring manager helping to improve interview feedback.

Your task is to enhance the following interview feedback to be more clear, specific, and actionable.

{target_map.get(target, target_map['all'])}

Additional context: {context or 'None'}

Respond with valid JSON only, no markdown."""
        
        return prompt
    
    def _build_evidence_prompt(
        self,
        competency: str,
        score: int,
        current_evidence: Optional[str],
        context: Optional[str]
    ) -> str:
        """Build the prompt for evidence suggestion."""
        
        score_expectations = {
            1: "Beginner - Shows very limited understanding",
            2: "Developing - Shows basic awareness but needs significant improvement",
            3: "Competent - Shows solid understanding with some areas to develop",
            4: "Strong - Shows strong capability with minor gaps",
            5: "Expert - Shows exceptional, deep expertise"
        }
        
        prompt = f"""
You are an expert interviewer helping to document interview evidence.

Competency: {competency}
Score: {score}/5 - {score_expectations.get(score, '')}

Current evidence: {current_evidence or '(none)'}
Additional context: {context or 'None'}

Suggest specific evidence/observations that would support this score. Focus on:
- Concrete behaviors observed
- Specific examples or situations
- What the candidate said or did

Return JSON with:
- "suggested_evidence": A concise paragraph describing the evidence
- "what_to_look_for": List of specific signals for this score
- "red_flags": List of warning signs at this level
- "positive_signs": List of positive indicators at this level

Respond with valid JSON only, no markdown.
""".strip()
        
        return prompt


# Singleton instance
_refiner: Optional[FeedbackRefiner] = None


def get_feedback_refiner() -> FeedbackRefiner:
    """Get or create the FeedbackRefiner singleton."""
    global _refiner
    if _refiner is None:
        _refiner = FeedbackRefiner()
    return _refiner
