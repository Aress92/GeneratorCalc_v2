"""
Celery tasks for report generation.

Zadania Celery dla generowania raportów.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List

from celery import current_task
from sqlalchemy.ext.asyncio import AsyncSession

from app.celery import celery_app
from app.core.database import AsyncSessionLocal
from app.models.reporting import Report, ReportStatus
from app.services.reporting_service import ReportingService
from app.models.user import User
from sqlalchemy import select


@celery_app.task(bind=True)
def generate_report_task(self, report_id: str):
    """Generate report task with progress tracking."""

    async def _generate_report():
        """Async wrapper for report generation."""
        async with AsyncSessionLocal() as db:
            try:
                # Update task status
                current_task.update_state(
                    state='PROGRESS',
                    meta={'progress': 0, 'status': 'initializing', 'step': 'Starting report generation...'}
                )

                # Get report
                stmt = select(Report).where(Report.id == report_id)
                result = await db.execute(stmt)
                report = result.scalar_one_or_none()

                if not report:
                    raise ValueError("Report not found")

                # Update report status
                report.status = ReportStatus.GENERATING
                report.progress_percentage = 0.0
                await db.commit()

                # Update task progress
                current_task.update_state(
                    state='PROGRESS',
                    meta={'progress': 10, 'status': 'generating', 'step': 'Analyzing data sources...'}
                )

                # Initialize reporting service
                reporting_service = ReportingService(db)

                # Update progress
                current_task.update_state(
                    state='PROGRESS',
                    meta={'progress': 25, 'status': 'generating', 'step': 'Collecting data...'}
                )

                # Generate report data
                sections = await reporting_service._generate_report_data(report)

                # Update progress
                current_task.update_state(
                    state='PROGRESS',
                    meta={'progress': 60, 'status': 'generating', 'step': 'Processing data and creating visualizations...'}
                )

                # Create report file
                file_path = await reporting_service._create_report_file(report, sections)

                # Update progress
                current_task.update_state(
                    state='PROGRESS',
                    meta={'progress': 90, 'status': 'generating', 'step': 'Finalizing report...'}
                )

                # Update report with results
                report.status = ReportStatus.COMPLETED
                report.progress_percentage = 100.0
                report.generated_at = datetime.utcnow()
                report.file_path = str(file_path)
                report.file_size_bytes = file_path.stat().st_size if file_path.exists() else 0
                report.expires_at = datetime.utcnow() + timedelta(days=30)

                await db.commit()

                # Final progress update
                current_task.update_state(
                    state='SUCCESS',
                    meta={'progress': 100, 'status': 'completed', 'step': 'Report generation completed successfully'}
                )

                return {
                    'status': 'completed',
                    'file_path': str(file_path),
                    'file_size': report.file_size_bytes
                }

            except Exception as e:
                # Update report with error
                if report:
                    report.status = ReportStatus.FAILED
                    report.error_message = str(e)
                    await db.commit()

                # Update task with error
                current_task.update_state(
                    state='FAILURE',
                    meta={'progress': 0, 'status': 'failed', 'error': str(e)}
                )

                raise

    # Run async function
    return asyncio.run(_generate_report())


@celery_app.task
def cleanup_expired_reports():
    """Cleanup expired report files."""

    async def _cleanup_reports():
        """Async wrapper for cleanup."""
        async with AsyncSessionLocal() as db:
            try:
                # Find expired reports
                expired_date = datetime.utcnow()
                stmt = select(Report).where(
                    Report.expires_at < expired_date,
                    Report.status == ReportStatus.COMPLETED
                )
                result = await db.execute(stmt)
                expired_reports = result.scalars().all()

                cleaned_count = 0
                for report in expired_reports:
                    try:
                        # Delete file if it exists
                        if report.file_path:
                            from pathlib import Path
                            file_path = Path(report.file_path)
                            if file_path.exists():
                                file_path.unlink()

                        # Update report status
                        report.file_path = None
                        report.file_size_bytes = None
                        report.download_url = None

                        cleaned_count += 1

                    except Exception as e:
                        print(f"Error cleaning up report {report.id}: {e}")
                        continue

                await db.commit()
                return {'cleaned_reports': cleaned_count}

            except Exception as e:
                print(f"Error in cleanup task: {e}")
                raise

    return asyncio.run(_cleanup_reports())


@celery_app.task
def generate_scheduled_reports():
    """Generate scheduled reports."""

    async def _generate_scheduled():
        """Async wrapper for scheduled report generation."""
        async with AsyncSessionLocal() as db:
            try:
                from app.models.reporting import ReportSchedule

                # Find due schedules
                current_time = datetime.utcnow()
                stmt = select(ReportSchedule).where(
                    ReportSchedule.is_active == True,
                    ReportSchedule.next_run_at <= current_time
                )
                result = await db.execute(stmt)
                due_schedules = result.scalars().all()

                generated_count = 0
                for schedule in due_schedules:
                    try:
                        # Create report from schedule
                        report = Report(
                            user_id=schedule.user_id,
                            title=f"{schedule.name} - {current_time.strftime('%Y-%m-%d %H:%M')}",
                            description=f"Scheduled report: {schedule.description}",
                            report_type=schedule.report_config.get('report_type', 'system_performance'),
                            report_config=schedule.report_config,
                            format=schedule.report_config.get('format', 'pdf'),
                            frequency='scheduled'
                        )

                        db.add(report)
                        await db.commit()
                        await db.refresh(report)

                        # Queue report generation
                        generate_report_task.delay(report.id)

                        # Update schedule
                        schedule.last_run_at = current_time
                        schedule.next_run_at = _calculate_next_run(schedule.frequency, current_time)
                        schedule.last_success_at = current_time
                        schedule.failure_count = 0

                        generated_count += 1

                    except Exception as e:
                        # Update schedule with failure
                        schedule.failure_count = (schedule.failure_count or 0) + 1

                        if schedule.failure_count >= schedule.max_failures:
                            schedule.is_active = False

                        print(f"Error generating scheduled report {schedule.id}: {e}")
                        continue

                await db.commit()
                return {'generated_reports': generated_count}

            except Exception as e:
                print(f"Error in scheduled report generation: {e}")
                raise

    return asyncio.run(_generate_scheduled())


@celery_app.task
def collect_system_metrics():
    """Collect system performance metrics."""

    async def _collect_metrics():
        """Async wrapper for metrics collection."""
        async with AsyncSessionLocal() as db:
            try:
                from app.models.reporting import SystemMetrics
                from app.models.optimization import OptimizationJob
                import psutil
                import time

                current_time = datetime.utcnow()

                # System metrics
                cpu_usage = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')

                system_metrics = [
                    SystemMetrics(
                        metric_name='cpu_usage_percent',
                        metric_category='performance',
                        metric_value=cpu_usage,
                        metric_unit='percent',
                        measured_at=current_time
                    ),
                    SystemMetrics(
                        metric_name='memory_usage_percent',
                        metric_category='performance',
                        metric_value=memory.percent,
                        metric_unit='percent',
                        measured_at=current_time
                    ),
                    SystemMetrics(
                        metric_name='disk_usage_percent',
                        metric_category='performance',
                        metric_value=disk.percent,
                        metric_unit='percent',
                        measured_at=current_time
                    ),
                    SystemMetrics(
                        metric_name='memory_available_gb',
                        metric_category='performance',
                        metric_value=memory.available / (1024**3),  # Convert to GB
                        metric_unit='gb',
                        measured_at=current_time
                    )
                ]

                # Application metrics
                one_hour_ago = current_time - timedelta(hours=1)

                # Count recent optimizations
                opt_stmt = select(OptimizationJob).where(
                    OptimizationJob.created_at >= one_hour_ago
                )
                opt_result = await db.execute(opt_stmt)
                recent_optimizations = len(opt_result.scalars().all())

                # Count active users (users who created optimizations in last 24 hours)
                twenty_four_hours_ago = current_time - timedelta(hours=24)
                active_users_stmt = select(OptimizationJob.user_id.distinct()).where(
                    OptimizationJob.created_at >= twenty_four_hours_ago
                )
                active_users_result = await db.execute(active_users_stmt)
                active_users_count = len(active_users_result.scalars().all())

                app_metrics = [
                    SystemMetrics(
                        metric_name='optimizations_last_hour',
                        metric_category='usage',
                        metric_value=recent_optimizations,
                        metric_unit='count',
                        measured_at=current_time,
                        period_start=one_hour_ago,
                        period_end=current_time
                    ),
                    SystemMetrics(
                        metric_name='active_users_last_24h',
                        metric_category='usage',
                        metric_value=active_users_count,
                        metric_unit='count',
                        measured_at=current_time,
                        period_start=twenty_four_hours_ago,
                        period_end=current_time
                    )
                ]

                # Add all metrics
                for metric in system_metrics + app_metrics:
                    db.add(metric)

                await db.commit()

                return {
                    'system_metrics_collected': len(system_metrics),
                    'app_metrics_collected': len(app_metrics)
                }

            except Exception as e:
                print(f"Error collecting system metrics: {e}")
                raise

    return asyncio.run(_collect_metrics())


def _calculate_next_run(frequency: str, current_time: datetime) -> datetime:
    """Calculate next run time based on frequency."""

    if frequency == 'daily':
        return current_time + timedelta(days=1)
    elif frequency == 'weekly':
        return current_time + timedelta(weeks=1)
    elif frequency == 'monthly':
        # Rough monthly calculation (30 days)
        return current_time + timedelta(days=30)
    elif frequency == 'quarterly':
        return current_time + timedelta(days=90)
    elif frequency == 'annually':
        return current_time + timedelta(days=365)
    else:
        # Default to daily
        return current_time + timedelta(days=1)