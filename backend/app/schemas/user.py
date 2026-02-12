"""
User Pydantic schemas.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(..., min_length=8)
    confirm_password: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "john@example.com",
                "full_name": "John Doe",
                "phone": "+1234567890",
                "password": "securepassword123",
                "confirm_password": "securepassword123"
            }
        }
    }


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: str
    avatar_url: Optional[str] = None
    role: str
    is_active: bool
    is_superuser: bool
    email_verified: bool
    last_login: Optional[str] = None
    created_at: str
    updated_at: str
    
    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserResponse):
    """Schema for user in database (includes sensitive data)."""
    hashed_password: str

