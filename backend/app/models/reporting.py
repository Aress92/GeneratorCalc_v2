"""
Reporting models for system performance and analytics.

Modele raportowania dla wydajności systemu i analiz.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, Integer, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR

from app.core.database import Base


class ReportType(str, Enum):
    """Types of reports."""
    SYSTEM_PERFORMANCE = "system_performance"
    OPTIMIZATION_SUMMARY = "optimization_summary"
    USER_ACTIVITY = "user_activity"
    IMPORT_ANALYTICS = "import_analytics"
    FUEL_SAVINGS = "fuel_savings"
    ENVIRONMENTAL_IMPACT = "environmental_impact"
    FINANCIAL_ANALYSIS = "financial_analysis"
    TECHNICAL_METRICS = "technical_metrics"
    COMPARATIVE_ANALYSIS = "comparative_analysis"
    CUSTOM = "custom"


class ReportStatus(str, Enum):
    """Report generation status."""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    SCHEDULED = "scheduled"


class ReportFormat(str, Enum):
    """Report export formats."""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    HTML = "html"


class ReportFrequency(str, Enum):
    """Report generation frequency."""
    ON_DEMAND = "on_demand"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"


class Report(Base):
    """Main report model."""

    __tablename__ = "reports"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)

    # Report metadata
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    report_type = Column(String(50), nullable=False)

    # Configuration
    report_config = Column(JSON, nullable=False)  # Report parameters and filters
    date_range = Column(JSON, nullable=True)      # Date range filters
    filters = Column(JSON, nullable=True)         # Additional filters

    # Generation settings
    format = Column(String(20), nullable=False, default=ReportFormat.PDF)
    frequency = Column(String(20), nullable=False, default=ReportFrequency.ON_DEMAND)

    # Status and progress
    status = Column(String(20), nullable=False, default=ReportStatus.PENDING)
    progress_percentage = Column(Float, default=0.0)

    # Generation tracking
    generated_at = Column(DateTime, nullable=True)
    generation_time_seconds = Column(Float, nullable=True)
    file_size_bytes = Column(Integer, nullable=True)

    # File storage
    file_path = Column(String(500), nullable=True)
    download_url = Column(String(500), nullable=True)
    expires_at = Column(DateTime, nullable=True)

    # Error handling
    error_message = Column(Text, nullable=True)
    error_traceback = Column(Text, nullable=True)

    # Scheduling
    is_scheduled = Column(Boolean, default=False)
    next_generation_at = Column(DateTime, nullable=True)
    last_generation_at = Column(DateTime, nullable=True)

    # Access control
    is_public = Column(Boolean, default=False)
    shared_with_users = Column(JSON, default=list)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User")
    report_data = relationship("ReportData", back_populates="report")
    report_exports = relationship("ReportExport", back_populates="report")


class ReportData(Base):
    """Report data and metrics."""

    __tablename__ = "report_data"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = Column(CHAR(36), ForeignKey("reports.id"), nullable=False)

    # Data section
    section_name = Column(String(100), nullable=False)  # e.g., "optimization_summary"
    section_order = Column(Integer, nullable=False, default=0)

    # Raw data
    raw_data = Column(JSON, nullable=False)
    aggregated_data = Column(JSON, nullable=True)

    # Visualization data
    chart_config = Column(JSON, nullable=True)
    chart_data = Column(JSON, nullable=True)

    # Metadata
    data_source = Column(String(100), nullable=True)  # Source table/service
    calculation_method = Column(String(100), nullable=True)

    # Quality metrics
    data_completeness = Column(Float, nullable=True)  # 0-1 score
    data_freshness_hours = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    report = relationship("Report", back_populates="report_data")


class ReportExport(Base):
    """Report export history and files."""

    __tablename__ = "report_exports"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = Column(CHAR(36), ForeignKey("reports.id"), nullable=False)
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)

    # Export details
    export_format = Column(String(20), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)

    # Export metadata
    export_config = Column(JSON, nullable=True)  # Export-specific settings
    generation_time_seconds = Column(Float, nullable=True)

    # Access tracking
    download_count = Column(Integer, default=0)
    last_downloaded_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    # Status
    is_available = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    report = relationship("Report", back_populates="report_exports")
    user = relationship("User")


class ReportTemplate(Base):
    """Pre-configured report templates."""

    __tablename__ = "report_templates"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_by_user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=True)

    # Template metadata
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)

    # Template configuration
    template_config = Column(JSON, nullable=False)
    default_filters = Column(JSON, nullable=True)

    # Usage statistics
    usage_count = Column(Integer, default=0)
    rating_average = Column(Float, nullable=True)
    rating_count = Column(Integer, default=0)

    # Status
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    is_system = Column(Boolean, default=False)  # System-provided templates

    # Version control
    version = Column(String(20), default="1.0")
    parent_template_id = Column(CHAR(36), ForeignKey("report_templates.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    created_by = relationship("User")
    parent_template = relationship("ReportTemplate", remote_side=[id])
    # TODO: Add template_id column to Report model for this relationship
    # generated_reports = relationship("Report", foreign_keys="Report.template_id")


class ReportSchedule(Base):
    """Scheduled report generation."""

    __tablename__ = "report_schedules"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    template_id = Column(CHAR(36), ForeignKey("report_templates.id"), nullable=True)

    # Schedule metadata
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Schedule configuration
    frequency = Column(String(20), nullable=False)
    cron_expression = Column(String(100), nullable=True)  # For custom schedules
    timezone = Column(String(50), default="UTC")

    # Report configuration
    report_config = Column(JSON, nullable=False)
    email_recipients = Column(JSON, default=list)

    # Status tracking
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    last_success_at = Column(DateTime, nullable=True)
    failure_count = Column(Integer, default=0)

    # Limits
    max_failures = Column(Integer, default=3)
    retention_days = Column(Integer, default=30)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User")
    template = relationship("ReportTemplate")


class SystemMetrics(Base):
    """System performance metrics for reporting."""

    __tablename__ = "system_metrics"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Metric metadata
    metric_name = Column(String(100), nullable=False)
    metric_category = Column(String(50), nullable=False)  # performance, usage, business

    # Metric data
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20), nullable=True)

    # Additional context
    dimensions = Column(JSON, nullable=True)  # Metric dimensions/tags

    # Time information
    measured_at = Column(DateTime, nullable=False)
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)

    # Aggregation info
    aggregation_type = Column(String(20), nullable=True)  # sum, avg, max, min, count
    sample_count = Column(Integer, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Indexes for efficient querying
    __table_args__ = (
        {"mysql_engine": "InnoDB"},
    )