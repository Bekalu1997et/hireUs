"""
Router for roles and competencies endpoints.

Provides REST API endpoints for role management.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.auth.router import get_current_user, get_current_founder
from app.modules.roles.service import RolesService
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse
from app.db.models import User


router = APIRouter()


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(get_current_founder),
    db: AsyncSession = Depends(get_db)
) -> RoleResponse:
    """
    Create a new role with competencies.
    
    Only founders can create roles. The role will be associated with the
    founder's organization.
    
    Competency weights will be automatically normalized to sum to 1.0.
    
    Args:
        role_data: Role creation data including competencies
        current_user: Current authenticated founder
        
    Returns:
        Created role with competencies
        
    Raises:
        400: If validation fails (e.g., no competencies, invalid weights)
        403: If user is not a founder
        
    Example:
        POST /api/roles
        {
            "title": "Senior Backend Engineer",
            "description": "Experienced backend developer",
            "seniority_level": "senior",
            "competencies": [
                {
                    "name": "Python",
                    "description": "Python programming",
                    "weight": 0.4
                },
                {
                    "name": "System Design",
                    "description": "Architecture skills",
                    "weight": 0.6
                }
            ]
        }
    """
    service = RolesService(db)
    role = await service.create_role(role_data, current_user.organization_id)
    return RoleResponse.model_validate(role)


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> RoleResponse:
    """
    Get a role by ID.
    
    The role must belong to the user's organization.
    
    Args:
        role_id: Role ID
        current_user: Current authenticated user
        
    Returns:
        Role with competencies
        
    Raises:
        404: If role not found
        403: If role doesn't belong to user's organization
        
    Example:
        GET /api/roles/1
    """
    service = RolesService(db)
    role = await service.get_role(role_id, current_user.organization_id)
    return RoleResponse.model_validate(role)


@router.get("", response_model=List[RoleResponse])
async def list_roles(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[RoleResponse]:
    """
    List all roles for the user's organization.
    
    Supports pagination through skip and limit parameters.
    
    Args:
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100, max: 100)
        current_user: Current authenticated user
        
    Returns:
        List of roles with competencies
        
    Example:
        GET /api/roles?skip=0&limit=10
    """
    service = RolesService(db)
    roles = await service.list_roles(
        current_user.organization_id,
        skip=skip,
        limit=min(limit, 100)  # Cap at 100
    )
    return [RoleResponse.model_validate(role) for role in roles]


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    current_user: User = Depends(get_current_founder),
    db: AsyncSession = Depends(get_db)
) -> RoleResponse:
    """
    Update a role.
    
    Only founders can update roles. The role must belong to the founder's
    organization.
    
    If competencies are provided, they will replace all existing competencies.
    Weights will be automatically normalized to sum to 1.0.
    
    Args:
        role_id: Role ID
        role_data: Role update data (all fields optional)
        current_user: Current authenticated founder
        
    Returns:
        Updated role with competencies
        
    Raises:
        404: If role not found
        403: If user is not a founder or role doesn't belong to organization
        400: If validation fails
        
    Example:
        PUT /api/roles/1
        {
            "title": "Staff Backend Engineer",
            "seniority_level": "staff"
        }
    """
    service = RolesService(db)
    role = await service.update_role(role_id, role_data, current_user.organization_id)
    return RoleResponse.model_validate(role)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    current_user: User = Depends(get_current_founder),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete a role.
    
    Only founders can delete roles. The role must belong to the founder's
    organization.
    
    This will also delete all associated competencies (cascade delete).
    
    Args:
        role_id: Role ID
        current_user: Current authenticated founder
        
    Raises:
        404: If role not found
        403: If user is not a founder or role doesn't belong to organization
        
    Example:
        DELETE /api/roles/1
    """
    service = RolesService(db)
    await service.delete_role(role_id, current_user.organization_id)
