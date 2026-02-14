from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field


# ============== Candidate Schemas ==============

class CandidateBase(BaseModel):
    """Base candidate schema with common fields."""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=200)
    phone: Optional[str] = None
    current_company: Optional[str] = None
    current_position: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    resume_url: Optional[str] = None
    source: Optional[str] = None  # e.g., "LinkedIn", "Referral", "Direct"
    notes: Optional[str] = None


class CandidateCreate(CandidateBase):
    """Schema for creating a new candidate."""
    organization_id: str
    role_id: Optional[str] = None
    workflow_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CandidateUpdate(BaseModel):
    """Schema for updating an existing candidate."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=200)
    phone: Optional[str] = None
    current_company: Optional[str] = None
    current_position: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    resume_url: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class CandidateInDB(CandidateBase):
    """Schema for candidate as stored in database."""
    id: str
    organization_id: str
    role_id: Optional[str] = None
    workflow_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CandidateResponse(CandidateInDB):
    """Schema for candidate response to client."""
    pass


class CandidateListResponse(BaseModel):
    """Response schema for list of candidates with pagination."""
    candidates: List[CandidateResponse]
    total: int
    skip: int
    limit: int


class CandidateSearchRequest(BaseModel):
    """Request schema for searching candidates."""
    query: Optional[str] = None
    organization_id: Optional[str] = None
    role_id: Optional[str] = None
    workflow_id: Optional[str] = None
    is_active: Optional[bool] = None
    source: Optional[str] = None
    skip: int = 0
    limit: int = 20


class CandidateSearchResponse(BaseModel):
    """Response schema for candidate search results."""
    candidates: List[CandidateResponse]
    total: int
    skip: int
    limit: int


class CandidateStageInfo(BaseModel):
    """Schema for candidate current stage info."""
    candidate_id: str
    workflow_id: Optional[str] = None
    current_stage_id: Optional[str] = None
    current_stage_name: Optional[str] = None

    class Config:
        from_attributes = True


class CandidateStats(BaseModel):
    """Schema for candidate statistics."""
    total_candidates: int
    active_candidates: int
    inactive_candidates: int
    by_source: Dict[str, int]
    by_role: Dict[str, int]


# ============== Assignment Schemas ==============

class CandidateAssignmentBase(BaseModel):
    """Base assignment schema."""
    interview_kit_id: Optional[str] = None
    assigned_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    status: str = "pending"  # pending, in_progress, completed, cancelled


class CandidateAssignmentCreate(CandidateAssignmentBase):
    """Schema for creating a candidate assignment."""
    candidate_id: str
    interviewer_id: str


class CandidateAssignmentUpdate(BaseModel):
    """Schema for updating a candidate assignment."""
    interview_kit_id: Optional[str] = None
    assigned_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None


class CandidateAssignmentInDB(CandidateAssignmentBase):
    """Schema for assignment as stored in database."""
    id: str
    candidate_id: str
    interviewer_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CandidateAssignmentResponse(CandidateAssignmentInDB):
    """Schema for assignment response."""
    pass


class CandidateAssignmentListResponse(BaseModel):
    """Response schema for list of assignments."""
    assignments: List[CandidateAssignmentResponse]
    total: int

