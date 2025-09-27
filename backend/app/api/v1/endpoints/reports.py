"""
Reporting endpoints.

Endpointy raportowania.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, or_
import json
import asyncio

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.reporting import Report, ReportTemplate, ReportSchedule
from app.schemas.reporting_schemas import (
    ReportCreate, ReportUpdate, ReportResponse, ReportList,
    ReportTemplateCreate, ReportTemplateResponse, ReportTemplateList,
    ReportScheduleCreate, ReportScheduleResponse, ReportProgress,
    ReportExportRequest, ReportExportResponse, DashboardMetrics
)
from app.services.reporting_service import ReportingService
from app.core.config import settings

router = APIRouter()


# Dashboard endpoints
@router.get("/dashboard/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard metrics for current user."""

    reporting_service = ReportingService(db)
    metrics = await reporting_service.get_dashboard_metrics(current_user.id)
    return metrics


# Reports endpoints
@router.post("/reports", response_model=ReportResponse)
async def create_report(
    report_data: ReportCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new report."""

    if current_user.role not in ['admin', 'engineer']:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    reporting_service = ReportingService(db)
    report = await reporting_service.create_report(current_user.id, report_data)

    # Start report generation in background
    background_tasks.add_task(reporting_service.generate_report, report.id)

    return ReportResponse.from_orm(report)


@router.get("/reports", response_model=ReportList)
async def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    report_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List reports for the current user."""

    conditions = [Report.user_id == current_user.id]

    if report_type:
        conditions.append(Report.report_type == report_type)
    if status:
        conditions.append(Report.status == status)

    stmt = select(Report).where(
        and_(*conditions)
    ).order_by(desc(Report.created_at)).offset(skip).limit(limit)

    result = await db.execute(stmt)
    reports = result.scalars().all()

    # Count total
    count_stmt = select(Report).where(and_(*conditions))
    count_result = await db.execute(count_stmt)
    total_count = len(count_result.scalars().all())

    return ReportList(
        reports=[ReportResponse.from_orm(r) for r in reports],
        total_count=total_count,
        page=skip // limit + 1,
        per_page=limit
    )


@router.get("/reports/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get report by ID."""

    stmt = select(Report).where(
        Report.id == report_id,
        Report.user_id == current_user.id
    )
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return ReportResponse.from_orm(report)


@router.put("/reports/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: str,
    report_update: ReportUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update report."""

    stmt = select(Report).where(
        Report.id == report_id,
        Report.user_id == current_user.id
    )
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Update fields
    update_data = report_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(report, field, value)

    await db.commit()
    await db.refresh(report)

    return ReportResponse.from_orm(report)


@router.delete("/reports/{report_id}")
async def delete_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete report."""

    stmt = select(Report).where(
        Report.id == report_id,
        Report.user_id == current_user.id
    )
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    await db.delete(report)
    await db.commit()

    return {"message": "Report deleted successfully"}


@router.get("/reports/{report_id}/progress", response_model=ReportProgress)
async def get_report_progress(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get report generation progress."""

    # Verify report belongs to user
    stmt = select(Report).where(
        Report.id == report_id,
        Report.user_id == current_user.id
    )
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    reporting_service = ReportingService(db)
    progress = await reporting_service.get_report_progress(report_id)

    return progress


@router.get("/reports/{report_id}/download")
async def download_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Download generated report file."""

    stmt = select(Report).where(
        Report.id == report_id,
        Report.user_id == current_user.id
    )
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if not report.file_path or report.status != 'completed':
        raise HTTPException(status_code=404, detail="Report file not available")

    return FileResponse(
        path=report.file_path,
        filename=f"{report.title}.{report.format}",
        media_type='application/octet-stream'
    )


@router.post("/reports/{report_id}/export", response_model=ReportExportResponse)
async def export_report(
    report_id: str,
    export_request: ReportExportRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export report in different format."""

    stmt = select(Report).where(
        Report.id == report_id,
        Report.user_id == current_user.id
    )
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if report.status != 'completed':
        raise HTTPException(status_code=400, detail="Report not yet completed")

    # Create export record
    from app.models.reporting import ReportExport
    export = ReportExport(
        report_id=report_id,
        user_id=current_user.id,
        export_format=export_request.export_format,
        file_name=f"{report.title}.{export_request.export_format}",
        file_path="",  # Will be set after generation
        file_size_bytes=0,
        export_config=export_request.export_config
    )

    db.add(export)
    await db.commit()
    await db.refresh(export)

    # Generate export in background
    reporting_service = ReportingService(db)
    background_tasks.add_task(
        reporting_service._create_report_file,
        report, [], f"export_{export.id}"
    )

    return ReportExportResponse.from_orm(export)


# Server-Sent Events for real-time updates
@router.get("/reports/{report_id}/events")
async def get_report_events(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Stream report generation events via Server-Sent Events."""

    # Verify report belongs to user
    stmt = select(Report).where(
        Report.id == report_id,
        Report.user_id == current_user.id
    )
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    async def event_stream():
        """Generate Server-Sent Events stream."""
        reporting_service = ReportingService(db)

        while True:
            try:
                # Get current progress
                progress = await reporting_service.get_report_progress(report_id)

                # Send progress event
                event_data = {
                    "type": "progress",
                    "report_id": report_id,
                    "data": progress.dict()
                }

                yield f"data: {json.dumps(event_data)}\n\n"

                # Check if report is complete
                if progress.status in ['completed', 'failed']:
                    break

                # Wait before next update
                await asyncio.sleep(2)

            except Exception as e:
                error_event = {
                    "type": "error",
                    "report_id": report_id,
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


# Templates endpoints
@router.post("/templates", response_model=ReportTemplateResponse)
async def create_report_template(
    template_data: ReportTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new report template."""

    if current_user.role not in ['admin', 'engineer']:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    template = ReportTemplate(
        created_by_user_id=current_user.id,
        name=template_data.name,
        description=template_data.description,
        category=template_data.category,
        template_config=template_data.template_config,
        default_filters=template_data.default_filters,
        is_public=template_data.is_public
    )

    db.add(template)
    await db.commit()
    await db.refresh(template)

    return ReportTemplateResponse.from_orm(template)


@router.get("/templates", response_model=ReportTemplateList)
async def list_report_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = Query(None),
    is_public: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List report templates."""

    conditions = [ReportTemplate.is_active == True]

    # Users can see their own templates and public ones
    conditions.append(
        or_(
            ReportTemplate.is_public == True,
            ReportTemplate.created_by_user_id == current_user.id
        )
    )

    if category:
        conditions.append(ReportTemplate.category == category)
    if is_public is not None:
        conditions.append(ReportTemplate.is_public == is_public)

    stmt = select(ReportTemplate).where(
        and_(*conditions)
    ).order_by(desc(ReportTemplate.usage_count)).offset(skip).limit(limit)

    result = await db.execute(stmt)
    templates = result.scalars().all()

    # Count total
    count_stmt = select(ReportTemplate).where(and_(*conditions))
    count_result = await db.execute(count_stmt)
    total_count = len(count_result.scalars().all())

    return ReportTemplateList(
        templates=[ReportTemplateResponse.from_orm(t) for t in templates],
        total_count=total_count,
        page=skip // limit + 1,
        per_page=limit
    )


@router.get("/templates/{template_id}", response_model=ReportTemplateResponse)
async def get_report_template(
    template_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get report template by ID."""

    stmt = select(ReportTemplate).where(
        ReportTemplate.id == template_id,
        or_(
            ReportTemplate.is_public == True,
            ReportTemplate.created_by_user_id == current_user.id
        )
    )
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return ReportTemplateResponse.from_orm(template)


# Schedules endpoints
@router.post("/schedules", response_model=ReportScheduleResponse)
async def create_report_schedule(
    schedule_data: ReportScheduleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new report schedule."""

    if current_user.role not in ['admin', 'engineer']:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    schedule = ReportSchedule(
        user_id=current_user.id,
        template_id=schedule_data.template_id,
        name=schedule_data.name,
        description=schedule_data.description,
        frequency=schedule_data.frequency,
        cron_expression=schedule_data.cron_expression,
        timezone=schedule_data.timezone,
        report_config=schedule_data.report_config,
        email_recipients=schedule_data.email_recipients
    )

    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)

    return ReportScheduleResponse.from_orm(schedule)


@router.get("/schedules", response_model=List[ReportScheduleResponse])
async def list_report_schedules(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List report schedules for current user."""

    stmt = select(ReportSchedule).where(
        ReportSchedule.user_id == current_user.id,
        ReportSchedule.is_active == True
    ).order_by(desc(ReportSchedule.created_at))

    result = await db.execute(stmt)
    schedules = result.scalars().all()

    return [ReportScheduleResponse.from_orm(s) for s in schedules]