"""
FastAPI microservice for SLSQP optimizer.
Mikroserwis FastAPI dla optymalizatora SLSQP.
"""

import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .schemas import OptimizationRequest, OptimizationResult, HealthResponse, ErrorResponse
from .optimizer import SLSQPOptimizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Version
VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    logger.info(f"Starting FRO Optimizer Service v{VERSION}")

    # Check scipy availability
    try:
        import scipy
        logger.info(f"SciPy version: {scipy.__version__}")
    except ImportError:
        logger.error("SciPy not available! Optimization will fail.")

    yield

    logger.info("Shutting down FRO Optimizer Service")


# Create FastAPI app
app = FastAPI(
    title="FRO SLSQP Optimizer",
    description="Microservice for regenerator optimization using SLSQP algorithm",
    version=VERSION,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="internal_server_error",
            message=str(exc),
            details={"type": type(exc).__name__}
        ).model_dump()
    )


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check."""
    return await health()


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    scipy_available = True
    try:
        import scipy
    except ImportError:
        scipy_available = False

    return HealthResponse(
        status="healthy" if scipy_available else "degraded",
        version=VERSION,
        scipy_available=scipy_available
    )


@app.post("/optimize", response_model=OptimizationResult)
async def optimize(request: OptimizationRequest):
    """
    Run SLSQP optimization.

    Args:
        request: Optimization request with configuration and parameters

    Returns:
        Optimization result with optimized design variables and performance metrics

    Raises:
        HTTPException: If optimization fails or input is invalid
    """
    logger.info(f"Received optimization request: objective={request.objective}, algorithm={request.algorithm}")

    # Validate algorithm
    if request.algorithm.upper() != "SLSQP":
        raise HTTPException(
            status_code=422,
            detail=ErrorResponse(
                error="validation_error",
                message=f"Unsupported algorithm: {request.algorithm}. Only SLSQP is supported.",
                details={"algorithm": request.algorithm}
            ).model_dump()
        )

    # Validate design variables
    if not request.design_variables:
        raise HTTPException(
            status_code=422,
            detail=ErrorResponse(
                error="validation_error",
                message="design_variables cannot be empty",
                details={}
            ).model_dump()
        )

    # Validate bounds
    if not request.bounds:
        raise HTTPException(
            status_code=422,
            detail=ErrorResponse(
                error="validation_error",
                message="bounds cannot be empty",
                details={}
            ).model_dump()
        )

    # Check that all design variables have bounds
    missing_bounds = set(request.design_variables.keys()) - set(request.bounds.keys())
    if missing_bounds:
        logger.warning(f"Some design variables missing bounds: {missing_bounds}. Using defaults.")

    try:
        # Create optimizer
        optimizer = SLSQPOptimizer()

        # Run optimization
        result = optimizer.optimize(request)

        logger.info(f"Optimization completed successfully: success={result['success']}, iterations={result['iterations']}")

        return OptimizationResult(**result)

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail=ErrorResponse(
                error="validation_error",
                message=str(e),
                details={}
            ).model_dump()
        )

    except Exception as e:
        logger.error(f"Optimization failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="optimization_error",
                message=f"Optimization failed: {str(e)}",
                details={"type": type(e).__name__}
            ).model_dump()
        )


@app.get("/api/docs")
async def api_docs():
    """Redirect to Swagger UI."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=7000,
        log_level="info",
        reload=False  # Set to True for development
    )
