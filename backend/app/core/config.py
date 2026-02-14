"""
Application configuration settings.
Loads environment variables and provides centralized access to all config values.
"""
import os
from pathlib import Path
import secrets
from typing import List, Optional
from functools import lru_cache
from pydantic_settings import BaseSettings


def _generate_secret_key() -> str:
    """Generate a secure random secret key if not provided."""
    return secrets.token_urlsafe(32)


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
    DATABASE_URL: str = "sqlite+aiosqlite:///./hireus.db"
    SYNC_DATABASE_URL: str = "sqlite:///./hireus.db"
    DB_AUTO_CREATE_TABLES: bool = False
    
    # JWT - Use secure default with fallback to generated key
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
    
    # AI Configuration (Ollama)
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "tinyllama"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    
    # Redis (for caching/sessions)
    REDIS_URL: Optional[str] = None
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = str(Path(__file__).resolve().parents[2] / ".env")
        case_sensitive = True
        extra = "ignore"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Use secure generated key if using default
        if self.SECRET_KEY == "your-secret-key-change-in-production":
            # Try to use environment variable first
            env_key = os.environ.get("SECRET_KEY")
            if env_key:
                self.SECRET_KEY = env_key
            else:
                # Generate a secure key (won't persist across restarts in dev)
                self.SECRET_KEY = _generate_secret_key()


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to ensure single instance throughout the application.
    """
    return Settings()


settings = get_settings()
