"""
Application configuration settings.
Loads environment variables and provides centralized access to all config values.
"""
import os
from typing import List, Optional
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings class.
    Uses pydantic-settings for environment variable management.
    """
    # Application
    APP_NAME: str = "HireUs - AI-Powered Hiring Platform"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/hireus"
    SYNC_DATABASE_URL: str = "postgresql://user:password@localhost:5432/hireus"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Password
    PASSWORD_MIN_LENGTH: int = 8
    
    # Email (optional)
    SMTP_TLS: bool = True
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # First superuser
    FIRST_SUPERUSER_EMAIL: str = "admin@hireus.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin123"
    
    # AI Configuration (OpenAI)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # Redis (for caching/sessions)
    REDIS_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to ensure single instance throughout the application.
    """
    return Settings()


settings = get_settings()

