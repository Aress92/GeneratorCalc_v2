"""
Pydantic models for request/response validation.
"""
from typing import Dict, Optional, List, Any
from pydantic import BaseModel, Field


class DesignVariables(BaseModel):
    """Design variables for optimization."""
    checker_height: float = Field(..., ge=0.1, le=5.0, description="Checker brick height in meters")
    checker_spacing: float = Field(..., ge=0.01, le=1.0, description="Spacing between checker bricks in meters")
    wall_thickness: float = Field(..., ge=0.1, le=2.0, description="Wall thickness in meters")
    thermal_conductivity: Optional[float] = Field(2.5, ge=0.1, le=10.0, description="Thermal conductivity W/(m·K)")
    specific_heat: Optional[float] = Field(900, ge=100, le=2000, description="Specific heat J/(kg·K)")
    density: Optional[float] = Field(2300, ge=500, le=5000, description="Density kg/m³")


class BoundsConfig(BaseModel):
    """Bounds for design variables."""
    checker_height: tuple[float, float] = (0.3, 2.0)
    checker_spacing: tuple[float, float] = (0.05, 0.3)
    wall_thickness: tuple[float, float] = (0.2, 0.8)
    thermal_conductivity: tuple[float, float] = (1.0, 5.0)
    specific_heat: tuple[float, float] = (700, 1200)
    density: tuple[float, float] = (1800, 2800)


class GeometryConfig(BaseModel):
    """Geometry configuration of regenerator."""
    length: float = Field(10.0, ge=1.0, le=50.0, description="Length in meters")
    width: float = Field(8.0, ge=1.0, le=30.0, description="Width in meters")


class ThermalConfig(BaseModel):
    """Thermal operating conditions."""
    gas_temp_inlet: float = Field(1600, ge=500, le=2000, description="Inlet gas temperature °C")
    gas_temp_outlet: float = Field(600, ge=200, le=1500, description="Outlet gas temperature °C")


class FlowConfig(BaseModel):
    """Flow configuration."""
    mass_flow_rate: float = Field(50, ge=1, le=500, description="Mass flow rate kg/s")
    cycle_time: float = Field(1200, ge=60, le=3600, description="Cycle time seconds")


class RegeneratorConfiguration(BaseModel):
    """Complete regenerator configuration."""
    geometry_config: GeometryConfig
    thermal_config: ThermalConfig
    flow_config: FlowConfig
    materials_config: Optional[Dict[str, Any]] = {}


class OptimizationRequest(BaseModel):
    """Request to run optimization."""
    configuration: RegeneratorConfiguration
    initial_guess: DesignVariables
    bounds: Optional[BoundsConfig] = BoundsConfig()
    objective_type: str = Field("minimize_fuel_consumption", description="Objective function type")
    max_iterations: int = Field(100, ge=10, le=1000)
    tolerance: float = Field(1e-6, ge=1e-10, le=1e-2)

    class Config:
        json_schema_extra = {
            "example": {
                "configuration": {
                    "geometry_config": {"length": 10.0, "width": 8.0},
                    "thermal_config": {"gas_temp_inlet": 1600, "gas_temp_outlet": 600},
                    "flow_config": {"mass_flow_rate": 50, "cycle_time": 1200}
                },
                "initial_guess": {
                    "checker_height": 0.5,
                    "checker_spacing": 0.1,
                    "wall_thickness": 0.3
                },
                "objective_type": "minimize_fuel_consumption",
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


class OptimizationIteration(BaseModel):
    """Single iteration data."""
    iteration: int
    design_variables: Dict[str, float]
    objective_value: float
    performance: PerformanceMetrics


class OptimizationResult(BaseModel):
    """Result from optimization run."""
    success: bool
    message: str
    final_design_variables: DesignVariables
    final_performance: PerformanceMetrics
    objective_value: float
    iterations: int
    convergence_reached: bool
    computation_time_seconds: float
    iteration_history: Optional[List[OptimizationIteration]] = []


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    message: str


class PerformanceRequest(BaseModel):
    """Request to calculate performance for given design variables."""
    configuration: RegeneratorConfiguration
    design_variables: DesignVariables
