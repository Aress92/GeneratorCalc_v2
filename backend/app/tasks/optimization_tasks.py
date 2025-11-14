"""
Celery tasks for optimization operations.

Zadania Celery dla operacji optymalizacji.
"""

from datetime import datetime, timedelta, UTC
from typing import Optional, Dict, Any
import structlog
from celery import Task
import asyncio
import nest_asyncio

from app.celery import celery_app
from app.core.database import AsyncSessionLocal
from app.services.optimization_service import OptimizationService
from app.models.optimization import OptimizationStatus

logger = structlog.get_logger(__name__)


class AsyncCeleryTask(Task):
    """Base class for async Celery tasks with proper event loop handling."""

    def __call__(self, *args, **kwargs):
        # Apply nest_asyncio to allow nested event loops in Celery worker context
        nest_asyncio.apply()

        # Create new event loop for this task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.run_async(*args, **kwargs))
        finally:
            loop.close()

    async def run_async(self, *args, **kwargs):
        # This method should be overridden by subclasses
        raise NotImplementedError("Subclasses must implement run_async")


class RunOptimizationTask(AsyncCeleryTask):
    """Celery task to run optimization in background."""

    name = "app.tasks.optimization_tasks.run_optimization_task"

    async def run_async(self, job_id: str) -> Dict[str, Any]:
        """
        Run optimization task asynchronously.

        Args:
            job_id: ID of the optimization job to run

        Returns:
            Dictionary with optimization results
        """
        logger.info("Starting optimization task", job_id=job_id, task_id=self.request.id)

        try:
            async with AsyncSessionLocal() as db:
                # Update job with Celery task ID
                from sqlalchemy import select
                from app.models.optimization import OptimizationJob

                stmt = select(OptimizationJob).where(OptimizationJob.id == job_id)
                result = await db.execute(stmt)
                job = result.scalar_one_or_none()

                if not job:
                    raise ValueError(f"Job {job_id} not found")

                job.celery_task_id = self.request.id
                job.status = OptimizationStatus.RUNNING
                job.started_at = datetime.now(UTC)
                await db.commit()

                # Create optimization service
                optimization_service = OptimizationService(db)

                # Progress callback for Celery
                # NOTE: This is called from SLSQP optimizer (sync context), so we can't use await
                # IMPORTANT: We ONLY update Celery state here, NOT the database!
                # Database updates will happen after optimization completes to avoid event loop conflicts
                def update_progress(current_iter: int, max_iter: int, objective_value: Optional[float] = None):
                    progress = min(100, (current_iter / max_iter) * 100)

                    # Update Celery task state (this is sync-safe)
                    self.update_state(
                        state='PROGRESS',
                        meta={
                            'current_iteration': current_iter,
                            'max_iterations': max_iter,
                            'progress': progress,
                            'objective_value': objective_value
                        }
                    )

                    logger.debug(
                        "Progress update",
                        iteration=current_iter,
                        max_iterations=max_iter,
                        progress=progress,
                        objective_value=objective_value
                    )

                # Set progress callback in optimization service
                optimization_service.progress_callback = update_progress

                # Run optimization
                result = await optimization_service.run_optimization(job_id)

                logger.info("Optimization completed successfully", job_id=job_id)

                return {
                    'job_id': job_id,
                    'status': 'completed',
                    'result_id': result.id if result else None,
                    'objective_value': result.objective_value if result else None,
                    'fuel_savings_percentage': result.fuel_savings_percentage if result else None,
                    'co2_reduction_percentage': result.co2_reduction_percentage if result else None
                }

        except Exception as e:
            logger.error("Optimization task failed", job_id=job_id, error=str(e), exc_info=True)

            # Update job status to failed (includes celery_task_id)
            try:
                await update_job_status_failed(job_id, str(e), self.request.id)
            except Exception as update_error:
                logger.error("Failed to update job status to failed", error=str(update_error))

            # Re-raise exception for Celery
            raise


# Register task with Celery
run_optimization_task = celery_app.register_task(RunOptimizationTask())


async def update_job_progress(
    job_id: str,
    current_iteration: int,
    progress_percentage: float,
    objective_value: Optional[float] = None
):
    """Update job progress in database."""
    try:
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select
            from app.models.optimization import OptimizationJob

            stmt = select(OptimizationJob).where(OptimizationJob.id == job_id)
            result = await db.execute(stmt)
            job = result.scalar_one_or_none()

            if job:
                job.current_iteration = current_iteration
                job.progress_percentage = progress_percentage
                if objective_value is not None:
                    job.final_objective_value = objective_value

                # Estimate completion time
                if job.started_at and progress_percentage > 0:
                    now = datetime.now(UTC)
                    elapsed = (now - job.started_at).total_seconds()
                    total_estimated = elapsed / (progress_percentage / 100)
                    remaining = total_estimated - elapsed
                    job.estimated_completion_at = now + timedelta(seconds=remaining)

                await db.commit()

    except Exception as e:
        logger.warning("Failed to update job progress", job_id=job_id, error=str(e))


async def update_job_status_failed(job_id: str, error_message: str, celery_task_id: Optional[str] = None):
    """Update job status to failed."""
    try:
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select
            from app.models.optimization import OptimizationJob

            stmt = select(OptimizationJob).where(OptimizationJob.id == job_id)
            result = await db.execute(stmt)
            job = result.scalar_one_or_none()

            if job:
                job.status = OptimizationStatus.FAILED
                job.error_message = error_message
                job.completed_at = datetime.now(UTC)
                if celery_task_id and not job.celery_task_id:
                    job.celery_task_id = celery_task_id
                if job.started_at:
                    job.runtime_seconds = (job.completed_at - job.started_at).total_seconds()

                await db.commit()

    except Exception as e:
        logger.error("Failed to update job status to failed", job_id=job_id, error=str(e))


@celery_app.task
def cleanup_old_optimization_jobs() -> Dict[str, int]:
    """
    Cleanup task to remove old completed optimization jobs.

    Runs periodically to clean up completed jobs older than 30 days.
    """

    logger.info("Starting optimization jobs cleanup")

    try:
        async def cleanup_async():
            async with AsyncSessionLocal() as db:
                from sqlalchemy import select, delete
                from app.models.optimization import OptimizationJob, OptimizationIteration

                # Delete jobs older than 30 days that are completed/failed/cancelled
                cutoff_date = datetime.now(UTC) - timedelta(days=30)

                # Get old jobs
                stmt = select(OptimizationJob).where(
                    OptimizationJob.completed_at < cutoff_date,
                    OptimizationJob.status.in_(['completed', 'failed', 'cancelled'])
                )
                result = await db.execute(stmt)
                old_jobs = result.scalars().all()

                jobs_deleted = 0
                iterations_deleted = 0

                for job in old_jobs:
                    # Delete associated iterations first
                    iter_delete_stmt = delete(OptimizationIteration).where(
                        OptimizationIteration.job_id == job.id
                    )
                    iter_result = await db.execute(iter_delete_stmt)
                    iterations_deleted += iter_result.rowcount

                    # Delete job
                    await db.delete(job)
                    jobs_deleted += 1

                await db.commit()

                logger.info("Optimization cleanup completed",
                           jobs_deleted=jobs_deleted,
                           iterations_deleted=iterations_deleted)

                return {
                    'jobs_deleted': jobs_deleted,
                    'iterations_deleted': iterations_deleted
                }

        # Run async code in new event loop
        nest_asyncio.apply()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(cleanup_async())
        finally:
            loop.close()

    except Exception as e:
        logger.error("Optimization cleanup failed", error=str(e))
        raise


@celery_app.task
def generate_optimization_report(result_id: str) -> Dict[str, Any]:
    """
    Generate optimization report (PDF, Excel).

    Args:
        result_id: ID of optimization result

    Returns:
        Dictionary with report paths
    """

    logger.info("Generating optimization report", result_id=result_id)

    try:
        async def generate_async():
            async with AsyncSessionLocal() as db:
                from sqlalchemy import select
                from app.models.optimization import OptimizationResult

                stmt = select(OptimizationResult).where(OptimizationResult.id == result_id)
                result = await db.execute(stmt)
                optimization_result = result.scalar_one_or_none()

                if not optimization_result:
                    raise ValueError(f"Optimization result {result_id} not found")

                # TODO: Implement actual report generation
                # This would integrate with reporting service when implemented

                report_data = {
                    'result_id': result_id,
                    'pdf_path': f'/reports/optimization_{result_id}.pdf',
                    'excel_path': f'/reports/optimization_{result_id}.xlsx',
                    'generated_at': datetime.now(UTC).isoformat()
                }

                logger.info("Optimization report generated", result_id=result_id)
                return report_data

        # Run async code in new event loop
        nest_asyncio.apply()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(generate_async())
        finally:
            loop.close()

    except Exception as e:
        logger.error("Report generation failed", result_id=result_id, error=str(e))
        raise


@celery_app.task
def send_optimization_notification(job_id: str, status: str) -> bool:
    """
    Send notification when optimization is completed.

    Args:
        job_id: ID of optimization job
        status: Final status (completed, failed, cancelled)

    Returns:
        True if notification sent successfully
    """

    logger.info("Sending optimization notification", job_id=job_id, status=status)

    try:
        # TODO: Implement actual notification service
        # This could send emails, push notifications, etc.

        # For now, just log the notification
        logger.info("Optimization notification sent", job_id=job_id, status=status)
        return True

    except Exception as e:
        logger.error("Failed to send notification", job_id=job_id, error=str(e))
        return False