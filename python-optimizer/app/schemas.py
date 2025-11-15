"""
Pydantic schemas for optimizer API input/output validation.
Schematy Pydantic dla walidacji wejścia/wyjścia API optymalizatora.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class DesignVariables(BaseModel):
    """Design variables for optimization."""
    checker_height: Optional[float] = Field(None, description="Checker height in meters")
    checker_spacing: Optional[float] = Field(None, description="Checker spacing in meters")
    wall_thickness: Optional[float] = Field(None, description="Wall thickness in meters")
    thermal_conductivity: Optional[float] = Field(None, description="Thermal conductivity in W/(m·K)")
    specific_heat: Optional[float] = Field(None, description="Specific heat in J/(kg·K)")
    density: Optional[float] = Field(None, description="Density in kg/m³")


class BoundsConfig(BaseModel):
    """Bounds configuration for design variables."""
    min: float = Field(..., description="Minimum value")
    max: float = Field(..., description="Maximum value")


class GeometryConfig(BaseModel):
    """Geometry configuration."""
    length: Optional[float] = Field(10.0, description="Regenerator length in meters")
    width: Optional[float] = Field(8.0, description="Regenerator width in meters")


class ThermalConfig(BaseModel):
    """Thermal configuration."""
    gas_temp_inlet: Optional[float] = Field(1600, description="Inlet gas temperature in °C")
    gas_temp_outlet: Optional[float] = Field(600, description="Outlet gas temperature in °C")


class FlowConfig(BaseModel):
    """Flow configuration."""
    mass_flow_rate: Optional[float] = Field(50, description="Mass flow rate in kg/s")
    cycle_time: Optional[float] = Field(1200, description="Cycle time in seconds")


class RegeneratorConfiguration(BaseModel):
    """Complete regenerator configuration."""
    geometry_config: Optional[GeometryConfig] = Field(default_factory=GeometryConfig)
    thermal_config: Optional[ThermalConfig] = Field(default_factory=ThermalConfig)
    flow_config: Optional[FlowConfig] = Field(default_factory=FlowConfig)
    materials_config: Optional[Dict[str, Any]] = Field(default_factory=dict)


class OptimizationConstraints(BaseModel):
    """Optimization constraints."""
    max_pressure_drop: Optional[float] = Field(2000, description="Maximum pressure drop in Pa")
    min_thermal_efficiency: Optional[float] = Field(0.2, description="Minimum thermal efficiency (0-1)")
    min_heat_transfer_coefficient: Optional[float] = Field(50, description="Minimum HTC in W/(m²·K)")


class OptimizationRequest(BaseModel):
    """Request for optimization."""
    configuration: RegeneratorConfiguration = Field(..., description="Regenerator configuration")
    design_variables: Dict[str, Any] = Field(..., description="Design variables to optimize")
    bounds: Dict[str, BoundsConfig] = Field(..., description="Bounds for each design variable")
    initial_values: Optional[Dict[str, float]] = Field(None, description="Initial guess for design variables")
    objective: str = Field("maximize_efficiency", description="Optimization objective")
    algorithm: str = Field("SLSQP", description="Optimization algorithm")
    max_iterations: int = Field(100, description="Maximum iterations")
    tolerance: float = Field(1e-6, description="Convergence tolerance")
    constraints: Optional[OptimizationConstraints] = Field(default_factory=OptimizationConstraints)

    class Config:
        json_schema_extra = {
            "example": {
                "configuration": {
                    "geometry_config": {"length": 10.0, "width": 8.0},
                    "thermal_config": {"gas_temp_inlet": 1600, "gas_temp_outlet": 600},
                    "flow_config": {"mass_flow_rate": 50, "cycle_time": 1200}
                },
                "design_variables": {
                    "checker_height": {},
                    "checker_spacing": {},
                    "wall_thickness": {}
                },
                "bounds": {
                    "checker_height": {"min": 0.3, "max": 2.0},
                    "checker_spacing": {"min": 0.05, "max": 0.3},
                    "wall_thickness": {"min": 0.2, "max": 0.8}
                },
                "initial_values": {
                    "checker_height": 0.5,
                    "checker_spacing": 0.1,
                    "wall_thickness": 0.3
                },
                "objective": "maximize_efficiency",
                "algorithm": "SLSQP",
                "max_iterations": 100,
                "tolerance": 1e-6
            }
        }


class PerformanceMetrics(BaseModel):
    """Performance metrics from physics calculations."""
    thermal_efficiency: float
    heat_transfer_rate: float
    pressure_drop: float
    ntu_value: float
    effectiveness: float
    heat_transfer_coefficient: float
    surface_area: float
    wall_heat_loss: float
    reynolds_number: float
    nusselt_number: float


class OptimizationResult(BaseModel):
    """Result of optimization."""
    success: bool = Field(..., description="Whether optimization succeeded")
    message: str = Field(..., description="Status message")
    iterations: int = Field(..., description="Number of iterations performed")
    final_objective_value: float = Field(..., description="Final objective function value")
    optimized_design_variables: Dict[str, float] = Field(..., description="Optimized design variables")
    performance_metrics: PerformanceMetrics = Field(..., description="Final performance metrics")
    convergence_info: Dict[str, Any] = Field(..., description="Convergence information")
    constraints_satisfied: bool = Field(..., description="Whether all constraints are satisfied")
    constraint_violations: Optional[Dict[str, float]] = Field(None, description="Constraint violations if any")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    scipy_available: bool = Field(..., description="Whether SciPy is available")


class ErrorResponse(BaseModel):
    """Error response."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
