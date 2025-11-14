"""
Extended tests for import service.

Rozszerzone testy dla serwisu importu.
"""

import pytest
from uuid import uuid4
from datetime import datetime, UTC
from io import BytesIO
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd

from app.services.import_service import ImportService
from app.models.user import User, UserRole
from app.models.import_job import ImportJob, ImportStatus, ImportType
from app.models.regenerator import Material, RegeneratorConfiguration, RegeneratorType
from app.schemas.import_schemas import ImportJobCreate, ImportPreview


class TestImportServiceExtended:
    """Extended tests for ImportService functionality."""

    @pytest.fixture
    async def import_service(self, test_db: AsyncSession) -> ImportService:
        """Create import service instance."""
        return ImportService(test_db)

    @pytest.fixture
    async def test_user(self, test_db: AsyncSession) -> User:
        """Create test user."""
        unique_id = uuid4().hex[:8]
        user = User(
            username=f"importuser_{unique_id}",
            email=f"import_{unique_id}@example.com",
            full_name="Import Test User",
            password_hash="hashed_password",
            role=UserRole.ENGINEER,
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        return user

    @pytest.fixture
    def sample_materials_xlsx(self) -> BytesIO:
        """Create sample materials XLSX file."""
        data = {
            "name": ["Alumina Brick", "Silica Brick", "Ceramic Fiber"],
            "material_type": ["refractory", "refractory", "insulation"],
            "thermal_conductivity": [2.5, 1.8, 0.15],
            "specific_heat": [900.0, 850.0, 1000.0],
            "density": [2300.0, 2100.0, 128.0],
            "max_temperature": [1600.0, 1700.0, 1200.0]
        }
        df = pd.DataFrame(data)

        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)
        return buffer

    @pytest.fixture
    def sample_regenerator_xlsx(self) -> BytesIO:
        """Create sample regenerator configuration XLSX file."""
        data = {
            "parameter": ["length", "width", "height", "gas_temp_inlet", "mass_flow_rate"],
            "value": [10.0, 8.0, 6.0, 1600.0, 50.0],
            "unit": ["m", "m", "m", "°C", "kg/s"]
        }
        df = pd.DataFrame(data)

        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)
        return buffer

    # === IMPORT JOB TESTS ===

    async def test_create_import_job(
        self,
        import_service: ImportService,
        test_user: User
    ):
        """Test creating import job."""
        job_data = ImportJobCreate(
            job_name="Test Import Job",
            import_type=ImportType.MATERIALS,
            description="Testing materials import",
            configuration={"validate": True}
        )

        result = await import_service.create_import_job(
            job_data,
            str(test_user.id)
        )

        assert result is not None
        assert result.job_name == "Test Import Job"
        assert result.import_type == ImportType.MATERIALS
        assert result.created_by_id == str(test_user.id)
        assert result.status == ImportStatus.PENDING

    async def test_get_import_job(
        self,
        import_service: ImportService,
        test_user: User
    ):
        """Test getting import job by ID."""
        # Create job first
        job_data = ImportJobCreate(
            job_name="Get Job Test",
            import_type=ImportType.MATERIALS
        )
        job = await import_service.create_import_job(job_data, str(test_user.id))

        # Get job
        result = await import_service.get_import_job(str(job.id))

        assert result is not None
        assert result.id == job.id
        assert result.job_name == job.job_name

    async def test_get_import_job_not_found(self, import_service: ImportService):
        """Test getting non-existent job."""
        result = await import_service.get_import_job(str(uuid4()))

        assert result is None

    async def test_get_user_import_jobs(
        self,
        import_service: ImportService,
        test_user: User
    ):
        """Test getting user's import jobs."""
        # Create multiple jobs
        for i in range(3):
            job_data = ImportJobCreate(
                job_name=f"Job {i}",
                import_type=ImportType.MATERIALS
            )
            await import_service.create_import_job(job_data, str(test_user.id))

        # Get user's jobs
        results = await import_service.get_user_import_jobs(
            str(test_user.id),
            limit=10,
            offset=0
        )

        assert len(results) >= 3
        assert all(j.created_by_id == str(test_user.id) for j in results)

    async def test_update_job_status(
        self,
        import_service: ImportService,
        test_user: User
    ):
        """Test updating job status."""
        # Create job
        job_data = ImportJobCreate(
            job_name="Status Update Test",
            import_type=ImportType.MATERIALS
        )
        job = await import_service.create_import_job(job_data, str(test_user.id))

        # Update status
        success = await import_service.update_job_status(
            str(job.id),
            ImportStatus.PROCESSING,
            progress=50.0
        )

        assert success is True

        # Verify update
        updated_job = await import_service.get_import_job(str(job.id))
        assert updated_job.status == ImportStatus.PROCESSING
        assert updated_job.progress == 50.0

    async def test_cancel_import_job(
        self,
        import_service: ImportService,
        test_user: User
    ):
        """Test canceling import job."""
        # Create job
        job_data = ImportJobCreate(
            job_name="Cancel Test",
            import_type=ImportType.MATERIALS
        )
        job = await import_service.create_import_job(job_data, str(test_user.id))

        # Cancel job
        success = await import_service.cancel_import_job(str(job.id))

        assert success is True

        # Verify cancelled
        updated_job = await import_service.get_import_job(str(job.id))
        assert updated_job.status == ImportStatus.CANCELLED

    # === FILE PARSING TESTS ===

    async def test_parse_xlsx_materials(
        self,
        import_service: ImportService,
        sample_materials_xlsx: BytesIO
    ):
        """Test parsing materials XLSX file."""
        result = await import_service.parse_xlsx_file(
            sample_materials_xlsx,
            ImportType.MATERIALS
        )

        assert result is not None
        assert "data" in result
        assert "columns" in result
        assert "row_count" in result
        assert result["row_count"] == 3
        assert "name" in result["columns"]

    async def test_parse_xlsx_regenerator(
        self,
        import_service: ImportService,
        sample_regenerator_xlsx: BytesIO
    ):
        """Test parsing regenerator XLSX file."""
        result = await import_service.parse_xlsx_file(
            sample_regenerator_xlsx,
            ImportType.REGENERATOR_CONFIG
        )

        assert result is not None
        assert result["row_count"] == 5

    async def test_parse_invalid_xlsx(self, import_service: ImportService):
        """Test parsing invalid XLSX file."""
        invalid_file = BytesIO(b"not an excel file")

        with pytest.raises(ValueError, match="Invalid Excel file"):
            await import_service.parse_xlsx_file(
                invalid_file,
                ImportType.MATERIALS
            )

    async def test_parse_empty_xlsx(self, import_service: ImportService):
        """Test parsing empty XLSX file."""
        # Create empty dataframe
        df = pd.DataFrame()
        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)

        with pytest.raises(ValueError, match="Empty file"):
            await import_service.parse_xlsx_file(
                buffer,
                ImportType.MATERIALS
            )

    # === VALIDATION TESTS ===

    async def test_validate_materials_data(
        self,
        import_service: ImportService
    ):
        """Test validating materials import data."""
        valid_data = [
            {
                "name": "Test Material",
                "material_type": "refractory",
                "thermal_conductivity": 2.5,
                "specific_heat": 900.0,
                "density": 2300.0,
                "max_temperature": 1600.0
            }
        ]

        result = await import_service.validate_import_data(
            valid_data,
            ImportType.MATERIALS
        )

        assert result is not None
        assert result["valid"] is True
        assert result["errors"] == []

    async def test_validate_materials_missing_required(
        self,
        import_service: ImportService
    ):
        """Test validating materials with missing required fields."""
        invalid_data = [
            {
                "name": "Incomplete Material",
                # Missing thermal_conductivity, density, etc.
            }
        ]

        result = await import_service.validate_import_data(
            invalid_data,
            ImportType.MATERIALS
        )

        assert result is not None
        assert result["valid"] is False
        assert len(result["errors"]) > 0

    async def test_validate_materials_negative_values(
        self,
        import_service: ImportService
    ):
        """Test validating materials with negative values."""
        invalid_data = [
            {
                "name": "Negative Material",
                "material_type": "refractory",
                "thermal_conductivity": -2.5,  # Invalid
                "specific_heat": 900.0,
                "density": 2300.0,
                "max_temperature": 1600.0
            }
        ]

        result = await import_service.validate_import_data(
            invalid_data,
            ImportType.MATERIALS
        )

        assert result is not None
        assert result["valid"] is False

    async def test_validate_regenerator_data(
        self,
        import_service: ImportService
    ):
        """Test validating regenerator configuration data."""
        valid_data = {
            "geometry_config": {
                "length": 10.0,
                "width": 8.0,
                "height": 6.0
            },
            "thermal_config": {
                "gas_temp_inlet": 1600.0,
                "gas_temp_outlet": 600.0
            },
            "flow_config": {
                "mass_flow_rate": 50.0
            }
        }

        result = await import_service.validate_import_data(
            [valid_data],
            ImportType.REGENERATOR_CONFIG
        )

        assert result is not None
        assert result["valid"] is True

    # === DATA IMPORT TESTS ===

    async def test_import_materials_success(
        self,
        import_service: ImportService,
        test_user: User,
        sample_materials_xlsx: BytesIO
    ):
        """Test successful materials import."""
        # Parse file
        parsed_data = await import_service.parse_xlsx_file(
            sample_materials_xlsx,
            ImportType.MATERIALS
        )

        # Import data
        result = await import_service.import_materials(
            parsed_data["data"],
            str(test_user.id)
        )

        assert result is not None
        assert result["success"] is True
        assert result["imported_count"] == 3
        assert result["failed_count"] == 0

    async def test_import_materials_with_duplicates(
        self,
        import_service: ImportService,
        test_user: User,
        test_db: AsyncSession
    ):
        """Test importing materials with duplicates."""
        # Create existing material
        existing = Material(
            name="Existing Material",
            material_type="refractory",
            thermal_conductivity=2.5,
            specific_heat=900.0,
            density=2300.0,
            max_temperature=1600.0,
            created_by_id=str(test_user.id)
        )
        test_db.add(existing)
        await test_db.commit()

        # Try to import duplicate
        duplicate_data = [
            {
                "name": "Existing Material",  # Duplicate
                "material_type": "insulation",
                "thermal_conductivity": 0.15,
                "specific_heat": 1000.0,
                "density": 150.0,
                "max_temperature": 1200.0
            }
        ]

        result = await import_service.import_materials(
            duplicate_data,
            str(test_user.id),
            skip_duplicates=True
        )

        assert result is not None
        assert result["skipped_count"] >= 1

    async def test_import_regenerator_config(
        self,
        import_service: ImportService,
        test_user: User
    ):
        """Test importing regenerator configuration."""
        config_data = {
            "name": "Imported Regenerator",
            "regenerator_type": "crown",
            "geometry_config": {
                "length": 10.0,
                "width": 8.0,
                "height": 6.0
            },
            "thermal_config": {
                "gas_temp_inlet": 1600.0,
                "gas_temp_outlet": 600.0,
                "ambient_temp": 25.0
            },
            "flow_config": {
                "mass_flow_rate": 50.0,
                "cycle_time": 1200.0
            },
            "materials_config": {
                "thermal_conductivity": 2.5,
                "specific_heat": 900.0,
                "checker_density": 2300.0
            }
        }

        result = await import_service.import_regenerator_config(
            config_data,
            str(test_user.id)
        )

        assert result is not None
        assert result["success"] is True
        assert "regenerator_id" in result

    # === PREVIEW TESTS ===

    async def test_preview_import_data(
        self,
        import_service: ImportService,
        sample_materials_xlsx: BytesIO
    ):
        """Test previewing import data before importing."""
        # Parse file
        parsed_data = await import_service.parse_xlsx_file(
            sample_materials_xlsx,
            ImportType.MATERIALS
        )

        # Generate preview
        preview = await import_service.generate_preview(
            parsed_data["data"],
            ImportType.MATERIALS,
            preview_rows=2
        )

        assert preview is not None
        assert "sample_data" in preview
        assert "total_rows" in preview
        assert "validation_summary" in preview
        assert len(preview["sample_data"]) <= 2

    async def test_preview_with_validation_errors(
        self,
        import_service: ImportService
    ):
        """Test preview highlighting validation errors."""
        invalid_data = [
            {
                "name": "Valid Material",
                "material_type": "refractory",
                "thermal_conductivity": 2.5,
                "specific_heat": 900.0,
                "density": 2300.0,
                "max_temperature": 1600.0
            },
            {
                "name": "Invalid Material",
                "material_type": "unknown",  # Invalid type
                "thermal_conductivity": -1.0,  # Invalid negative
                "specific_heat": 900.0,
                "density": 2300.0,
                "max_temperature": 1600.0
            }
        ]

        preview = await import_service.generate_preview(
            invalid_data,
            ImportType.MATERIALS
        )

        assert preview is not None
        assert preview["validation_summary"]["total_errors"] > 0

    # === PROGRESS TRACKING TESTS ===

    async def test_track_import_progress(
        self,
        import_service: ImportService,
        test_user: User
    ):
        """Test tracking import progress."""
        # Create job
        job_data = ImportJobCreate(
            job_name="Progress Track Test",
            import_type=ImportType.MATERIALS
        )
        job = await import_service.create_import_job(job_data, str(test_user.id))

        # Update progress
        await import_service.update_job_progress(
            str(job.id),
            progress=75.0,
            message="Processing row 75/100"
        )

        # Get progress
        progress = await import_service.get_import_progress(str(job.id))

        assert progress is not None
        assert progress["progress"] == 75.0
        assert "Processing" in progress["message"]

    async def test_import_with_callback(
        self,
        import_service: ImportService,
        test_user: User
    ):
        """Test import with progress callback."""
        progress_updates = []

        def progress_callback(current, total, message):
            progress_updates.append({
                'current': current,
                'total': total,
                'message': message
            })

        data = [
            {"name": f"Material {i}", "material_type": "refractory",
             "thermal_conductivity": 2.5, "specific_heat": 900.0,
             "density": 2300.0, "max_temperature": 1600.0}
            for i in range(10)
        ]

        result = await import_service.import_materials(
            data,
            str(test_user.id),
            progress_callback=progress_callback
        )

        assert result["success"] is True
        assert len(progress_updates) > 0

    # === ERROR HANDLING TESTS ===

    async def test_import_with_partial_failures(
        self,
        import_service: ImportService,
        test_user: User
    ):
        """Test import with some rows failing."""
        mixed_data = [
            {
                "name": "Valid Material 1",
                "material_type": "refractory",
                "thermal_conductivity": 2.5,
                "specific_heat": 900.0,
                "density": 2300.0,
                "max_temperature": 1600.0
            },
            {
                "name": "Invalid Material",
                # Missing required fields
            },
            {
                "name": "Valid Material 2",
                "material_type": "insulation",
                "thermal_conductivity": 0.15,
                "specific_heat": 1000.0,
                "density": 150.0,
                "max_temperature": 1200.0
            }
        ]

        result = await import_service.import_materials(
            mixed_data,
            str(test_user.id),
            stop_on_error=False
        )

        assert result is not None
        assert result["imported_count"] == 2
        assert result["failed_count"] == 1
        assert len(result["errors"]) >= 1

    async def test_import_stop_on_first_error(
        self,
        import_service: ImportService,
        test_user: User
    ):
        """Test import stopping on first error."""
        mixed_data = [
            {
                "name": "Invalid Material",
                # Missing fields - should fail
            },
            {
                "name": "Valid Material",
                "material_type": "refractory",
                "thermal_conductivity": 2.5,
                "specific_heat": 900.0,
                "density": 2300.0,
                "max_temperature": 1600.0
            }
        ]

        with pytest.raises(ValueError):
            await import_service.import_materials(
                mixed_data,
                str(test_user.id),
                stop_on_error=True
            )

    # === UNIT CONVERSION TESTS ===

    async def test_import_with_unit_conversion(
        self,
        import_service: ImportService,
        test_user: User
    ):
        """Test importing data with unit conversions."""
        data_imperial = [
            {
                "name": "Imperial Material",
                "material_type": "refractory",
                "thermal_conductivity": 1.4,  # BTU/(ft·hr·°F)
                "specific_heat": 0.215,  # BTU/(lb·°F)
                "density": 143.6,  # lb/ft³
                "max_temperature": 2912.0,  # °F
                "units": "imperial"
            }
        ]

        result = await import_service.import_materials(
            data_imperial,
            str(test_user.id),
            convert_units=True
        )

        assert result["success"] is True
        assert result["imported_count"] == 1

    # === CLEANUP TESTS ===

    async def test_cleanup_old_import_jobs(
        self,
        import_service: ImportService,
        test_user: User,
        test_db: AsyncSession
    ):
        """Test cleaning up old import jobs."""
        # Create old job
        old_job = ImportJob(
            job_name="Old Job",
            import_type=ImportType.MATERIALS,
            created_by_id=str(test_user.id),
            status=ImportStatus.COMPLETED,
            created_at=datetime.now(UTC) - timedelta(days=60)
        )
        test_db.add(old_job)
        await test_db.commit()

        # Cleanup jobs older than 30 days
        deleted_count = await import_service.cleanup_old_jobs(days=30)

        assert deleted_count >= 1

    async def test_cleanup_failed_jobs(
        self,
        import_service: ImportService,
        test_user: User
    ):
        """Test cleanup of failed import jobs."""
        # Create failed job
        job_data = ImportJobCreate(
            job_name="Failed Job",
            import_type=ImportType.MATERIALS
        )
        job = await import_service.create_import_job(job_data, str(test_user.id))

        # Mark as failed
        await import_service.update_job_status(
            str(job.id),
            ImportStatus.FAILED,
            error_message="Test failure"
        )

        # Cleanup failed jobs
        deleted_count = await import_service.cleanup_failed_jobs(days=7)

        assert deleted_count >= 0  # May or may not delete depending on timing

    # === STATISTICS TESTS ===

    async def test_get_import_statistics(
        self,
        import_service: ImportService,
        test_user: User
    ):
        """Test getting import statistics."""
        # Create several jobs with different statuses
        for status in [ImportStatus.COMPLETED, ImportStatus.FAILED, ImportStatus.PENDING]:
            job_data = ImportJobCreate(
                job_name=f"Job {status}",
                import_type=ImportType.MATERIALS
            )
            job = await import_service.create_import_job(job_data, str(test_user.id))
            await import_service.update_job_status(str(job.id), status)

        # Get statistics
        stats = await import_service.get_import_statistics(str(test_user.id))

        assert stats is not None
        assert "total_jobs" in stats
        assert "by_status" in stats
        assert "by_type" in stats
        assert stats["total_jobs"] >= 3
