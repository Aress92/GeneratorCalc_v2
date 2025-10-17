"""
Maintenance tasks for periodic cleanup and system health.

Zadania konserwacyjne dla okresowego czyszczenia i zdrowia systemu.
"""

import os
import structlog
from datetime import datetime, timedelta, UTC
from pathlib import Path
from typing import List
import asyncio
import nest_asyncio

from celery import Task
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_

from app.celery import celery_app
from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.models.import_job import ImportJob
from app.models.optimization import OptimizationJob
from app.models.reporting import Report

logger = structlog.get_logger(__name__)


class AsyncCeleryTask(Task):
    """Base class for async Celery tasks."""

    def __call__(self, *args, **kwargs):
        # Apply nest_asyncio to allow nested event loops in Celery worker context
        nest_asyncio.apply()

        # Create new event loop for this task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._async_call(*args, **kwargs))
        finally:
            loop.close()

    async def _async_call(self, *args, **kwargs):
        # This method should be overridden by subclasses
        pass


@celery_app.task(bind=True, base=AsyncCeleryTask, name="app.tasks.maintenance.cleanup_expired_tasks")
async def cleanup_expired_tasks(self) -> dict:
    """
    Clean up expired tasks and temporary data.

    Czyści wygasłe zadania i dane tymczasowe.
    """
    try:
        async with AsyncSessionLocal() as db:
            cutoff_date = datetime.now(UTC) - timedelta(days=7)  # 7 days ago

            # Count records to be deleted
            import_jobs_query = select(ImportJob).where(
                and_(
                    ImportJob.status.in_(["COMPLETED", "FAILED", "CANCELLED"]),
                    ImportJob.created_at < cutoff_date
                )
            )
            import_jobs_result = await db.execute(import_jobs_query)
            import_jobs_count = len(import_jobs_result.scalars().all())

            optimization_jobs_query = select(OptimizationJob).where(
                and_(
                    OptimizationJob.status.in_(["COMPLETED", "FAILED", "CANCELLED"]),
                    OptimizationJob.created_at < cutoff_date
                )
            )
            optimization_jobs_result = await db.execute(optimization_jobs_query)
            optimization_jobs_count = len(optimization_jobs_result.scalars().all())

            # Delete expired import jobs
            if import_jobs_count > 0:
                delete_import_query = delete(ImportJob).where(
                    and_(
                        ImportJob.status.in_(["COMPLETED", "FAILED", "CANCELLED"]),
                        ImportJob.created_at < cutoff_date
                    )
                )
                await db.execute(delete_import_query)

            # Delete expired optimization jobs
            if optimization_jobs_count > 0:
                delete_optimization_query = delete(OptimizationJob).where(
                    and_(
                        OptimizationJob.status.in_(["COMPLETED", "FAILED", "CANCELLED"]),
                        OptimizationJob.created_at < cutoff_date
                    )
                )
                await db.execute(delete_optimization_query)

            await db.commit()

            logger.info(
                "Cleanup completed",
                import_jobs_cleaned=import_jobs_count,
                optimization_jobs_cleaned=optimization_jobs_count
            )

            return {
                "status": "success",
                "import_jobs_cleaned": import_jobs_count,
                "optimization_jobs_cleaned": optimization_jobs_count,
                "cleaned_at": datetime.now(UTC).isoformat()
            }

    except Exception as e:
        logger.error("Cleanup failed", error=str(e))
        return {
            "status": "error",
            "error": str(e),
            "cleaned_at": datetime.now(UTC).isoformat()
        }


@celery_app.task(bind=True, base=AsyncCeleryTask, name="app.tasks.maintenance.cleanup_old_files")
async def cleanup_old_files(self) -> dict:
    """
    Clean up old temporary files and uploads.

    Czyści stare pliki tymczasowe i przesłane.
    """
    try:
        cleaned_files = 0
        total_size = 0

        # Clean up upload directory
        upload_dir = Path(settings.UPLOAD_DIR)
        if upload_dir.exists():
            cutoff_time = datetime.now().timestamp() - (7 * 24 * 3600)  # 7 days ago

            for file_path in upload_dir.rglob("*"):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    try:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        cleaned_files += 1
                        total_size += file_size
                    except OSError as e:
                        logger.warning("Could not delete file", file_path=str(file_path), error=str(e))

        # Clean up temp directory if it exists
        temp_dir = Path("/tmp/fro")
        if temp_dir.exists():
            cutoff_time = datetime.now().timestamp() - (24 * 3600)  # 1 day ago

            for file_path in temp_dir.rglob("*"):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    try:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        cleaned_files += 1
                        total_size += file_size
                    except OSError as e:
                        logger.warning("Could not delete temp file", file_path=str(file_path), error=str(e))

        logger.info(
            "File cleanup completed",
            files_cleaned=cleaned_files,
            total_size_mb=total_size / (1024 * 1024)
        )

        return {
            "status": "success",
            "files_cleaned": cleaned_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "cleaned_at": datetime.now(UTC).isoformat()
        }

    except Exception as e:
        logger.error("File cleanup failed", error=str(e))
        return {
            "status": "error",
            "error": str(e),
            "cleaned_at": datetime.now(UTC).isoformat()
        }