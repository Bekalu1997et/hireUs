from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ============== Organization Schemas ==============

class OrganizationBase(BaseModel):
    """Base organization schema with common fields."""
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None  # e.g., "1-10", "11-50", "51-200", "201-500", "500+"
    location: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class OrganizationCreate(OrganizationBase):
    """Schema for creating a new organization."""
    pass


class OrganizationUpdate(BaseModel):
    """Schema for updating an existing organization."""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    location: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class OrganizationInDB(OrganizationBase):
    """Schema for organization as stored in database."""
    id: str
    owner_id: str
    settings: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrganizationResponse(OrganizationInDB):
    """Schema for organization response to client."""
    pass


class OrganizationListResponse(BaseModel):
    """Response schema for list of organizations with pagination."""
    organizations: List[OrganizationResponse]
    total: int
    skip: int
    limit: int


class OrganizationStats(BaseModel):
    """Schema for organization statistics."""
    total_users: int
    active_users: int
    total_roles: int
    active_roles: int
    total_candidates: int
    active_candidates: int
    total_workflows: int


# ============== Organization Member Schemas ==============

class OrganizationMemberRole(str):
    """Organization member roles."""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class OrganizationMemberBase(BaseModel):
    """Base organization member schema."""
    role: str = OrganizationMemberRole.MEMBER


class OrganizationMemberCreate(OrganizationMemberBase):
    """Schema for adding a member to organization."""
    user_id: str
    organization_id: str


class OrganizationMemberUpdate(BaseModel):
    """Schema for updating organization member."""
    role: Optional[str] = None


class OrganizationMemberInDB(OrganizationMemberBase):
    """Schema for member as stored in database."""
    id: str
    user_id: str
    organization_id: str
    joined_at: datetime

    class Config:
        from_attributes = True


class OrganizationMemberResponse(OrganizationMemberInDB):
    """Schema for member response."""
    pass


class OrganizationMemberListResponse(BaseModel):
    """Response schema for list of organization members."""
    members: List[OrganizationMemberResponse]
    total: int

