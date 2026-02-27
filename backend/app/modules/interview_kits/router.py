"""
Interview Kit router.
Defines API endpoints for interview kit operations including AI generation.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.interview_kits.service import InterviewKitService
from app.schemas.interview_kit import (
    InterviewKitCreate,
    InterviewKitUpdate,
    InterviewKitResponse,
    InterviewKitListResponse,
    GenerateInterviewKitRequest,
    GenerateInterviewKitResponse,
    AIGeneratedInterviewKit,
)
from app.core.security import get_current_active_user
from app.db.models import User


router = APIRouter(prefix="/interview-kits", tags=["Interview Kits"])


@router.post("/", response_model=InterviewKitResponse, status_code=status.HTTP_201_CREATED)
async def create_interview_kit(
    kit_data: InterviewKitCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new interview kit.
    """
    service = InterviewKitService(db)
    return await service.create(kit_data, user_id=current_user.id)


@router.get("/", response_model=InterviewKitListResponse)
async def get_interview_kits(
    organization_id: Optional[str] = Query(None, description="Filter by organization"),
    role_id: Optional[str] = Query(None, description="Filter by role"),
    interview_type: Optional[str] = Query(None, description="Filter by type: coding, system_design, pm_case, behavioral"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None, description="Search in title, description"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get paginated list of interview kits.
    """
    service = InterviewKitService(db)
    return await service.get_all(
        organization_id=organization_id,
        role_id=role_id,
        interview_type=interview_type,
        skip=skip,
        limit=limit,
        is_active=is_active,
        search=search
    )


@router.get("/{kit_id}", response_model=InterviewKitResponse)
async def get_interview_kit(
    kit_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get interview kit by ID.
    """
    service = InterviewKitService(db)
    return await service.get_by_id(kit_id)


@router.put("/{kit_id}", response_model=InterviewKitResponse)
async def update_interview_kit(
    kit_id: str,
    kit_data: InterviewKitUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an interview kit.
    """
    service = InterviewKitService(db)
    return await service.update(kit_id, kit_data, user_id=current_user.id)


@router.delete("/{kit_id}")
async def delete_interview_kit(
    kit_id: str,
    hard_delete: bool = Query(False, description="Permanently delete the kit"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete an interview kit (soft delete by default).
    """
    service = InterviewKitService(db)
    return await service.delete(kit_id, hard_delete=hard_delete)


@router.post("/{kit_id}/duplicate", response_model=InterviewKitResponse)
async def duplicate_interview_kit(
    kit_id: str,
    new_title: Optional[str] = Query(None, description="Title for the duplicated kit"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Duplicate an existing interview kit.
    """
    service = InterviewKitService(db)
    return await service.duplicate(kit_id, new_title=new_title)


# ============== AI Interview Kit Generation Endpoints ==============

@router.post("/generate", response_model=GenerateInterviewKitResponse)
async def generate_interview_kit(
    request: GenerateInterviewKitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate an interview kit using AI (Ollama).
    
    This endpoint creates a comprehensive interview kit including:
    - Problem statement
    - Evaluation rubric with criteria
    - Red flags to watch for
    - Good answer outline
    - Structured questions
    - Tips for interviewer
    """
    service = InterviewKitService(db)
    return await service.generate_kit(request)


@router.post("/create-with-ai", response_model=InterviewKitResponse, status_code=status.HTTP_201_CREATED)
async def create_interview_kit_with_ai(
    organization_id: str,
    role_id: Optional[str] = None,
    role_title: str = Query(..., description="Job title for the role"),
    seniority: str = Query(..., description="Seniority level"),
    stack: list = Query(default_factory=list, description="Technology stack"),
    interview_type: str = Query(..., description="Type of interview: coding, system_design, pm_case, behavioral"),
    competencies: list = Query(default_factory=list, description="Core competencies to evaluate"),
    duration_minutes: int = Query(60, ge=15, le=180, description="Estimated interview duration"),
    additional_context: Optional[str] = Query(None, description="Any additional context"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate AI interview kit and create it in one step.
    
    This is a convenience endpoint that:
    1. Generates an interview kit using AI
    2. Creates a new interview kit with the generated content
    """
    service = InterviewKitService(db)
    
    # First generate the kit
    request = GenerateInterviewKitRequest(
        role_id=role_id,
        role_title=role_title,
        seniority=seniority,
        stack=stack,
        interview_type=interview_type,
        competencies=competencies,
        duration_minutes=duration_minutes,
        additional_context=additional_context,
    )
    
    kit_response = await service.generate_kit(request)
    
    if not kit_response.success or not kit_response.kit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=kit_response.error or "Failed to generate interview kit"
        )
    
    # Create kit with AI-generated content
    kit_data = InterviewKitCreate(
        organization_id=organization_id,
        role_id=role_id,
        role_title=role_title,  # Note: This will be overridden by AI-generated title
        seniority=seniority,
        stack=stack,
        interview_type=interview_type,
        competencies=competencies,
        duration_minutes=duration_minutes,
        additional_context=additional_context,
    )
    
    return await service.create_with_ai_kit(
        kit_data=kit_data,
        ai_kit=kit_response.kit,
        user_id=current_user.id
    )


@router.post("/{kit_id}/regenerate", response_model=GenerateInterviewKitResponse)
async def regenerate_interview_kit(
    kit_id: str,
    request: GenerateInterviewKitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Regenerate an existing interview kit using AI.
    
    This will replace the existing kit content with new AI-generated content.
    """
    service = InterviewKitService(db)
    
    # First generate the new kit
    kit_response = await service.generate_kit(request)
    
    if not kit_response.success or not kit_response.kit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=kit_response.error or "Failed to generate interview kit"
        )
    
    # Update existing kit with new AI-generated content
    update_data = InterviewKitUpdate(
        title=kit_response.kit.title,
        problem_statement=kit_response.kit.problem_statement,
        evaluation_rubric=kit_response.kit.evaluation_rubric,
        red_flags=kit_response.kit.red_flags,
        good_answer_outline=kit_response.kit.good_answer_outline,
        questions=kit_response.kit.questions,
        tips_for_interviewer=kit_response.kit.tips_for_interviewer,
    )
    
    await service.update(kit_id, update_data, user_id=current_user.id)
    
    return kit_response


@router.get("/template")
async def get_interview_kit_template():
    """
    Get a template/example of what the AI interview kit generation expects and returns.
    """
    return {
        "input": {
            "role_title": "Senior Python Backend Engineer",
            "seniority": "senior",
            "stack": ["Python", "FastAPI", "PostgreSQL", "Redis"],
            "interview_type": "coding",
            "competencies": ["Python Development", "System Design", "API Design"],
            "duration_minutes": 60,
            "additional_context": "Experience with microservices is a plus"
        },
        "output": {
            "title": "Senior Python Backend Engineer - Coding Interview",
            "problem_statement": "Design and implement a RESTful API for a task management system...",
            "evaluation_rubric": [
                {
                    "name": "Problem Understanding",
                    "description": "How well does the candidate understand the requirements?",
                    "max_score": 5,
                    "weight": 2
                },
                {
                    "name": "Code Quality",
                    "description": "Is the code clean, well-organized, and follows best practices?",
                    "max_score": 5,
                    "weight": 3
                }
            ],
            "red_flags": [
                "Unable to explain their code",
                "No consideration for edge cases",
                "Poor variable naming"
            ],
            "good_answer_outline": "1. Clarify requirements... 2. Design the data model... 3. Implement the solution...",
            "questions": [
                {
                    "question": "Implement a REST endpoint to create a new task...",
                    "type": "coding",
                    "duration_minutes": 20,
                    "difficulty": "medium",
                    "notes": "Allow candidate to ask clarifying questions"
                }
            ],
            "tips_for_interviewer": "Give hints if the candidate gets stuck...",
            "suggested_duration_breakdown": {
                "introduction": 5,
                "main_problem": 40,
                "questions": 10,
                "wrap_up": 5
            }
        }
    }


# ============== Question Bank Endpoints ==============

@router.get("/{kit_id}/questions")
async def get_kit_questions(
    kit_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all questions from an interview kit.
    """
    service = InterviewKitService(db)
    kit = await service.get_by_id(kit_id)
    return {
        "questions": kit.questions or [],
        "total": len(kit.questions) if kit.questions else 0
    }
