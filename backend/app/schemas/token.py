"""
Pydantic schemas for authentication.
Contains request/response schemas for auth endpoints.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ============== User Schemas ==============

class UserBase(BaseModel):
    """
    Base user schema with common attributes.
    """
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    """
    Schema for creating a new user.
    """
    password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "john@example.com",
                "full_name": "John Doe",
                "password": "securepassword123",
                "confirm_password": "securepassword123"
            }
        }
    }


class UserUpdate(BaseModel):
    """
    Schema for updating user information.
    """
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """
    Schema for user response.
    """
    id: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    is_active: bool
    is_superuser: bool
    email_verified: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserResponse):
    """
    Schema for user in database (includes hashed password).
    """
    hashed_password: str


class UserListResponse(BaseModel):
    """
    Schema for paginated user list response.
    """
    items: list[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============== Token Schemas ==============

class Token(BaseModel):
    """
    JWT token response.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """
    JWT token payload.
    """
    sub: str
    exp: Optional[datetime] = None
    type: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """
    Request to refresh access token.
    """
    refresh_token: str


# ============== Login Schemas ==============

class LoginRequest(BaseModel):
    """
    Login request schema.
    """
    email: EmailStr
    password: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "john@example.com",
                "password": "securepassword123"
            }
        }
    }


class LoginResponse(Token):
    """
    Login response with user information.
    """
    user: UserResponse


# ============== Register Schemas ==============

class RegisterRequest(UserCreate):
    """
    Registration request schema.
    """
    pass


class RegisterResponse(Token):
    """
    Registration response with user information.
    """
    user: UserResponse


# ============== Password Schemas ==============

class PasswordResetRequest(BaseModel):
    """
    Request password reset email.
    """
    email: EmailStr
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "john@example.com"
            }
        }
    }


class PasswordResetConfirm(BaseModel):
    """
    Confirm password reset with new password.
    """
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_new_password: str


class ChangePasswordRequest(BaseModel):
    """
    Change password for authenticated user.
    """
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_new_password: str


# ============== Message Schemas ==============

class Message(BaseModel):
    """
    Generic message response.
    """
    message: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Operation successful"
            }
        }
    }


# ============== Health Check Schemas ==============

class HealthCheck(BaseModel):
    """
    Health check response.
    """
    status: str
    database: str
    version: str = "1.0.0"
