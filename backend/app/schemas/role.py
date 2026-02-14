"""
Role schemas for API request/response validation.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


# ============== Input Schemas ==============

class RoleCreateInput(BaseModel):
    """Input schema for creating a role."""
    title: str = Field(..., min_length=1, max_length=255, description="Job title")
    seniority: str = Field(..., description="Seniority level")
    department: Optional[str] = Field(None, description="Department name")
    tech_stack: List[str] = Field(default_factory=list, description="Technology stack")
    team_context: Optional[str] = Field(None, description="Additional team context")


class RoleBlueprintGenerateInput(BaseModel):
    """Input schema for generating role blueprint with AI."""
    title: str = Field(..., min_length=1, max_length=255, description="Job title")
    seniority: str = Field(..., description="Seniority level (Junior, Mid, Senior, Lead, etc.)")
    stack: List[str] = Field(default_factory=list, description="Technology stack")
    team_context: Optional[str] = Field(None, description="Additional team context")


class RoleUpdateInput(BaseModel):
    """Input schema for updating a role."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    seniority: Optional[str] = None
    department: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    core_competencies: Optional[List[Dict[str, Any]]] = None
    interview_stages: Optional[List[Dict[str, Any]]] = None
    mission: Optional[str] = None
    must_have: Optional[Dict[str, Any]] = None
    nice_to_have: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


# ============== AI Output Schemas ==============

class CompetencyResponse(BaseModel):
    """Competency response schema."""
    name: str
    description: str
    weight: str = "must-have"


class InterviewStageResponse(BaseModel):
    """Interview stage response schema."""
    name: str
    duration_minutes: int = 60
    description: str
    interview_type: str


class RoleBlueprintResponse(BaseModel):
    """Role blueprint AI response schema."""
    mission: str
    competencies: List[CompetencyResponse]
    must_have: Dict[str, Any]
    nice_to_have: Dict[str, Any]
    interview_stages: List[InterviewStageResponse]


# ============== Database Schemas ==============

class RoleBase(BaseModel):
    """Base role schema with common fields."""
    title: str
    description: Optional[str] = None
    seniority: Optional[str] = None
    department: Optional[str] = None
    tech_stack: List[str] = Field(default_factory=list)
    core_competencies: List[Dict[str, Any]] = Field(default_factory=list)
    interview_stages: List[Dict[str, Any]] = Field(default_factory=list)
    mission: Optional[str] = None
    must_have: Dict[str, Any] = Field(default_factory=dict)
    nice_to_have: Dict[str, Any] = Field(default_factory=dict)


class RoleCreate(RoleBase):
    """Schema for creating a role in the database."""
    organization_id: str


class RoleUpdate(RoleBase):
    """Schema for updating a role."""
    pass


class RoleInDB(RoleBase):
    """Schema for role stored in database."""
    id: str
    organization_id: str
    slug: str
    is_active: bool
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============== Response Schemas ==============

class RoleResponse(BaseModel):
    """Role response schema for API responses."""
    id: str
    organization_id: str
    title: str
    slug: str
    description: Optional[str] = None
    seniority: Optional[str] = None
    department: Optional[str] = None
    tech_stack: List[str]
    core_competencies: List[Dict[str, Any]]
    interview_stages: List[Dict[str, Any]]
    mission: Optional[str] = None
    must_have: Dict[str, Any]
    nice_to_have: Dict[str, Any]
    is_active: bool
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class RoleListResponse(BaseModel):
    """Paginated list of roles."""
    items: List[RoleResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class RoleDetailResponse(RoleResponse):
    """Detailed role response with all fields."""
    pass


# ============== AI Generation Schemas ==============

class AIGeneratedBlueprint(BaseModel):
    """Schema for AI-generated role blueprint data."""
    mission: str
    competencies: List[Dict[str, Any]]
    must_have: Dict[str, Any]
    nice_to_have: Dict[str, Any]
    interview_stages: List[Dict[str, Any]]


class GenerateBlueprintRequest(BaseModel):
    """Request schema for generating role blueprint."""
    title: str
    seniority: str
    stack: List[str] = Field(default_factory=list)
    team_context: Optional[str] = None


class GenerateBlueprintResponse(BaseModel):
    """Response schema for role blueprint generation."""
    success: bool
    blueprint: Optional[AIGeneratedBlueprint] = None
    error: Optional[str] = None
    model_used: str = "gemini-pro"


# ============== Validation Schemas ==============

class SeniorityLevel(str, Enum):
    """Seniority level enumeration."""
    INTERN = "intern"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"
    DIRECTOR = "director"
    VP = "vp"


class InterviewType(str, Enum):
    """Interview type enumeration."""
    CODING = "coding"
    SYSTEM_DESIGN = "system_design"
    BEHAVIORAL = "behavioral"
    CULTURE_FIT = "culture_fit"
    TECHNICAL_SCREEN = "technical_screen"
    FINAL_ROUND = "final_round"

