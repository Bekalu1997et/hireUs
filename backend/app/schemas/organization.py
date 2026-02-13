"""
Pydantic schemas for organization management and invitations.
"""
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class OrganizationUpdate(BaseModel):
    """Schema for updating organization details."""
    name: str | None = Field(default=None, min_length=1, max_length=255)
    domain: str | None = Field(default=None, min_length=1, max_length=255)


class OrganizationResponse(BaseModel):
    """Schema for organization response."""
    id: int
    name: str
    domain: str
    created_at: datetime

    class Config:
        from_attributes = True


class InviteRequest(BaseModel):
    """Schema for inviting a team member."""
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)


class InviteAccept(BaseModel):
    """Schema for accepting an invite."""
    token: str = Field(min_length=1)
    password: str = Field(min_length=8, max_length=128)
