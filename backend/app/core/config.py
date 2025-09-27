"""
Application configuration settings.

Konfiguracja aplikacji z walidacją i zarządzaniem zmiennych środowiskowych.
"""

from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, EmailStr, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8 hours
    SERVER_NAME: str = "Forglass Regenerator Optimizer"
    SERVER_HOST: AnyHttpUrl = "http://localhost"
    PROJECT_NAME: str = "Forglass Regenerator Optimizer"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Security
    ALLOWED_HOSTS: Union[str, List[str]] = ["localhost", "127.0.0.1"]
    BACKEND_CORS_ORIGINS: Union[str, List[AnyHttpUrl]] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Parse CORS origins from environment variable."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def assemble_allowed_hosts(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Parse allowed hosts from environment variable."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 3600

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  # 1 hour

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[EmailStr] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    @field_validator("EMAILS_FROM_NAME")
    @classmethod
    def get_project_name(cls, v: Optional[str]) -> str:
        """Get project name for email sender."""
        if not v:
            return "Forglass Regenerator Optimizer"
        return v

    # File storage
    UPLOAD_DIR: str = "/app/uploads"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: str = ".xlsx,.xls,.json"

    @field_validator("ALLOWED_EXTENSIONS", mode="before")
    @classmethod
    def parse_allowed_extensions(cls, v: str) -> str:
        """Parse allowed extensions from string."""
        return v

    def get_allowed_extensions_list(self) -> List[str]:
        """Get allowed extensions as list."""
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]

    # Optimization
    DEFAULT_OPTIMIZATION_TIMEOUT: int = 3600  # 1 hour
    MAX_PARALLEL_OPTIMIZATIONS: int = 10
    OPTIMIZATION_CHECKPOINT_INTERVAL: int = 10  # iterations

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    SENTRY_DSN: Optional[str] = None

    # Monitoring
    PROMETHEUS_METRICS_PATH: str = "/metrics"
    ENABLE_METRICS: bool = True

    # Features flags
    ENABLE_PHYSICS_SOLVER_PYOMO: bool = False
    ENABLE_EXPERIMENTAL_ALGORITHMS: bool = False
    ENABLE_ML_PREDICTIONS: bool = False

    model_config = {
        "case_sensitive": True,
        "env_file": ".env"
    }


settings = Settings()