"""
Extended tests for reporting service.

Rozszerzone testy dla serwisu raportowania.
"""

import pytest
from uuid import uuid4
from datetime import datetime, UTC
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.reporting_service import ReportingService
from app.models.user import User, UserRole
from app.models.reporting import Report, ReportTemplate, ReportFormat, ReportStatus
from app.models.optimization import OptimizationScenario, OptimizationResult, OptimizationJob, OptimizationStatus
from app.models.regenerator import RegeneratorConfiguration, RegeneratorType, ConfigurationStatus
from app.schemas.reporting_schemas import ReportCreate, ReportTemplateCreate, ReportFilter


class TestReportingServiceExtended:
    """Extended tests for ReportingService functionality."""

    @pytest.fixture
    async def reporting_service(self, test_db: AsyncSession) -> ReportingService:
        """Create reporting service instance."""
        return ReportingService(test_db)

    @pytest.fixture
    async def test_user(self, test_db: AsyncSession) -> User:
        """Create test user."""
        unique_id = uuid4().hex[:8]
        user = User(
            username=f"reportuser_{unique_id}",
            email=f"report_{unique_id}@example.com",
            full_name="Report Test User",
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
    async def test_regenerator(self, test_db: AsyncSession, test_user: User) -> RegeneratorConfiguration:
        """Create test regenerator."""
        config = RegeneratorConfiguration(
            user_id=str(test_user.id),
            name=f"Test Regenerator {uuid4().hex[:6]}",
            regenerator_type=RegeneratorType.CROWN,
            status=ConfigurationStatus.COMPLETED,
            geometry_config={"length": 10.0, "width": 8.0, "height": 6.0},
            materials_config={"thermal_conductivity": 2.5},
            thermal_config={"gas_temp_inlet": 1600.0},
            flow_config={"mass_flow_rate": 50.0}
        )
        test_db.add(config)
        await test_db.commit()
        await test_db.refresh(config)
        return config

    @pytest.fixture
    async def test_scenario(
        self,
        test_db: AsyncSession,
        test_user: User,
        test_regenerator: RegeneratorConfiguration
    ) -> OptimizationScenario:
        """Create test optimization scenario."""
        scenario = OptimizationScenario(
            user_id=str(test_user.id),
            base_configuration_id=str(test_regenerator.id),
            name=f"Test Scenario {uuid4().hex[:6]}",
            scenario_type="geometry_optimization",
            objective="minimize_fuel_consumption",
            algorithm="slsqp",
            design_variables={"checker_height": {"min": 0.5, "max": 1.0}},
            max_iterations=100,
            tolerance=1e-6
        )
        test_db.add(scenario)
        await test_db.commit()
        await test_db.refresh(scenario)
        return scenario

    @pytest.fixture
    async def test_optimization_job(
        self,
        test_db: AsyncSession,
        test_scenario: OptimizationScenario,
        test_user: User
    ) -> OptimizationJob:
        """Create completed optimization job."""
        job = OptimizationJob(
            scenario_id=str(test_scenario.id),
            user_id=str(test_user.id),
            job_name="Test Optimization",
            status=OptimizationStatus.COMPLETED,
            progress=100.0
        )
        test_db.add(job)
        await test_db.commit()
        await test_db.refresh(job)
        return job

    @pytest.fixture
    async def test_report_template(
        self,
        test_db: AsyncSession,
        test_user: User
    ) -> ReportTemplate:
        """Create test report template."""
        template = ReportTemplate(
            name=f"Test Template {uuid4().hex[:6]}",
            description="Test template description",
            category="optimization",
            format=ReportFormat.PDF,
            template_config={
                "sections": ["summary", "results", "charts"],
                "logo": "company_logo.png"
            },
            created_by_id=str(test_user.id),
            is_active=True,
            is_default=False
        )
        test_db.add(template)
        await test_db.commit()
        await test_db.refresh(template)
        return template

    # === REPORT CREATION TESTS ===

    async def test_create_report_pdf(
        self,
        reporting_service: ReportingService,
        test_user: User,
        test_optimization_job: OptimizationJob
    ):
        """Test creating PDF report."""
        report_data = ReportCreate(
            report_name="Test PDF Report",
            report_format=ReportFormat.PDF,
            description="Testing PDF report generation",
            data_source_id=str(test_optimization_job.id),
            data_source_type="optimization_job",
            configuration={
                "include_charts": True,
                "include_recommendations": True
            }
        )

        result = await reporting_service.create_report(
            report_data,
            str(test_user.id)
        )

        assert result is not None
        assert result.report_name == "Test PDF Report"
        assert result.format == ReportFormat.PDF
        assert result.created_by_id == str(test_user.id)
        assert result.status == ReportStatus.PENDING

    async def test_create_report_excel(
        self,
        reporting_service: ReportingService,
        test_user: User,
        test_optimization_job: OptimizationJob
    ):
        """Test creating Excel report."""
        report_data = ReportCreate(
            report_name="Test Excel Report",
            report_format=ReportFormat.EXCEL,
            data_source_id=str(test_optimization_job.id),
            data_source_type="optimization_job"
        )

        result = await reporting_service.create_report(
            report_data,
            str(test_user.id)
        )

        assert result.format == ReportFormat.EXCEL

    async def test_create_report_from_template(
        self,
        reporting_service: ReportingService,
        test_user: User,
        test_optimization_job: OptimizationJob,
        test_report_template: ReportTemplate
    ):
        """Test creating report from template."""
        report_data = ReportCreate(
            report_name="Report from Template",
            report_format=ReportFormat.PDF,
            data_source_id=str(test_optimization_job.id),
            data_source_type="optimization_job",
            template_id=str(test_report_template.id)
        )

        result = await reporting_service.create_report(
            report_data,
            str(test_user.id)
        )

        assert result.template_id == str(test_report_template.id)

    # === REPORT GENERATION TESTS ===

    @patch('app.services.pdf_generator.PDFGenerator.generate')
    async def test_generate_pdf_report(
        self,
        mock_pdf_gen,
        reporting_service: ReportingService,
        test_user: User,
        test_optimization_job: OptimizationJob
    ):
        """Test generating PDF report."""
        # Mock PDF generation
        mock_pdf_gen.return_value = b"PDF content"

        # Create report
        report_data = ReportCreate(
            report_name="Generate PDF Test",
            report_format=ReportFormat.PDF,
            data_source_id=str(test_optimization_job.id),
            data_source_type="optimization_job"
        )
        report = await reporting_service.create_report(report_data, str(test_user.id))

        # Generate report
        file_path = await reporting_service.generate_report(str(report.id))

        assert file_path is not None
        assert mock_pdf_gen.called

        # Verify report status updated
        updated_report = await reporting_service.get_report(str(report.id))
        assert updated_report.status == ReportStatus.COMPLETED
        assert updated_report.file_path is not None

    @patch('app.services.excel_generator.ExcelGenerator.generate')
    async def test_generate_excel_report(
        self,
        mock_excel_gen,
        reporting_service: ReportingService,
        test_user: User,
        test_optimization_job: OptimizationJob
    ):
        """Test generating Excel report."""
        # Mock Excel generation
        mock_excel_gen.return_value = b"Excel content"

        # Create report
        report_data = ReportCreate(
            report_name="Generate Excel Test",
            report_format=ReportFormat.EXCEL,
            data_source_id=str(test_optimization_job.id),
            data_source_type="optimization_job"
        )
        report = await reporting_service.create_report(report_data, str(test_user.id))

        # Generate report
        file_path = await reporting_service.generate_report(str(report.id))

        assert file_path is not None
        assert mock_excel_gen.called

    async def test_generate_report_not_found(
        self,
        reporting_service: ReportingService
    ):
        """Test generating non-existent report."""
        with pytest.raises(ValueError, match="Report .* not found"):
            await reporting_service.generate_report(str(uuid4()))

    # === REPORT RETRIEVAL TESTS ===

    async def test_get_report_by_id(
        self,
        reporting_service: ReportingService,
        test_user: User,
        test_optimization_job: OptimizationJob
    ):
        """Test getting report by ID."""
        # Create report
        report_data = ReportCreate(
            report_name="Get Report Test",
            report_format=ReportFormat.PDF,
            data_source_id=str(test_optimization_job.id),
            data_source_type="optimization_job"
        )
        report = await reporting_service.create_report(report_data, str(test_user.id))

        # Get report
        result = await reporting_service.get_report(str(report.id))

        assert result is not None
        assert result.id == report.id
        assert result.report_name == report.report_name

    async def test_get_user_reports(
        self,
        reporting_service: ReportingService,
        test_user: User,
        test_optimization_job: OptimizationJob
    ):
        """Test getting user's reports."""
        # Create multiple reports
        for i in range(3):
            report_data = ReportCreate(
                report_name=f"Report {i}",
                report_format=ReportFormat.PDF,
                data_source_id=str(test_optimization_job.id),
                data_source_type="optimization_job"
            )
            await reporting_service.create_report(report_data, str(test_user.id))

        # Get user's reports
        results = await reporting_service.get_user_reports(
            str(test_user.id),
            limit=10,
            offset=0
        )

        assert len(results) >= 3
        assert all(r.created_by_id == str(test_user.id) for r in results)

    async def test_get_reports_by_format(
        self,
        reporting_service: ReportingService,
        test_user: User,
        test_optimization_job: OptimizationJob
    ):
        """Test filtering reports by format."""
        # Create PDF reports
        for i in range(2):
            report_data = ReportCreate(
                report_name=f"PDF Report {i}",
                report_format=ReportFormat.PDF,
                data_source_id=str(test_optimization_job.id),
                data_source_type="optimization_job"
            )
            await reporting_service.create_report(report_data, str(test_user.id))

        # Get PDF reports
        filter_data = ReportFilter(format=ReportFormat.PDF)
        results = await reporting_service.get_reports(
            user_id=str(test_user.id),
            filters=filter_data
        )

        assert all(r.format == ReportFormat.PDF for r in results)

    async def test_get_reports_by_status(
        self,
        reporting_service: ReportingService,
        test_user: User,
        test_optimization_job: OptimizationJob
    ):
        """Test filtering reports by status."""
        # Create pending report
        report_data = ReportCreate(
            report_name="Pending Report",
            report_format=ReportFormat.PDF,
            data_source_id=str(test_optimization_job.id),
            data_source_type="optimization_job"
        )
        await reporting_service.create_report(report_data, str(test_user.id))

        # Get pending reports
        filter_data = ReportFilter(status=ReportStatus.PENDING)
        results = await reporting_service.get_reports(
            user_id=str(test_user.id),
            filters=filter_data
        )

        assert all(r.status == ReportStatus.PENDING for r in results)

    # === REPORT DELETION TESTS ===

    async def test_delete_report(
        self,
        reporting_service: ReportingService,
        test_user: User,
        test_optimization_job: OptimizationJob
    ):
        """Test deleting report."""
        # Create report
        report_data = ReportCreate(
            report_name="Delete Test Report",
            report_format=ReportFormat.PDF,
            data_source_id=str(test_optimization_job.id),
            data_source_type="optimization_job"
        )
        report = await reporting_service.create_report(report_data, str(test_user.id))

        # Delete report
        success = await reporting_service.delete_report(str(report.id))

        assert success is True

        # Verify deleted
        deleted_report = await reporting_service.get_report(str(report.id))
        assert deleted_report is None or deleted_report.is_deleted is True

    # === TEMPLATE TESTS ===

    async def test_create_report_template(
        self,
        reporting_service: ReportingService,
        test_user: User
    ):
        """Test creating report template."""
        template_data = ReportTemplateCreate(
            name="New Test Template",
            description="New template for testing",
            category="optimization",
            format=ReportFormat.PDF,
            template_config={
                "sections": ["executive_summary", "technical_details"],
                "theme": "professional"
            }
        )

        result = await reporting_service.create_template(
            template_data,
            str(test_user.id)
        )

        assert result is not None
        assert result.name == "New Test Template"
        assert result.category == "optimization"
        assert result.created_by_id == str(test_user.id)

    async def test_get_template_by_id(
        self,
        reporting_service: ReportingService,
        test_report_template: ReportTemplate
    ):
        """Test getting template by ID."""
        result = await reporting_service.get_template(str(test_report_template.id))

        assert result is not None
        assert result.id == test_report_template.id
        assert result.name == test_report_template.name

    async def test_get_templates_by_category(
        self,
        reporting_service: ReportingService,
        test_user: User
    ):
        """Test getting templates by category."""
        # Create templates in different categories
        for category in ["optimization", "comparison"]:
            template_data = ReportTemplateCreate(
                name=f"Template {category}",
                category=category,
                format=ReportFormat.PDF,
                template_config={}
            )
            await reporting_service.create_template(template_data, str(test_user.id))

        # Get optimization templates
        results = await reporting_service.get_templates(
            category="optimization"
        )

        assert all(t.category == "optimization" for t in results)

    async def test_get_default_templates(
        self,
        reporting_service: ReportingService,
        test_db: AsyncSession,
        test_user: User
    ):
        """Test getting default templates."""
        # Create default template
        default_template = ReportTemplate(
            name="Default Template",
            category="optimization",
            format=ReportFormat.PDF,
            template_config={},
            created_by_id=str(test_user.id),
            is_default=True
        )
        test_db.add(default_template)
        await test_db.commit()

        # Get default templates
        results = await reporting_service.get_default_templates()

        assert len(results) >= 1
        assert all(t.is_default is True for t in results)

    async def test_update_template(
        self,
        reporting_service: ReportingService,
        test_report_template: ReportTemplate,
        test_user: User
    ):
        """Test updating report template."""
        update_data = {
            "description": "Updated template description",
            "template_config": {
                "sections": ["summary", "detailed_analysis", "recommendations"]
            }
        }

        result = await reporting_service.update_template(
            str(test_report_template.id),
            update_data,
            str(test_user.id)
        )

        assert result is not None
        assert result.description == update_data["description"]

    async def test_delete_template(
        self,
        reporting_service: ReportingService,
        test_report_template: ReportTemplate
    ):
        """Test deleting template."""
        success = await reporting_service.delete_template(
            str(test_report_template.id)
        )

        assert success is True

        # Verify deleted (soft delete - is_active = False)
        deleted_template = await reporting_service.get_template(
            str(test_report_template.id)
        )
        assert deleted_template is not None
        assert deleted_template.is_active is False

    # === REPORT CONTENT TESTS ===

    async def test_prepare_report_data_optimization(
        self,
        reporting_service: ReportingService,
        test_optimization_job: OptimizationJob
    ):
        """Test preparing data for optimization report."""
        report_data = await reporting_service.prepare_report_data(
            data_source_id=str(test_optimization_job.id),
            data_source_type="optimization_job"
        )

        assert report_data is not None
        assert "job_info" in report_data
        assert "scenario_info" in report_data or "results" in report_data

    async def test_prepare_report_data_comparison(
        self,
        reporting_service: ReportingService,
        test_scenario: OptimizationScenario,
        test_optimization_job: OptimizationJob
    ):
        """Test preparing data for comparison report."""
        # Create second scenario for comparison
        report_data = await reporting_service.prepare_comparison_data(
            scenario_ids=[str(test_scenario.id)]
        )

        assert report_data is not None
        assert "scenarios" in report_data

    # === STATISTICS TESTS ===

    async def test_get_report_statistics(
        self,
        reporting_service: ReportingService,
        test_user: User,
        test_optimization_job: OptimizationJob
    ):
        """Test getting report statistics."""
        # Create multiple reports
        for i in range(3):
            report_data = ReportCreate(
                report_name=f"Stats Report {i}",
                report_format=ReportFormat.PDF if i % 2 == 0 else ReportFormat.EXCEL,
                data_source_id=str(test_optimization_job.id),
                data_source_type="optimization_job"
            )
            await reporting_service.create_report(report_data, str(test_user.id))

        # Get statistics
        stats = await reporting_service.get_report_statistics(str(test_user.id))

        assert stats is not None
        assert "total_reports" in stats
        assert "by_format" in stats
        assert "by_status" in stats
        assert stats["total_reports"] >= 3

    # === DOWNLOAD & SHARING TESTS ===

    async def test_get_report_download_url(
        self,
        reporting_service: ReportingService,
        test_user: User,
        test_optimization_job: OptimizationJob
    ):
        """Test getting report download URL."""
        # Create and generate report
        report_data = ReportCreate(
            report_name="Download Test",
            report_format=ReportFormat.PDF,
            data_source_id=str(test_optimization_job.id),
            data_source_type="optimization_job"
        )
        report = await reporting_service.create_report(report_data, str(test_user.id))

        # Mock file path
        report.file_path = "/reports/test_report.pdf"
        await reporting_service.db.commit()

        # Get download URL
        url = await reporting_service.get_download_url(str(report.id))

        assert url is not None
        assert isinstance(url, str)

    async def test_generate_shareable_link(
        self,
        reporting_service: ReportingService,
        test_user: User,
        test_optimization_job: OptimizationJob
    ):
        """Test generating shareable link for report."""
        # Create report
        report_data = ReportCreate(
            report_name="Share Test",
            report_format=ReportFormat.PDF,
            data_source_id=str(test_optimization_job.id),
            data_source_type="optimization_job"
        )
        report = await reporting_service.create_report(report_data, str(test_user.id))

        # Generate shareable link
        link = await reporting_service.generate_share_link(
            str(report.id),
            expiry_hours=24
        )

        assert link is not None
        assert isinstance(link, str)

    # === ERROR HANDLING TESTS ===

    async def test_create_report_invalid_data_source(
        self,
        reporting_service: ReportingService,
        test_user: User
    ):
        """Test creating report with invalid data source."""
        report_data = ReportCreate(
            report_name="Invalid Source",
            report_format=ReportFormat.PDF,
            data_source_id=str(uuid4()),  # Non-existent
            data_source_type="optimization_job"
        )

        with pytest.raises(ValueError, match="Data source .* not found"):
            await reporting_service.create_report(report_data, str(test_user.id))

    async def test_generate_report_already_completed(
        self,
        reporting_service: ReportingService,
        test_user: User,
        test_optimization_job: OptimizationJob,
        test_db: AsyncSession
    ):
        """Test generating already completed report."""
        # Create completed report
        report_data = ReportCreate(
            report_name="Already Complete",
            report_format=ReportFormat.PDF,
            data_source_id=str(test_optimization_job.id),
            data_source_type="optimization_job"
        )
        report = await reporting_service.create_report(report_data, str(test_user.id))

        # Mark as completed
        report.status = ReportStatus.COMPLETED
        report.file_path = "/reports/existing.pdf"
        await test_db.commit()

        # Try to generate again
        file_path = await reporting_service.generate_report(str(report.id))

        # Should return existing file path
        assert file_path == "/reports/existing.pdf"
