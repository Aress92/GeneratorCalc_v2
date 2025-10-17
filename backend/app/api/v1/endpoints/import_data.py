"""
Import data endpoints.

Endpointy importu danych.
"""

import os
import tempfile
from pathlib import Path
from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, BackgroundTasks, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.import_job import ImportJob
from app.schemas.import_schemas import (
    ImportPreview, ImportJobCreate, ImportJobResponse, ImportJobStatus,
    RegeneratorDataResponse, UnitConversionCreate, UnitConversionResponse,
    ValidationRuleCreate, ValidationRuleResponse, ColumnMapping
)
from app.services.import_service import ImportService
from app.core.config import settings

router = APIRouter()


@router.post("/preview", response_model=ImportPreview)
async def preview_import_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Preview uploaded file for import.

    Returns file structure, suggested column mapping, and validation errors.
    """
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are supported")

    # Validate file size
    if file.size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE / (1024*1024):.1f}MB")

    # Save temporary file
    temp_dir = Path(tempfile.gettempdir())
    temp_file = temp_dir / f"preview_{uuid.uuid4()}.xlsx"

    try:
        # Write uploaded file to temp location
        with open(temp_file, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Create import service and preview file
        import_service = ImportService(db)
        preview = await import_service.preview_file(str(temp_file), file.filename)

        return preview

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to preview file: {str(e)}")

    finally:
        # Clean up temp file
        if temp_file.exists():
            os.unlink(temp_file)


@router.post("/dry-run")
async def dry_run_import(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform dry run import with custom column mapping.

    Requires form data with:
    - file: Excel file to import
    - import_type: Type of import (form field)
    - column_mapping: JSON string of column mappings (form field)
    """
    from fastapi import Form
    import json

    # Get form data
    import_type_str = Form(...)
    column_mapping_json = Form(...)

    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are supported")

    # Validate file size
    if file.size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE / (1024*1024):.1f}MB")

    # Save temporary file
    temp_dir = Path(tempfile.gettempdir())
    temp_file = temp_dir / f"dryrun_{uuid.uuid4()}.xlsx"

    try:
        # Write uploaded file to temp location
        with open(temp_file, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Parse column mapping
        try:
            column_mapping_data = json.loads(column_mapping_json)
            column_mapping = [ColumnMapping(**mapping) for mapping in column_mapping_data]
        except (json.JSONDecodeError, ValueError) as e:
            raise HTTPException(status_code=400, detail=f"Invalid column mapping format: {str(e)}")

        # Validate import type
        try:
            from app.models.import_job import ImportType
            import_type = ImportType(import_type_str)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid import type: {import_type_str}")

        # Create import service and perform dry run
        import_service = ImportService(db)
        result = await import_service.dry_run_import(
            current_user.id,
            str(temp_file),
            column_mapping,
            import_type
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dry run import failed: {str(e)}")

    finally:
        # Clean up temp file
        if temp_file.exists():
            os.unlink(temp_file)


@router.post("/dry-run-simple")
async def dry_run_import_simple(
    import_type: str = Form(...),
    column_mapping: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform dry run import with simpler form handling.
    """
    import json

    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are supported")

    # Validate file size
    if file.size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE / (1024*1024):.1f}MB")

    # Save temporary file
    temp_dir = Path(tempfile.gettempdir())
    temp_file = temp_dir / f"dryrun_{uuid.uuid4()}.xlsx"

    try:
        # Write uploaded file to temp location
        with open(temp_file, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Parse column mapping
        try:
            column_mapping_data = json.loads(column_mapping)
            column_mapping_list = [ColumnMapping(**mapping) for mapping in column_mapping_data]
        except (json.JSONDecodeError, ValueError) as e:
            raise HTTPException(status_code=400, detail=f"Invalid column mapping format: {str(e)}")

        # Validate import type
        try:
            from app.models.import_job import ImportType
            import_type_enum = ImportType(import_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid import type: {import_type}")

        # Create import service and perform dry run
        import_service = ImportService(db)
        result = await import_service.dry_run_import(
            current_user.id,
            str(temp_file),
            column_mapping_list,
            import_type_enum
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dry run import failed: {str(e)}")

    finally:
        # Clean up temp file
        if temp_file.exists():
            os.unlink(temp_file)


@router.post("/jobs", response_model=ImportJobResponse)
async def create_import_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    job_data: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new import job.

    Uploads file and creates an import job that will be processed in the background.
    """
    import json

    # Parse job data from form
    try:
        job_data_dict = json.loads(job_data)
        job_data_obj = ImportJobCreate(**job_data_dict)
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid job data format: {str(e)}")

    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are supported")

    # Validate file size
    if file.size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE / (1024*1024):.1f}MB")

    # Save uploaded file to temp location
    temp_dir = Path(settings.UPLOAD_DIR) / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_file = temp_dir / f"upload_{uuid.uuid4()}.xlsx"

    try:
        # Write uploaded file
        with open(temp_file, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Create import service and job
        import_service = ImportService(db)
        job = await import_service.create_import_job(
            current_user.id,
            str(temp_file),
            job_data_obj
        )

        # Schedule background processing
        background_tasks.add_task(import_service.process_import_job, job.id)

        # Convert to response format
        return ImportJobResponse(
            id=job.id,
            user_id=job.user_id,
            filename=job.filename,
            original_filename=job.original_filename,
            file_size=job.file_size,
            import_type=job.import_type,
            status=job.status,
            total_rows=job.total_rows,
            processed_rows=job.processed_rows,
            valid_rows=job.valid_rows,
            invalid_rows=job.invalid_rows,
            validation_errors=job.validation_errors or [],
            validation_warnings=job.validation_warnings or [],
            column_mapping=job.column_mapping or [],
            metadata_info=job.metadata_info or {},
            processing_options=job.processing_options or {},
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
            error_message=job.error_message
        )

    except Exception as e:
        # Clean up temp file on error
        if temp_file.exists():
            os.unlink(temp_file)
        raise HTTPException(status_code=500, detail=f"Failed to create import job: {str(e)}")


@router.get("/jobs/{job_id}", response_model=ImportJobResponse)
async def get_import_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get import job details."""
    import_service = ImportService(db)
    job = await import_service.get_import_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Import job not found")

    # Check ownership or admin access
    if job.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")

    return ImportJobResponse(
        id=job.id,
        user_id=job.user_id,
        filename=job.filename,
        original_filename=job.original_filename,
        file_size=job.file_size,
        import_type=job.import_type,
        status=job.status,
        total_rows=job.total_rows,
        processed_rows=job.processed_rows,
        valid_rows=job.valid_rows,
        invalid_rows=job.invalid_rows,
        validation_errors=job.validation_errors or [],
        validation_warnings=job.validation_warnings or [],
        column_mapping=job.column_mapping or [],
        metadata_info=job.metadata_info or {},
        processing_options=job.processing_options or {},
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        error_message=job.error_message
    )


@router.get("/jobs/{job_id}/status", response_model=ImportJobStatus)
async def get_import_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get import job status for progress monitoring."""
    import_service = ImportService(db)
    job = await import_service.get_import_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Import job not found")

    # Check ownership or admin access
    if job.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")

    # Calculate progress percentage
    progress = 0.0
    if job.total_rows > 0:
        progress = (job.processed_rows / job.total_rows) * 100

    return ImportJobStatus(
        id=job.id,
        status=job.status,
        total_rows=job.total_rows,
        processed_rows=job.processed_rows,
        valid_rows=job.valid_rows,
        invalid_rows=job.invalid_rows,
        progress_percentage=progress,
        error_message=job.error_message,
        started_at=job.started_at,
        completed_at=job.completed_at
    )


@router.get("/jobs", response_model=List[ImportJobResponse])
async def get_user_import_jobs(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's import jobs."""
    import_service = ImportService(db)
    jobs = await import_service.get_user_import_jobs(current_user.id, limit, offset)

    return [
        ImportJobResponse(
            id=job.id,
            user_id=job.user_id,
            filename=job.filename,
            original_filename=job.original_filename,
            file_size=job.file_size,
            import_type=job.import_type,
            status=job.status,
            total_rows=job.total_rows,
            processed_rows=job.processed_rows,
            valid_rows=job.valid_rows,
            invalid_rows=job.invalid_rows,
            validation_errors=job.validation_errors or [],
            validation_warnings=job.validation_warnings or [],
            column_mapping=job.column_mapping or [],
            metadata_info=job.metadata_info or {},
            processing_options=job.processing_options or {},
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
            error_message=job.error_message
        )
        for job in jobs
    ]


@router.get("/jobs/{job_id}/results", response_model=List[RegeneratorDataResponse])
async def get_import_job_results(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get imported regenerator data from a completed job."""
    import_service = ImportService(db)
    job = await import_service.get_import_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Import job not found")

    # Check ownership or admin access
    if job.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")

    # Get imported regenerators
    from sqlalchemy import select
    from app.models.import_job import ImportedRegenerator

    result = await db.execute(
        select(ImportedRegenerator).where(ImportedRegenerator.import_job_id == job_id)
    )
    regenerators = result.scalars().all()

    return [
        RegeneratorDataResponse(
            id=reg.id,
            import_job_id=reg.import_job_id,
            name=reg.name,
            description=reg.description,
            regenerator_type=reg.regenerator_type,
            length=reg.length,
            width=reg.width,
            height=reg.height,
            volume=reg.volume,
            design_temperature=reg.design_temperature,
            max_temperature=reg.max_temperature,
            working_pressure=reg.working_pressure,
            air_flow_rate=reg.air_flow_rate,
            gas_flow_rate=reg.gas_flow_rate,
            pressure_drop=reg.pressure_drop,
            checker_material=reg.checker_material,
            insulation_material=reg.insulation_material,
            refractory_material=reg.refractory_material,
            thermal_efficiency=reg.thermal_efficiency,
            heat_recovery_rate=reg.heat_recovery_rate,
            fuel_consumption=reg.fuel_consumption,
            is_validated=reg.is_validated,
            validation_score=reg.validation_score,
            validation_notes=reg.validation_notes,
            created_at=reg.created_at,
            updated_at=reg.updated_at
        )
        for reg in regenerators
    ]


@router.delete("/jobs/{job_id}")
async def delete_import_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an import job and its data."""
    import_service = ImportService(db)
    job = await import_service.get_import_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Import job not found")

    # Check ownership or admin access
    if job.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")

    # Delete imported data
    from sqlalchemy import delete
    from app.models.import_job import ImportedRegenerator

    await db.execute(
        delete(ImportedRegenerator).where(ImportedRegenerator.import_job_id == job_id)
    )

    # Delete job
    await db.delete(job)
    await db.commit()

    # Clean up file
    file_path = Path(settings.UPLOAD_DIR) / "imports" / job.filename
    if file_path.exists():
        os.unlink(file_path)

    return {"message": "Import job deleted successfully"}


@router.get("/templates/{import_type}")
async def get_import_template(
    import_type: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get Excel template for specific import type.
    """
    from app.models.import_job import ImportType

    try:
        import_type_enum = ImportType(import_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid import type: {import_type}")

    # Generate template based on import type
    if import_type_enum == ImportType.REGENERATOR_CONFIG:
        template_data = {
            'headers': [
                'Name', 'Description', 'Type', 'Length (m)', 'Width (m)', 'Height (m)',
                'Design Temperature (C)', 'Max Temperature (C)', 'Working Pressure (Pa)',
                'Air Flow Rate (m3/h)', 'Gas Flow Rate (m3/h)', 'Pressure Drop (Pa)',
                'Checker Material', 'Insulation Material', 'Refractory Material',
                'Thermal Efficiency (%)', 'Heat Recovery Rate (%)', 'Fuel Consumption (kW)'
            ],
            'sample_data': [
                ['Regenerator 1', 'Crown type regenerator', 'crown', 12.5, 8.0, 6.5,
                 1450, 1650, 500, 15000, 12000, 800,
                 'Alumina brick', 'Ceramic fiber', 'Fire brick',
                 85.5, 78.2, 2500],
                ['Regenerator 2', 'End-port regenerator', 'end-port', 15.0, 6.0, 5.0,
                 1350, 1550, 400, 18000, 14000, 650,
                 'Silica brick', 'Mineral wool', 'Refractory concrete',
                 82.1, 75.8, 2800]
            ]
        }
    else:
        template_data = {
            'headers': ['Column1', 'Column2', 'Column3'],
            'sample_data': [['Sample1', 'Value1', 123], ['Sample2', 'Value2', 456]]
        }

    return {
        'import_type': import_type,
        'template': template_data,
        'description': f'Excel template for {import_type} import',
        'instructions': [
            'Download this template and fill in your data',
            'Keep the header row as the first row',
            'Ensure data types match the expected format',
            'Save as .xlsx format before uploading'
        ]
    }


@router.get("/validation-rules")
async def get_validation_rules(
    import_type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get validation rules for import types.
    """
    # Initialize physics validator to get rules
    from app.services.validation_service import RegeneratorPhysicsValidator
    validator = RegeneratorPhysicsValidator()

    rules = await validator.get_validation_rules_summary()

    if import_type:
        # Filter rules for specific import type
        # This could be expanded based on import type
        pass

    return {
        'validation_rules': rules,
        'description': 'Physics and engineering validation constraints',
        'last_updated': '2025-09-24'
    }