"""
Pydantic schemas for import functionality.

Schematy Pydantic dla funkcjonalności importu.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator

from app.models.import_job import ImportStatus, ImportType


class ValidationError(BaseModel):
    """Validation error details."""
    row: int
    column: str
    message: str
    severity: str = Field(..., description="error, warning, info")
    value: Optional[Any] = None


class ColumnMapping(BaseModel):
    """Column mapping configuration."""
    source_column: str
    target_field: str
    data_type: str = Field(..., description="string, float, integer, boolean, date")
    unit: Optional[str] = None
    conversion_factor: Optional[float] = None
    is_required: bool = False


class ImportPreview(BaseModel):
    """Preview of import data before processing."""
    headers: List[str]
    sample_rows: List[List[Any]]
    total_rows: int
    detected_type: Optional[ImportType] = None
    suggested_mapping: List[ColumnMapping] = []
    validation_errors: List[ValidationError] = []


class ImportJobCreate(BaseModel):
    """Create import job request."""
    original_filename: str
    import_type: ImportType
    column_mapping: List[ColumnMapping] = []
    processing_options: Dict[str, Any] = {}


class ImportJobUpdate(BaseModel):
    """Update import job request."""
    column_mapping: Optional[List[ColumnMapping]] = None
    processing_options: Optional[Dict[str, Any]] = None


class ImportJobStatus(BaseModel):
    """Import job status response."""
    id: str
    status: ImportStatus
    total_rows: int
    processed_rows: int
    valid_rows: int
    invalid_rows: int
    progress_percentage: float = Field(..., description="0-100")
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    @field_validator('progress_percentage')
    @classmethod
    def calculate_progress(cls, v, info):
        """Calculate progress percentage."""
        values = info.data
        if values.get('total_rows', 0) > 0:
            return (values.get('processed_rows', 0) / values['total_rows']) * 100
        return 0.0


class ImportJobResponse(BaseModel):
    """Complete import job response."""
    id: str
    user_id: str
    filename: str
    original_filename: str
    file_size: int
    import_type: ImportType
    status: ImportStatus

    total_rows: int
    processed_rows: int
    valid_rows: int
    invalid_rows: int

    validation_errors: List[ValidationError] = []
    validation_warnings: List[ValidationError] = []
    column_mapping: List[ColumnMapping] = []

    metadata_info: Dict[str, Any] = {}
    processing_options: Dict[str, Any] = {}

    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    error_message: Optional[str] = None


class RegeneratorDataCreate(BaseModel):
    """Create regenerator data from import."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    regenerator_type: str = Field(..., description="crown, end-port, cross-fired")

    # Geometric properties (all in metric units)
    length: float = Field(..., gt=0, description="Length in meters")
    width: float = Field(..., gt=0, description="Width in meters")
    height: float = Field(..., gt=0, description="Height in meters")

    # Thermal properties
    design_temperature: float = Field(..., description="Design temperature in Celsius")
    max_temperature: float = Field(..., description="Maximum temperature in Celsius")
    working_pressure: Optional[float] = Field(None, description="Working pressure in Pascal")

    # Flow properties
    air_flow_rate: Optional[float] = Field(None, description="Air flow rate in m3/h")
    gas_flow_rate: Optional[float] = Field(None, description="Gas flow rate in m3/h")
    pressure_drop: Optional[float] = Field(None, description="Pressure drop in Pascal")

    # Material properties
    checker_material: Optional[str] = None
    insulation_material: Optional[str] = None
    refractory_material: Optional[str] = None

    # Performance data
    thermal_efficiency: Optional[float] = Field(None, ge=0, le=100, description="Efficiency percentage")
    heat_recovery_rate: Optional[float] = Field(None, ge=0, le=100, description="Heat recovery percentage")
    fuel_consumption: Optional[float] = Field(None, ge=0, description="Fuel consumption kW or BTU/h")

    @field_validator('max_temperature')
    @classmethod
    def validate_max_temp(cls, v, info):
        """Validate max temperature is higher than design temperature."""
        design_temp = info.data.get('design_temperature')
        if design_temp and v <= design_temp:
            raise ValueError('Maximum temperature must be higher than design temperature')
        return v

    @field_validator('regenerator_type')
    @classmethod
    def validate_regenerator_type(cls, v):
        """Validate regenerator type."""
        allowed_types = ['crown', 'end-port', 'cross-fired']
        if v.lower() not in allowed_types:
            raise ValueError(f'Regenerator type must be one of: {", ".join(allowed_types)}')
        return v.lower()


class RegeneratorDataResponse(BaseModel):
    """Regenerator data response."""
    id: str
    import_job_id: str
    name: str
    description: Optional[str] = None
    regenerator_type: str

    # Geometric properties
    length: float
    width: float
    height: float
    volume: Optional[float] = None

    # Thermal properties
    design_temperature: float
    max_temperature: float
    working_pressure: Optional[float] = None

    # Flow properties
    air_flow_rate: Optional[float] = None
    gas_flow_rate: Optional[float] = None
    pressure_drop: Optional[float] = None

    # Material properties
    checker_material: Optional[str] = None
    insulation_material: Optional[str] = None
    refractory_material: Optional[str] = None

    # Performance data
    thermal_efficiency: Optional[float] = None
    heat_recovery_rate: Optional[float] = None
    fuel_consumption: Optional[float] = None

    # Validation
    is_validated: bool
    validation_score: Optional[float] = None
    validation_notes: Optional[str] = None

    created_at: datetime
    updated_at: datetime


class UnitConversionCreate(BaseModel):
    """Create unit conversion rule."""
    from_unit: str
    to_unit: str
    conversion_factor: float
    conversion_offset: float = 0.0
    unit_type: str
    description: Optional[str] = None


class UnitConversionResponse(BaseModel):
    """Unit conversion response."""
    id: str
    from_unit: str
    to_unit: str
    conversion_factor: float
    conversion_offset: float
    unit_type: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ValidationRuleCreate(BaseModel):
    """Create validation rule."""
    name: str
    description: Optional[str] = None
    import_type: ImportType
    field_name: str
    rule_type: str = Field(..., description="range, regex, required, custom")
    rule_config: Dict[str, Any]
    severity: str = Field(..., description="error, warning, info")


class ValidationRuleResponse(BaseModel):
    """Validation rule response."""
    id: str
    name: str
    description: Optional[str] = None
    import_type: ImportType
    field_name: str
    rule_type: str
    rule_config: Dict[str, Any]
    severity: str
    is_active: bool
    created_at: datetime
    updated_at: datetime