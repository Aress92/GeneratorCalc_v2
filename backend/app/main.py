"""
Main FastAPI application for Forglass Regenerator Optimizer.

Aplikacja główna systemu optymalizacji regeneratorów pieców szklarskich.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import init_db
from app.core.exceptions import FROptimizationError
from app.core.logging import setup_logging
from app.core.metrics import setup_metrics


logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    logger.info("Starting Forglass Regenerator Optimizer API")

    # Initialize database
    await init_db()

    # Setup metrics collection
    setup_metrics()

    logger.info("Application startup complete")
    yield

    logger.info("Shutting down application")


app = FastAPI(
    title="Forglass Regenerator Optimizer API",
    description="System optymalizacji regeneratorów pieców szklarskich",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else None,
    docs_url=f"{settings.API_V1_STR}/docs" if settings.DEBUG else None,
    redoc_url=f"{settings.API_V1_STR}/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Setup logging
setup_logging()

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

# CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    origins = [str(origin).rstrip('/') for origin in settings.BACKEND_CORS_ORIGINS]
    logger.info("CORS origins configured", origins=origins)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.exception_handler(FROptimizationError)
async def optimization_exception_handler(
    request: Request, exc: FROptimizationError
) -> JSONResponse:
    """Handle custom optimization errors."""
    logger.error(
        "Optimization error occurred",
        error=str(exc),
        path=request.url.path,
        method=request.method,
    )
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "type": "optimization_error"},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected errors."""
    logger.exception(
        "Unexpected error occurred",
        path=request.url.path,
        method=request.method,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "internal_error"},
    )


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "fro-api"}


@app.get("/metrics")
async def metrics() -> Response:
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )