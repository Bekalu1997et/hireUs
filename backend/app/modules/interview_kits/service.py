"""
Interview Kit service for business logic.
Handles interview kit CRUD operations and AI generation.
"""
import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.db.models import InterviewKit, Organization, Role
from app.schemas.interview_kit import (
    InterviewKitCreate,
    InterviewKitUpdate,
    InterviewKitResponse,
    InterviewKitListResponse,
    GenerateInterviewKitRequest,
    GenerateInterviewKitResponse,
    AIGeneratedInterviewKit,
)
from app.core.llm.schema import InterviewType
from app.modules.interview_kits.ai import (
    InterviewKitInput,
    get_kit_generator,
)


class InterviewKitService:
    """
    Interview Kit service for business logic operations.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize with database session.
        """
        self.db = db
        self.kit_generator = get_kit_generator()
    
    def _model_to_response(self, kit: InterviewKit) -> InterviewKitResponse:
        """Convert database model to response schema."""
        return InterviewKitResponse(
            id=kit.id,
            organization_id=kit.organization_id,
            role_id=kit.role_id,
            title=kit.title,
            type=kit.type,
            description=kit.description,
            problem_statement=kit.problem_statement,
            evaluation_rubric=kit.evaluation_rubric or [],
            red_flags=kit.red_flags or [],
            good_answer_outline=kit.good_answer_outline,
            questions=kit.questions or [],
            estimated_duration_minutes=kit.estimated_duration_minutes,
            version=kit.version,
            is_template=kit.is_template,
            is_active=kit.is_active,
            created_by=kit.created_by,
            created_at=kit.created_at,
            updated_at=kit.updated_at,
        )
    
    async def create(
        self, 
        kit_data: InterviewKitCreate, 
        user_id: Optional[str] = None
    ) -> InterviewKitResponse:
        """
        Create a new interview kit.
        """
        # Verify organization exists
        org_query = select(Organization).where(
            Organization.id == kit_data.organization_id,
            Organization.is_active == True
        )
        org_result = await self.db.execute(org_query)
        org = org_result.scalar_one_or_none()
        
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Verify role exists if provided
        if kit_data.role_id:
            role_query = select(Role).where(Role.id == kit_data.role_id)
            role_result = await self.db.execute(role_query)
            role = role_result.scalar_one_or_none()
            
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Role not found"
                )
        
        # Create interview kit
        kit = InterviewKit(
            id=str(uuid.uuid4()),
            organization_id=kit_data.organization_id,
            role_id=kit_data.role_id,
            title=kit_data.title,
            type=kit_data.type,
            description=kit_data.description,
            problem_statement=kit_data.problem_statement,
            evaluation_rubric=kit_data.evaluation_rubric,
            red_flags=kit_data.red_flags,
            good_answer_outline=kit_data.good_answer_outline,
            questions=kit_data.questions,
            estimated_duration_minutes=kit_data.estimated_duration_minutes,
            created_by=user_id,
        )
        
        self.db.add(kit)
        await self.db.commit()
        await self.db.refresh(kit)
        
        return self._model_to_response(kit)
    
    async def get_by_id(self, kit_id: str) -> InterviewKitResponse:
        """
        Get interview kit by ID.
        """
        query = select(InterviewKit).where(InterviewKit.id == kit_id)
        result = await self.db.execute(query)
        kit = result.scalar_one_or_none()
        
        if not kit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview kit not found"
            )
        
        return self._model_to_response(kit)
    
    async def get_all(
        self,
        organization_id: Optional[str] = None,
        role_id: Optional[str] = None,
        interview_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> InterviewKitListResponse:
        """
        Get paginated list of interview kits.
        """
        # Build query
        query = select(InterviewKit)
        
        filters = []
        if organization_id:
            filters.append(InterviewKit.organization_id == organization_id)
        if role_id:
            filters.append(InterviewKit.role_id == role_id)
        if interview_type:
            filters.append(InterviewKit.type == interview_type)
        if is_active is not None:
            filters.append(InterviewKit.is_active == is_active)
        if search:
            search_term = f"%{search}%"
            filters.append(
                or_(
                    InterviewKit.title.ilike(search_term),
                    InterviewKit.description.ilike(search_term)
                )
            )
        
        if filters:
            query = query.where(and_(*filters))
        
        # Get total count
        count_query = select(InterviewKit)
        if filters:
            count_query = count_query.where(and_(*filters))
        count_result = await self.db.execute(count_query)
        total = len(count_result.scalars().all())
        
        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(InterviewKit.created_at.desc())
        result = await self.db.execute(query)
        kits = list(result.scalars().all())
        
        return InterviewKitListResponse(
            items=[self._model_to_response(kit) for kit in kits],
            total=total,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit,
            total_pages=(total + limit - 1) // limit if limit > 0 else 1,
        )
    
    async def update(
        self, 
        kit_id: str, 
        kit_data: InterviewKitUpdate,
        user_id: Optional[str] = None
    ) -> InterviewKitResponse:
        """
        Update an interview kit.
        """
        query = select(InterviewKit).where(InterviewKit.id == kit_id)
        result = await self.db.execute(query)
        kit = result.scalar_one_or_none()
        
        if not kit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview kit not found"
            )
        
        # Update fields
        update_data = kit_data.model_dump(exclude_unset=True)
        
        # Increment version if content changed
        if update_data:
            kit.version += 1
        
        for field, value in update_data.items():
            setattr(kit, field, value)
        
        await self.db.commit()
        await self.db.refresh(kit)
        
        return self._model_to_response(kit)
    
    async def delete(self, kit_id: str, hard_delete: bool = False) -> dict:
        """
        Delete an interview kit.
        Soft delete by default (sets is_active=False).
        """
        query = select(InterviewKit).where(InterviewKit.id == kit_id)
        result = await self.db.execute(query)
        kit = result.scalar_one_or_none()
        
        if not kit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview kit not found"
            )
        
        if hard_delete:
            await self.db.delete(kit)
        else:
            kit.is_active = False
        
        await self.db.commit()
        
        return {"message": "Interview kit deleted successfully"}
    
    async def duplicate(self, kit_id: str, new_title: Optional[str] = None) -> InterviewKitResponse:
        """
        Duplicate an existing interview kit.
        """
        # Get original kit
        query = select(InterviewKit).where(InterviewKit.id == kit_id)
        result = await self.db.execute(query)
        original = result.scalar_one_or_none()
        
        if not original:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview kit not found"
            )
        
        # Create duplicate
        duplicate = InterviewKit(
            id=str(uuid.uuid4()),
            organization_id=original.organization_id,
            role_id=original.role_id,
            title=new_title or f"{original.title} (Copy)",
            type=original.type,
            description=original.description,
            problem_statement=original.problem_statement,
            evaluation_rubric=original.evaluation_rubric,
            red_flags=original.red_flags,
            good_answer_outline=original.good_answer_outline,
            questions=original.questions,
            estimated_duration_minutes=original.estimated_duration_minutes,
            version=1,
        )
        
        self.db.add(duplicate)
        await self.db.commit()
        await self.db.refresh(duplicate)
        
        return self._model_to_response(duplicate)
    
    async def generate_kit(
        self, 
        request: GenerateInterviewKitRequest
    ) -> GenerateInterviewKitResponse:
        """
        Generate an interview kit using AI (Ollama).
        """
        try:
            # Check if Ollama is configured
            if not self.kit_generator.is_configured():
                return GenerateInterviewKitResponse(
                    success=False,
                    error="AI service not configured. Please set OLLAMA_BASE_URL and OLLAMA_MODEL in environment.",
                )
            
            # Map interview type string to enum
            try:
                interview_type = InterviewType(request.interview_type)
            except ValueError:
                return GenerateInterviewKitResponse(
                    success=False,
                    error=f"Invalid interview type: {request.interview_type}. Must be one of: coding, system_design, pm_case, behavioral",
                )
            
            # Create input for AI
            ai_input = InterviewKitInput(
                role_title=request.role_title,
                seniority=request.seniority,
                stack=request.stack,
                interview_type=interview_type,
                competencies=request.competencies,
                duration_minutes=request.duration_minutes,
                additional_context=request.additional_context,
            )
            
            # Generate kit
            kit = await self.kit_generator.generate(ai_input)
            
            # Convert to dict format for response
            response_kit = AIGeneratedInterviewKit(
                title=kit.title,
                problem_statement=kit.problem_statement,
                evaluation_rubric=[
                    {
                        "name": criterion.name,
                        "description": criterion.description,
                        "max_score": criterion.max_score,
                        "weight": criterion.weight,
                    }
                    for criterion in kit.evaluation_rubric
                ],
                red_flags=kit.red_flags,
                good_answer_outline=kit.good_answer_outline,
                questions=[
                    {
                        "question": q.question,
                        "type": q.type,
                        "duration_minutes": q.duration_minutes,
                        "difficulty": q.difficulty,
                        "notes": q.notes,
                    }
                    for q in kit.questions
                ],
                tips_for_interviewer=kit.tips_for_interviewer,
                suggested_duration_breakdown=kit.suggested_duration_breakdown,
            )
            
            return GenerateInterviewKitResponse(
                success=True,
                kit=response_kit,
            )
            
        except ValueError as e:
            return GenerateInterviewKitResponse(
                success=False,
                error=str(e),
            )
        except Exception as e:
            return GenerateInterviewKitResponse(
                success=False,
                error=f"AI generation failed: {str(e)}",
            )
    
    async def create_with_ai_kit(
        self,
        kit_data: InterviewKitCreate,
        ai_kit: AIGeneratedInterviewKit,
        user_id: Optional[str] = None
    ) -> InterviewKitResponse:
        """
        Create an interview kit using AI-generated content.
        """
        # Merge AI kit with kit data
        merged_data = kit_data.model_dump()
        
        # Override with AI-generated data
        merged_data["title"] = ai_kit.title
        merged_data["problem_statement"] = ai_kit.problem_statement
        merged_data["evaluation_rubric"] = ai_kit.evaluation_rubric
        merged_data["red_flags"] = ai_kit.red_flags
        merged_data["good_answer_outline"] = ai_kit.good_answer_outline
        merged_data["questions"] = ai_kit.questions
        merged_data["tips_for_interviewer"] = ai_kit.tips_for_interviewer
        
        # Create kit with merged data
        kit_create = InterviewKitCreate(**merged_data)
        
        return await self.create(kit_create, user_id)
