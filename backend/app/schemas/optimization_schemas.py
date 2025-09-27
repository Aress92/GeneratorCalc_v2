"""
Pydantic schemas for optimization API.

Schematy Pydantic dla API optymalizacji.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum

from pydantic import BaseModel, Field, field_validator

from app.models.optimization import (
    OptimizationStatus, OptimizationObjective, OptimizationAlgorithm,
    ScenarioType
)


class OptimizationObjectiveSchema(str, Enum):
    """Optimization objectives schema."""
    MINIMIZE_FUEL_CONSUMPTION = "minimize_fuel_consumption"
    MINIMIZE_CO2_EMISSIONS = "minimize_co2_emissions"
    MAXIMIZE_EFFICIENCY = "maximize_efficiency"
    MINIMIZE_COST = "minimize_cost"
    MULTI_OBJECTIVE = "multi_objective"


class OptimizationAlgorithmSchema(str, Enum):
    """Optimization algorithms schema."""
    SLSQP = "slsqp"
    GENETIC = "genetic"
    DIFFERENTIAL_EVOLUTION = "differential_evolution"
    PSO = "particle_swarm"
    SIMULATED_ANNEALING = "simulated_annealing"


class ScenarioTypeSchema(str, Enum):
    """Scenario types schema."""
    BASELINE = "baseline"
    GEOMETRY_OPTIMIZATION = "geometry_optimization"
    MATERIAL_OPTIMIZATION = "material_optimization"
    OPERATING_CONDITIONS = "operating_conditions"
    COMPREHENSIVE = "comprehensive"


# Design Variable Schemas
class DesignVariableConfig(BaseModel):
    """Configuration for a single design variable."""
    name: str = Field(..., description="Variable name")
    description: Optional[str] = Field(None, description="Variable description")
    unit: Optional[str] = Field(None, description="Physical unit")
    min_value: float = Field(..., description="Minimum allowed value")
    max_value: float = Field(..., description="Maximum allowed value")
    baseline_value: Optional[float] = Field(None, description="Baseline value for comparison")
    step_size: Optional[float] = Field(None, description="Optimization step size")
    variable_type: str = Field("continuous", description="continuous, discrete, integer")

    @field_validator("max_value")
    @classmethod
    def max_greater_than_min(cls, v, info):
        if info.data.get("min_value") is not None and v <= info.data["min_value"]:
            raise ValueError("max_value must be greater than min_value")
        return v


class OptimizationConstraint(BaseModel):
    """Optimization constraint definition."""
    name: str = Field(..., description="Constraint name")
    constraint_type: str = Field(..., description="equality, inequality")
    expression: Optional[str] = Field(None, description="Mathematical expression")
    function_name: Optional[str] = Field(None, description="Python function name")
    bounds: Optional[Dict[str, float]] = Field(None, description="Lower and upper bounds")
    tolerance: float = Field(1e-6, description="Constraint tolerance")
    is_active: bool = Field(True, description="Whether constraint is active")


# Scenario Schemas
class OptimizationScenarioCreate(BaseModel):
    """Create optimization scenario."""
    name: str = Field(..., min_length=1, max_length=255, description="Scenario name")
    description: Optional[str] = Field(None, max_length=2000, description="Scenario description")
    scenario_type: ScenarioTypeSchema = Field(..., description="Type of optimization scenario")
    base_configuration_id: str = Field(..., description="Base regenerator configuration ID")

    # Optimization setup
    objective: OptimizationObjectiveSchema = Field(..., description="Optimization objective")
    algorithm: OptimizationAlgorithmSchema = Field(OptimizationAlgorithmSchema.SLSQP, description="Algorithm to use")

    # Variables and constraints
    design_variables: Dict[str, DesignVariableConfig] = Field(..., description="Design variables to optimize")
    constraints: Optional[List[OptimizationConstraint]] = Field([], description="Optimization constraints")

    # Algorithm parameters
    max_iterations: int = Field(1000, ge=10, le=10000, description="Maximum iterations")
    max_function_evaluations: int = Field(5000, ge=50, le=50000, description="Maximum function evaluations")
    tolerance: float = Field(1e-6, ge=1e-12, le=1e-2, description="Convergence tolerance")
    max_runtime_minutes: int = Field(120, ge=1, le=720, description="Maximum runtime in minutes")

    # Multi-objective weights
    objective_weights: Optional[Dict[str, float]] = Field(None, description="Weights for multi-objective optimization")


class OptimizationScenarioUpdate(BaseModel):
    """Update optimization scenario."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    scenario_type: Optional[ScenarioTypeSchema] = None

    objective: Optional[OptimizationObjectiveSchema] = None
    algorithm: Optional[OptimizationAlgorithmSchema] = None

    design_variables: Optional[Dict[str, DesignVariableConfig]] = None
    constraints: Optional[List[OptimizationConstraint]] = None

    max_iterations: Optional[int] = Field(None, ge=10, le=10000)
    max_function_evaluations: Optional[int] = Field(None, ge=50, le=50000)
    tolerance: Optional[float] = Field(None, ge=1e-12, le=1e-2)
    max_runtime_minutes: Optional[int] = Field(None, ge=1, le=720)

    objective_weights: Optional[Dict[str, float]] = None
    is_active: Optional[bool] = None


class OptimizationScenarioResponse(BaseModel):
    """Optimization scenario response."""
    id: str
    user_id: str
    name: str
    description: Optional[str]
    scenario_type: ScenarioTypeSchema
    base_configuration_id: str

    objective: OptimizationObjectiveSchema
    algorithm: OptimizationAlgorithmSchema

    design_variables: Dict[str, Any]
    constraints: Optional[List[Dict[str, Any]]] = None

    max_iterations: int
    max_function_evaluations: int
    tolerance: float
    max_runtime_minutes: int

    objective_weights: Optional[Dict[str, float]]

    status: str
    is_active: bool
    is_template: bool

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Job Schemas
class OptimizationJobCreate(BaseModel):
    """Create optimization job."""
    job_name: Optional[str] = Field(None, max_length=255, description="Optional job name")
    initial_values: Optional[Dict[str, float]] = Field({}, description="Initial values for design variables")
    priority: int = Field(1, ge=1, le=5, description="Job priority (1=highest, 5=lowest)")


class OptimizationJobResponse(BaseModel):
    """Optimization job response."""
    id: str
    scenario_id: str
    user_id: str
    job_name: Optional[str]
    celery_task_id: Optional[str]

    status: OptimizationStatus
    current_iteration: int
    current_function_evaluations: int
    progress_percentage: float

    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    estimated_completion_at: Optional[datetime]
    runtime_seconds: Optional[float]

    final_objective_value: Optional[float]
    convergence_achieved: bool

    error_message: Optional[str]
    warning_messages: List[str]

    memory_usage_mb: Optional[float]
    cpu_usage_percentage: Optional[float]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OptimizationProgress(BaseModel):
    """Real-time optimization progress."""
    job_id: str
    status: OptimizationStatus
    current_iteration: int
    max_iterations: int
    progress_percentage: float
    current_objective_value: Optional[float]

    recent_iterations: List[Dict[str, Any]]
    estimated_completion_at: Optional[datetime]
    runtime_seconds: float

    convergence_history: Optional[List[float]] = Field(None, description="History of objective values")
    constraint_violations: Optional[Dict[str, float]] = Field(None, description="Current constraint violations")


# Results Schemas
class PerformanceMetrics(BaseModel):
    """Performance metrics for regenerator."""
    thermal_efficiency: float = Field(..., description="Thermal efficiency (%)")
    heat_transfer_rate: float = Field(..., description="Heat transfer rate (W)")
    pressure_drop: float = Field(..., description="Pressure drop (Pa)")
    ntu_value: float = Field(..., description="Number of Transfer Units")
    effectiveness: float = Field(..., description="Heat exchanger effectiveness")
    heat_transfer_coefficient: float = Field(..., description="Heat transfer coefficient (W/m²K)")
    surface_area: float = Field(..., description="Heat transfer surface area (m²)")
    wall_heat_loss: Optional[float] = Field(None, description="Wall heat loss (W)")


class EconomicAnalysis(BaseModel):
    """Economic analysis results."""
    fuel_savings_percentage: Optional[float] = Field(None, description="Fuel savings (%)")
    co2_reduction_percentage: Optional[float] = Field(None, description="CO2 reduction (%)")
    annual_cost_savings: Optional[float] = Field(None, description="Annual cost savings (€)")
    payback_period_months: Optional[float] = Field(None, description="Payback period (months)")
    capital_cost_estimate: Optional[float] = Field(None, description="Estimated capital cost (€)")
    net_present_value: Optional[float] = Field(None, description="Net present value (€)")


class SensitivityAnalysis(BaseModel):
    """Sensitivity analysis results."""
    variable_sensitivities: Dict[str, float] = Field(..., description="Sensitivity of objective to each variable")
    critical_variables: List[str] = Field(..., description="Most critical variables")
    robustness_score: float = Field(..., description="Solution robustness score (0-1)")
    uncertainty_range: Dict[str, float] = Field(..., description="Uncertainty ranges for key metrics")


class OptimizationResultResponse(BaseModel):
    """Complete optimization result."""
    id: str
    job_id: str

    # Final configuration
    optimized_configuration: Dict[str, Any]
    design_variables_final: Dict[str, float]

    # Objective results
    objective_value: float
    objective_components: Optional[Dict[str, float]]
    constraint_violations: Optional[Dict[str, float]]

    # Performance comparison
    baseline_metrics: PerformanceMetrics
    optimized_metrics: PerformanceMetrics
    improvement_percentages: Dict[str, float]

    # Economic analysis
    economic_analysis: EconomicAnalysis

    # Technical results
    thermal_efficiency: Optional[float]
    pressure_drop: Optional[float]
    heat_transfer_coefficient: Optional[float]
    ntu_value: Optional[float]

    # Geometry results (if applicable)
    optimized_geometry: Optional[Dict[str, Any]]
    volume_changes: Optional[Dict[str, float]]
    surface_area_changes: Optional[Dict[str, float]]

    # Material results (if applicable)
    material_recommendations: Optional[List[Dict[str, Any]]]
    material_cost_impact: Optional[Dict[str, float]]

    # Analysis
    sensitivity_analysis: Optional[SensitivityAnalysis]

    # Quality metrics
    solution_feasibility: Optional[float]
    optimization_confidence: Optional[float]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Template Schemas
class OptimizationTemplateCreate(BaseModel):
    """Create optimization template."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    template_type: ScenarioTypeSchema
    regenerator_type: Optional[str] = Field(None, description="crown, end-port, cross-fired")

    template_config: Dict[str, Any] = Field(..., description="Complete scenario template")
    default_parameters: Optional[Dict[str, Any]] = Field(None, description="Default parameter values")

    is_public: bool = Field(True, description="Whether template is publicly available")


class OptimizationTemplateResponse(BaseModel):
    """Optimization template response."""
    id: str
    name: str
    description: Optional[str]
    template_type: ScenarioTypeSchema
    regenerator_type: Optional[str]

    template_config: Dict[str, Any]
    default_parameters: Optional[Dict[str, Any]]

    usage_count: int
    success_rate: Optional[float]
    average_improvement: Optional[float]

    is_active: bool
    is_public: bool
    is_verified: bool

    created_by_user_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# List Schemas
class OptimizationScenarioList(BaseModel):
    """List of optimization scenarios."""
    scenarios: List[OptimizationScenarioResponse]
    total_count: int
    page: int
    per_page: int


class OptimizationJobList(BaseModel):
    """List of optimization jobs."""
    jobs: List[OptimizationJobResponse]
    total_count: int
    page: int
    per_page: int


class OptimizationTemplateList(BaseModel):
    """List of optimization templates."""
    templates: List[OptimizationTemplateResponse]
    total_count: int
    page: int
    per_page: int


# Status Schemas
class OptimizationJobStatus(BaseModel):
    """Simple job status response."""
    job_id: str
    status: OptimizationStatus
    progress_percentage: float
    current_iteration: int
    estimated_completion_at: Optional[datetime]
    error_message: Optional[str]