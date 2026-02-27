"""
Decision Brief Service.
Business logic for generating and managing decision briefs.
"""
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Candidate, Role
from app.modules.decisions.repository import DecisionBriefRepository
from app.modules.decisions.ai.schema import (
    DecisionBriefInput,
    DecisionBriefOutput,
)
from app.modules.decisions.ai.decision_brief_generator import DecisionBriefGenerator


class DecisionBriefService:
    """
    Service for managing and generating decision briefs.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = DecisionBriefRepository(db)
        self.generator = DecisionBriefGenerator()
    
    async def generate_brief(
        self,
        input_data: DecisionBriefInput,
        organization_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Generate a decision brief for a candidate.
        
        Args:
            input_data: Input parameters for brief generation
            organization_id: ID of the organization
            user_id: ID of the user generating the brief
            
        Returns:
            Dictionary with brief data and metadata
        """
        # Get candidate details
        candidate_data = await self.repository.get_candidate_with_details(
            input_data.candidate_id
        )
        
        if not candidate_data:
            raise ValueError(f"Candidate with ID {input_data.candidate_id} not found")
        
        # Verify organization access
        if candidate_data.get("organization_id") != organization_id:
            # For now, allow if candidate exists
            # In production, check proper access
            pass
        
        # Get evaluations
        evaluations = await self.repository.get_candidate_evaluations(
            input_data.candidate_id,
            submitted_only=True
        )
        
        if not evaluations:
            raise ValueError("No submitted evaluations found for this candidate")
        
        # Get role data
        role_data = None
        if candidate_data.get("role"):
            role_data = {
                "title": candidate_data["role"].get("title"),
                "mission": candidate_data["role"].get("mission"),
                "core_competencies": candidate_data["role"].get("core_competencies", []),
                "must_have": candidate_data["role"].get("must_have", []),
                "nice_to_have": candidate_data["role"].get("nice_to_have", []),
            }
        
        # Generate brief
        brief_output = await self.generator.generate_brief(
            input_data=input_data,
            candidate_data=candidate_data,
            evaluations=evaluations,
            role_data=role_data
        )
        
        # Build response
        response = {
            "id": str(uuid.uuid4()),
            "candidate_id": input_data.candidate_id,
            "candidate_name": candidate_data["full_name"],
            "role_title": candidate_data["role"]["title"] if candidate_data["role"] else "Unknown",
            "organization_id": organization_id,
            "generated_by": user_id,
            "generated_at": brief_output.generated_at.isoformat(),
            "content": brief_output.model_dump(),
        }
        
        return response
    
    async def get_candidate_briefs(
        self,
        candidate_id: str,
        organization_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all briefs for a candidate.
        
        Note: In production, these would be stored in a database table.
        For now, returns a list with the latest generated brief if available.
        """
        # Get candidate data
        candidate_data = await self.repository.get_candidate_with_details(candidate_id)
        
        if not candidate_data:
            raise ValueError(f"Candidate with ID {candidate_id} not found")
        
        # Get evaluations
        evaluations = await self.repository.get_candidate_evaluations(
            candidate_id,
            submitted_only=True
        )
        
        if not evaluations:
            return []
        
        # Generate current stats
        stats = await self.repository.get_evaluation_statistics(candidate_id)
        
        # Build brief summary
        brief_summary = {
            "candidate_id": candidate_id,
            "candidate_name": candidate_data["full_name"],
            "role_title": candidate_data["role"]["title"] if candidate_data["role"] else "Unknown",
            "total_evaluations": stats["total_evaluations"],
            "overall_average": stats["overall_average"],
            "recommendation_counts": stats["recommendation_counts"],
            "last_updated": datetime.utcnow().isoformat(),
        }
        
        return [brief_summary]
    
    async def get_brief_statistics(
        self,
        candidate_id: str
    ) -> Dict[str, Any]:
        """
        Get statistics for a candidate's evaluation data.
        """
        return await self.repository.get_evaluation_statistics(candidate_id)
    
    async def get_comparable_candidates(
        self,
        organization_id: str,
        role_id: Optional[str] = None,
        min_evaluations: int = 1,
        skip: int = 0,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get candidates eligible for decision briefs.
        """
        candidates = await self.repository.get_candidates_for_organization(
            organization_id=organization_id,
            has_evaluations=True,
            min_evaluations=min_evaluations,
            skip=skip,
            limit=limit
        )
        
        total = await self.repository.count_candidates_with_evaluations(
            organization_id,
            min_evaluations
        )
        
        return {
            "candidates": candidates,
            "count": len(candidates),
            "total": total,
            "page": skip // limit + 1 if limit > 0 else 1,
            "page_size": limit,
            "total_pages": (total + limit - 1) // limit if limit > 0 else 1
        }
    
    async def generate_bulk_briefs(
        self,
        candidate_ids: List[str],
        organization_id: str,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """
        Generate briefs for multiple candidates.
        """
        results = []
        errors = []
        
        for candidate_id in candidate_ids:
            try:
                brief = await self.generate_brief(
                    input_data=DecisionBriefInput(candidate_id=candidate_id),
                    organization_id=organization_id,
                    user_id=user_id
                )
                results.append(brief)
            except Exception as e:
                errors.append({
                    "candidate_id": candidate_id,
                    "error": str(e)
                })
        
        return {
            "successful": results,
            "failed": errors,
            "total": len(candidate_ids),
            "success_count": len(results),
            "failure_count": len(errors)
        }
    
    async def get_signal_gap_analysis(
        self,
        candidate_id: str
    ) -> Dict[str, Any]:
        """
        Get signal gap analysis for a candidate.
        """
        # Get candidate data
        candidate_data = await self.repository.get_candidate_with_details(candidate_id)
        
        if not candidate_data:
            raise ValueError(f"Candidate with ID {candidate_id} not found")
        
        # Get evaluations
        evaluations = await self.repository.get_candidate_evaluations(
            candidate_id,
            submitted_only=True
        )
        
        # Get role competencies
        role_data = None
        if candidate_data.get("role"):
            role_data = {
                "core_competencies": candidate_data["role"].get("core_competencies", []),
            }
        
        # Use generator to detect gaps
        signal_gaps = self.generator._detect_signal_gaps(evaluations, role_data)
        
        # Analyze agreement
        agreement = self.generator._analyze_agreement(evaluations)
        
        # Get stats
        stats = await self.repository.get_evaluation_statistics(candidate_id)
        
        return {
            "candidate_id": candidate_id,
            "candidate_name": candidate_data["full_name"],
            "total_evaluations": stats["total_evaluations"],
            "overall_signal_strength": self._calculate_signal_strength(
                stats, signal_gaps, agreement
            ),
            "signal_gaps": signal_gaps,
            "interview_agreement": agreement,
            "evaluation_stats": {
                "overall_average": stats["overall_average"],
                "average_confidence": stats.get("average_confidence", 0),
                "recommendation_counts": stats["recommendation_counts"],
            }
        }
    
    def _calculate_signal_strength(
        self,
        stats: Dict[str, Any],
        signal_gaps: List[Dict[str, Any]],
        agreement: Dict[str, Any]
    ) -> str:
        """
        Calculate overall signal strength.
        """
        # Check for signal gaps
        if signal_gaps:
            high_severity_gaps = [g for g in signal_gaps if g.get("status") == "missing"]
            if high_severity_gaps:
                return "weak"
        
        # Check evaluation count
        if stats["total_evaluations"] == 0:
            return "none"
        
        # Check confidence
        avg_confidence = stats.get("average_confidence", 0)
        if avg_confidence < 2.5:
            return "weak"
        elif avg_confidence < 3.5:
            return "moderate"
        
        # Check agreement
        agreement_level = agreement.get("level", "")
        if agreement_level == "conflicting_views":
            return "moderate"
        elif agreement_level == "mixed_opinions":
            return "moderate"
        
        return "strong"

