"""
Optimization endpoints.

Endpointy optymalizacji.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
import json

from app.api.dependencies import get_current_user, get_db
from app.models.user import User, UserRole
from app.models.optimization import OptimizationScenario, OptimizationJob, OptimizationResult
from app.schemas.optimization_schemas import (
    OptimizationScenarioCreate, OptimizationScenarioUpdate, OptimizationScenarioResponse,
    OptimizationJobCreate, OptimizationJobResponse, OptimizationResultResponse,
    OptimizationProgress, OptimizationJobStatus, OptimizationScenarioList,
    OptimizationJobList, OptimizationTemplateCreate, OptimizationTemplateResponse,
    OptimizationTemplateList
)
from app.services.optimization_service import OptimizationService
from app.core.config import settings

router = APIRouter()


# Scenarios endpoints
@router.post("/scenarios", response_model=OptimizationScenarioResponse)
async def create_optimization_scenario(
    scenario_data: OptimizationScenarioCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new optimization scenario."""

    # Check if user has permission to create scenarios
    if current_user.role not in [UserRole.ADMIN, UserRole.ENGINEER]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # Check if base configuration exists
    from app.models.regenerator import RegeneratorConfiguration
    stmt = select(RegeneratorConfiguration).where(
        RegeneratorConfiguration.id == scenario_data.base_configuration_id
    )
    result = await db.execute(stmt)
    base_config = result.scalar_one_or_none()

    if not base_config:
        raise HTTPException(status_code=404, detail="Base configuration not found")

    # Create scenario
    scenario = OptimizationScenario(
        user_id=current_user.id,
        name=scenario_data.name,
        description=scenario_data.description,
        scenario_type=scenario_data.scenario_type,
        base_configuration_id=scenario_data.base_configuration_id,
        objective=scenario_data.objective,
        algorithm=scenario_data.algorithm,
        optimization_config={
            "algorithm": scenario_data.algorithm,
            "objective": scenario_data.objective,
            "max_iterations": scenario_data.max_iterations,
            "tolerance": scenario_data.tolerance
        },
        design_variables={
            var_name: var_config.dict()
            for var_name, var_config in scenario_data.design_variables.items()
        },
        constraints_config={
            "constraints": [c.dict() for c in (scenario_data.constraints or [])]
        },
        bounds_config={
            var_name: {"min": var_config.min_value, "max": var_config.max_value}
            for var_name, var_config in scenario_data.design_variables.items()
        },
        max_iterations=scenario_data.max_iterations,
        max_function_evaluations=scenario_data.max_function_evaluations,
        tolerance=scenario_data.tolerance,
        max_runtime_minutes=scenario_data.max_runtime_minutes,
        objective_weights=scenario_data.objective_weights
    )

    db.add(scenario)
    await db.commit()
    await db.refresh(scenario)

    return OptimizationScenarioResponse.model_validate(scenario)


@router.get("/scenarios", response_model=OptimizationScenarioList)
async def list_optimization_scenarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List optimization scenarios for the current user."""

    stmt = select(OptimizationScenario).where(
        OptimizationScenario.user_id == current_user.id,
        OptimizationScenario.is_active == True
    ).order_by(desc(OptimizationScenario.created_at)).offset(skip).limit(limit)

    result = await db.execute(stmt)
    scenarios = result.scalars().all()

    # Count total
    count_stmt = select(OptimizationScenario).where(
        OptimizationScenario.user_id == current_user.id,
        OptimizationScenario.is_active == True
    )
    count_result = await db.execute(count_stmt)
    total_count = len(count_result.scalars().all())

    return OptimizationScenarioList(
        scenarios=[OptimizationScenarioResponse.from_orm(s) for s in scenarios],
        total_count=total_count,
        page=skip // limit + 1,
        per_page=limit
    )


@router.get("/scenarios/{scenario_id}", response_model=OptimizationScenarioResponse)
async def get_optimization_scenario(
    scenario_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get optimization scenario by ID."""

    stmt = select(OptimizationScenario).where(
        OptimizationScenario.id == scenario_id,
        OptimizationScenario.user_id == current_user.id
    )
    result = await db.execute(stmt)
    scenario = result.scalar_one_or_none()

    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    return OptimizationScenarioResponse.from_orm(scenario)


@router.put("/scenarios/{scenario_id}", response_model=OptimizationScenarioResponse)
async def update_optimization_scenario(
    scenario_id: str,
    scenario_update: OptimizationScenarioUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update optimization scenario."""

    stmt = select(OptimizationScenario).where(
        OptimizationScenario.id == scenario_id,
        OptimizationScenario.user_id == current_user.id
    )
    result = await db.execute(stmt)
    scenario = result.scalar_one_or_none()

    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Update fields
    update_data = scenario_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(scenario, field, value)

    await db.commit()
    await db.refresh(scenario)

    return OptimizationScenarioResponse.from_orm(scenario)


@router.delete("/scenarios/{scenario_id}")
async def delete_optimization_scenario(
    scenario_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete (deactivate) optimization scenario."""

    stmt = select(OptimizationScenario).where(
        OptimizationScenario.id == scenario_id,
        OptimizationScenario.user_id == current_user.id
    )
    result = await db.execute(stmt)
    scenario = result.scalar_one_or_none()

    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    scenario.is_active = False
    await db.commit()

    return {"message": "Scenario deleted successfully"}


# Jobs endpoints
@router.post("/scenarios/{scenario_id}/jobs", response_model=OptimizationJobResponse)
async def create_optimization_job(
    scenario_id: str,
    job_data: OptimizationJobCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create and start optimization job."""

    if current_user.role not in ['admin', 'engineer']:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # Check scenario exists and belongs to user
    stmt = select(OptimizationScenario).where(
        OptimizationScenario.id == scenario_id,
        OptimizationScenario.user_id == current_user.id
    )
    result = await db.execute(stmt)
    scenario = result.scalar_one_or_none()

    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Create job
    optimization_service = OptimizationService(db)
    job = await optimization_service.create_optimization_job(
        scenario_id=scenario_id,
        user_id=current_user.id,
        job_config=job_data
    )

    # Start optimization in background
    background_tasks.add_task(optimization_service.run_optimization, job.id)

    return OptimizationJobResponse.from_orm(job)


@router.get("/jobs", response_model=OptimizationJobList)
async def list_optimization_jobs(
    scenario_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List optimization jobs for the current user."""

    conditions = [OptimizationJob.user_id == current_user.id]
    if scenario_id:
        conditions.append(OptimizationJob.scenario_id == scenario_id)

    stmt = select(OptimizationJob).where(
        and_(*conditions)
    ).order_by(desc(OptimizationJob.created_at)).offset(skip).limit(limit)

    result = await db.execute(stmt)
    jobs = result.scalars().all()

    # Count total
    count_stmt = select(OptimizationJob).where(and_(*conditions))
    count_result = await db.execute(count_stmt)
    total_count = len(count_result.scalars().all())

    return OptimizationJobList(
        jobs=[OptimizationJobResponse.from_orm(j) for j in jobs],
        total_count=total_count,
        page=skip // limit + 1,
        per_page=limit
    )


@router.get("/jobs/{job_id}", response_model=OptimizationJobResponse)
async def get_optimization_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get optimization job by ID."""

    stmt = select(OptimizationJob).where(
        OptimizationJob.id == job_id,
        OptimizationJob.user_id == current_user.id
    )
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return OptimizationJobResponse.from_orm(job)


@router.get("/jobs/{job_id}/progress", response_model=OptimizationProgress)
async def get_optimization_progress(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get real-time optimization progress."""

    # Verify job belongs to user
    stmt = select(OptimizationJob).where(
        OptimizationJob.id == job_id,
        OptimizationJob.user_id == current_user.id
    )
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    optimization_service = OptimizationService(db)
    progress = await optimization_service.get_optimization_progress(job_id)

    return progress


@router.get("/jobs/{job_id}/status", response_model=OptimizationJobStatus)
async def get_optimization_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get simple optimization job status."""

    stmt = select(OptimizationJob).where(
        OptimizationJob.id == job_id,
        OptimizationJob.user_id == current_user.id
    )
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return OptimizationJobStatus(
        job_id=job.id,
        status=job.status,
        progress_percentage=job.progress_percentage,
        current_iteration=job.current_iteration,
        estimated_completion_at=job.estimated_completion_at,
        error_message=job.error_message
    )


@router.post("/jobs/{job_id}/cancel")
async def cancel_optimization_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel running optimization job."""

    stmt = select(OptimizationJob).where(
        OptimizationJob.id == job_id,
        OptimizationJob.user_id == current_user.id
    )
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status not in ['pending', 'initializing', 'running']:
        raise HTTPException(status_code=400, detail="Job cannot be cancelled")

    # Cancel Celery task if exists
    if job.celery_task_id:
        from app.celery import celery_app
        celery_app.control.revoke(job.celery_task_id, terminate=True)

    job.status = 'cancelled'
    await db.commit()

    return {"message": "Job cancelled successfully"}


# Results endpoints
@router.get("/jobs/{job_id}/results", response_model=OptimizationResultResponse)
async def get_optimization_results(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get optimization results."""

    # Verify job belongs to user
    stmt = select(OptimizationJob).where(
        OptimizationJob.id == job_id,
        OptimizationJob.user_id == current_user.id
    )
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get results
    result_stmt = select(OptimizationResult).where(
        OptimizationResult.job_id == job_id
    )
    result_result = await db.execute(result_stmt)
    optimization_result = result_result.scalar_one_or_none()

    if not optimization_result:
        raise HTTPException(status_code=404, detail="Results not available yet")

    return OptimizationResultResponse.from_orm(optimization_result)


# Server-Sent Events for real-time updates
@router.get("/jobs/{job_id}/events")
async def get_optimization_events(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Stream optimization events via Server-Sent Events."""

    # Verify job belongs to user
    stmt = select(OptimizationJob).where(
        OptimizationJob.id == job_id,
        OptimizationJob.user_id == current_user.id
    )
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    async def event_stream():
        """Generate Server-Sent Events stream."""
        optimization_service = OptimizationService(db)

        while True:
            try:
                # Get current progress
                progress = await optimization_service.get_optimization_progress(job_id)

                # Send progress event
                event_data = {
                    "type": "progress",
                    "job_id": job_id,
                    "data": progress.dict()
                }

                yield f"data: {json.dumps(event_data)}\n\n"

                # Check if job is complete
                if progress.status in ['completed', 'failed', 'cancelled']:
                    break

                # Wait before next update
                await asyncio.sleep(2)

            except Exception as e:
                error_event = {
                    "type": "error",
                    "job_id": job_id,
                    "data": {"error": str(e)}
                }
                yield f"data: {json.dumps(error_event)}\n\n"
                break

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )