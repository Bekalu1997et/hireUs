from typing import Optional, List, Dict, Any
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Candidate
from app.schemas.candidate import CandidateCreate, CandidateUpdate


class CandidateRepository:
    """Repository for candidate operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: The async database session.
        """
        self.db = db

    async def get_by_id(self, candidate_id: str) -> Optional[Candidate]:
        """
        Get a candidate by ID.
        
        Args:
            candidate_id: The ID of the candidate.
            
        Returns:
            The candidate if found, None otherwise.
        """
        result = await self.db.execute(
            select(Candidate).where(Candidate.id == candidate_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str, organization_id: str) -> Optional[Candidate]:
        """
        Get a candidate by email within an organization.
        
        Args:
            email: The email of the candidate.
            organization_id: The ID of the organization.
            
        Returns:
            The candidate if found, None otherwise.
        """
        result = await self.db.execute(
            select(Candidate).where(
                and_(
                    Candidate.email == email,
                    Candidate.organization_id == organization_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        organization_id: str,
        skip: int = 0,
        limit: int = 20,
        role_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        is_active: Optional[bool] = None,
        source: Optional[str] = None,
    ) -> List[Candidate]:
        """
        Get all candidates for an organization with optional filters.
        
        Args:
            organization_id: The ID of the organization.
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            role_id: Filter by role ID.
            workflow_id: Filter by workflow ID.
            is_active: Filter by active status.
            source: Filter by source.
            
        Returns:
            List of candidates.
        """
        query = select(Candidate).where(Candidate.organization_id == organization_id)

        if role_id is not None:
            query = query.where(Candidate.role_id == role_id)
        if workflow_id is not None:
            query = query.where(Candidate.workflow_id == workflow_id)
        if is_active is not None:
            query = query.where(Candidate.is_active == is_active)
        if source is not None:
            query = query.where(Candidate.source == source)

        query = query.offset(skip).limit(limit).order_by(Candidate.created_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count(
        self,
        organization_id: str,
        role_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        is_active: Optional[bool] = None,
        source: Optional[str] = None,
    ) -> int:
        """
        Count candidates with optional filters.
        
        Args:
            organization_id: The ID of the organization.
            role_id: Filter by role ID.
            workflow_id: Filter by workflow ID.
            is_active: Filter by active status.
            source: Filter by source.
            
        Returns:
            Total count of candidates.
        """
        query = select(func.count()).select_from(Candidate).where(
            Candidate.organization_id == organization_id
        )

        if role_id is not None:
            query = query.where(Candidate.role_id == role_id)
        if workflow_id is not None:
            query = query.where(Candidate.workflow_id == workflow_id)
        if is_active is not None:
            query = query.where(Candidate.is_active == is_active)
        if source is not None:
            query = query.where(Candidate.source == source)

        result = await self.db.execute(query)
        return result.scalar_one()

    async def search(
        self,
        organization_id: str,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Candidate]:
        """
        Search candidates by name, email, or company.
        
        Args:
            organization_id: The ID of the organization.
            query: Search query string.
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            
        Returns:
            List of matching candidates.
        """
        search_pattern = f"%{query}%"
        stmt = select(Candidate).where(
            and_(
                Candidate.organization_id == organization_id,
                or_(
                    Candidate.full_name.ilike(search_pattern),
                    Candidate.email.ilike(search_pattern),
                )
            )
        ).offset(skip).limit(limit).order_by(Candidate.created_at.desc())

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, candidate_data: CandidateCreate) -> Candidate:
        """
        Create a new candidate.
        
        Args:
            candidate_data: The candidate data to create.
            
        Returns:
            The created candidate.
        """
        candidate = Candidate(
            email=candidate_data.email,
            full_name=candidate_data.full_name,
            phone=candidate_data.phone,
            linkedin_url=candidate_data.linkedin_url,
            portfolio_url=candidate_data.portfolio_url,
            resume_url=candidate_data.resume_url,
            source=candidate_data.source,
            status=candidate_data.status or "applied",
            organization_id=candidate_data.organization_id,
            role_id=candidate_data.role_id,
            workflow_id=candidate_data.workflow_id,
            candidate_metadata=candidate_data.candidate_metadata,
        )
        
        self.db.add(candidate)
        await self.db.commit()
        await self.db.refresh(candidate)
        return candidate

    async def update(
        self,
        candidate_id: str,
        candidate_data: CandidateUpdate,
    ) -> Optional[Candidate]:
        """
        Update an existing candidate.
        
        Args:
            candidate_id: The ID of the candidate to update.
            candidate_data: The updated candidate data.
            
        Returns:
            The updated candidate if found, None otherwise.
        """
        candidate = await self.get_by_id(candidate_id)
        if not candidate:
            return None

        update_data = candidate_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(candidate, field, value)

        await self.db.commit()
        await self.db.refresh(candidate)
        return candidate

    async def delete(self, candidate_id: str) -> bool:
        """
        Delete a candidate (soft delete by setting is_active to False).
        
        Args:
            candidate_id: The ID of the candidate to delete.
            
        Returns:
            True if deleted, False if not found.
        """
        candidate = await self.get_by_id(candidate_id)
        if not candidate:
            return False

        candidate.is_active = False
        await self.db.commit()
        return True

    async def activate(self, candidate_id: str) -> Optional[Candidate]:
        """
        Activate a candidate.
        
        Args:
            candidate_id: The ID of the candidate to activate.
            
        Returns:
            The activated candidate if found, None otherwise.
        """
        candidate = await self.get_by_id(candidate_id)
        if not candidate:
            return None

        candidate.is_active = True
        await self.db.commit()
        await self.db.refresh(candidate)
        return candidate

    async def deactivate(self, candidate_id: str) -> Optional[Candidate]:
        """
        Deactivate a candidate.
        
        Args:
            candidate_id: The ID of the candidate to deactivate.
            
        Returns:
            The deactivated candidate if found, None otherwise.
        """
        candidate = await self.get_by_id(candidate_id)
        if not candidate:
            return None

        candidate.is_active = False
        await self.db.commit()
        await self.db.refresh(candidate)
        return candidate

    async def exists(self, candidate_id: str) -> bool:
        """
        Check if a candidate exists.
        
        Args:
            candidate_id: The ID of the candidate.
            
        Returns:
            True if exists, False otherwise.
        """
        result = await self.db.execute(
            select(Candidate.id).where(Candidate.id == candidate_id)
        )
        return result.scalar_one_or_none() is not None

    async def exists_by_email(self, email: str, organization_id: str) -> bool:
        """
        Check if a candidate with email exists in organization.
        
        Args:
            email: The email to check.
            organization_id: The ID of the organization.
            
        Returns:
            True if exists, False otherwise.
        """
        result = await self.db.execute(
            select(Candidate.id).where(
                and_(
                    Candidate.email == email,
                    Candidate.organization_id == organization_id
                )
            )
        )
        return result.scalar_one_or_none() is not None

    async def get_stats(self, organization_id: str) -> Dict[str, Any]:
        """
        Get candidate statistics for an organization.
        
        Args:
            organization_id: The ID of the organization.
            
        Returns:
            Dictionary with candidate statistics.
        """
        # Total and active counts
        total_result = await self.db.execute(
            select(func.count()).select_from(Candidate).where(
                Candidate.organization_id == organization_id
            )
        )
        total = total_result.scalar_one()

        active_result = await self.db.execute(
            select(func.count()).select_from(Candidate).where(
                and_(
                    Candidate.organization_id == organization_id,
                    Candidate.is_active == True
                )
            )
        )
        active = active_result.scalar_one()

        inactive = total - active

        # By source
        source_result = await self.db.execute(
            select(Candidate.source, func.count())
            .where(Candidate.organization_id == organization_id)
            .group_by(Candidate.source)
        )
        by_source = {row[0]: row[1] for row in source_result.all() if row[0]}

        # By role
        role_result = await self.db.execute(
            select(Candidate.role_id, func.count())
            .where(
                and_(
                    Candidate.organization_id == organization_id,
                    Candidate.role_id.isnot(None)
                )
            )
            .group_by(Candidate.role_id)
        )
        by_role = {row[0]: row[1] for row in role_result.all() if row[0]}

        return {
            "total_candidates": total,
            "active_candidates": active,
            "inactive_candidates": inactive,
            "by_source": by_source,
            "by_role": by_role,
        }
