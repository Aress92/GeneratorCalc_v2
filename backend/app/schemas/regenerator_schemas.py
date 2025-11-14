"""
Pydantic schemas for regenerator configuration system.

Schematy Pydantic dla systemu konfiguracji regeneratorów.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict

from app.models.regenerator import RegeneratorType, ConfigurationStatus


# Base schemas for common fields
class TimestampMixin:
    """Mixin for timestamp fields."""
    created_at: datetime
    updated_at: datetime


class MaterialProperties(BaseModel):
    """Material properties schema."""
    density: Optional[float] = Field(None, description="Density in kg/m³")
    thermal_conductivity: Optional[float] = Field(None, description="Thermal conductivity in W/(m·K)")
    specific_heat: Optional[float] = Field(None, description="Specific heat in kJ/(kg·K)")
    max_temperature: Optional[float] = Field(None, description="Maximum temperature in °C")
    porosity: Optional[float] = Field(None, ge=0, le=100, description="Porosity percentage")
    surface_area: Optional[float] = Field(None, description="Surface area in m²/m³")
    thermal_expansion: Optional[float] = Field(None, description="Thermal expansion coefficient")
    compressive_strength: Optional[float] = Field(None, description="Compressive strength in MPa")
    thermal_shock_resistance: Optional[str] = Field(None, description="Thermal shock resistance rating")


# Material schemas
class MaterialCreate(BaseModel):
    """Create material request."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    material_code: Optional[str] = None
    material_type: str = Field(..., description="refractory, insulation, checker, etc.")
    category: Optional[str] = None
    application: Optional[str] = None
    properties: MaterialProperties
    chemical_composition: Optional[Dict[str, float]] = None
    cost_per_unit: Optional[float] = None
    cost_unit: Optional[str] = None
    availability: Optional[str] = None

    @field_validator('material_type')
    @classmethod
    def validate_material_type(cls, v):
        """Validate material type."""
        allowed_types = ['refractory', 'insulation', 'checker', 'structural', 'sealing', 'other']
        if v.lower() not in allowed_types:
            raise ValueError(f'Material type must be one of: {", ".join(allowed_types)}')
        return v.lower()


class MaterialUpdate(BaseModel):
    """Update material request."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    material_code: Optional[str] = None
    material_type: Optional[str] = None
    category: Optional[str] = None
    application: Optional[str] = None
    properties: Optional[MaterialProperties] = None
    chemical_composition: Optional[Dict[str, float]] = None
    cost_per_unit: Optional[float] = None
    cost_unit: Optional[str] = None
    availability: Optional[str] = None
    is_active: Optional[bool] = None


class MaterialResponse(BaseModel, TimestampMixin):
    """Material response schema."""
    id: str
    name: str
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    material_code: Optional[str] = None
    material_type: str
    category: Optional[str] = None
    application: Optional[str] = None
    properties: MaterialProperties
    chemical_composition: Optional[Dict[str, float]] = None
    cost_per_unit: Optional[float] = None
    cost_unit: Optional[str] = None
    availability: Optional[str] = None
    version: str
    approval_status: str
    is_active: bool
    is_standard: bool
    created_by_user_id: Optional[str] = None
    approved_by_user_id: Optional[str] = None
    approved_at: Optional[datetime] = None


# Geometry schemas
class GeometryData(BaseModel):
    """3D geometry data structure."""
    vertices: List[List[float]] = Field(..., description="3D vertices as [x, y, z] coordinates")
    faces: List[List[int]] = Field(..., description="Face indices referencing vertices")
    normals: Optional[List[List[float]]] = Field(None, description="Face normals")
    uvs: Optional[List[List[float]]] = Field(None, description="UV coordinates for texturing")


class TransformationMatrix(BaseModel):
    """3D transformation matrix."""
    position: List[float] = Field([0, 0, 0], description="Position [x, y, z]")
    rotation: List[float] = Field([0, 0, 0], description="Rotation [x, y, z] in radians")
    scale: List[float] = Field([1, 1, 1], description="Scale [x, y, z]")


class GeometryComponentCreate(BaseModel):
    """Create geometry component request."""
    component_name: str = Field(..., min_length=1, max_length=255)
    component_type: str = Field(..., description="checker, wall, insulation, etc.")
    parent_component_id: Optional[str] = None
    geometry_data: GeometryData
    transformation_matrix: Optional[TransformationMatrix] = None
    material_id: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    opacity: float = Field(1.0, ge=0.0, le=1.0)
    is_visible: bool = True


class GeometryComponentResponse(BaseModel, TimestampMixin):
    """Geometry component response."""
    id: str
    configuration_id: str
    component_name: str
    component_type: str
    parent_component_id: Optional[str] = None
    geometry_data: GeometryData
    transformation_matrix: Optional[TransformationMatrix] = None
    material_id: Optional[str] = None
    volume: Optional[float] = None
    surface_area: Optional[float] = None
    mass: Optional[float] = None
    color: Optional[str] = None
    opacity: float
    is_visible: bool


# Configuration schemas
class GeometryConfig(BaseModel):
    """Geometry configuration step."""
    length: Optional[float] = Field(None, gt=0, description="Length in meters")
    width: Optional[float] = Field(None, gt=0, description="Width in meters")
    height: Optional[float] = Field(None, gt=0, description="Height in meters")
    wall_thickness: Optional[float] = Field(None, gt=0, description="Wall thickness in meters")
    checker_height: Optional[float] = Field(None, gt=0, description="Checker pack height in meters")
    checker_pattern: Optional[str] = Field(None, description="Checker arrangement pattern")
    flue_width: Optional[float] = Field(None, gt=0, description="Flue width in meters")
    wall_width: Optional[float] = Field(None, gt=0, description="Wall width in meters")

    # Additional fields that might be in existing data
    inlet_area: Optional[float] = Field(None, description="Inlet area in m²")
    outlet_area: Optional[float] = Field(None, description="Outlet area in m²")


class ThermalConfig(BaseModel):
    """Thermal configuration step."""
    design_temperature: Optional[float] = Field(None, description="Design temperature in °C")
    max_temperature: Optional[float] = Field(None, description="Maximum temperature in °C")
    operating_temperature: Optional[float] = Field(None, description="Normal operating temperature in °C")
    temperature_gradient: Optional[float] = Field(None, description="Temperature gradient in °C/m")
    thermal_cycling: bool = Field(False, description="Subject to thermal cycling")
    heating_rate: Optional[float] = Field(None, description="Heating rate in °C/min")
    cooling_rate: Optional[float] = Field(None, description="Cooling rate in °C/min")

    # Additional fields from existing data
    ambient_temp: Optional[float] = Field(None, description="Ambient temperature in °C")
    gas_temp_inlet: Optional[float] = Field(None, description="Gas inlet temperature in °C")
    gas_temp_outlet: Optional[float] = Field(None, description="Gas outlet temperature in °C")
    target_efficiency: Optional[float] = Field(None, description="Target thermal efficiency")


class FlowConfig(BaseModel):
    """Flow configuration step."""
    air_flow_rate: Optional[float] = Field(None, gt=0, description="Air flow rate in m³/h")
    gas_flow_rate: Optional[float] = Field(None, gt=0, description="Gas flow rate in m³/h")
    working_pressure: Optional[float] = Field(None, description="Working pressure in Pa")
    max_pressure_drop: Optional[float] = Field(None, gt=0, description="Maximum pressure drop in Pa")
    flow_direction: Optional[str] = Field(None, description="up-flow, down-flow, cross-flow")

    # Additional fields from existing data
    cycle_time: Optional[float] = Field(None, description="Cycle time in seconds")
    mass_flow_rate: Optional[float] = Field(None, description="Mass flow rate in kg/s")
    pressure_inlet: Optional[float] = Field(None, description="Inlet pressure in Pa")
    pressure_outlet: Optional[float] = Field(None, description="Outlet pressure in Pa")
    flow_distribution: Optional[str] = Field(None, description="uniform, parabolic, custom")


class MaterialsConfig(BaseModel):
    """Materials configuration step."""
    checker_material_id: Optional[str] = Field(None, description="Checker material ID")
    insulation_material_id: Optional[str] = None
    refractory_material_id: Optional[str] = None
    structural_material_id: Optional[str] = None
    sealing_material_id: Optional[str] = None
    material_assignments: Dict[str, str] = Field(default_factory=dict, description="Component to material mapping")

    # Additional fields from existing data
    density: Optional[float] = Field(None, description="Material density")
    specific_heat: Optional[float] = Field(None, description="Specific heat")
    thermal_conductivity: Optional[float] = Field(None, description="Thermal conductivity")
    wall_material: Optional[str] = Field(None, description="Wall material name")
    checker_material: Optional[str] = Field(None, description="Checker material name")


class ConstraintsConfig(BaseModel):
    """Constraints configuration step."""
    max_thermal_stress: Optional[float] = Field(None, description="Maximum thermal stress in MPa")
    max_pressure_drop: Optional[float] = Field(None, gt=0, description="Maximum allowable pressure drop in Pa")
    min_efficiency: Optional[float] = Field(None, ge=0, le=100, description="Minimum thermal efficiency %")
    safety_factor: Optional[float] = Field(2.0, gt=1.0, description="Safety factor")

    # Additional fields from existing data (may have different structure)
    min_heat_transfer_coefficient: Optional[float] = Field(None, description="Minimum heat transfer coefficient")
    code_compliance: List[str] = Field(default_factory=list, description="Applicable codes and standards")
    environmental_limits: Dict[str, float] = Field(default_factory=dict)


class VisualizationConfig(BaseModel):
    """Visualization configuration step."""
    show_temperature_gradient: bool = True
    show_flow_arrows: bool = True
    show_materials: bool = True
    show_stress_analysis: bool = False
    camera_position: List[float] = Field([10, 10, 10], description="Default camera position")
    render_quality: str = Field("medium", description="low, medium, high")
    enable_animations: bool = True


# Main configuration schemas
class RegeneratorConfigurationCreate(BaseModel):
    """Create regenerator configuration request."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    regenerator_type: RegeneratorType
    based_on_template_id: Optional[str] = None

    # Optional initial configuration data
    geometry_config: Optional[GeometryConfig] = None
    thermal_config: Optional[ThermalConfig] = None
    flow_config: Optional[FlowConfig] = None
    materials_config: Optional[MaterialsConfig] = None
    constraints_config: Optional[ConstraintsConfig] = None
    visualization_config: Optional[VisualizationConfig] = None


class RegeneratorConfigurationUpdate(BaseModel):
    """Update regenerator configuration request."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    current_step: Optional[int] = Field(None, ge=1, le=7)
    completed_steps: Optional[List[int]] = None

    # Configuration steps
    geometry_config: Optional[GeometryConfig] = None
    thermal_config: Optional[ThermalConfig] = None
    flow_config: Optional[FlowConfig] = None
    materials_config: Optional[MaterialsConfig] = None
    constraints_config: Optional[ConstraintsConfig] = None
    visualization_config: Optional[VisualizationConfig] = None


class RegeneratorConfigurationResponse(BaseModel, TimestampMixin):
    """Regenerator configuration response."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    regenerator_type: RegeneratorType
    configuration_version: str
    status: ConfigurationStatus

    # Wizard progress
    current_step: int
    total_steps: int
    completed_steps: List[int]

    # Configuration data
    geometry_config: Optional[GeometryConfig] = None
    thermal_config: Optional[ThermalConfig] = None
    flow_config: Optional[FlowConfig] = None
    materials_config: Optional[MaterialsConfig] = None
    constraints_config: Optional[ConstraintsConfig] = None
    visualization_config: Optional[VisualizationConfig] = None

    # 3D model data
    model_geometry: Optional[Dict[str, Any]] = None
    model_materials: Optional[Dict[str, Any]] = None

    # Validation
    is_validated: bool
    validation_score: Optional[float] = None
    validation_errors: List[Dict[str, Any]]
    validation_warnings: List[Dict[str, Any]]

    # Template info
    based_on_template_id: Optional[str] = None
    is_template: bool

    # Completion
    completed_at: Optional[datetime] = None


# Template schemas
class ConfigurationTemplateCreate(BaseModel):
    """Create configuration template request."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    regenerator_type: RegeneratorType
    category: Optional[str] = None
    template_config: Dict[str, Any] = Field(..., description="Template configuration structure")
    default_values: Optional[Dict[str, Any]] = None
    required_fields: Optional[List[str]] = None
    is_public: bool = True


class ConfigurationTemplateResponse(BaseModel, TimestampMixin):
    """Configuration template response."""
    id: str
    name: str
    description: Optional[str] = None
    regenerator_type: RegeneratorType
    category: Optional[str] = None
    template_config: Dict[str, Any]
    default_values: Optional[Dict[str, Any]] = None
    required_fields: Optional[List[str]] = None
    usage_count: int
    is_active: bool
    is_public: bool
    created_by_user_id: Optional[str] = None


# Wizard schemas
class WizardStepValidation(BaseModel):
    """Wizard step validation result."""
    step_number: int
    step_name: str
    is_valid: bool
    is_complete: bool
    errors: List[Dict[str, str]]
    warnings: List[Dict[str, str]]
    completion_percentage: float = Field(..., ge=0, le=100)


class WizardProgress(BaseModel):
    """Overall wizard progress."""
    configuration_id: str
    current_step: int
    total_steps: int
    completed_steps: List[int]
    overall_completion: float = Field(..., ge=0, le=100)
    next_available_steps: List[int]
    step_validations: List[WizardStepValidation]
    can_proceed_to_next: bool
    can_complete_configuration: bool


# Constraint schemas
class ConfigurationConstraintCreate(BaseModel):
    """Create configuration constraint request."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    constraint_type: str = Field(..., description="geometric, thermal, flow, material")
    regenerator_type: Optional[RegeneratorType] = None
    constraint_config: Dict[str, Any] = Field(..., description="Constraint parameters")
    severity: str = Field(..., description="error, warning, info")
    rule_expression: Optional[str] = None
    validation_function: Optional[str] = None


class ConfigurationConstraintResponse(BaseModel, TimestampMixin):
    """Configuration constraint response."""
    id: str
    name: str
    description: Optional[str] = None
    constraint_type: str
    regenerator_type: Optional[RegeneratorType] = None
    constraint_config: Dict[str, Any]
    severity: str
    rule_expression: Optional[str] = None
    validation_function: Optional[str] = None
    is_active: bool


# Search and filter schemas
class MaterialFilter(BaseModel):
    """Material search and filter parameters."""
    search: Optional[str] = None
    material_type: Optional[str] = None
    category: Optional[str] = None
    application: Optional[str] = None
    manufacturer: Optional[str] = None
    min_max_temperature: Optional[float] = None
    max_max_temperature: Optional[float] = None
    approval_status: Optional[str] = None
    is_active: Optional[bool] = True
    is_standard: Optional[bool] = None


class ConfigurationFilter(BaseModel):
    """Configuration search and filter parameters."""
    search: Optional[str] = None
    regenerator_type: Optional[RegeneratorType] = None
    status: Optional[ConfigurationStatus] = None
    created_by_user_id: Optional[str] = None
    is_template: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None