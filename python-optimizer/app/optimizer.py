"""
SLSQP optimization algorithm implementation.
Implementacja algorytmu optymalizacji SLSQP.
"""

import numpy as np
from typing import Dict, List, Tuple, Any
from scipy.optimize import minimize, OptimizeResult, NonlinearConstraint, Bounds
import logging

from .physics_model import RegeneratorPhysicsModel
from .schemas import OptimizationRequest, PerformanceMetrics

logger = logging.getLogger(__name__)


def convert_numpy_types(obj: Any) -> Any:
    """Recursively convert numpy types to Python native types."""
    if isinstance(obj, (np.bool_, np.bool)):
        return bool(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return type(obj)(convert_numpy_types(item) for item in obj)
    else:
        return obj


class SLSQPOptimizer:
    """SLSQP optimizer for regenerator optimization."""

    def __init__(self):
        self.physics_model: RegeneratorPhysicsModel = None
        self.iteration_count = 0
        self.iteration_history: List[Dict[str, Any]] = []

    def optimize(self, request: OptimizationRequest) -> Dict[str, Any]:
        """
        Run SLSQP optimization.

        Args:
            request: Optimization request with configuration and parameters

        Returns:
            Dictionary with optimization results
        """
        # Initialize physics model
        config_dict = {
            'geometry_config': request.configuration.geometry_config.model_dump() if request.configuration.geometry_config else {},
            'thermal_config': request.configuration.thermal_config.model_dump() if request.configuration.thermal_config else {},
            'flow_config': request.configuration.flow_config.model_dump() if request.configuration.flow_config else {},
            'materials_config': request.configuration.materials_config or {}
        }
        self.physics_model = RegeneratorPhysicsModel(config_dict)

        # Setup optimization problem
        bounds, initial_guess = self._setup_problem(request)

        # Reset iteration tracking
        self.iteration_count = 0
        self.iteration_history = []

        # Define objective function
        def objective_function(x: np.ndarray) -> float:
            """Objective function to minimize."""
            self.iteration_count += 1

            # Convert array to design variables dict
            design_vars = self._array_to_design_vars(x, request.design_variables)

            # Calculate physics
            performance = self.physics_model.calculate_thermal_performance(design_vars)

            # Calculate objective based on request
            if request.objective == "maximize_efficiency":
                # Minimize negative efficiency (= maximize efficiency)
                obj_value = -performance["thermal_efficiency"]
            elif request.objective == "minimize_fuel_consumption":
                obj_value = -performance["thermal_efficiency"]
            elif request.objective == "minimize_co2_emissions":
                obj_value = -performance["thermal_efficiency"]
            elif request.objective == "minimize_pressure_drop":
                obj_value = performance["pressure_drop"]
            else:
                # Default: maximize efficiency
                obj_value = -performance["thermal_efficiency"]

            # Store iteration data
            self.iteration_history.append({
                'iteration': self.iteration_count,
                'design_vars': design_vars.copy(),
                'objective_value': obj_value,
                'performance': performance.copy()
            })

            logger.debug(f"Iteration {self.iteration_count}: obj={obj_value:.6f}, η={performance['thermal_efficiency']:.4f}")

            return obj_value

        # Define constraint function
        def constraint_function(x: np.ndarray) -> np.ndarray:
            """Constraint function."""
            design_vars = self._array_to_design_vars(x, request.design_variables)
            performance = self.physics_model.calculate_thermal_performance(design_vars)

            constraints_values = []

            # Pressure drop constraint (< max_pressure_drop)
            max_pressure_drop = request.constraints.max_pressure_drop if request.constraints else 2000
            constraints_values.append(max_pressure_drop - performance["pressure_drop"])

            # Thermal efficiency constraint (> min_thermal_efficiency)
            min_efficiency = request.constraints.min_thermal_efficiency if request.constraints else 0.2
            constraints_values.append(performance["thermal_efficiency"] - min_efficiency)

            # Heat transfer coefficient constraint (> min_heat_transfer_coefficient)
            min_htc = request.constraints.min_heat_transfer_coefficient if request.constraints else 50
            constraints_values.append(performance["heat_transfer_coefficient"] - min_htc)

            return np.array(constraints_values)

        # Set up nonlinear constraints
        nonlinear_constraint = NonlinearConstraint(
            constraint_function,
            lb=0,
            ub=np.inf
        )

        # Run SLSQP optimization
        logger.info(f"Starting SLSQP optimization with {len(initial_guess)} design variables")

        try:
            result = minimize(
                objective_function,
                initial_guess,
                method='SLSQP',
                bounds=bounds,
                constraints=[nonlinear_constraint],
                options={
                    'maxiter': request.max_iterations,
                    'ftol': request.tolerance,
                    'disp': True
                }
            )

            logger.info(f"Optimization completed: success={result.success}, iterations={self.iteration_count}, final_obj={result.fun:.6f}")

        except Exception as e:
            logger.error(f"Optimization failed: {str(e)}")
            raise

        # Process results
        return self._process_results(result, request)

    def _setup_problem(
        self,
        request: OptimizationRequest
    ) -> Tuple[Bounds, np.ndarray]:
        """Set up optimization problem bounds and initial guess."""

        design_vars = request.design_variables
        bounds_config = request.bounds

        # Default bounds for common variables
        default_bounds = {
            "checker_height": (0.3, 2.0),
            "checker_spacing": (0.05, 0.3),
            "wall_thickness": (0.2, 0.8),
            "thermal_conductivity": (1.0, 5.0),
            "specific_heat": (700, 1200),
            "density": (1800, 2800)
        }

        # Build bounds arrays
        lower_bounds = []
        upper_bounds = []
        initial_values = []

        for var_name in design_vars.keys():
            # Get bounds
            if var_name in bounds_config:
                bounds_range = (bounds_config[var_name].min, bounds_config[var_name].max)
            else:
                bounds_range = default_bounds.get(var_name, (0.1, 10.0))

            lower_bounds.append(bounds_range[0])
            upper_bounds.append(bounds_range[1])

            # Initial value from request or middle of range
            if request.initial_values and var_name in request.initial_values:
                initial_values.append(request.initial_values[var_name])
            else:
                initial_values.append((bounds_range[0] + bounds_range[1]) / 2)

        bounds = Bounds(np.array(lower_bounds), np.array(upper_bounds))
        initial_guess = np.array(initial_values)

        logger.info(f"Optimization bounds: {dict(zip(design_vars.keys(), zip(lower_bounds, upper_bounds)))}")
        logger.info(f"Initial guess: {dict(zip(design_vars.keys(), initial_values))}")

        return bounds, initial_guess

    def _array_to_design_vars(self, x: np.ndarray, design_vars_config: Dict) -> Dict[str, float]:
        """Convert optimization array to design variables dictionary."""
        design_vars = {}
        for i, var_name in enumerate(design_vars_config.keys()):
            design_vars[var_name] = float(x[i])
        return design_vars

    def _process_results(
        self,
        scipy_result: OptimizeResult,
        request: OptimizationRequest
    ) -> Dict[str, Any]:
        """Process scipy optimization result."""

        # Extract final design variables
        final_design_vars = self._array_to_design_vars(
            scipy_result.x, request.design_variables
        )

        # Calculate final performance
        final_performance_raw = self.physics_model.calculate_thermal_performance(final_design_vars)

        # Convert numpy types to Python native types
        final_performance = convert_numpy_types(final_performance_raw)

        # Check constraints
        constraints_satisfied = True
        constraint_violations = {}

        max_pressure_drop = request.constraints.max_pressure_drop if request.constraints else 2000
        min_efficiency = request.constraints.min_thermal_efficiency if request.constraints else 0.2
        min_htc = request.constraints.min_heat_transfer_coefficient if request.constraints else 50

        if final_performance["pressure_drop"] > max_pressure_drop:
            constraints_satisfied = False
            constraint_violations["pressure_drop"] = final_performance["pressure_drop"] - max_pressure_drop

        if final_performance["thermal_efficiency"] < min_efficiency:
            constraints_satisfied = False
            constraint_violations["thermal_efficiency"] = min_efficiency - final_performance["thermal_efficiency"]

        if final_performance["heat_transfer_coefficient"] < min_htc:
            constraints_satisfied = False
            constraint_violations["heat_transfer_coefficient"] = min_htc - final_performance["heat_transfer_coefficient"]

        # Build result (convert numpy types to Python types)
        return {
            "success": bool(scipy_result.success and constraints_satisfied),
            "message": scipy_result.message if scipy_result.success else f"Optimization failed: {scipy_result.message}",
            "iterations": self.iteration_count,
            "final_objective_value": float(scipy_result.fun),
            "optimized_design_variables": final_design_vars,
            "performance_metrics": PerformanceMetrics(**final_performance),
            "convergence_info": {
                "converged": bool(scipy_result.success),
                "status": int(scipy_result.status),
                "nfev": int(scipy_result.nfev) if hasattr(scipy_result, 'nfev') else self.iteration_count,
                "njev": int(scipy_result.njev) if hasattr(scipy_result, 'njev') else 0,
                "nit": int(scipy_result.nit) if hasattr(scipy_result, 'nit') else self.iteration_count
            },
            "constraints_satisfied": bool(constraints_satisfied),
            "constraint_violations": constraint_violations if constraint_violations else None
        }
