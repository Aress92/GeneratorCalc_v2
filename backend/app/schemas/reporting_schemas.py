"""
Pydantic schemas for reporting system.

Schematy Pydantic dla systemu raportowania.
"""

from datetime import datetime, date
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator

from app.models.reporting import ReportType, ReportStatus, ReportFormat, ReportFrequency


# Base schemas
class ReportBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    report_type: ReportType
    report_config: Dict[str, Any] = Field(default_factory=dict)
    date_range: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None


class ReportCreate(ReportBase):
    format: ReportFormat = ReportFormat.PDF
    frequency: ReportFrequency = ReportFrequency.ON_DEMAND

    @field_validator('report_config')
    @classmethod
    def validate_report_config(cls, v, info):
        """Validate report configuration based on report type."""
        report_type = info.data.get('report_type')

        if report_type == ReportType.OPTIMIZATION_SUMMARY:
            required_fields = ['scenario_ids', 'metrics']
            for field in required_fields:
                if field not in v:
                    raise ValueError(f"Missing required field '{field}' for optimization summary report")

        elif report_type == ReportType.FUEL_SAVINGS:
            if 'baseline_period' not in v or 'comparison_period' not in v:
                raise ValueError("Fuel savings report requires baseline_period and comparison_period")

        return v


class ReportUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    report_config: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None


class ReportResponse(ReportBase):
    id: str
    user_id: str
    status: ReportStatus
    progress_percentage: float
    format: ReportFormat
    frequency: ReportFrequency
    generated_at: Optional[datetime]
    generation_time_seconds: Optional[float]
    file_size_bytes: Optional[int]
    download_url: Optional[str]
    expires_at: Optional[datetime]
    error_message: Optional[str]
    is_scheduled: bool
    is_public: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReportList(BaseModel):
    reports: List[ReportResponse]
    total_count: int
    page: int
    per_page: int


# Report Data schemas
class ReportDataCreate(BaseModel):
    section_name: str
    section_order: int = 0
    raw_data: Dict[str, Any]
    aggregated_data: Optional[Dict[str, Any]] = None
    chart_config: Optional[Dict[str, Any]] = None
    chart_data: Optional[Dict[str, Any]] = None


class ReportDataResponse(ReportDataCreate):
    id: str
    report_id: str
    data_source: Optional[str]
    calculation_method: Optional[str]
    data_completeness: Optional[float]
    data_freshness_hours: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


# Report Export schemas
class ReportExportRequest(BaseModel):
    export_format: ReportFormat
    export_config: Optional[Dict[str, Any]] = None


class ReportExportResponse(BaseModel):
    id: str
    report_id: str
    export_format: ReportFormat
    file_name: str
    file_size_bytes: int
    download_count: int
    expires_at: Optional[datetime]
    is_available: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Report Template schemas
class ReportTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    template_config: Dict[str, Any]
    default_filters: Optional[Dict[str, Any]] = None
    is_public: bool = False


class ReportTemplateResponse(ReportTemplateCreate):
    id: str
    created_by_user_id: Optional[str]
    usage_count: int
    rating_average: Optional[float]
    rating_count: int
    is_active: bool
    is_system: bool
    version: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReportTemplateList(BaseModel):
    templates: List[ReportTemplateResponse]
    total_count: int
    page: int
    per_page: int


# Report Schedule schemas
class ReportScheduleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    frequency: ReportFrequency
    cron_expression: Optional[str] = None
    timezone: str = "UTC"
    report_config: Dict[str, Any]
    email_recipients: List[str] = Field(default_factory=list)
    template_id: Optional[str] = None

    @field_validator('cron_expression')
    @classmethod
    def validate_cron(cls, v, info):
        """Validate cron expression if provided."""
        if v and info.data.get('frequency') != ReportFrequency.ON_DEMAND:
            # Basic cron validation (5 fields)
            parts = v.split()
            if len(parts) != 5:
                raise ValueError("Cron expression must have 5 fields (minute hour day month weekday)")
        return v


class ReportScheduleResponse(ReportScheduleCreate):
    id: str
    user_id: str
    is_active: bool
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    last_success_at: Optional[datetime]
    failure_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# System Metrics schemas
class SystemMetricCreate(BaseModel):
    metric_name: str
    metric_category: str
    metric_value: float
    metric_unit: Optional[str] = None
    dimensions: Optional[Dict[str, Any]] = None
    measured_at: datetime
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


class SystemMetricResponse(SystemMetricCreate):
    id: str
    aggregation_type: Optional[str]
    sample_count: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# Specialized report schemas
class OptimizationSummaryConfig(BaseModel):
    scenario_ids: List[str]
    metrics: List[str] = ["fuel_savings", "co2_reduction", "thermal_efficiency"]
    include_iterations: bool = False
    include_comparison: bool = True
    group_by: Optional[str] = None  # scenario_type, user, date


class FuelSavingsConfig(BaseModel):
    baseline_period: Dict[str, str]  # start_date, end_date
    comparison_period: Dict[str, str]
    regenerator_ids: Optional[List[str]] = None
    include_economic_analysis: bool = True
    currency: str = "USD"


class SystemPerformanceConfig(BaseModel):
    metrics: List[str] = ["api_response_time", "optimization_success_rate", "user_activity"]
    time_period: Dict[str, str]
    aggregation: str = "daily"  # daily, weekly, monthly
    include_trends: bool = True


class UserActivityConfig(BaseModel):
    user_ids: Optional[List[str]] = None
    activity_types: List[str] = ["login", "import", "optimize", "export"]
    time_period: Dict[str, str]
    include_details: bool = False


# Report generation progress
class ReportProgress(BaseModel):
    report_id: str
    status: ReportStatus
    progress_percentage: float
    current_step: Optional[str] = None
    estimated_completion: Optional[datetime] = None
    steps_completed: int = 0
    total_steps: int = 1


# Dashboard analytics schemas
class DashboardMetrics(BaseModel):
    total_optimizations: int
    active_users: int
    fuel_savings_total: float  # %
    co2_reduction_total: float  # tons
    system_uptime: float  # %
    api_response_time_avg: float  # ms
    optimizations_this_month: int
    success_rate: float  # %


class OptimizationTrends(BaseModel):
    date: date
    optimization_count: int
    success_count: int
    average_fuel_savings: float
    average_runtime_minutes: float


class UserEngagement(BaseModel):
    date: date
    active_users: int
    new_users: int
    total_sessions: int
    average_session_duration: float


class SystemHealth(BaseModel):
    timestamp: datetime
    cpu_usage: float  # %
    memory_usage: float  # %
    disk_usage: float  # %
    active_connections: int
    queue_length: int
    error_rate: float  # %


# Export formats
class PDFExportConfig(BaseModel):
    include_cover_page: bool = True
    include_executive_summary: bool = True
    page_orientation: str = "portrait"  # portrait, landscape
    include_charts: bool = True
    chart_resolution: int = 300  # DPI


class ExcelExportConfig(BaseModel):
    include_raw_data: bool = True
    include_charts: bool = True
    sheet_names: Optional[Dict[str, str]] = None
    formatting: str = "corporate"  # corporate, simple, colorful


# Real-time reporting
class ReportWebhook(BaseModel):
    url: str = Field(..., pattern=r'^https?://')
    events: List[str] = ["report_completed", "report_failed"]
    headers: Optional[Dict[str, str]] = None
    retry_count: int = 3