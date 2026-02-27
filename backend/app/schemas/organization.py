"""
Pydantic schemas for organizations and invitations.
"""
from pydantic import BaseModel, EmailStr, Field


class OrganizationUpdate(BaseModel):
    """Schema for updating organization details."""
    name: str | None = Field(None, min_length=1, max_length=255)
    domain: str | None = Field(None, min_length=1, max_length=255)


class OrganizationResponse(BaseModel):
    """Schema for organization response."""
    id: int
    name: str
    domain: str

    class Config:
        from_attributes = True


class InviteRequest(BaseModel):
    """Schema for inviting a team member."""
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)


class InviteAccept(BaseModel):
    """Schema for accepting an invitation."""
    token: str = Field(min_length=10)
    password: str = Field(min_length=8, max_length=72)
