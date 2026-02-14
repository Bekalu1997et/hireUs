from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.candicates.repository import CandidateRepository
from app.schemas.candidate import (
    CandidateCreate,
    CandidateUpdate,
    CandidateResponse,
    CandidateListResponse,
    CandidateSearchRequest,
    CandidateSearchResponse,
    CandidateStats,
)


class CandidateService:
    """Service for candidate operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize the service with a database session.
        
        Args:
            db: The async database session.
        """
        self.db = db
        self.repository = CandidateRepository(db)

    async def create_candidate(self, candidate_data: CandidateCreate) -> CandidateResponse:
        """
        Create a new candidate.
        
        Args:
            candidate_data: The candidate data to create.
            
        Returns:
            The created candidate.
        """
        # Check if email already exists in the organization
        exists = await self.repository.exists_by_email(
            candidate_data.email, 
            candidate_data.organization_id
        )
        if exists:
            raise ValueError("Candidate with this email already exists in the organization")

        # Generate ID if not provided
        if not hasattr(candidate_data, 'id') or not candidate_data.id:
            candidate_data.id = str(uuid.uuid4())

        candidate = await self.repository.create(candidate_data)
        return CandidateResponse.model_validate(candidate)

    async def get_candidate(self, candidate_id: str) -> Optional[CandidateResponse]:
        """
        Get a candidate by ID.
        
        Args:
            candidate_id: The ID of the candidate.
            
        Returns:
            The candidate if found, None otherwise.
        """
        candidate = await self.repository.get_by_id(candidate_id)
        if not candidate:
            return None
        return CandidateResponse.model_validate(candidate)

    async def get_candidates(
        self,
        organization_id: str,
        skip: int = 0,
        limit: int = 20,
        role_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        is_active: Optional[bool] = None,
        source: Optional[str] = None,
    ) -> CandidateListResponse:
        """
        Get candidates with pagination and filters.
        
        Args:
            organization_id: The ID of the organization.
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            role_id: Filter by role ID.
            workflow_id: Filter by workflow ID.
            is_active: Filter by active status.
            source: Filter by source.
            
        Returns:
            List of candidates with pagination info.
        """
        candidates = await self.repository.get_all(
            organization_id=organization_id,
            skip=skip,
            limit=limit,
            role_id=role_id,
            workflow_id=workflow_id,
            is_active=is_active,
            source=source,
        )
        
        total = await self.repository.count(
            organization_id=organization_id,
            role_id=role_id,
            workflow_id=workflow_id,
            is_active=is_active,
            source=source,
        )

        return CandidateListResponse(
            candidates=[CandidateResponse.model_validate(c) for c in candidates],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def search_candidates(
        self,
        organization_id: str,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> CandidateSearchResponse:
        """
        Search candidates by name, email, or company.
        
        Args:
            organization_id: The ID of the organization.
            query: Search query string.
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            
        Returns:
            Search results with pagination info.
        """
        candidates = await self.repository.search(
            organization_id=organization_id,
            query=query,
            skip=skip,
            limit=limit,
        )
        
        total = len(candidates)  # For search, we return all matches

        return CandidateSearchResponse(
            candidates=[CandidateResponse.model_validate(c) for c in candidates],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def update_candidate(
        self,
        candidate_id: str,
        candidate_data: CandidateUpdate,
    ) -> Optional[CandidateResponse]:
        """
        Update a candidate.
        
        Args:
            candidate_id: The ID of the candidate to update.
            candidate_data: The updated candidate data.
            
        Returns:
            The updated candidate if found, None otherwise.
        """
        candidate = await self.repository.update(candidate_id, candidate_data)
        if not candidate:
            return None
        return CandidateResponse.model_validate(candidate)

    async def delete_candidate(self, candidate_id: str) -> bool:
        """
        Delete a candidate (soft delete).
        
        Args:
            candidate_id: The ID of the candidate to delete.
            
        Returns:
            True if deleted, False if not found.
        """
        return await self.repository.delete(candidate_id)

    async def activate_candidate(self, candidate_id: str) -> Optional[CandidateResponse]:
        """
        Activate a candidate.
        
        Args:
            candidate_id: The ID of the candidate to activate.
            
        Returns:
            The activated candidate if found, None otherwise.
        """
        candidate = await self.repository.activate(candidate_id)
        if not candidate:
            return None
        return CandidateResponse.model_validate(candidate)

    async def deactivate_candidate(self, candidate_id: str) -> Optional[CandidateResponse]:
        """
        Deactivate a candidate.
        
        Args:
            candidate_id: The ID of the candidate to deactivate.
            
        Returns:
            The deactivated candidate if found, None otherwise.
        """
        candidate = await self.repository.deactivate(candidate_id)
        if not candidate:
            return None
        return CandidateResponse.model_validate(candidate)

    async def get_candidate_stats(self, organization_id: str) -> CandidateStats:
        """
        Get candidate statistics for an organization.
        
        Args:
            organization_id: The ID of the organization.
            
        Returns:
            Candidate statistics.
        """
        stats = await self.repository.get_stats(organization_id)
        return CandidateStats(**stats)

    async def check_email_exists(
        self, 
        email: str, 
        organization_id: str
    ) -> bool:
        """
        Check if a candidate email exists in the organization.
        
        Args:
            email: The email to check.
            organization_id: The ID of the organization.
            
        Returns:
            True if exists, False otherwise.
        """
        return await self.repository.exists_by_email(email, organization_id)

