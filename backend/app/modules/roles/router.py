"""
Role router.
Defines API endpoints for role operations including AI blueprint generation.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.roles.service import RoleService
from app.schemas.role import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RoleListResponse,
    RoleDetailResponse,
    GenerateBlueprintRequest,
    GenerateBlueprintResponse,
    AIGeneratedBlueprint,
)
from app.core.security import get_current_active_user
from app.db.models import User


router = APIRouter(prefix="/roles", tags=["Roles"])


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new role.
    """
    service = RoleService(db)
    return await service.create(role_data, user_id=current_user.id)


@router.get("/", response_model=RoleListResponse)
async def get_roles(
    organization_id: Optional[str] = Query(None, description="Filter by organization"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None, description="Search in title, seniority, department"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get paginated list of roles.
    """
    service = RoleService(db)
    return await service.get_all(
        organization_id=organization_id,
        skip=skip,
        limit=limit,
        is_active=is_active,
        search=search
    )


@router.get("/{role_id}", response_model=RoleDetailResponse)
async def get_role(
    role_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get role by ID with full details.
    """
    service = RoleService(db)
    return await service.get_by_id(role_id)


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: str,
    role_data: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a role.
    """
    service = RoleService(db)
    return await service.update(role_id, role_data, user_id=current_user.id)


@router.delete("/{role_id}")
async def delete_role(
    role_id: str,
    hard_delete: bool = Query(False, description="Permanently delete the role"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a role (soft delete by default).
    """
    service = RoleService(db)
    return await service.delete(role_id, hard_delete=hard_delete)


@router.post("/{role_id}/deactivate", response_model=RoleResponse)
async def deactivate_role(
    role_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Deactivate a role.
    """
    service = RoleService(db)
    return await service.deactivate(role_id)


@router.post("/{role_id}/activate", response_model=RoleResponse)
async def activate_role(
    role_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Activate a deactivated role.
    """
    service = RoleService(db)
    return await service.activate(role_id)


@router.post("/{role_id}/duplicate", response_model=RoleResponse)
async def duplicate_role(
    role_id: str,
    new_title: Optional[str] = Query(None, description="Title for the duplicated role"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Duplicate an existing role.
    """
    service = RoleService(db)
    return await service.duplicate(role_id, new_title=new_title)


# ============== AI Blueprint Generation Endpoints ==============

@router.post("/blueprint/generate", response_model=GenerateBlueprintResponse)
async def generate_role_blueprint(
    request: GenerateBlueprintRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a role blueprint using AI (Ollama).
    
    This endpoint creates a comprehensive role definition including:
    - Role mission statement
    - Core competencies (5-8)
    - Must-have vs nice-to-have requirements
    - Interview stage suggestions
    """
    service = RoleService(db)
    return await service.generate_blueprint(request)


@router.post("/blueprint/create", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role_with_blueprint(
    organization_id: str,
    title: str,
    seniority: str,
    stack: list = Query(default_factory=list),
    team_context: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate AI blueprint and create a role in one step.
    
    This is a convenience endpoint that:
    1. Generates a role blueprint using AI
    2. Creates a new role with the generated blueprint
    """
    service = RoleService(db)
    
    # First generate the blueprint
    request = GenerateBlueprintRequest(
        title=title,
        seniority=seniority,
        stack=stack,
        team_context=team_context
    )
    
    blueprint_response = await service.generate_blueprint(request)
    
    if not blueprint_response.success or not blueprint_response.blueprint:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=blueprint_response.error or "Failed to generate blueprint"
        )
    
    # Create role with blueprint
    role_data = RoleCreate(
        organization_id=organization_id,
        title=title,
        seniority=seniority,
        stack=stack,
        team_context=team_context
    )
    
    return await service.create_with_ai_blueprint(
        role_data=role_data,
        blueprint=blueprint_response.blueprint,
        user_id=current_user.id
    )


@router.post("/{role_id}/blueprint/update", response_model=RoleResponse)
async def update_role_with_blueprint(
    role_id: str,
    request: GenerateBlueprintRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a role by regenerating its blueprint with AI.
    
    This will replace the existing role definition with a new AI-generated one.
    """
    service = RoleService(db)
    
    # First generate the new blueprint
    blueprint_response = await service.generate_blueprint(request)
    
    if not blueprint_response.success or not blueprint_response.blueprint:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=blueprint_response.error or "Failed to generate blueprint"
        )
    
    # Update role with new blueprint data
    update_data = RoleUpdate(
        title=request.title,
        seniority=request.seniority,
        tech_stack=request.stack,
        mission=blueprint_response.blueprint.mission,
        core_competencies=blueprint_response.blueprint.competencies,
        must_have=blueprint_response.blueprint.must_have,
        nice_to_have=blueprint_response.blueprint.nice_to_have,
        interview_stages=blueprint_response.blueprint.interview_stages,
    )
    
    return await service.update(role_id, update_data, user_id=current_user.id)


@router.get("/blueprint/template")
async def get_blueprint_template():
    """
    Get a template/example of what the AI blueprint generation expects and returns.
    """
    return {
        "input": {
            "title": "Senior Python Backend Engineer",
            "seniority": "senior",
            "stack": ["Python", "FastAPI", "PostgreSQL", "Redis"],
            "team_context": "Small engineering team building a new product"
        },
        "output": {
            "mission": "Lead the development of scalable backend services...",
            "competencies": [
                {
                    "name": "Python Development",
                    "description": "Expert-level Python programming...",
                    "weight": "must-have"
                }
            ],
            "must_have": {
                "technical_skills": ["Python", "FastAPI", "PostgreSQL"],
                "years_experience": "5+ years",
                "education": "BS in Computer Science or equivalent",
                "key_experiences": ["Microservices architecture", "API design"]
            },
            "nice_to_have": {
                "additional_skills": ["TypeScript", "Kubernetes"],
                "preferred_experiences": ["Startup experience", "Open source contributions"],
                "certifications": ["AWS Solutions Architect"]
            },
            "interview_stages": [
                {
                    "name": "Phone Screen",
                    "duration_minutes": 30,
                    "description": "Initial screening call...",
                    "interview_type": "behavioral"
                }
            ]
        }
    }
