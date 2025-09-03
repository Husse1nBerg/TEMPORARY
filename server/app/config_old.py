import os
from typing import Optional

try:
    # Try Pydantic v2
    from pydantic_settings import BaseSettings
    from pydantic import ConfigDict, field_validator
    PYDANTIC_V2 = True
except ImportError:
    try:
        # Fallback to Pydantic v1
        from pydantic import BaseSettings, validator
        PYDANTIC_V2 = False
    except ImportError:
        raise ImportError("Neither pydantic-settings (v2) nor pydantic BaseSettings (v1) found")


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/crops_tracker"
    TEST_DATABASE_URL: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Crops Price Tracker"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for tracking crop prices across different stores"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # Scraping
    SCRAPING_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    SCRAPING_DELAY_MIN: float = 1.0
    SCRAPING_DELAY_MAX: float = 3.0
    SCRAPING_TIMEOUT: int = 30
    SCRAPING_MAX_RETRIES: int = 3
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Email (for notifications)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # AI Services
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # Monitoring
    ENABLE_METRICS: bool = True
    ENABLE_HEALTH_CHECKS: bool = True
    
    # Development
    DEBUG: bool = False
    TESTING: bool = False
    
    if PYDANTIC_V2:
        model_config = ConfigDict(
            env_file=".env",
            case_sensitive=True,
            extra="allow"
        )
        
        @field_validator("BACKEND_CORS_ORIGINS", mode="before")
        @classmethod
        def assemble_cors_origins(cls, v):
            if isinstance(v, str) and not v.startswith("["):
                return [i.strip() for i in v.split(",")]
            elif isinstance(v, (list, str)):
                return v
            raise ValueError(v)
        
        @field_validator("DATABASE_URL", mode="before")
        @classmethod
        def validate_database_url(cls, v):
            if v and not v.startswith(("postgresql://", "sqlite:///")):
                raise ValueError("DATABASE_URL must be a valid PostgreSQL or SQLite URL")
            return v
    else:
        # Pydantic v1 configuration
        class Config:
            env_file = ".env"
            case_sensitive = True
            extra = "allow"
        
        @validator("BACKEND_CORS_ORIGINS", pre=True)
        def assemble_cors_origins(cls, v):
            if isinstance(v, str) and not v.startswith("["):
                return [i.strip() for i in v.split(",")]
            elif isinstance(v, (list, str)):
                return v
            raise ValueError(v)
        
        @validator("DATABASE_URL", pre=True)
        def validate_database_url(cls, v):
            if v and not v.startswith(("postgresql://", "sqlite:///")):
                raise ValueError("DATABASE_URL must be a valid PostgreSQL or SQLite URL")
            return v


class TestSettings(Settings):
    TESTING: bool = True
    DATABASE_URL: str = "sqlite:///./test.db"
    REDIS_URL: str = "redis://localhost:6379/15"
    CELERY_BROKER_URL: str = "redis://localhost:6379/15"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/15"


def get_settings() -> Settings:
    """Get application settings based on environment."""
    if os.getenv("TESTING"):
        return TestSettings()
    return Settings()


settings = get_settings()