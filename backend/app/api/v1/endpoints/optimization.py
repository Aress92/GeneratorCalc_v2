"""
Optimization endpoints.

Endpointy optymalizacji.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
import json
import asyncio

from app.api.dependencies import get_current_user, get_db
from app.models.user import User, UserRole
from app.models.optimization import OptimizationScenario, OptimizationJob, OptimizationResult
from app.schemas.optimization_schemas import (
    OptimizationScenarioCreate, OptimizationScenarioUpdate, OptimizationScenarioResponse,
    OptimizationJobCreate, OptimizationJobResponse, OptimizationResultResponse,
    OptimizationProgress, OptimizationJobStatus, OptimizationScenarioList,
    OptimizationJobList, OptimizationTemplateCreate, OptimizationTemplateResponse,
    OptimizationTemplateList, OptimizationCalculationPreview
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
        design_variables=scenario_data.design_variables,
        constraints_config={
            "constraints": scenario_data.constraints or []
        },
        bounds_config={
            var_name: {"min": var_config.get("min_value"), "max": var_config.get("max_value")}
            for var_name, var_config in scenario_data.design_variables.items()
            if isinstance(var_config, dict) and "min_value" in var_config and "max_value" in var_config
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

    user_id_str = str(current_user.id)
    stmt = select(OptimizationScenario).where(
        OptimizationScenario.user_id == user_id_str,
        OptimizationScenario.is_active == True
    ).order_by(desc(OptimizationScenario.created_at)).offset(skip).limit(limit)

    result = await db.execute(stmt)
    scenarios = result.scalars().all()

    # Count total
    count_stmt = select(OptimizationScenario).where(
        OptimizationScenario.user_id == user_id_str,
        OptimizationScenario.is_active == True
    )
    count_result = await db.execute(count_stmt)
    total_count = len(count_result.scalars().all())

    return OptimizationScenarioList(
        scenarios=[OptimizationScenarioResponse.model_validate(s) for s in scenarios],
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

    user_id_str = str(current_user.id)
    stmt = select(OptimizationScenario).where(
        OptimizationScenario.id == scenario_id,
        OptimizationScenario.user_id == user_id_str
    )
    result = await db.execute(stmt)
    scenario = result.scalar_one_or_none()

    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    return OptimizationScenarioResponse.model_validate(scenario)


@router.get("/scenarios/{scenario_id}/calculation-preview", response_model=OptimizationCalculationPreview)
async def get_scenario_calculation_preview(
    scenario_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed calculation preview for an optimization scenario.
    Shows step-by-step formulas and intermediate results.

    Pobierz szczegółowy podgląd obliczeń dla scenariusza optymalizacji.
    Pokazuje krok po kroku wzory i wyniki pośrednie.
    """

    user_id_str = str(current_user.id)
    stmt = select(OptimizationScenario).where(
        OptimizationScenario.id == scenario_id,
        OptimizationScenario.user_id == user_id_str
    )
    result = await db.execute(stmt)
    scenario = result.scalar_one_or_none()

    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Generate calculation preview
    service = OptimizationService(db)
    preview = await service.preview_scenario_calculations(scenario_id, design_vars_input=None)

    return preview


@router.put("/scenarios/{scenario_id}", response_model=OptimizationScenarioResponse)
async def update_optimization_scenario(
    scenario_id: str,
    scenario_update: OptimizationScenarioUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update optimization scenario."""

    user_id_str = str(current_user.id)
    stmt = select(OptimizationScenario).where(
        OptimizationScenario.id == scenario_id,
        OptimizationScenario.user_id == user_id_str
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

    return OptimizationScenarioResponse.model_validate(scenario)


@router.delete("/scenarios/{scenario_id}")
async def delete_optimization_scenario(
    scenario_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete (deactivate) optimization scenario."""

    user_id_str = str(current_user.id)
    stmt = select(OptimizationScenario).where(
        OptimizationScenario.id == scenario_id,
        OptimizationScenario.user_id == user_id_str
    )
    result = await db.execute(stmt)
    scenario = result.scalar_one_or_none()

    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    scenario.is_active = False
    await db.commit()

    return {"message": "Scenario deleted successfully"}


@router.post("/scenarios/bulk-delete")
async def bulk_delete_scenarios(
    scenario_ids: list[str],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Bulk delete (deactivate) optimization scenarios."""

    if not scenario_ids:
        raise HTTPException(status_code=400, detail="No scenario IDs provided")

    user_id_str = str(current_user.id)
    stmt = select(OptimizationScenario).where(
        OptimizationScenario.id.in_(scenario_ids),
        OptimizationScenario.user_id == user_id_str,
        OptimizationScenario.is_active == True
    )
    result = await db.execute(stmt)
    scenarios = result.scalars().all()

    if not scenarios:
        raise HTTPException(status_code=404, detail="No scenarios found to delete")

    deleted_count = 0
    for scenario in scenarios:
        scenario.is_active = False
        deleted_count += 1

    await db.commit()

    return {
        "message": f"Successfully deleted {deleted_count} scenario(s)",
        "deleted_count": deleted_count
    }


# Jobs endpoints
@router.post("/scenarios/{scenario_id}/jobs", response_model=OptimizationJobResponse)
async def create_optimization_job(
    scenario_id: str,
    job_data: OptimizationJobCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create and start optimization job using Celery.

    Tworzy i uruchamia zadanie optymalizacji za pomocą Celery.
    """
    try:
        # Permission check
        if current_user.role not in [UserRole.ADMIN, UserRole.ENGINEER]:
            raise HTTPException(
                status_code=403,
                detail={
                    "error_type": "PERMISSION_DENIED",
                    "message": "Brak uprawnień do tworzenia zadań optymalizacji",
                    "details": "Wymagana rola: ADMIN lub ENGINEER",
                    "suggestion": "Skontaktuj się z administratorem w celu nadania odpowiednich uprawnień",
                    "user_role": current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
                }
            )

        # Check scenario exists and belongs to user
        user_id_str = str(current_user.id)
        stmt = select(OptimizationScenario).where(
            OptimizationScenario.id == scenario_id,
            OptimizationScenario.user_id == user_id_str
        )
        result = await db.execute(stmt)
        scenario = result.scalar_one_or_none()

        if not scenario:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_type": "SCENARIO_NOT_FOUND",
                    "message": f"Scenariusz optymalizacji nie został znaleziony",
                    "details": f"Scenariusz o ID '{scenario_id}' nie istnieje lub nie należy do tego użytkownika",
                    "suggestion": "Sprawdź poprawność ID scenariusza lub utwórz nowy scenariusz w zakładce 'Scenariusze'",
                    "scenario_id": scenario_id
                }
            )

        # Validate scenario is active
        if not scenario.is_active:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_type": "SCENARIO_INACTIVE",
                    "message": "Scenariusz jest nieaktywny",
                    "details": f"Scenariusz '{scenario.name}' został dezaktywowany i nie może być użyty",
                    "suggestion": "Aktywuj scenariusz lub utwórz nowy",
                    "scenario_id": scenario_id,
                    "scenario_name": scenario.name
                }
            )

        # Check for design variables
        if not scenario.design_variables or len(scenario.design_variables) == 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_type": "NO_DESIGN_VARIABLES",
                    "message": "Scenariusz nie ma zdefiniowanych zmiennych projektowych",
                    "details": "Optymalizacja wymaga co najmniej jednej zmiennej projektowej (np. checker_height, checker_spacing)",
                    "suggestion": "Edytuj scenariusz i dodaj zmienne projektowe w sekcji 'Design Variables'",
                    "scenario_id": scenario_id,
                    "scenario_name": scenario.name
                }
            )

        # Validate base configuration exists
        from app.models.regenerator import RegeneratorConfiguration
        config_stmt = select(RegeneratorConfiguration).where(
            RegeneratorConfiguration.id == scenario.base_configuration_id
        )
        config_result = await db.execute(config_stmt)
        base_config = config_result.scalar_one_or_none()

        if not base_config:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_type": "BASE_CONFIG_NOT_FOUND",
                    "message": "Bazowa konfiguracja regeneratora nie została znaleziona",
                    "details": f"Konfiguracja o ID '{scenario.base_configuration_id}' nie istnieje w bazie danych",
                    "suggestion": "Utwórz nową konfigurację regeneratora w zakładce 'Konfiguracje' lub wybierz inną konfigurację bazową dla scenariusza",
                    "scenario_id": scenario_id,
                    "config_id": scenario.base_configuration_id
                }
            )

        # ✅ RATE LIMITING: Check per-user concurrent jobs limit
        user_jobs_stmt = select(OptimizationJob).where(
            OptimizationJob.user_id == user_id_str,
            OptimizationJob.status.in_(['pending', 'initializing', 'running'])
        )
        user_jobs_result = await db.execute(user_jobs_stmt)
        active_user_jobs = user_jobs_result.scalars().all()

        if len(active_user_jobs) >= settings.MAX_CONCURRENT_JOBS_PER_USER:
            raise HTTPException(
                status_code=429,
                detail={
                    "error_type": "USER_RATE_LIMIT_EXCEEDED",
                    "message": f"Przekroczono limit współbieżnych zadań użytkownika ({len(active_user_jobs)}/{settings.MAX_CONCURRENT_JOBS_PER_USER})",
                    "details": f"Możesz mieć maksymalnie {settings.MAX_CONCURRENT_JOBS_PER_USER} aktywnych zadań optymalizacji jednocześnie",
                    "suggestion": "Poczekaj na zakończenie lub anuluj jedno z aktywnych zadań przed utworzeniem nowego",
                    "active_jobs_count": len(active_user_jobs),
                    "max_allowed": settings.MAX_CONCURRENT_JOBS_PER_USER,
                    "active_job_ids": [job.id for job in active_user_jobs],
                    "active_job_names": [job.job_name or f"Job {job.id[:8]}" for job in active_user_jobs]
                }
            )

        # ✅ RATE LIMITING: Check per-scenario concurrent jobs limit
        scenario_jobs_stmt = select(OptimizationJob).where(
            OptimizationJob.scenario_id == scenario_id,
            OptimizationJob.status.in_(['pending', 'initializing', 'running'])
        )
        scenario_jobs_result = await db.execute(scenario_jobs_stmt)
        active_scenario_jobs = scenario_jobs_result.scalars().all()

        if len(active_scenario_jobs) >= settings.MAX_CONCURRENT_JOBS_PER_SCENARIO:
            raise HTTPException(
                status_code=429,
                detail={
                    "error_type": "SCENARIO_RATE_LIMIT_EXCEEDED",
                    "message": f"Dla tego scenariusza działa już {len(active_scenario_jobs)} zadanie",
                    "details": f"Maksymalnie {settings.MAX_CONCURRENT_JOBS_PER_SCENARIO} zadanie może być aktywne jednocześnie dla jednego scenariusza",
                    "suggestion": "Poczekaj na zakończenie lub anuluj aktywne zadanie przed utworzeniem nowego",
                    "scenario_id": scenario_id,
                    "scenario_name": scenario.name,
                    "active_jobs_count": len(active_scenario_jobs),
                    "max_allowed": settings.MAX_CONCURRENT_JOBS_PER_SCENARIO,
                    "active_job_ids": [job.id for job in active_scenario_jobs]
                }
            )

        # Create job
        optimization_service = OptimizationService(db)
        job = await optimization_service.create_optimization_job(
            scenario_id=scenario_id,
            user_id=user_id_str,
            job_config=job_data
        )

        # Start optimization using Celery (true async with separate worker)
        # Note: celery_task_id will be set by the task itself when it starts
        from app.tasks.optimization_tasks import run_optimization_task
        run_optimization_task.delay(job.id)

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as ve:
        # Handle validation errors from service layer
        raise HTTPException(
            status_code=400,
            detail={
                "error_type": "VALIDATION_ERROR",
                "message": "Błąd walidacji danych wejściowych",
                "details": str(ve),
                "suggestion": "Sprawdź poprawność danych wejściowych (np. wartości początkowe, granice zmiennych)",
                "scenario_id": scenario_id
            }
        )
    except Exception as e:
        # Catch-all for unexpected errors
        import traceback
        error_trace = traceback.format_exc()

        raise HTTPException(
            status_code=500,
            detail={
                "error_type": "INTERNAL_SERVER_ERROR",
                "message": "Nieoczekiwany błąd podczas tworzenia zadania optymalizacji",
                "details": str(e),
                "suggestion": "Spróbuj ponownie za chwilę. Jeśli problem się powtarza, skontaktuj się z administratorem",
                "error_trace": error_trace if settings.DEBUG else None
            }
        )

    return OptimizationJobResponse.model_validate(job)


@router.get("/jobs", response_model=OptimizationJobList)
async def list_optimization_jobs(
    scenario_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List optimization jobs for the current user."""

    user_id_str = str(current_user.id)
    conditions = [OptimizationJob.user_id == user_id_str]
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
        jobs=[OptimizationJobResponse.model_validate(j) for j in jobs],
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

    user_id_str = str(current_user.id)
    stmt = select(OptimizationJob).where(
        OptimizationJob.id == job_id,
        OptimizationJob.user_id == user_id_str
    )
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return OptimizationJobResponse.model_validate(job)


@router.get("/jobs/{job_id}/progress", response_model=OptimizationProgress)
async def get_optimization_progress(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get real-time optimization progress."""

    # Verify job belongs to user
    user_id_str = str(current_user.id)
    stmt = select(OptimizationJob).where(
        OptimizationJob.id == job_id,
        OptimizationJob.user_id == user_id_str
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

    user_id_str = str(current_user.id)
    stmt = select(OptimizationJob).where(
        OptimizationJob.id == job_id,
        OptimizationJob.user_id == user_id_str
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

    user_id_str = str(current_user.id)
    stmt = select(OptimizationJob).where(
        OptimizationJob.id == job_id,
        OptimizationJob.user_id == user_id_str
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


@router.post("/jobs/bulk-delete")
async def bulk_delete_jobs(
    job_ids: list[str],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Bulk delete optimization jobs. Only completed, failed, or cancelled jobs can be deleted."""

    if not job_ids:
        raise HTTPException(status_code=400, detail="No job IDs provided")

    user_id_str = str(current_user.id)
    stmt = select(OptimizationJob).where(
        OptimizationJob.id.in_(job_ids),
        OptimizationJob.user_id == user_id_str
    )
    result = await db.execute(stmt)
    jobs = result.scalars().all()

    if not jobs:
        raise HTTPException(status_code=404, detail="No jobs found to delete")

    deleted_count = 0
    skipped_count = 0
    for job in jobs:
        # Only allow deletion of finished jobs
        if job.status in ['completed', 'failed', 'cancelled']:
            await db.delete(job)
            deleted_count += 1
        else:
            skipped_count += 1

    await db.commit()

    return {
        "message": f"Successfully deleted {deleted_count} job(s), skipped {skipped_count} running job(s)",
        "deleted_count": deleted_count,
        "skipped_count": skipped_count
    }


# Results endpoints
@router.get("/jobs/{job_id}/results", response_model=OptimizationResultResponse)
async def get_optimization_results(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get optimization results."""

    # Verify job belongs to user
    user_id_str = str(current_user.id)
    stmt = select(OptimizationJob).where(
        OptimizationJob.id == job_id,
        OptimizationJob.user_id == user_id_str
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

    return OptimizationResultResponse.model_validate(optimization_result)


@router.get("/jobs/{job_id}/iterations")
async def get_optimization_iterations(
    job_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get optimization iterations for a job."""

    # Verify job belongs to user
    user_id_str = str(current_user.id)
    stmt = select(OptimizationJob).where(
        OptimizationJob.id == job_id,
        OptimizationJob.user_id == user_id_str
    )
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get iterations
    from app.models.optimization import OptimizationIteration
    iter_stmt = select(OptimizationIteration).where(
        OptimizationIteration.job_id == job_id
    ).order_by(OptimizationIteration.iteration_number.asc()).offset(skip).limit(limit)

    iter_result = await db.execute(iter_stmt)
    iterations = iter_result.scalars().all()

    # Return as list of dicts
    return [
        {
            "id": str(iteration.id),
            "job_id": str(iteration.job_id),
            "iteration_number": iteration.iteration_number,
            "function_evaluation": iteration.function_evaluation,
            "design_variables": iteration.design_variables,
            "objective_value": iteration.objective_value,
            "objective_components": iteration.objective_components,
            "constraint_values": iteration.constraint_values,
            "constraint_violations": iteration.constraint_violations,
            "performance_metrics": iteration.performance_metrics,
            "evaluation_time_seconds": iteration.evaluation_time_seconds,
            "is_feasible": iteration.is_feasible,
            "is_improvement": iteration.is_improvement,
            "created_at": iteration.created_at.isoformat() if iteration.created_at else None
        }
        for iteration in iterations
    ]


# Server-Sent Events for real-time updates
@router.get("/jobs/{job_id}/events")
async def get_optimization_events(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Stream optimization events via Server-Sent Events."""

    # Verify job belongs to user
    user_id_str = str(current_user.id)
    stmt = select(OptimizationJob).where(
        OptimizationJob.id == job_id,
        OptimizationJob.user_id == user_id_str
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
                    "data": progress.model_dump() if hasattr(progress, 'model_dump') else progress
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