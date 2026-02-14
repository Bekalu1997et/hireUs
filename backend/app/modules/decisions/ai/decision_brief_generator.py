"""
AI-powered Decision Brief Generator.
Generates structured hiring decision briefs from candidate evaluation data.
"""
import json
import time
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.core.llm.base import LLMClient, LLMResponse
from app.modules.decisions.ai.schema import (
    DecisionBriefInput,
    DecisionBriefOutput,
    CandidateSummaryBrief,
    CandidateStrengths,
    RiskArea,
    SignalGap,
    InterviewAgreement,
    SuggestedDecision,
    SuggestedDecisionOutput,
    InterviewAgreementLevel,
)


class DecisionBriefGenerator:
    """
    Generates AI-powered decision briefs for hiring candidates.
    
    This module analyzes candidate evaluation data to produce:
    - Candidate summary
    - Strengths identification
    - Risk area analysis
    - Signal gap detection
    - Interview agreement analysis
    - Suggested hiring decision
    """
    
    # Prompt templates
    SYSTEM_PROMPT = """You are an expert hiring manager and talent acquisition specialist. 
Your task is to analyze candidate evaluation data and generate a comprehensive, unbiased decision brief.

Key principles:
1. Be objective and evidence-based
2. Highlight both strengths and concerns clearly
3. Consider the whole picture, not just scores
4. Acknowledge areas where more information is needed
5. Provide actionable recommendations
6. Avoid bias based on non-relevant factors

Output a structured JSON response following the exact schema provided."""

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        model_name: Optional[str] = None,
    ):
        """
        Initialize the decision brief generator.
        
        Args:
            llm_client: LLM client for generating content (uses Gemini if not provided)
            model_name: Model name to use for generation
        """
        self.llm_client = llm_client
        self.model_name = model_name
        
        # Try to get default LLM client if not provided
        if self.llm_client is None:
            try:
                from app.core.llm.gemini import GeminiClient
                self.llm_client = GeminiClient()
            except Exception:
                # Will handle gracefully when generating
                pass
    
    def _build_candidate_context(
        self,
        candidate_data: Dict[str, Any],
        evaluations: List[Dict[str, Any]],
        role_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build a context string from candidate data and evaluations."""
        context_parts = []
        
        # Basic candidate info
        context_parts.append("=== CANDIDATE INFORMATION ===")
        context_parts.append(f"Name: {candidate_data.get('full_name', 'Unknown')}")
        context_parts.append(f"Email: {candidate_data.get('email', 'Unknown')}")
        context_parts.append(f"Role: {role_data.get('title', 'Unknown') if role_data else 'Unknown'}")
        context_parts.append(f"Status: {candidate_data.get('status', 'Unknown')}")
        
        # Role requirements if available
        if role_data:
            context_parts.append("\n=== ROLE REQUIREMENTS ===")
            context_parts.append(f"Mission: {role_data.get('mission', 'N/A')}")
            
            competencies = role_data.get('core_competencies', [])
            if competencies:
                context_parts.append(f"Core Competencies: {', '.join([c.get('name', c) if isinstance(c, dict) else c for c in competencies])}")
        
        # Evaluations
        context_parts.append("\n=== EVALUATIONS ===")
        for i, eval_data in enumerate(evaluations):
            context_parts.append(f"\n--- Evaluation {i+1} ---")
            
            # Interviewer info
            interviewer = eval_data.get('interviewer', {})
            context_parts.append(f"Interviewer: {interviewer.get('full_name', 'Unknown')}")
            
            # Scores
            scores = eval_data.get('scores', {})
            if scores:
                context_parts.append("\nCompetency Scores:")
                for comp, score_data in scores.items():
                    if isinstance(score_data, dict):
                        score = score_data.get('score', score_data.get('value', 'N/A'))
                        notes = score_data.get('notes', '')
                        context_parts.append(f"  - {comp}: {score}/5 {notes if notes else ''}")
                    elif isinstance(score_data, (int, float)):
                        context_parts.append(f"  - {comp}: {score_data}/5")
            
            # Confidence
            confidence = eval_data.get('confidence', 'N/A')
            context_parts.append(f"Confidence Level: {confidence}/5")
            
            # Written feedback
            if eval_data.get('strengths'):
                context_parts.append(f"Strengths: {eval_data['strengths']}")
            if eval_data.get('weaknesses'):
                context_parts.append(f"Areas for Improvement: {eval_data['weaknesses']}")
            if eval_data.get('summary'):
                context_parts.append(f"Summary: {eval_data['summary']}")
            if eval_data.get('recommendation'):
                context_parts.append(f"Recommendation: {eval_data['recommendation']}")
        
        return "\n".join(context_parts)
    
    def _build_generation_prompt(
        self,
        context: str,
        focus_areas: Optional[List[str]] = None,
        custom_prompt: Optional[str] = None
    ) -> str:
        """Build the full generation prompt."""
        prompt = f"""{self.SYSTEM_PROMPT}

{context}

Based on the above information, generate a comprehensive decision brief.

Focus areas (if specified): {', '.join(focus_areas) if focus_areas else 'All areas'}
{custom_prompt if custom_prompt else ''}

IMPORTANT: Output must be valid JSON matching this schema:
{{
    "candidate_summary": {{
        "name": "string",
        "role_applied": "string",
        "overall_score": 0.0,
        "total_evaluations": 0,
        "recommendation_breakdown": {{"strong_hire": 0, "hire": 0, "neutral": 0, "no_hire": 0, "strong_no_hire": 0}}
    }},
    "strengths": [
        {{
            "category": "string",
            "description": "string",
            "evidence": ["string"],
            "competency_scores": {{"string": 0.0}}
        }}
    ],
    "risk_areas": [
        {{
            "category": "string",
            "description": "string",
            "severity": "low|medium|high",
            "mitigation": "string",
            "evidence": ["string"]
        }}
    ],
    "signal_gaps": [
        {{
            "competency": "string",
            "status": "missing|weak|conflicting",
            "reason": "string",
            "recommendation": "string",
            "confidence_impact": "string"
        }}
    ],
    "interview_agreement": {{
        "level": "strong_agreement|moderate_agreement|mixed_opinions|conflicting_views",
        "description": "string",
        "agreements": ["string"],
        "disagreements": ["string"],
        "confidence_score": 0.0,
        "evaluator_count": 0
    }},
    "suggested_decision": {{
        "decision": "strong_hire|hire|neutral|no_hire|strong_no_hire|defer",
        "confidence": 0.0,
        "reasoning": "string",
        "key_factors": ["string"],
        "risks_acknowledged": ["string"],
        "next_steps": ["string"]
    }}
}}

Ensure the JSON is valid and complete. Do not include markdown formatting or code blocks."""
        return prompt
    
    async def generate_brief(
        self,
        input_data: DecisionBriefInput,
        candidate_data: Dict[str, Any],
        evaluations: List[Dict[str, Any]],
        role_data: Optional[Dict[str, Any]] = None
    ) -> DecisionBriefOutput:
        """
        Generate a decision brief for a candidate.
        
        Args:
            input_data: Input parameters for brief generation
            candidate_data: Basic candidate information
            evaluations: List of evaluation data dictionaries
            role_data: Role requirements and competencies
            
        Returns:
            DecisionBriefOutput with generated brief content
        """
        start_time = time.time()
        
        # Build context
        context = self._build_candidate_context(candidate_data, evaluations, role_data)
        
        # Build prompt
        prompt = self._build_generation_prompt(
            context,
            input_data.focus_areas,
            input_data.custom_prompt
        )
        
        # Generate using LLM
        raw_output = ""
        model_used = "unknown"
        
        if self.llm_client:
            try:
                response: LLMResponse = await self.llm_client.generate(
                    prompt=prompt,
                    temperature=0.3,  # Lower temperature for more consistent outputs
                    max_tokens=4000,
                )
                raw_output = response.content
                model_used = self.model_name or getattr(response, 'model', 'unknown')
            except Exception as e:
                # Fallback to structured extraction
                raw_output = self._extract_structured_data(candidate_data, evaluations, role_data)
        else:
            # Fallback without LLM
            raw_output = self._extract_structured_data(candidate_data, evaluations, role_data)
        
        # Parse output
        parsed_data = self._parse_llm_output(raw_output)
        
        # Build output object
        processing_time = int((time.time() - start_time) * 1000)
        
        # Calculate overall score from evaluations
        overall_score = self._calculate_overall_score(evaluations)
        
        # Create candidate summary
        candidate_summary = CandidateSummaryBrief(
            name=candidate_data.get('full_name', 'Unknown'),
            role_applied=role_data.get('title', 'Unknown') if role_data else 'Unknown',
            overall_score=overall_score,
            total_evaluations=len(evaluations),
            recommendation_breakdown=self._count_recommendations(evaluations)
        )
        
        # Build final output
        output = DecisionBriefOutput(
            generated_at=datetime.utcnow(),
            candidate=candidate_summary,
            strengths=[
                CandidateStrengths(**s) for s in parsed_data.get('strengths', [])
            ],
            risk_areas=[
                RiskArea(**r) for r in parsed_data.get('risk_areas', [])
            ],
            signal_gaps=[
                SignalGap(**g) for g in parsed_data.get('signal_gaps', [])
            ],
            interview_agreement=InterviewAgreement(**parsed_data.get('interview_agreement', {
                'level': 'moderate_agreement',
                'description': 'Analysis based on available evaluations',
                'agreements': [],
                'disagreements': [],
                'confidence_score': 0.5,
                'evaluator_count': len(evaluations)
            })),
            suggested_decision=SuggestedDecisionOutput(**parsed_data.get('suggested_decision', {
                'decision': 'neutral',
                'confidence': 0.5,
                'reasoning': 'Insufficient data for strong recommendation',
                'key_factors': [],
                'risks_acknowledged': [],
                'next_steps': ['Gather more evaluations for better decision']
            })),
            evaluation_ids=[e.get('id', '') for e in evaluations if e.get('id')],
            model_used=model_used,
            processing_time_ms=processing_time
        )
        
        return output
    
    def _extract_structured_data(
        self,
        candidate_data: Dict[str, Any],
        evaluations: List[Dict[str, Any]],
        role_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract structured data from evaluations without LLM.
        Used as fallback when LLM is unavailable.
        """
        # Extract strengths from evaluations
        strengths = []
        seen_strengths = set()
        
        for eval_data in evaluations:
            if eval_data.get('strengths'):
                # Parse strengths (simple heuristic)
                strength_text = eval_data['strengths']
                if strength_text and len(strength_text) > 10:
                    strengths.append({
                        'category': 'General Strength',
                        'description': strength_text[:500],
                        'evidence': [f"Evaluation by {eval_data.get('interviewer', {}).get('full_name', 'Unknown')}"],
                        'competency_scores': {}
                    })
        
        # Extract risk areas
        risk_areas = []
        for eval_data in evaluations:
            if eval_data.get('weaknesses'):
                weakness_text = eval_data['weaknesses']
                if weakness_text and len(weakness_text) > 10:
                    risk_areas.append({
                        'category': 'Area for Improvement',
                        'description': weakness_text[:500],
                        'severity': 'medium',
                        'mitigation': 'Consider in final evaluation',
                        'evidence': [f"Evaluation by {eval_data.get('interviewer', {}).get('full_name', 'Unknown')}"]
                    })
        
        # Analyze interview agreement
        agreement_level = self._analyze_agreement(evaluations)
        
        # Generate suggested decision
        suggested = self._generate_suggested_decision(evaluations, overall_score=self._calculate_overall_score(evaluations))
        
        return {
            'strengths': strengths[:5],  # Limit to 5
            'risk_areas': risk_areas[:5],
            'signal_gaps': self._detect_signal_gaps(evaluations, role_data),
            'interview_agreement': agreement_level,
            'suggested_decision': suggested
        }
    
    def _parse_llm_output(self, raw_output: str) -> Dict[str, Any]:
        """Parse LLM output into structured data."""
        import re
        
        # Try to extract JSON from the output
        json_match = re.search(r'\{[\s\S]*\}', raw_output)
        
        if json_match:
            json_str = json_match.group()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        # Return empty structure if parsing fails
        return {
            'strengths': [],
            'risk_areas': [],
            'signal_gaps': [],
            'interview_agreement': {},
            'suggested_decision': {}
        }
    
    def _calculate_overall_score(self, evaluations: List[Dict[str, Any]]) -> float:
        """Calculate average overall score from evaluations."""
        if not evaluations:
            return 0.0
        
        all_scores = []
        for eval_data in evaluations:
            scores = eval_data.get('scores', {})
            for score_data in scores.values():
                if isinstance(score_data, dict):
                    score = score_data.get('score')
                    if isinstance(score, (int, float)):
                        all_scores.append(float(score))
                elif isinstance(score_data, (int, float)):
                    all_scores.append(float(score_data))
        
        if not all_scores:
            return 0.0
        
        return round(sum(all_scores) / len(all_scores), 2)
    
    def _count_recommendations(self, evaluations: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count recommendation types from evaluations."""
        counts = {
            'strong_hire': 0,
            'hire': 0,
            'neutral': 0,
            'no_hire': 0,
            'strong_no_hire': 0
        }
        
        for eval_data in evaluations:
            rec = eval_data.get('recommendation', '').lower()
            if rec in counts:
                counts[rec] += 1
            elif 'strong' in rec and 'hire' in rec:
                counts['strong_hire'] += 1
            elif 'hire' in rec:
                counts['hire'] += 1
            elif 'no' in rec:
                counts['no_hire'] += 1
            elif 'strong' in rec and 'no' in rec:
                counts['strong_no_hire'] += 1
            else:
                counts['neutral'] += 1
        
        return counts
    
    def _analyze_agreement(self, evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze agreement between evaluators."""
        if len(evaluations) < 2:
            return {
                'level': 'moderate_agreement',
                'description': 'Single evaluation - agreement cannot be assessed',
                'agreements': [],
                'disagreements': [],
                'confidence_score': 0.5,
                'evaluator_count': len(evaluations)
            }
        
        # Compare recommendations
        recommendations = [e.get('recommendation', 'neutral') for e in evaluations]
        
        # Check score variance
        scores_per_competency: Dict[str, List[float]] = {}
        for eval_data in evaluations:
            scores = eval_data.get('scores', {})
            for comp, score_data in scores.items():
                if isinstance(score_data, dict):
                    score = score_data.get('score')
                else:
                    score = score_data
                if isinstance(score, (int, float)) and comp not in scores_per_competency:
                    scores_per_competency[comp] = []
                if isinstance(score, (int, float)):
                    scores_per_competency[comp].append(float(score))
        
        # Calculate variance
        variances = []
        for comp_scores in scores_per_competency.values():
            if len(comp_scores) >= 2:
                mean = sum(comp_scores) / len(comp_scores)
                variance = sum((s - mean) ** 2 for s in comp_scores) / len(comp_scores)
                variances.append(variance)
        
        avg_variance = sum(variances) / len(variances) if variances else 0
        
        # Determine agreement level
        if avg_variance < 0.2:
            level = 'strong_agreement'
            description = 'Strong agreement among evaluators on competency scores'
        elif avg_variance < 0.5:
            level = 'moderate_agreement'
            description = 'Moderate agreement among evaluators with minor differences'
        elif avg_variance < 1.0:
            level = 'mixed_opinions'
            description = 'Mixed opinions with some significant differences'
        else:
            level = 'conflicting_views'
            description = 'Conflicting views among evaluators'
        
        return {
            'level': level,
            'description': description,
            'agreements': ['Scores are consistent for ' + ', '.join(scores_per_competency.keys()[:3])] if scores_per_competency else [],
            'disagreements': ['Some variance in scoring for ' + str(len(variances)) + ' competencies'] if variances else [],
            'confidence_score': round(max(0.5 - avg_variance * 0.3, 0.1), 2),
            'evaluator_count': len(evaluations)
        }
    
    def _detect_signal_gaps(
        self,
        evaluations: List[Dict[str, Any]],
        role_data: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, str]]:
        """Detect signal gaps in evaluations."""
        gaps = []
        
        # Get role competencies
        role_competencies = set()
        if role_data and isinstance(role_data.get('core_competencies'), list):
            for comp in role_data['core_competencies']:
                if isinstance(comp, dict):
                    role_competencies.add(comp.get('name', ''))
                else:
                    role_competencies.add(str(comp))
        
        # Get evaluated competencies
        evaluated_comps = set()
        for eval_data in evaluations:
            scores = eval_data.get('scores', {})
            for comp in scores.keys():
                evaluated_comps.add(comp)
        
        # Check for missing competencies
        missing_comps = role_competencies - evaluated_comps
        for comp in missing_comps:
            if comp:
                gaps.append({
                    'competency': comp,
                    'status': 'missing',
                    'reason': f'No evaluation data for {comp}',
                    'recommendation': f'Conduct additional interview focusing on {comp}',
                    'confidence_impact': f'High impact - {comp} is a required competency'
                })
        
        # Check for low confidence
        low_conf_evals = [e for e in evaluations if e.get('confidence', 5) < 3]
        if low_conf_evals:
            gaps.append({
                'competency': 'Overall Confidence',
                'status': 'weak',
                'reason': f'{len(low_conf_evals)} evaluation(s) have confidence below 3',
                'recommendation': 'Consider gathering additional feedback or clarification',
                'confidence_impact': 'Moderate impact on overall assessment reliability'
            })
        
        return gaps
    
    def _generate_suggested_decision(
        self,
        evaluations: List[Dict[str, Any]],
        overall_score: float
    ) -> Dict[str, Any]:
        """Generate a suggested hiring decision."""
        # Calculate recommendation counts
        rec_counts = self._count_recommendations(evaluations)
        
        # Calculate weighted score
        weights = {'strong_hire': 2, 'hire': 1, 'neutral': 0, 'no_hire': -1, 'strong_no_hire': -2}
        total_weight = sum(count * weights.get(rec, 0) for rec, count in rec_counts.items())
        rec_score = total_weight / max(sum(rec_counts.values()), 1)
        
        # Combine with overall score
        combined_score = (overall_score / 5) * 0.4 + (rec_score + 2) / 4 * 0.6
        
        # Determine decision
        if combined_score >= 0.85:
            decision = 'strong_hire'
            reasoning = 'Strong positive signals across all evaluations'
        elif combined_score >= 0.65:
            decision = 'hire'
            reasoning = 'Overall positive assessment with some areas for consideration'
        elif combined_score >= 0.45:
            decision = 'neutral'
            reasoning = 'Mixed signals require careful consideration'
        elif combined_score >= 0.25:
            decision = 'no_hire'
            reasoning = 'Concerns outweigh positive signals'
        else:
            decision = 'strong_no_hire'
            reasoning = 'Significant concerns across multiple evaluations'
        
        # Generate key factors
        key_factors = []
        if overall_score >= 4:
            key_factors.append('Strong overall performance scores')
        elif overall_score < 3:
            key_factors.append('Below average performance scores')
        
        positive_recs = rec_counts['strong_hire'] + rec_counts['hire']
        negative_recs = rec_counts['no_hire'] + rec_counts['strong_no_hire']
        if positive_recs > negative_recs:
            key_factors.append('Majority positive hiring recommendations')
        elif negative_recs > positive_recs:
            key_factors.append('Majority negative hiring recommendations')
        
        # Generate next steps
        next_steps = []
        if len(evaluations) < 2:
            next_steps.append('Gather additional evaluations for more robust decision')
        if decision == 'neutral':
            next_steps.append('Conduct follow-up interview to clarify concerns')
        if decision in ['strong_hire', 'hire']:
            next_steps.append('Proceed with offer preparation')
        elif decision in ['no_hire', 'strong_no_hire']:
            next_steps.append('Document decision and provide feedback to candidate')
        
        return {
            'decision': decision,
            'confidence': round(min(combined_score + 0.2, 0.95), 2),
            'reasoning': reasoning,
            'key_factors': key_factors if key_factors else ['Based on available evaluation data'],
            'risks_acknowledged': [],
            'next_steps': next_steps if next_steps else ['Review final decision with hiring team']
        }

