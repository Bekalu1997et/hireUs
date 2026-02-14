"""
Role service for business logic.
Handles role CRUD operations and AI blueprint generation.
"""
import uuid
import re
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.db.models import Role, Organization
from app.schemas.role import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RoleListResponse,
    RoleDetailResponse,
    AIGeneratedBlueprint,
    GenerateBlueprintRequest,
    GenerateBlueprintResponse,
)
from app.modules.roles.ai import (
    RoleBlueprintInput,
    get_blueprint_generator,
)


class RoleService:
    """
    Role service for business logic operations.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize with database session.
        """
        self.db = db
        self.blueprint_generator = get_blueprint_generator()
    
    def _generate_slug(self, title: str) -> str:
        """
        Generate URL-friendly slug from title.
        """
        # Convert to lowercase and replace spaces with hyphens
        slug = title.lower().strip()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_-]+', '-', slug)
        slug = re.sub(r'^-+|-+$', '', slug)
        # Add unique suffix
        slug = f"{slug}-{uuid.uuid4().hex[:8]}"
        return slug
    
    def _model_to_response(self, role: Role) -> RoleResponse:
        """Convert database model to response schema."""
        return RoleResponse(
            id=role.id,
            organization_id=role.organization_id,
            title=role.title,
            slug=role.slug,
            description=role.description,
            seniority=role.seniority,
            department=role.department,
            tech_stack=role.tech_stack or [],
            core_competencies=role.core_competencies or [],
            interview_stages=role.interview_stages or [],
            mission=role.mission,
            must_have=role.must_have or {},
            nice_to_have=role.nice_to_have or {},
            is_active=role.is_active,
            created_by=role.created_by,
            created_at=role.created_at,
            updated_at=role.updated_at,
        )
    
    async def create(
        self, 
        role_data: RoleCreate, 
        user_id: Optional[str] = None
    ) -> RoleResponse:
        """
        Create a new role.
        """
        # Verify organization exists
        org_query = select(Organization).where(
            Organization.id == role_data.organization_id,
            Organization.is_active == True
        )
        org_result = await self.db.execute(org_query)
        org = org_result.scalar_one_or_none()
        
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Create role
        role = Role(
            id=str(uuid.uuid4()),
            organization_id=role_data.organization_id,
            title=role_data.title,
            slug=self._generate_slug(role_data.title),
            description=role_data.description,
            seniority=role_data.seniority,
            department=role_data.department,
            tech_stack=role_data.tech_stack,
            core_competencies=role_data.core_competencies,
            interview_stages=role_data.interview_stages,
            mission=role_data.mission,
            must_have=role_data.must_have,
            nice_to_have=role_data.nice_to_have,
            created_by=user_id,
        )
        
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        
        return self._model_to_response(role)
    
    async def get_by_id(self, role_id: str) -> RoleDetailResponse:
        """
        Get role by ID with full details.
        """
        query = select(Role).where(Role.id == role_id)
        result = await self.db.execute(query)
        role = result.scalar_one_or_none()
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        return self._model_to_response(role)
    
    async def get_all(
        self,
        organization_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> RoleListResponse:
        """
        Get paginated list of roles.
        """
        # Build query
        query = select(Role)
        
        filters = []
        if organization_id:
            filters.append(Role.organization_id == organization_id)
        if is_active is not None:
            filters.append(Role.is_active == is_active)
        if search:
            search_term = f"%{search}%"
            filters.append(
                or_(
                    Role.title.ilike(search_term),
                    Role.seniority.ilike(search_term),
                    Role.department.ilike(search_term)
                )
            )
        
        if filters:
            query = query.where(and_(*filters))
        
        # Get total count
        count_query = select(Role)
        if filters:
            count_query = count_query.where(and_(*filters))
        count_result = await self.db.execute(count_query)
        total = len(count_result.scalars().all())
        
        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(Role.created_at.desc())
        result = await self.db.execute(query)
        roles = list(result.scalars().all())
        
        return RoleListResponse(
            items=[self._model_to_response(role) for role in roles],
            total=total,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit,
            total_pages=(total + limit - 1) // limit if limit > 0 else 1,
        )
    
    async def update(
        self, 
        role_id: str, 
        role_data: RoleUpdate,
        user_id: Optional[str] = None
    ) -> RoleResponse:
        """
        Update a role.
        """
        query = select(Role).where(Role.id == role_id)
        result = await self.db.execute(query)
        role = result.scalar_one_or_none()
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        # Update fields
        update_data = role_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(role, field, value)
        
        await self.db.commit()
        await self.db.refresh(role)
        
        return self._model_to_response(role)
    
    async def delete(self, role_id: str, hard_delete: bool = False) -> dict:
        """
        Delete a role.
        Soft delete by default (sets is_active=False).
        """
        query = select(Role).where(Role.id == role_id)
        result = await self.db.execute(query)
        role = result.scalar_one_or_none()
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        if hard_delete:
            await self.db.delete(role)
        else:
            role.is_active = False
        
        await self.db.commit()
        
        return {"message": "Role deleted successfully"}
    
    async def deactivate(self, role_id: str) -> RoleResponse:
        """
        Deactivate a role (soft delete).
        """
        return await self.delete(role_id, hard_delete=False)
    
    async def activate(self, role_id: str) -> RoleResponse:
        """
        Activate a deactivated role.
        """
        query = select(Role).where(Role.id == role_id)
        result = await self.db.execute(query)
        role = result.scalar_one_or_none()
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        role.is_active = True
        await self.db.commit()
        await self.db.refresh(role)
        
        return self._model_to_response(role)
    
    async def generate_blueprint(
        self, 
        request: GenerateBlueprintRequest
    ) -> GenerateBlueprintResponse:
        """
        Generate a role blueprint using AI (Gemini).
        """
        try:
            # Check if Gemini is configured
            if not self.blueprint_generator.is_configured():
                return GenerateBlueprintResponse(
                    success=False,
                    error="AI service not configured. Please set GEMINI_API_KEY in environment.",
                )
            
            # Create input for AI
            ai_input = RoleBlueprintInput(
                title=request.title,
                seniority=request.seniority,
                stack=request.stack,
                team_context=request.team_context,
            )
            
            # Generate blueprint
            blueprint = await self.blueprint_generator.generate(ai_input)
            
            # Convert to dict format for response
            response_blueprint = AIGeneratedBlueprint(
                mission=blueprint.mission,
                competencies=[
                    {
                        "name": comp.name,
                        "description": comp.description,
                        "weight": comp.weight,
                    }
                    for comp in blueprint.competencies
                ],
                must_have=blueprint.must_have,
                nice_to_have=blueprint.nice_to_have,
                interview_stages=[
                    {
                        "name": stage.name,
                        "duration_minutes": stage.duration_minutes,
                        "description": stage.description,
                        "interview_type": stage.interview_type,
                    }
                    for stage in blueprint.interview_stages
                ],
            )
            
            return GenerateBlueprintResponse(
                success=True,
                blueprint=response_blueprint,
            )
            
        except ValueError as e:
            return GenerateBlueprintResponse(
                success=False,
                error=str(e),
            )
        except Exception as e:
            return GenerateBlueprintResponse(
                success=False,
                error=f"AI generation failed: {str(e)}",
            )
    
    async def create_with_ai_blueprint(
        self,
        role_data: RoleCreate,
        blueprint: AIGeneratedBlueprint,
        user_id: Optional[str] = None
    ) -> RoleResponse:
        """
        Create a role using AI-generated blueprint data.
        """
        # Merge AI blueprint with role data
        merged_data = role_data.model_dump()
        
        # Override with AI-generated data
        merged_data["mission"] = blueprint.mission
        merged_data["core_competencies"] = blueprint.competencies
        merged_data["must_have"] = blueprint.must_have
        merged_data["nice_to_have"] = blueprint.nice_to_have
        merged_data["interview_stages"] = blueprint.interview_stages
        
        # Create role with merged data
        role_create = RoleCreate(**merged_data)
        
        return await self.create(role_create, user_id)
    
    async def duplicate(self, role_id: str, new_title: Optional[str] = None) -> RoleResponse:
        """
        Duplicate an existing role.
        """
        # Get original role
        query = select(Role).where(Role.id == role_id)
        result = await self.db.execute(query)
        original = result.scalar_one_or_none()
        
        if not original:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        # Create duplicate
        duplicate = Role(
            id=str(uuid.uuid4()),
            organization_id=original.organization_id,
            title=new_title or f"{original.title} (Copy)",
            slug=self._generate_slug(new_title or f"{original.title} (Copy)"),
            description=original.description,
            seniority=original.seniority,
            department=original.department,
            tech_stack=original.tech_stack,
            core_competencies=original.core_competencies,
            interview_stages=original.interview_stages,
            mission=original.mission,
            must_have=original.must_have,
            nice_to_have=original.nice_to_have,
        )
        
        self.db.add(duplicate)
        await self.db.commit()
        await self.db.refresh(duplicate)
        
        return self._model_to_response(duplicate)

