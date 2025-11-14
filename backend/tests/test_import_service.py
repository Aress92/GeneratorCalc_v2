"""
Tests for import service.

Testy dla serwisu importu.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
from io import BytesIO

from app.services.import_service import ImportService
from app.models.user import User, UserRole
from app.models.import_job import ImportJob, ImportStatus, ImportType
from app.schemas.import_schemas import ImportJobCreate, ColumnMapping


class TestImportService:
    """Test import service functionality."""

    @pytest.fixture
    async def import_service(self, test_db: AsyncSession) -> ImportService:
        """Create import service instance."""
        return ImportService(test_db)

    @pytest.fixture
    async def test_user(self, test_db: AsyncSession) -> User:
        """Create test user."""
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
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
    def sample_excel_data(self) -> bytes:
        """Create sample Excel data for testing."""
        data = {
            'Name': ['Regenerator 1', 'Regenerator 2', 'Regenerator 3'],
            'Type': ['CROWN', 'END_PORT', 'CROSS_FIRED'],
            'Length': [10.0, 12.0, 15.0],
            'Width': [8.0, 10.0, 12.0],
            'Height': [6.0, 7.0, 8.0],
            'Wall_Thickness': [0.4, 0.5, 0.6],
            'Gas_Temp_Inlet': [1600.0, 1700.0, 1800.0],
            'Gas_Temp_Outlet': [600.0, 650.0, 700.0],
            'Mass_Flow_Rate': [50.0, 60.0, 70.0],
            'Cycle_Time': [1200.0, 1400.0, 1600.0]
        }

        df = pd.DataFrame(data)
        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        return buffer.getvalue()

    @pytest.fixture
    def sample_csv_data(self) -> str:
        """Create sample CSV data for testing."""
        return """Name,Type,Length,Width,Height,Wall_Thickness,Gas_Temp_Inlet,Gas_Temp_Outlet,Mass_Flow_Rate,Cycle_Time
Regenerator 1,CROWN,10.0,8.0,6.0,0.4,1600.0,600.0,50.0,1200.0
Regenerator 2,END_PORT,12.0,10.0,7.0,0.5,1700.0,650.0,60.0,1400.0
Regenerator 3,CROSS_FIRED,15.0,12.0,8.0,0.6,1800.0,700.0,70.0,1600.0"""

    async def test_preview_excel_file(self, import_service: ImportService, sample_excel_data: bytes):
        """Test previewing Excel file."""
        with patch('pandas.read_excel') as mock_read_excel:
            mock_df = pd.DataFrame({
                'Name': ['Test Regenerator'],
                'Type': ['CROWN'],
                'Length': [10.0]
            })
            mock_read_excel.return_value = mock_df

            result = await import_service.preview_file(sample_excel_data, 'regenerators.xlsx')

            assert result is not None
            assert 'columns' in result
            assert 'sample_data' in result
            assert 'row_count' in result
            assert len(result['columns']) == 3

    async def test_preview_csv_file(self, import_service: ImportService, sample_csv_data: str):
        """Test previewing CSV file."""
        csv_bytes = sample_csv_data.encode('utf-8')

        with patch('pandas.read_csv') as mock_read_csv:
            mock_df = pd.DataFrame({
                'Name': ['Test Regenerator'],
                'Type': ['CROWN'],
                'Length': [10.0]
            })
            mock_read_csv.return_value = mock_df

            result = await import_service.preview_file(csv_bytes, 'regenerators.csv')

            assert result is not None
            assert 'columns' in result
            assert 'sample_data' in result
            assert 'row_count' in result

    async def test_validate_column_mapping(self, import_service: ImportService):
        """Test column mapping validation."""
        column_mapping = [
            ColumnMapping(source_column='Name', target_field='name', is_required=True),
            ColumnMapping(source_column='Type', target_field='regenerator_type', is_required=True),
            ColumnMapping(source_column='Length', target_field='geometry_config.length', is_required=True),
            ColumnMapping(source_column='Width', target_field='geometry_config.width', is_required=True)
        ]

        available_columns = ['Name', 'Type', 'Length', 'Width', 'Height']

        result = await import_service.validate_column_mapping(column_mapping, available_columns)

        assert result['is_valid'] is True
        assert len(result['errors']) == 0

        # Test invalid mapping
        invalid_mapping = [
            ColumnMapping(source_column='NonExistent', target_field='name', is_required=True)
        ]

        result = await import_service.validate_column_mapping(invalid_mapping, available_columns)

        assert result['is_valid'] is False
        assert len(result['errors']) > 0

    async def test_dry_run_import(self, import_service: ImportService, test_user: User, sample_excel_data: bytes):
        """Test dry run import validation."""
        column_mapping = [
            ColumnMapping(source_column='Name', target_field='name', is_required=True),
            ColumnMapping(source_column='Type', target_field='regenerator_type', is_required=True),
            ColumnMapping(source_column='Length', target_field='geometry_config.length', is_required=True),
            ColumnMapping(source_column='Width', target_field='geometry_config.width', is_required=True)
        ]

        with patch('pandas.read_excel') as mock_read_excel:
            mock_df = pd.DataFrame({
                'Name': ['Valid Regenerator', 'Invalid Regenerator'],
                'Type': ['CROWN', 'INVALID_TYPE'],
                'Length': [10.0, -5.0],  # Negative length should be invalid
                'Width': [8.0, 6.0]
            })
            mock_read_excel.return_value = mock_df

            result = await import_service.dry_run_import(
                sample_excel_data,
                'regenerators.xlsx',
                ImportType.REGENERATORS,
                column_mapping,
                str(test_user.id)
            )

            assert result is not None
            assert 'validation_summary' in result
            assert 'valid_rows' in result
            assert 'invalid_rows' in result
            assert 'errors' in result

    async def test_create_import_job(self, import_service: ImportService, test_user: User):
        """Test creating import job."""
        job_data = ImportJobCreate(
            filename='test_regenerators.xlsx',
            import_type=ImportType.REGENERATORS,
            column_mapping=[
                ColumnMapping(source_column='Name', target_field='name', is_required=True),
                ColumnMapping(source_column='Type', target_field='regenerator_type', is_required=True)
            ],
            import_settings={
                'skip_duplicates': True,
                'validate_data': True
            }
        )

        result = await import_service.create_import_job(job_data, str(test_user.id))

        assert result is not None
        assert result.filename == 'test_regenerators.xlsx'
        assert result.import_type == ImportType.REGENERATORS
        assert result.status == ImportStatus.PENDING
        assert result.created_by_id == str(test_user.id)

    async def test_get_import_job(self, import_service: ImportService, test_user: User):
        """Test getting import job by ID."""
        # Create job first
        job_data = ImportJobCreate(
            filename='test_file.xlsx',
            import_type=ImportType.REGENERATORS,
            column_mapping=[],
            import_settings={}
        )
        job = await import_service.create_import_job(job_data, str(test_user.id))

        # Get the job
        result = await import_service.get_import_job(str(job.id))

        assert result is not None
        assert result.id == job.id
        assert result.filename == 'test_file.xlsx'

    async def test_get_user_import_jobs(self, import_service: ImportService, test_user: User):
        """Test getting user's import jobs."""
        # Create a job first
        job_data = ImportJobCreate(
            filename='user_test_file.xlsx',
            import_type=ImportType.REGENERATORS,
            column_mapping=[],
            import_settings={}
        )
        job = await import_service.create_import_job(job_data, str(test_user.id))

        # Get user jobs
        jobs = await import_service.get_user_import_jobs(str(test_user.id), limit=10, offset=0)

        assert len(jobs) >= 1
        found_job = next((j for j in jobs if j.id == job.id), None)
        assert found_job is not None

    async def test_update_job_status(self, import_service: ImportService, test_user: User):
        """Test updating job status."""
        # Create job first
        job_data = ImportJobCreate(
            filename='status_test.xlsx',
            import_type=ImportType.REGENERATORS,
            column_mapping=[],
            import_settings={}
        )
        job = await import_service.create_import_job(job_data, str(test_user.id))

        # Update status
        await import_service.update_job_status(str(job.id), ImportStatus.PROCESSING, "Starting import process")

        # Verify update
        updated_job = await import_service.get_import_job(str(job.id))
        assert updated_job.status == ImportStatus.PROCESSING
        assert updated_job.status_message == "Starting import process"

    async def test_update_job_progress(self, import_service: ImportService, test_user: User):
        """Test updating job progress."""
        # Create job first
        job_data = ImportJobCreate(
            filename='progress_test.xlsx',
            import_type=ImportType.REGENERATORS,
            column_mapping=[],
            import_settings={}
        )
        job = await import_service.create_import_job(job_data, str(test_user.id))

        # Update progress
        await import_service.update_job_progress(str(job.id), 50.0, 10, 20, "Processing row 10 of 20")

        # Verify update
        updated_job = await import_service.get_import_job(str(job.id))
        assert updated_job.progress_percentage == 50.0
        assert updated_job.rows_processed == 10
        assert updated_job.total_rows == 20

    async def test_mark_job_completed(self, import_service: ImportService, test_user: User):
        """Test marking job as completed."""
        # Create job first
        job_data = ImportJobCreate(
            filename='completion_test.xlsx',
            import_type=ImportType.REGENERATORS,
            column_mapping=[],
            import_settings={}
        )
        job = await import_service.create_import_job(job_data, str(test_user.id))

        # Mark as completed
        await import_service.mark_job_completed(str(job.id), 15, 3, 5, "Import completed successfully")

        # Verify completion
        completed_job = await import_service.get_import_job(str(job.id))
        assert completed_job.status == ImportStatus.COMPLETED
        assert completed_job.records_imported == 15
        assert completed_job.records_failed == 3
        assert completed_job.records_skipped == 5

    async def test_mark_job_failed(self, import_service: ImportService, test_user: User):
        """Test marking job as failed."""
        # Create job first
        job_data = ImportJobCreate(
            filename='failure_test.xlsx',
            import_type=ImportType.REGENERATORS,
            column_mapping=[],
            import_settings={}
        )
        job = await import_service.create_import_job(job_data, str(test_user.id))

        # Mark as failed
        await import_service.mark_job_failed(str(job.id), "Database connection failed")

        # Verify failure
        failed_job = await import_service.get_import_job(str(job.id))
        assert failed_job.status == ImportStatus.FAILED
        assert "Database connection failed" in failed_job.error_details

    async def test_get_import_templates(self, import_service: ImportService):
        """Test getting import templates."""
        templates = await import_service.get_import_templates()

        assert isinstance(templates, list)
        assert len(templates) > 0

        # Check template structure
        template = templates[0]
        assert 'name' in template
        assert 'import_type' in template
        assert 'columns' in template
        assert 'sample_data' in template

    async def test_generate_import_template(self, import_service: ImportService):
        """Test generating import template."""
        template_data = await import_service.generate_import_template(ImportType.REGENERATORS)

        assert template_data is not None
        assert isinstance(template_data, bytes)  # Should be Excel file data

    async def test_validate_import_data(self, import_service: ImportService):
        """Test import data validation."""
        # Valid data
        valid_data = {
            'name': 'Test Regenerator',
            'regenerator_type': 'CROWN',
            'geometry_config': {
                'length': 10.0,
                'width': 8.0,
                'height': 6.0
            }
        }

        result = await import_service._validate_import_data(valid_data, ImportType.REGENERATORS)
        assert result['is_valid'] is True
        assert len(result['errors']) == 0

        # Invalid data
        invalid_data = {
            'name': '',  # Empty name
            'regenerator_type': 'INVALID_TYPE',
            'geometry_config': {
                'length': -5.0,  # Negative length
                'width': 8.0
            }
        }

        result = await import_service._validate_import_data(invalid_data, ImportType.REGENERATORS)
        assert result['is_valid'] is False
        assert len(result['errors']) > 0

    async def test_process_import_batch(self, import_service: ImportService, test_user: User):
        """Test processing import batch."""
        batch_data = [
            {
                'name': 'Batch Regenerator 1',
                'regenerator_type': 'CROWN',
                'geometry_config': {'length': 10.0, 'width': 8.0}
            },
            {
                'name': 'Batch Regenerator 2',
                'regenerator_type': 'END_PORT',
                'geometry_config': {'length': 12.0, 'width': 10.0}
            }
        ]

        with patch.object(import_service, '_create_regenerator_from_data') as mock_create:
            mock_create.return_value = True

            result = await import_service._process_import_batch(
                batch_data, ImportType.REGENERATORS, str(test_user.id)
            )

            assert result['successful'] == 2
            assert result['failed'] == 0
            assert mock_create.call_count == 2

    async def test_handle_import_errors(self, import_service: ImportService):
        """Test error handling during import."""
        # Test with various error types
        errors = [
            {'row': 1, 'error': 'Invalid regenerator type', 'field': 'regenerator_type'},
            {'row': 2, 'error': 'Negative length value', 'field': 'geometry_config.length'},
            {'row': 3, 'error': 'Missing required field', 'field': 'name'}
        ]

        summary = await import_service._generate_error_summary(errors)

        assert 'total_errors' in summary
        assert 'error_types' in summary
        assert 'affected_fields' in summary
        assert summary['total_errors'] == 3

    async def test_cleanup_failed_imports(self, import_service: ImportService, test_user: User):
        """Test cleaning up failed import data."""
        # Create failed job
        job_data = ImportJobCreate(
            filename='cleanup_test.xlsx',
            import_type=ImportType.REGENERATORS,
            column_mapping=[],
            import_settings={}
        )
        job = await import_service.create_import_job(job_data, str(test_user.id))
        await import_service.mark_job_failed(str(job.id), "Test failure")

        # Test cleanup
        cleaned_count = await import_service.cleanup_failed_imports(days_old=0)

        assert isinstance(cleaned_count, int)
        assert cleaned_count >= 0

    async def test_import_job_statistics(self, import_service: ImportService, test_user: User):
        """Test getting import job statistics."""
        # Create some jobs first
        for i in range(3):
            job_data = ImportJobCreate(
                filename=f'stats_test_{i}.xlsx',
                import_type=ImportType.REGENERATORS,
                column_mapping=[],
                import_settings={}
            )
            await import_service.create_import_job(job_data, str(test_user.id))

        stats = await import_service.get_import_statistics(str(test_user.id))

        assert 'total_jobs' in stats
        assert 'by_status' in stats
        assert 'by_import_type' in stats
        assert 'recent_jobs' in stats
        assert stats['total_jobs'] >= 3