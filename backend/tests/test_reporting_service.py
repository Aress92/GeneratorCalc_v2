"""
Tests for reporting service.

Testy dla serwisu raportów.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.services.reporting_service import ReportingService
from app.models.user import User, UserRole
from app.models.reporting import Report, ReportType, ReportStatus, ReportTemplate
from app.schemas.reporting_schemas import ReportCreate, ReportTemplateCreate


class TestReportingService:
    """Test reporting service functionality."""

    @pytest.fixture
    async def reporting_service(self, test_db: AsyncSession) -> ReportingService:
        """Create reporting service instance."""
        return ReportingService(test_db)

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
    async def test_report_template(self, test_db: AsyncSession, test_user: User) -> ReportTemplate:
        """Create test report template."""
        template = ReportTemplate(
            name="Test Report Template",
            description="Template for testing reports",
            report_type=ReportType.OPTIMIZATION_SUMMARY,
            template_config={
                "sections": ["executive_summary", "methodology", "results", "recommendations"],
                "include_charts": True,
                "include_tables": True,
                "chart_types": ["line", "bar", "pie"]
            },
            output_formats=["pdf", "xlsx"],
            is_active=True,
            created_by_id=str(test_user.id)
        )
        test_db.add(template)
        await test_db.commit()
        await test_db.refresh(template)
        return template

    @pytest.fixture
    async def test_report(self, test_db: AsyncSession, test_user: User, test_report_template: ReportTemplate) -> Report:
        """Create test report."""
        report = Report(
            name="Test Optimization Report",
            description="Test report for optimization results",
            report_type=ReportType.OPTIMIZATION_SUMMARY,
            status=ReportStatus.COMPLETED,
            template_id=str(test_report_template.id),
            file_path="/reports/test_report.pdf",
            file_size=1024000,
            report_data={
                "optimization_id": "test-optimization-123",
                "baseline_efficiency": 0.75,
                "optimized_efficiency": 0.85,
                "fuel_savings": 12.5,
                "co2_reduction": 8.3
            },
            generated_at=datetime.utcnow(),
            created_by_id=str(test_user.id)
        )
        test_db.add(report)
        await test_db.commit()
        await test_db.refresh(report)
        return report

    async def test_create_report(self, reporting_service: ReportingService, test_user: User, test_report_template: ReportTemplate):
        """Test creating a new report."""
        report_data = ReportCreate(
            name="New Test Report",
            description="New test report for optimization",
            report_type=ReportType.PERFORMANCE_ANALYSIS,
            template_id=str(test_report_template.id),
            report_data={
                "regenerator_id": "test-regenerator-456",
                "analysis_period": "2024-01-01 to 2024-01-31",
                "performance_metrics": {
                    "thermal_efficiency": 0.82,
                    "pressure_drop": 1800.0,
                    "fuel_consumption": 125.7
                }
            },
            output_format="pdf"
        )

        result = await reporting_service.create_report(report_data, str(test_user.id))

        assert result.name == "New Test Report"
        assert result.report_type == ReportType.PERFORMANCE_ANALYSIS
        assert result.template_id == str(test_report_template.id)
        assert result.status == ReportStatus.PENDING
        assert result.created_by_id == str(test_user.id)

    async def test_get_report_by_id(self, reporting_service: ReportingService, test_report: Report):
        """Test getting report by ID."""
        result = await reporting_service.get_report(str(test_report.id))

        assert result is not None
        assert result.id == test_report.id
        assert result.name == test_report.name
        assert result.report_type == test_report.report_type

    async def test_get_report_not_found(self, reporting_service: ReportingService):
        """Test getting non-existent report."""
        result = await reporting_service.get_report("non-existent-id")
        assert result is None

    async def test_get_user_reports(self, reporting_service: ReportingService, test_user: User, test_report: Report):
        """Test getting user's reports."""
        reports = await reporting_service.get_user_reports(str(test_user.id), limit=10, offset=0)

        assert len(reports) >= 1
        found_report = next((r for r in reports if r.id == test_report.id), None)
        assert found_report is not None

    async def test_delete_report(self, reporting_service: ReportingService, test_report: Report, test_user: User):
        """Test deleting report."""
        success = await reporting_service.delete_report(str(test_report.id), str(test_user.id))

        assert success is True

        # Verify report is deleted
        deleted_report = await reporting_service.get_report(str(test_report.id))
        assert deleted_report is None

    async def test_update_report_status(self, reporting_service: ReportingService, test_report: Report):
        """Test updating report status."""
        await reporting_service.update_report_status(str(test_report.id), ReportStatus.PROCESSING, "Generating PDF")

        updated_report = await reporting_service.get_report(str(test_report.id))
        assert updated_report.status == ReportStatus.PROCESSING
        assert updated_report.status_message == "Generating PDF"

    async def test_mark_report_completed(self, reporting_service: ReportingService, test_report: Report):
        """Test marking report as completed."""
        file_path = "/reports/completed_report.pdf"
        file_size = 2048000

        await reporting_service.mark_report_completed(str(test_report.id), file_path, file_size)

        completed_report = await reporting_service.get_report(str(test_report.id))
        assert completed_report.status == ReportStatus.COMPLETED
        assert completed_report.file_path == file_path
        assert completed_report.file_size == file_size
        assert completed_report.generated_at is not None

    async def test_mark_report_failed(self, reporting_service: ReportingService, test_report: Report):
        """Test marking report as failed."""
        error_message = "Failed to generate charts"

        await reporting_service.mark_report_failed(str(test_report.id), error_message)

        failed_report = await reporting_service.get_report(str(test_report.id))
        assert failed_report.status == ReportStatus.FAILED
        assert error_message in failed_report.error_details

    async def test_get_dashboard_metrics(self, reporting_service: ReportingService, test_user: User, test_report: Report):
        """Test getting dashboard metrics."""
        metrics = await reporting_service.get_dashboard_metrics(str(test_user.id))

        assert "total_reports" in metrics
        assert "reports_by_type" in metrics
        assert "reports_by_status" in metrics
        assert "recent_reports" in metrics
        assert "storage_usage" in metrics

        assert metrics["total_reports"] >= 1

    async def test_get_report_analytics(self, reporting_service: ReportingService, test_user: User):
        """Test getting report analytics."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)

        analytics = await reporting_service.get_report_analytics(str(test_user.id), start_date, end_date)

        assert "total_reports" in analytics
        assert "reports_by_day" in analytics
        assert "reports_by_type" in analytics
        assert "average_generation_time" in analytics
        assert "success_rate" in analytics

    async def test_create_report_template(self, reporting_service: ReportingService, test_user: User):
        """Test creating report template."""
        template_data = ReportTemplateCreate(
            name="New Test Template",
            description="New template for testing",
            report_type=ReportType.SYSTEM_ANALYSIS,
            template_config={
                "sections": ["overview", "technical_analysis", "conclusions"],
                "include_charts": True,
                "chart_types": ["scatter", "heatmap"]
            },
            output_formats=["pdf", "xlsx", "csv"]
        )

        result = await reporting_service.create_report_template(template_data, str(test_user.id))

        assert result.name == "New Test Template"
        assert result.report_type == ReportType.SYSTEM_ANALYSIS
        assert result.created_by_id == str(test_user.id)
        assert result.is_active is True

    async def test_get_report_templates(self, reporting_service: ReportingService, test_report_template: ReportTemplate):
        """Test getting report templates."""
        templates = await reporting_service.get_report_templates(limit=10, offset=0)

        assert len(templates) >= 1
        found_template = next((t for t in templates if t.id == test_report_template.id), None)
        assert found_template is not None

    async def test_get_templates_by_type(self, reporting_service: ReportingService, test_report_template: ReportTemplate):
        """Test getting templates by report type."""
        templates = await reporting_service.get_templates_by_type(ReportType.OPTIMIZATION_SUMMARY)

        assert isinstance(templates, list)
        if templates:  # If any exist
            found_template = next((t for t in templates if t.id == test_report_template.id), None)
            assert found_template is not None

    async def test_generate_report_data(self, reporting_service: ReportingService):
        """Test generating report data."""
        report_config = {
            "optimization_id": "test-optimization-789",
            "include_baseline": True,
            "include_charts": True,
            "date_range": {
                "start": "2024-01-01",
                "end": "2024-01-31"
            }
        }

        with patch.object(reporting_service, '_fetch_optimization_data') as mock_fetch:
            mock_fetch.return_value = {
                "baseline_efficiency": 0.78,
                "optimized_efficiency": 0.88,
                "improvement": 0.10
            }

            result = await reporting_service._generate_report_data(ReportType.OPTIMIZATION_SUMMARY, report_config)

            assert result is not None
            assert "baseline_efficiency" in result

    @patch('app.services.pdf_generator.PDFGenerator.generate_optimization_report')
    async def test_generate_pdf_report(self, mock_pdf_gen, reporting_service: ReportingService, test_report: Report):
        """Test generating PDF report."""
        mock_pdf_gen.return_value = b"PDF content"

        result = await reporting_service._generate_pdf_report(test_report)

        assert result == b"PDF content"
        mock_pdf_gen.assert_called_once()

    @patch('app.services.excel_generator.ExcelGenerator.generate_optimization_report')
    async def test_generate_excel_report(self, mock_excel_gen, reporting_service: ReportingService, test_report: Report):
        """Test generating Excel report."""
        mock_excel_gen.return_value = b"Excel content"

        result = await reporting_service._generate_excel_report(test_report)

        assert result == b"Excel content"
        mock_excel_gen.assert_called_once()

    async def test_validate_report_data(self, reporting_service: ReportingService):
        """Test report data validation."""
        # Valid data
        valid_data = {
            "optimization_id": "valid-optimization-123",
            "baseline_efficiency": 0.75,
            "optimized_efficiency": 0.85,
            "date_range": {
                "start": "2024-01-01",
                "end": "2024-01-31"
            }
        }

        result = await reporting_service._validate_report_data(valid_data, ReportType.OPTIMIZATION_SUMMARY)
        assert result["is_valid"] is True

        # Invalid data
        invalid_data = {
            "optimization_id": "",  # Empty ID
            "baseline_efficiency": 1.5,  # Invalid efficiency > 1
            "optimized_efficiency": -0.1  # Negative efficiency
        }

        result = await reporting_service._validate_report_data(invalid_data, ReportType.OPTIMIZATION_SUMMARY)
        assert result["is_valid"] is False
        assert len(result["errors"]) > 0

    async def test_cleanup_old_reports(self, reporting_service: ReportingService):
        """Test cleaning up old reports."""
        cleaned_count = await reporting_service.cleanup_old_reports(days_old=30)

        assert isinstance(cleaned_count, int)
        assert cleaned_count >= 0

    async def test_get_report_file_info(self, reporting_service: ReportingService, test_report: Report):
        """Test getting report file information."""
        file_info = await reporting_service.get_report_file_info(str(test_report.id))

        assert file_info is not None
        assert "file_path" in file_info
        assert "file_size" in file_info
        assert "generated_at" in file_info
        assert "format" in file_info

    async def test_download_report(self, reporting_service: ReportingService, test_report: Report):
        """Test downloading report file."""
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = b"report content"

            content = await reporting_service.download_report(str(test_report.id))

            assert content == b"report content"

    async def test_get_report_statistics(self, reporting_service: ReportingService, test_user: User):
        """Test getting report statistics."""
        stats = await reporting_service.get_report_statistics(str(test_user.id))

        assert "total_reports" in stats
        assert "by_type" in stats
        assert "by_status" in stats
        assert "total_size" in stats
        assert "generation_times" in stats

    async def test_schedule_report_generation(self, reporting_service: ReportingService, test_user: User, test_report_template: ReportTemplate):
        """Test scheduling report generation."""
        schedule_config = {
            "frequency": "weekly",
            "day_of_week": "monday",
            "time": "09:00",
            "email_recipients": ["test@example.com"]
        }

        report_config = {
            "template_id": str(test_report_template.id),
            "output_format": "pdf",
            "auto_email": True
        }

        result = await reporting_service.schedule_report_generation(
            "Weekly Optimization Report",
            schedule_config,
            report_config,
            str(test_user.id)
        )

        assert result is not None
        assert "schedule_id" in result
        assert "next_run" in result

    async def test_export_report_data(self, reporting_service: ReportingService, test_report: Report):
        """Test exporting report data."""
        export_data = await reporting_service.export_report_data(str(test_report.id), "json")

        assert export_data is not None
        assert isinstance(export_data, (str, bytes))

    async def test_bulk_report_operations(self, reporting_service: ReportingService, test_user: User):
        """Test bulk report operations."""
        # Create multiple reports for testing
        report_ids = []
        for i in range(3):
            report_data = ReportCreate(
                name=f"Bulk Test Report {i}",
                description=f"Report {i} for bulk testing",
                report_type=ReportType.OPTIMIZATION_SUMMARY,
                report_data={"test_data": f"data_{i}"},
                output_format="pdf"
            )
            report = await reporting_service.create_report(report_data, str(test_user.id))
            report_ids.append(str(report.id))

        # Test bulk delete
        deleted_count = await reporting_service.bulk_delete_reports(report_ids, str(test_user.id))

        assert deleted_count == 3