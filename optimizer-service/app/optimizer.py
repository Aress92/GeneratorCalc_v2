"""
Regenerator Physics Model and SLSQP Optimization Logic.
Extracted from backend/app/services/optimization_service.py
"""
import numpy as np
from typing import Dict, Any, Tuple, List, Callable, Optional
from scipy.optimize import minimize, OptimizeResult, NonlinearConstraint, Bounds
import time
import logging

from app.models import (
    RegeneratorConfiguration,
    DesignVariables,
    PerformanceMetrics,
    OptimizationIteration,
    BoundsConfig
)

logger = logging.getLogger(__name__)


class RegeneratorPhysicsModel:
    """
    Physics model for regenerator thermal calculations.
    Fizyczny model regeneratora dla obliczeń termicznych.
    """

    def __init__(self, configuration: RegeneratorConfiguration):
        """Initialize physics model with regenerator configuration."""
        self.config = configuration
        self.geometry = configuration.geometry_config
        self.thermal = configuration.thermal_config
        self.flow = configuration.flow_config
        self.materials = configuration.materials_config or {}

    def calculate_thermal_performance(self, design_variables: Dict[str, float]) -> PerformanceMetrics:
        """
        Calculate thermal performance metrics for given design variables.

        Args:
            design_variables: Dictionary with optimized parameters

        Returns:
            PerformanceMetrics with calculated values
        """
        # Extract key parameters
        checker_height = design_variables.get("checker_height", 0.5)  # m
        checker_spacing = design_variables.get("checker_spacing", 0.1)  # m
        wall_thickness = design_variables.get("wall_thickness", 0.3)  # m

        # Material properties
        checker_conductivity = design_variables.get("thermal_conductivity", 2.5)  # W/(m·K)
        checker_heat_capacity = design_variables.get("specific_heat", 900)  # J/(kg·K)
        checker_density = design_variables.get("density", 2300)  # kg/m³

        # Operating conditions
        gas_temp_inlet = self.thermal.gas_temp_inlet  # °C
        gas_temp_outlet = self.thermal.gas_temp_outlet  # °C
        mass_flow_rate = self.flow.mass_flow_rate  # kg/s
        cycle_time = self.flow.cycle_time  # s

        # Calculate heat transfer area
        checker_volume = self._calculate_checker_volume(checker_height, checker_spacing)
        surface_area = self._calculate_surface_area(checker_volume, checker_spacing)

        # Heat transfer coefficient calculation (simplified)
        reynolds_number = self._calculate_reynolds(mass_flow_rate, checker_spacing)
        nusselt_number = self._calculate_nusselt(reynolds_number)
        heat_transfer_coeff = self._calculate_htc(nusselt_number, checker_conductivity, checker_spacing)

        # NTU calculation
        heat_capacity_rate = mass_flow_rate * 1100  # J/(s·K) - specific heat of combustion gases
        ntu = (heat_transfer_coeff * surface_area) / heat_capacity_rate

        # Effectiveness calculation
        effectiveness = self._calculate_effectiveness(ntu)

        # Heat transfer rate - based on actual temperature drop in gases
        heat_available = heat_capacity_rate * (gas_temp_inlet - gas_temp_outlet)
        actual_heat_transfer = effectiveness * heat_available

        # Pressure drop calculation
        pressure_drop = self._calculate_pressure_drop(mass_flow_rate, checker_spacing, checker_height)

        # Thermal efficiency - regenerator heat recovery efficiency
        if heat_available > 0:
            thermal_efficiency = actual_heat_transfer / heat_available
        else:
            thermal_efficiency = 0.0

        # Wall heat losses
        wall_heat_loss = self._calculate_wall_losses(wall_thickness, gas_temp_inlet)

        # Energy balance - adjust for wall losses
        net_efficiency = thermal_efficiency - (wall_heat_loss / max(heat_available, 1))
        net_efficiency = min(max(net_efficiency, 0.0), 1.0)  # Bounded 0-100%

        return PerformanceMetrics(
            thermal_efficiency=net_efficiency,
            heat_transfer_rate=actual_heat_transfer,
            pressure_drop=pressure_drop,
            ntu_value=ntu,
            effectiveness=effectiveness,
            heat_transfer_coefficient=heat_transfer_coeff,
            surface_area=surface_area,
            wall_heat_loss=wall_heat_loss,
            reynolds_number=reynolds_number,
            nusselt_number=nusselt_number
        )

    def _calculate_checker_volume(self, height: float, spacing: float) -> float:
        """Calculate checker brick volume."""
        length = self.geometry.length  # m
        width = self.geometry.width  # m
        porosity = 0.7  # 70% void space in checker pattern
        return length * width * height * (1 - porosity)

    def _calculate_surface_area(self, volume: float, spacing: float) -> float:
        """Calculate heat transfer surface area."""
        # Surface area per unit volume for checker pattern
        specific_surface = 400 / spacing  # m²/m³ (empirical correlation)
        return volume * specific_surface

    def _calculate_reynolds(self, mass_flow: float, spacing: float) -> float:
        """Calculate Reynolds number."""
        gas_density = 0.4  # kg/m³ at high temperature
        gas_viscosity = 5e-5  # Pa·s at high temperature
        velocity = mass_flow / (gas_density * 60)  # m/s (60 m² cross-sectional area)
        return (gas_density * velocity * spacing) / gas_viscosity

    def _calculate_nusselt(self, reynolds: float) -> float:
        """Calculate Nusselt number using correlation for packed beds."""
        prandtl = 0.7  # Typical for combustion gases
        if reynolds < 10:
            return 2.0 + 1.1 * (reynolds * prandtl) ** 0.6
        else:
            return 2.0 + 0.6 * (reynolds ** 0.5) * (prandtl ** 0.33)

    def _calculate_htc(self, nusselt: float, conductivity: float, spacing: float) -> float:
        """Calculate heat transfer coefficient."""
        gas_conductivity = 0.08  # W/(m·K) for combustion gases at high temp
        return (nusselt * gas_conductivity) / spacing

    def _calculate_effectiveness(self, ntu: float) -> float:
        """Calculate heat exchanger effectiveness."""
        # For counter-flow heat exchanger with equal heat capacity rates
        return ntu / (1 + ntu)

    def _calculate_pressure_drop(self, mass_flow: float, spacing: float, height: float) -> float:
        """Calculate pressure drop through regenerator."""
        gas_density = 0.4  # kg/m³
        velocity = mass_flow / (gas_density * 60)  # m/s
        reynolds = self._calculate_reynolds(mass_flow, spacing)
        friction_factor = 150 / reynolds + 1.75
        return friction_factor * (height / spacing) * 0.5 * gas_density * (velocity ** 2)

    def _calculate_wall_losses(self, wall_thickness: float, gas_temp: float) -> float:
        """Calculate heat losses through walls."""
        wall_conductivity = 1.2  # W/(m·K) for refractory
        wall_area = 200  # m² typical wall area
        temp_diff = gas_temp - 50  # °C to ambient + shell temp
        return (wall_conductivity * wall_area * temp_diff) / wall_thickness


class SLSQPOptimizer:
    """SLSQP optimization algorithm wrapper."""

    def __init__(self, physics_model: RegeneratorPhysicsModel):
        self.physics_model = physics_model
        self.iteration_history: List[Dict[str, Any]] = []
        self.iteration_count = 0
        self.best_objective = float('inf')
        self.progress_callback: Optional[Callable] = None

    def optimize(
        self,
        initial_guess: DesignVariables,
        bounds: BoundsConfig,
        objective_type: str,
        max_iterations: int,
        tolerance: float
    ) -> Tuple[OptimizeResult, List[OptimizationIteration]]:
        """
        Run SLSQP optimization.

        Args:
            initial_guess: Initial design variables
            bounds: Bounds for design variables
            objective_type: Type of objective function
            max_iterations: Maximum number of iterations
            tolerance: Convergence tolerance

        Returns:
            Tuple of (scipy OptimizeResult, iteration history)
        """
        # Reset state
        self.iteration_history = []
        self.iteration_count = 0
        self.best_objective = float('inf')

        # Convert to numpy arrays
        design_var_names = ["checker_height", "checker_spacing", "wall_thickness",
                            "thermal_conductivity", "specific_heat", "density"]

        initial_array = np.array([
            initial_guess.checker_height,
            initial_guess.checker_spacing,
            initial_guess.wall_thickness,
            initial_guess.thermal_conductivity or 2.5,
            initial_guess.specific_heat or 900,
            initial_guess.density or 2300
        ])

        bounds_array = Bounds(
            lb=np.array([
                bounds.checker_height[0],
                bounds.checker_spacing[0],
                bounds.wall_thickness[0],
                bounds.thermal_conductivity[0],
                bounds.specific_heat[0],
                bounds.density[0]
            ]),
            ub=np.array([
                bounds.checker_height[1],
                bounds.checker_spacing[1],
                bounds.wall_thickness[1],
                bounds.thermal_conductivity[1],
                bounds.specific_heat[1],
                bounds.density[1]
            ])
        )

        def objective_function(x: np.ndarray) -> float:
            """Objective function to minimize."""
            self.iteration_count += 1

            # Convert array to design variables dict
            design_vars = {
                "checker_height": float(x[0]),
                "checker_spacing": float(x[1]),
                "wall_thickness": float(x[2]),
                "thermal_conductivity": float(x[3]),
                "specific_heat": float(x[4]),
                "density": float(x[5])
            }

            # Calculate physics
            performance = self.physics_model.calculate_thermal_performance(design_vars)

            # Calculate objective based on type
            if objective_type == "minimize_fuel_consumption":
                # Maximize thermal efficiency (minimize negative efficiency)
                obj_value = -performance.thermal_efficiency
            elif objective_type == "minimize_co2_emissions":
                obj_value = -performance.thermal_efficiency
            elif objective_type == "maximize_efficiency":
                obj_value = -performance.thermal_efficiency
            else:
                obj_value = -performance.thermal_efficiency  # Default

            # Store iteration data
            self.iteration_history.append({
                'iteration': self.iteration_count,
                'design_vars': design_vars.copy(),
                'objective_value': obj_value,
                'performance': performance
            })

            # Update best objective
            if obj_value < self.best_objective:
                self.best_objective = obj_value
                logger.info(f"Iteration {self.iteration_count}: New best objective = {obj_value:.6f}")

            # Call progress callback if provided
            if self.progress_callback:
                try:
                    self.progress_callback(self.iteration_count, max_iterations, obj_value)
                except Exception as e:
                    logger.warning(f"Progress callback failed: {e}")

            return obj_value

        def constraint_function(x: np.ndarray) -> np.ndarray:
            """Constraint function."""
            design_vars = {
                "checker_height": float(x[0]),
                "checker_spacing": float(x[1]),
                "wall_thickness": float(x[2]),
                "thermal_conductivity": float(x[3]),
                "specific_heat": float(x[4]),
                "density": float(x[5])
            }
            performance = self.physics_model.calculate_thermal_performance(design_vars)

            constraints_values = []

            # Pressure drop constraint (< 2000 Pa)
            constraints_values.append(2000 - performance.pressure_drop)

            # Thermal efficiency constraint (> 0.2)
            constraints_values.append(performance.thermal_efficiency - 0.2)

            # Heat transfer coefficient constraint (> 50 W/m²K)
            constraints_values.append(performance.heat_transfer_coefficient - 50)

            return np.array(constraints_values)

        # Set up constraints
        nonlinear_constraint = NonlinearConstraint(
            constraint_function,
            lb=0,
            ub=np.inf
        )

        # Run SLSQP optimization
        logger.info(f"Starting SLSQP optimization with max_iterations={max_iterations}, tolerance={tolerance}")
        start_time = time.time()

        result = minimize(
            objective_function,
            initial_array,
            method='SLSQP',
            bounds=bounds_array,
            constraints=[nonlinear_constraint],
            options={
                'maxiter': max_iterations,
                'ftol': tolerance,
                'disp': True
            }
        )

        computation_time = time.time() - start_time
        logger.info(f"Optimization completed in {computation_time:.2f}s, success={result.success}")

        # Convert iteration history to OptimizationIteration objects
        iteration_objects = [
            OptimizationIteration(
                iteration=iter_data['iteration'],
                design_variables=iter_data['design_vars'],
                objective_value=iter_data['objective_value'],
                performance=iter_data['performance']
            )
            for iter_data in self.iteration_history
        ]

        return result, iteration_objects, computation_time

    def set_progress_callback(self, callback: Callable):
        """Set progress callback function."""
        self.progress_callback = callback
