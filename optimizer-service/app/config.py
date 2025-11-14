"""
Configuration for optimizer microservice.
"""
import os
from typing import Optional


class Settings:
    """Application settings."""

    # Server settings
    HOST: str = os.getenv("OPTIMIZER_HOST", "127.0.0.1")
    PORT: int = int(os.getenv("OPTIMIZER_PORT", "8001"))

    # CORS settings
    CORS_ORIGINS: list = [
        "http://localhost:5000",   # .NET API
        "http://localhost:8000",   # Python API (if still running)
        "http://localhost:3000",   # Frontend
    ]

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Optimization defaults
    DEFAULT_MAX_ITERATIONS: int = 100
    DEFAULT_TOLERANCE: float = 1e-6

    # API settings
    API_TITLE: str = "SLSQP Optimizer Microservice"
    API_DESCRIPTION: str = "Thermal optimization for glass furnace regenerators using SLSQP algorithm"
    API_VERSION: str = "1.0.0"


settings = Settings()
