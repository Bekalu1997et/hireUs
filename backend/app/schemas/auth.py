"""
Pydantic schemas for authentication.
"""
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=1, max_length=255)
    organization_name: str = Field(min_length=1, max_length=255)
    organization_domain: str = Field(min_length=1, max_length=255)


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded token data."""
    email: str
    user_id: int
    role: str
    organization_id: int


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    email: str
    full_name: str
    role: str
    organization_id: int
    
    class Config:
        from_attributes = True
