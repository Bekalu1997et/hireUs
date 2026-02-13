"""
Service layer for roles and competencies operations.

Handles business logic for role management including validation of
competencies and weight normalization.
"""
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.roles.repository import RolesRepository
from app.db.models import Role
from app.schemas.role import RoleCreate, RoleUpdate


class RolesService:
    """Service for roles and competencies operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = RolesRepository(db)
    
    def _validate_competencies(self, competencies_data: List[dict]) -> None:
        """
        Validate that competencies meet business rules.
        
        Rules:
        - At least one competency must be defined
        - Competency weights must sum to approximately 1.0 (±0.01 tolerance)
        
        Args:
            competencies_data: List of competency dictionaries
            
        Raises:
            HTTPException: If validation fails
        """
        if not competencies_data or len(competencies_data) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one competency is required"
            )
        
        # Calculate total weight
        total_weight = sum(comp["weight"] for comp in competencies_data)
        
        # Check if weights sum to approximately 1.0 (tolerance of 0.01)
        if abs(total_weight - 1.0) > 0.01:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Competency weights must sum to 1.0 (current sum: {total_weight:.3f})"
            )
    
    def _normalize_competency_weights(self, competencies_data: List[dict]) -> List[dict]:
        """
        Normalize competency weights to sum to exactly 1.0.
        
        This is useful when weights are close to 1.0 but not exact due to
        floating point precision or user input.
        
        Args:
            competencies_data: List of competency dictionaries
            
        Returns:
            List of competency dictionaries with normalized weights
        """
        total_weight = sum(comp["weight"] for comp in competencies_data)
        
        if total_weight == 0:
            # If all weights are 0, distribute equally
            equal_weight = 1.0 / len(competencies_data)
            return [
                {**comp, "weight": equal_weight}
                for comp in competencies_data
            ]
        
        # Normalize weights to sum to 1.0
        return [
            {**comp, "weight": comp["weight"] / total_weight}
            for comp in competencies_data
        ]
    
    async def create_role(
        self,
        role_data: RoleCreate,
        organization_id: int
    ) -> Role:
        """
        Create a new role with competencies.
        
        Validates competencies and normalizes weights before creation.
        
        Args:
            role_data: Role creation data
            organization_id: Organization ID
            
        Returns:
            Created Role object
            
        Raises:
            HTTPException: If validation fails
        """
        # Convert competencies to dict format
        competencies_data = [
            {
                "name": comp.name,
                "description": comp.description,
                "weight": comp.weight
            }
            for comp in role_data.competencies
        ]
        
        # Validate competencies
        self._validate_competencies(competencies_data)
        
        # Normalize weights to ensure they sum to exactly 1.0
        competencies_data = self._normalize_competency_weights(competencies_data)
        
        # Create role
        role = await self.repository.create_role(
            title=role_data.title,
            description=role_data.description,
            seniority_level=role_data.seniority_level,
            organization_id=organization_id,
            competencies_data=competencies_data
        )
        
        await self.db.commit()
        
        return role
    
    async def get_role(self, role_id: int, organization_id: int) -> Role:
        """
        Get a role by ID.
        
        Validates that the role belongs to the specified organization.
        
        Args:
            role_id: Role ID
            organization_id: Organization ID
            
        Returns:
            Role object
            
        Raises:
            HTTPException: If role not found or doesn't belong to organization
        """
        role = await self.repository.get_role_by_id(role_id)
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        if role.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Role does not belong to your organization"
            )
        
        return role
    
    async def list_roles(
        self,
        organization_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Role]:
        """
        List all roles for an organization.
        
        Args:
            organization_id: Organization ID
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of Role objects
        """
        return await self.repository.list_roles_by_organization(
            organization_id=organization_id,
            skip=skip,
            limit=limit
        )
    
    async def update_role(
        self,
        role_id: int,
        role_data: RoleUpdate,
        organization_id: int
    ) -> Role:
        """
        Update a role.
        
        Validates that the role belongs to the organization and validates
        competencies if they are being updated.
        
        Args:
            role_id: Role ID
            role_data: Role update data
            organization_id: Organization ID
            
        Returns:
            Updated Role object
            
        Raises:
            HTTPException: If role not found, doesn't belong to organization,
                          or validation fails
        """
        # Verify role exists and belongs to organization
        await self.get_role(role_id, organization_id)
        
        # Prepare competencies data if provided
        competencies_data = None
        if role_data.competencies is not None:
            competencies_data = [
                {
                    "name": comp.name,
                    "description": comp.description,
                    "weight": comp.weight
                }
                for comp in role_data.competencies
            ]
            
            # Validate and normalize competencies
            self._validate_competencies(competencies_data)
            competencies_data = self._normalize_competency_weights(competencies_data)
        
        # Update role
        role = await self.repository.update_role(
            role_id=role_id,
            title=role_data.title,
            description=role_data.description,
            seniority_level=role_data.seniority_level,
            competencies_data=competencies_data
        )
        
        await self.db.commit()
        
        return role
    
    async def delete_role(self, role_id: int, organization_id: int) -> None:
        """
        Delete a role.
        
        Validates that the role belongs to the organization before deletion.
        
        Args:
            role_id: Role ID
            organization_id: Organization ID
            
        Raises:
            HTTPException: If role not found or doesn't belong to organization
        """
        # Verify role exists and belongs to organization
        await self.get_role(role_id, organization_id)
        
        # Delete role
        deleted = await self.repository.delete_role(role_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        await self.db.commit()
