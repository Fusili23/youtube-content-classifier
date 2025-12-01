"""
Application Configuration
Manages environment variables and application settings using Pydantic
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    # Application
    SECRET_KEY: str
    ENVIRONMENT: str = "development"
    
    # LLM Configuration
    LLM_PROVIDER: str = "gemini"  # Options: "openai", "gemini"
    WHISPER_MODEL_SIZE: str = "base"  # Options: "tiny", "base", "small", "medium", "large"
    
    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Temporary file storage
    TEMP_DIR: str = "/app/temp"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
