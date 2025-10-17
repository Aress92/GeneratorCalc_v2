"""
Celery configuration for background tasks.

Konfiguracja Celery dla zadań w tle - optymalizacja, eksport, import.
"""

from celery import Celery

from app.core.config import settings


# Create Celery app
celery_app = Celery(
    "forglass-regenerator-optimizer",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.optimization",
        "app.tasks.import_export",
        "app.tasks.reports",
        "app.tasks.maintenance",
    ],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    result_expires=3600,  # 1 hour
    beat_schedule={
        "cleanup-expired-tasks": {
            "task": "app.tasks.maintenance.cleanup_expired_tasks",
            "schedule": 3600.0,  # Every hour
        },
        "cleanup-old-files": {
            "task": "app.tasks.maintenance.cleanup_old_files",
            "schedule": 24 * 3600.0,  # Daily
        },
    },
)