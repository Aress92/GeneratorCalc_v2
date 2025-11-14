"""
FastAPI application for SLSQP Optimizer Microservice.
Exposes HTTP endpoints for .NET backend to call for thermal optimization.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.config import settings
from app.models import (
    OptimizationRequest,
    OptimizationResult,
    PerformanceRequest,
    PerformanceMetrics,
    HealthResponse,
    DesignVariables
)
from app.optimizer import RegeneratorPhysicsModel, SLSQPOptimizer

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("🚀 SLSQP Optimizer Microservice starting...")
    logger.info(f"   Host: {settings.HOST}")
    logger.info(f"   Port: {settings.PORT}")
    logger.info(f"   CORS Origins: {settings.CORS_ORIGINS}")
    yield
    logger.info("👋 SLSQP Optimizer Microservice shutting down...")


app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.API_VERSION,
        message="SLSQP Optimizer Microservice is running"
    )


@app.post("/api/v1/optimize", response_model=OptimizationResult, tags=["Optimization"])
async def run_optimization(request: OptimizationRequest):
    """
    Run SLSQP optimization for regenerator configuration.

    This is the main endpoint that .NET API will call to perform optimization.

    Args:
        request: OptimizationRequest with configuration, initial guess, and parameters

    Returns:
        OptimizationResult with optimized design variables and performance metrics
    """
    try:
        logger.info(f"Received optimization request: objective={request.objective_type}, "
                   f"max_iter={request.max_iterations}")

        # Initialize physics model
        physics_model = RegeneratorPhysicsModel(request.configuration)

        # Initialize optimizer
        optimizer = SLSQPOptimizer(physics_model)

        # Run optimization
        scipy_result, iteration_history, computation_time = optimizer.optimize(
            initial_guess=request.initial_guess,
            bounds=request.bounds,
            objective_type=request.objective_type,
            max_iterations=request.max_iterations,
            tolerance=request.tolerance
        )

        # Extract final design variables
        final_design_vars = DesignVariables(
            checker_height=float(scipy_result.x[0]),
            checker_spacing=float(scipy_result.x[1]),
            wall_thickness=float(scipy_result.x[2]),
            thermal_conductivity=float(scipy_result.x[3]),
            specific_heat=float(scipy_result.x[4]),
            density=float(scipy_result.x[5])
        )

        # Calculate final performance
        final_performance = physics_model.calculate_thermal_performance({
            "checker_height": final_design_vars.checker_height,
            "checker_spacing": final_design_vars.checker_spacing,
            "wall_thickness": final_design_vars.wall_thickness,
            "thermal_conductivity": final_design_vars.thermal_conductivity,
            "specific_heat": final_design_vars.specific_heat,
            "density": final_design_vars.density
        })

        logger.info(f"Optimization completed: success={scipy_result.success}, "
                   f"iterations={scipy_result.nit}, "
                   f"final_objective={scipy_result.fun:.6f}, "
                   f"thermal_efficiency={final_performance.thermal_efficiency:.4f}")

        return OptimizationResult(
            success=bool(scipy_result.success),
            message=scipy_result.message,
            final_design_variables=final_design_vars,
            final_performance=final_performance,
            objective_value=float(scipy_result.fun),
            iterations=int(scipy_result.nit),
            convergence_reached=bool(scipy_result.success),
            computation_time_seconds=computation_time,
            iteration_history=iteration_history[-10:] if len(iteration_history) > 10 else iteration_history
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Optimization failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@app.post("/api/v1/performance", response_model=PerformanceMetrics, tags=["Calculation"])
async def calculate_performance(request: PerformanceRequest):
    """
    Calculate thermal performance for given design variables without optimization.

    Useful for:
    - Validating configurations
    - Previewing calculations
    - Testing physics model

    Args:
        request: PerformanceRequest with configuration and design variables

    Returns:
        PerformanceMetrics with calculated values
    """
    try:
        logger.info("Received performance calculation request")

        # Initialize physics model
        physics_model = RegeneratorPhysicsModel(request.configuration)

        # Calculate performance
        performance = physics_model.calculate_thermal_performance({
            "checker_height": request.design_variables.checker_height,
            "checker_spacing": request.design_variables.checker_spacing,
            "wall_thickness": request.design_variables.wall_thickness,
            "thermal_conductivity": request.design_variables.thermal_conductivity or 2.5,
            "specific_heat": request.design_variables.specific_heat or 900,
            "density": request.design_variables.density or 2300
        })

        logger.info(f"Performance calculated: thermal_efficiency={performance.thermal_efficiency:.4f}, "
                   f"pressure_drop={performance.pressure_drop:.2f} Pa")

        return performance

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Performance calculation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Calculation failed: {str(e)}")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred"}
    )


def main():
    """Run the FastAPI application."""
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,  # Disable reload in production
        log_level=settings.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()
