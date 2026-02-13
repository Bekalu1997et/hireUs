from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:hireus@localhost:5432/hireus",
        description="PostgreSQL database URL"
    )
    
    # JWT Authentication
    jwt_secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT token generation"
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT algorithm"
    )
    jwt_expiration_minutes: int = Field(
        default=60 * 24,  # 24 hours
        description="JWT token expiration time in minutes"
    )
    
    # OpenAI
    openai_api_key: str = Field(
        default="",
        description="OpenAI API key for LLM integration"
    )
    openai_model: str = Field(
        default="gpt-4",
        description="OpenAI model to use"
    )

    # Ollama (local LLM fallback)
    ollama_enabled: bool = Field(
        default=True,
        description="Enable Ollama local LLM fallback"
    )
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama API base URL"
    )
    ollama_model: str = Field(
        default="tinyllama:latest",
        description="Ollama model to use"
    )
    ollama_timeout_seconds: int = Field(
        default=120,
        description="Ollama request timeout in seconds"
    )
    
    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins"
    )
    
    # Application
    app_name: str = Field(
        default="Structured Interview Platform",
        description="Application name"
    )
    debug: bool = Field(
        default=True,
        description="Debug mode"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
