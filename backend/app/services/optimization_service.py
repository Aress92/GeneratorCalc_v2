"""
Optimization service implementing SLSQP and other algorithms for regenerator optimization.

Serwis optymalizacji implementujący SLSQP i inne algorytmy dla optymalizacji regeneratorów.
"""

import numpy as np
from datetime import datetime, timedelta, UTC
from typing import Dict, List, Optional, Tuple, Any, Callable
import structlog
import asyncio
from scipy.optimize import minimize, OptimizeResult
from scipy.optimize import NonlinearConstraint, LinearConstraint, Bounds
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.optimization import (
    OptimizationScenario, OptimizationJob, OptimizationResult, OptimizationIteration,
    OptimizationStatus, OptimizationObjective, OptimizationAlgorithm
)
from app.models.regenerator import RegeneratorConfiguration
from app.schemas.optimization_schemas import (
    OptimizationJobCreate, OptimizationProgress, OptimizationResultResponse
)
from app.core.config import settings

logger = structlog.get_logger(__name__)


class RegeneratorPhysicsModel:
    """
    Physics model for regenerator thermal calculations.
    Fizyczny model regeneratora dla obliczeń termicznych.
    """

    def __init__(self, configuration: Dict[str, Any]):
        """Initialize physics model with regenerator configuration."""
        self.config = configuration
        self.geometry = configuration.get("geometry_config", {})
        self.materials = configuration.get("materials_config", {})
        self.thermal = configuration.get("thermal_config", {})
        self.flow = configuration.get("flow_config", {})

    def calculate_thermal_performance(self, design_variables: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate thermal performance metrics for given design variables.

        Args:
            design_variables: Dictionary with optimized parameters

        Returns:
            Dictionary with performance metrics
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
        gas_temp_inlet = self.thermal.get("gas_temp_inlet", 1600)  # °C
        gas_temp_outlet = self.thermal.get("gas_temp_outlet", 600)  # °C
        mass_flow_rate = self.flow.get("mass_flow_rate", 50)  # kg/s
        cycle_time = self.flow.get("cycle_time", 1200)  # s

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
        # For regenerator: heat recovered = effectiveness × available heat
        heat_available = heat_capacity_rate * (gas_temp_inlet - gas_temp_outlet)  # Available heat in gases
        actual_heat_transfer = effectiveness * heat_available

        # Pressure drop calculation
        pressure_drop = self._calculate_pressure_drop(mass_flow_rate, checker_spacing, checker_height)

        # Thermal efficiency - regenerator heat recovery efficiency
        # Efficiency = heat recovered / heat available in hot gases
        heat_available = heat_capacity_rate * (gas_temp_inlet - gas_temp_outlet)  # Available heat in gases
        if heat_available > 0:
            thermal_efficiency = actual_heat_transfer / heat_available
        else:
            thermal_efficiency = 0.0

        # Wall heat losses
        wall_heat_loss = self._calculate_wall_losses(wall_thickness, gas_temp_inlet)

        # Energy balance - adjust for wall losses
        net_efficiency = thermal_efficiency - (wall_heat_loss / max(heat_available, 1))

        return {
            "thermal_efficiency": min(max(net_efficiency, 0.0), 1.0),  # Bounded 0-100%
            "heat_transfer_rate": actual_heat_transfer,  # W
            "pressure_drop": pressure_drop,  # Pa
            "ntu_value": ntu,
            "effectiveness": effectiveness,
            "heat_transfer_coefficient": heat_transfer_coeff,  # W/(m²·K)
            "surface_area": surface_area,  # m²
            "wall_heat_loss": wall_heat_loss,  # W
            "reynolds_number": reynolds_number,
            "nusselt_number": nusselt_number
        }

    def _calculate_checker_volume(self, height: float, spacing: float) -> float:
        """Calculate checker brick volume."""
        length = self.geometry.get("length", 10.0)  # m
        width = self.geometry.get("width", 8.0)  # m
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
        friction_factor = 150 / self._calculate_reynolds(mass_flow, spacing) + 1.75
        return friction_factor * (height / spacing) * 0.5 * gas_density * (velocity ** 2)

    def _calculate_wall_losses(self, wall_thickness: float, gas_temp: float) -> float:
        """Calculate heat losses through walls."""
        wall_conductivity = 1.2  # W/(m·K) for refractory
        wall_area = 200  # m² typical wall area
        temp_diff = gas_temp - 50  # °C to ambient + shell temp
        return (wall_conductivity * wall_area * temp_diff) / wall_thickness


class OptimizationService:
    """Service for running optimization algorithms on regenerator configurations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.physics_model = None
        self.progress_callback = None  # Optional callback for Celery progress updates

    async def create_optimization_job(
        self,
        scenario_id: str,
        user_id: str,
        job_config: OptimizationJobCreate
    ) -> OptimizationJob:
        """Create a new optimization job."""

        # Get scenario
        scenario = await self._get_scenario(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        # Get base configuration
        base_config = await self._get_configuration(scenario.base_configuration_id)
        if not base_config:
            raise ValueError(f"Base configuration not found")

        # Create job
        job = OptimizationJob(
            scenario_id=scenario_id,
            user_id=user_id,
            job_name=job_config.job_name,
            execution_config=scenario.optimization_config,
            initial_values=job_config.initial_values or {},
            status=OptimizationStatus.PENDING
        )

        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)

        logger.info("Created optimization job", job_id=job.id, scenario_id=scenario_id)
        return job

    async def run_optimization(self, job_id: str) -> OptimizationResult:
        """
        Run optimization algorithm for the given job.
        Main optimization logic using SLSQP or other algorithms.
        """

        # Get job and scenario
        job = await self._get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        scenario = await self._get_scenario(job.scenario_id)
        base_config = await self._get_configuration(scenario.base_configuration_id)

        try:
            # Update job status
            await self._update_job_status(job_id, OptimizationStatus.INITIALIZING)

            # Initialize physics model
            full_config = {
                'geometry_config': base_config.geometry_config or {},
                'materials_config': base_config.materials_config or {},
                'thermal_config': base_config.thermal_config or {},
                'flow_config': base_config.flow_config or {}
            }
            self.physics_model = RegeneratorPhysicsModel(full_config)

            # Set up optimization problem
            bounds, constraints, initial_guess = self._setup_optimization_problem(scenario, job)

            # Update to running
            await self._update_job_status(job_id, OptimizationStatus.RUNNING)

            # Run optimization algorithm
            if scenario.algorithm == OptimizationAlgorithm.SLSQP:
                result = await self._run_slsqp_optimization(
                    job_id, scenario, initial_guess, bounds, constraints
                )
            else:
                raise ValueError(f"Algorithm {scenario.algorithm} not implemented yet")

            # Process results
            optimization_result = await self._process_optimization_result(
                job_id, result, scenario, base_config
            )

            # Update job status
            await self._update_job_status(job_id, OptimizationStatus.COMPLETED)

            logger.info("Optimization completed successfully", job_id=job_id)
            return optimization_result

        except Exception as e:
            logger.error("Optimization failed", job_id=job_id, error=str(e))
            await self._update_job_status(
                job_id,
                OptimizationStatus.FAILED,
                error_message=str(e)
            )
            raise

    async def _run_slsqp_optimization(
        self,
        job_id: str,
        scenario: OptimizationScenario,
        initial_guess: np.ndarray,
        bounds: Bounds,
        constraints: List
    ) -> OptimizeResult:
        """Run SLSQP optimization algorithm."""

        iteration_count = 0

        def objective_function(x: np.ndarray) -> float:
            """Objective function to minimize."""
            nonlocal iteration_count
            iteration_count += 1

            # Convert array to design variables dict
            design_vars = self._array_to_design_vars(x, scenario.design_variables)

            # Calculate physics
            performance = self.physics_model.calculate_thermal_performance(design_vars)

            # Calculate objective based on scenario
            if scenario.objective == OptimizationObjective.MINIMIZE_FUEL_CONSUMPTION:
                # Maximize thermal efficiency (minimize negative efficiency)
                obj_value = -performance["thermal_efficiency"]
            elif scenario.objective == OptimizationObjective.MINIMIZE_CO2_EMISSIONS:
                # Similar to fuel consumption for regenerators
                obj_value = -performance["thermal_efficiency"]
            elif scenario.objective == OptimizationObjective.MAXIMIZE_EFFICIENCY:
                obj_value = -performance["thermal_efficiency"]
            else:
                obj_value = -performance["thermal_efficiency"]  # Default

            # Store iteration data for later logging (can't use async in scipy callback)
            if not hasattr(self, '_iteration_data'):
                self._iteration_data = []
            self._iteration_data.append({
                'iteration': iteration_count,
                'design_vars': design_vars.copy(),
                'objective_value': obj_value,
                'performance': performance.copy()
            })

            # Call progress callback if provided (for Celery progress updates)
            if self.progress_callback:
                try:
                    self.progress_callback(iteration_count, scenario.max_iterations, obj_value)
                except Exception as e:
                    logger.warning("Progress callback failed", error=str(e))

            return obj_value

        def constraint_function(x: np.ndarray) -> np.ndarray:
            """Constraint function."""
            design_vars = self._array_to_design_vars(x, scenario.design_variables)
            performance = self.physics_model.calculate_thermal_performance(design_vars)

            constraints_values = []

            # Pressure drop constraint (< 2000 Pa)
            constraints_values.append(2000 - performance["pressure_drop"])

            # Thermal efficiency constraint (> 0.2)
            constraints_values.append(performance["thermal_efficiency"] - 0.2)

            # Heat transfer coefficient constraint (> 50 W/m²K)
            constraints_values.append(performance["heat_transfer_coefficient"] - 50)

            return np.array(constraints_values)

        # Set up constraints
        nonlinear_constraint = NonlinearConstraint(
            constraint_function,
            lb=0,
            ub=np.inf
        )

        # Initialize iteration data storage
        self._iteration_data = []

        # SLSQP optimization
        result = minimize(
            objective_function,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=[nonlinear_constraint],
            options={
                'maxiter': scenario.max_iterations,
                'ftol': scenario.tolerance,
                'disp': True
            }
        )

        # Log all iterations after optimization completes
        for iter_data in getattr(self, '_iteration_data', []):
            await self._log_iteration(
                job_id,
                iter_data['iteration'],
                iter_data['design_vars'],
                iter_data['objective_value'],
                iter_data['performance']
            )

        return result

    def _setup_optimization_problem(
        self,
        scenario: OptimizationScenario,
        job: OptimizationJob
    ) -> Tuple[Bounds, List, np.ndarray]:
        """Set up optimization problem bounds, constraints, and initial guess."""

        design_vars = scenario.design_variables
        bounds_config = scenario.bounds_config or {}

        # Default bounds for common variables
        default_bounds = {
            "checker_height": (0.3, 2.0),      # m
            "checker_spacing": (0.05, 0.3),    # m
            "wall_thickness": (0.2, 0.8),      # m
            "thermal_conductivity": (1.0, 5.0), # W/(m·K)
            "specific_heat": (700, 1200),       # J/(kg·K)
            "density": (1800, 2800)             # kg/m³
        }

        # Build bounds arrays
        lower_bounds = []
        upper_bounds = []
        initial_values = []

        for var_name, var_config in design_vars.items():
            # Handle both dict format {"min": 0.3, "max": 2.0} and tuple format (0.3, 2.0)
            bounds_entry = bounds_config.get(var_name, default_bounds.get(var_name, (0.1, 10.0)))

            if isinstance(bounds_entry, dict):
                bounds_range = (bounds_entry["min"], bounds_entry["max"])
            else:
                bounds_range = bounds_entry

            lower_bounds.append(bounds_range[0])
            upper_bounds.append(bounds_range[1])

            # Initial value from job or middle of range
            if var_name in job.initial_values:
                initial_values.append(job.initial_values[var_name])
            else:
                initial_values.append((bounds_range[0] + bounds_range[1]) / 2)

        bounds = Bounds(np.array(lower_bounds), np.array(upper_bounds))
        initial_guess = np.array(initial_values)
        constraints = []  # Will be set up in algorithm-specific method

        return bounds, constraints, initial_guess

    def _array_to_design_vars(self, x: np.ndarray, design_vars_config: Dict) -> Dict[str, float]:
        """Convert optimization array to design variables dictionary."""
        design_vars = {}
        for i, var_name in enumerate(design_vars_config.keys()):
            design_vars[var_name] = float(x[i])
        return design_vars

    async def _log_iteration(
        self,
        job_id: str,
        iteration: int,
        design_vars: Dict,
        objective_value: float,
        performance: Dict
    ):
        """Log optimization iteration to database."""
        try:
            iteration_record = OptimizationIteration(
                job_id=job_id,
                iteration_number=iteration,
                function_evaluation=iteration,
                design_variables=design_vars,
                objective_value=objective_value,
                performance_metrics=performance,
                is_improvement=iteration == 1 or objective_value < getattr(self, '_best_objective', float('inf')),
                evaluation_time_seconds=0.1  # Placeholder
            )

            self.db.add(iteration_record)
            await self.db.commit()

            # Update best objective tracking
            self._best_objective = min(getattr(self, '_best_objective', float('inf')), objective_value)

        except Exception as e:
            logger.warning("Failed to log iteration", error=str(e))

    async def _process_optimization_result(
        self,
        job_id: str,
        scipy_result: OptimizeResult,
        scenario: OptimizationScenario,
        base_config: RegeneratorConfiguration
    ) -> OptimizationResult:
        """Process scipy optimization result and create OptimizationResult."""

        # Extract final design variables
        final_design_vars = self._array_to_design_vars(
            scipy_result.x, scenario.design_variables
        )

        # Calculate final performance
        final_performance = self.physics_model.calculate_thermal_performance(final_design_vars)

        # Calculate baseline performance for comparison
        baseline_vars = {}
        for var_name, var_config in scenario.design_variables.items():
            baseline_vars[var_name] = var_config.get("baseline_value", 1.0)
        baseline_performance = self.physics_model.calculate_thermal_performance(baseline_vars)

        # Calculate improvements
        efficiency_improvement = (
            (final_performance["thermal_efficiency"] - baseline_performance["thermal_efficiency"])
            / baseline_performance["thermal_efficiency"] * 100
        )

        # Estimate economic benefits
        fuel_savings = efficiency_improvement  # % fuel savings ≈ efficiency improvement
        co2_reduction = fuel_savings * 0.95   # Slightly less CO2 reduction
        annual_savings = fuel_savings * 50000  # €50k base fuel cost assumption

        # Create result record
        result = OptimizationResult(
            job_id=job_id,
            optimized_configuration=final_performance,
            design_variables_final=final_design_vars,
            objective_value=float(scipy_result.fun),
            baseline_metrics=baseline_performance,
            optimized_metrics=final_performance,
            improvement_percentages={
                "thermal_efficiency": efficiency_improvement,
                "pressure_drop": (baseline_performance["pressure_drop"] - final_performance["pressure_drop"]) / baseline_performance["pressure_drop"] * 100
            },
            fuel_savings_percentage=fuel_savings,
            co2_reduction_percentage=co2_reduction,
            annual_cost_savings=annual_savings,
            payback_period_months=24.0 if annual_savings > 1000 else None,
            thermal_efficiency=final_performance["thermal_efficiency"],
            pressure_drop=final_performance["pressure_drop"],
            heat_transfer_coefficient=final_performance["heat_transfer_coefficient"],
            ntu_value=final_performance["ntu_value"],
            solution_feasibility=1.0 if scipy_result.success else 0.5,
            optimization_confidence=0.9 if scipy_result.success else 0.3
        )

        self.db.add(result)
        await self.db.commit()
        await self.db.refresh(result)

        return result

    async def get_optimization_progress(self, job_id: str) -> OptimizationProgress:
        """Get current optimization progress."""
        job = await self._get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        # Get latest iterations
        stmt = select(OptimizationIteration).where(
            OptimizationIteration.job_id == job_id
        ).order_by(OptimizationIteration.iteration_number.desc()).limit(10)

        result = await self.db.execute(stmt)
        recent_iterations = result.scalars().all()

        return OptimizationProgress(
            job_id=job_id,
            status=job.status,
            current_iteration=job.current_iteration,
            max_iterations=job.scenario.max_iterations,
            progress_percentage=job.progress_percentage,
            current_objective_value=job.final_objective_value,
            recent_iterations=[
                {
                    "iteration": it.iteration_number,
                    "objective_value": it.objective_value,
                    "design_variables": it.design_variables
                }
                for it in recent_iterations
            ],
            estimated_completion_at=job.estimated_completion_at,
            runtime_seconds=job.runtime_seconds or 0
        )

    async def preview_scenario_calculations(self, scenario_id: str, design_vars_input: Optional[Dict[str, float]] = None):
        """
        Generate detailed calculation preview for a scenario.
        Shows step-by-step formulas and intermediate results.

        Generuje szczegółowy podgląd obliczeń dla scenariusza.
        Pokazuje krok po kroku wzory i wyniki pośrednie.
        """
        from app.schemas.optimization_schemas import OptimizationCalculationPreview, CalculationStepDetail

        # Get scenario and configuration
        scenario = await self._get_scenario(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        base_config = await self._get_configuration(scenario.base_configuration_id)
        if not base_config:
            raise ValueError(f"Base configuration not found")

        # Initialize physics model
        full_config = {
            'geometry_config': base_config.geometry_config or {},
            'materials_config': base_config.materials_config or {},
            'thermal_config': base_config.thermal_config or {},
            'flow_config': base_config.flow_config or {}
        }
        physics_model = RegeneratorPhysicsModel(full_config)

        # Get design variables (use input or baseline values)
        if design_vars_input:
            design_vars = design_vars_input
        else:
            design_vars = {}
            for var_name, var_config in scenario.design_variables.items():
                design_vars[var_name] = var_config.get("baseline_value",
                    (var_config.get("min_value", 0.5) + var_config.get("max_value", 1.5)) / 2)

        # Extract parameters for calculations
        h = design_vars.get("checker_height", 0.5)
        s = design_vars.get("checker_spacing", 0.1)
        w = design_vars.get("wall_thickness", 0.3)
        k_checker = design_vars.get("thermal_conductivity", 2.5)
        cp_checker = design_vars.get("specific_heat", 900)
        rho_checker = design_vars.get("density", 2300)

        T_in = full_config['thermal_config'].get("gas_temp_inlet", 1600)
        T_out = full_config['thermal_config'].get("gas_temp_outlet", 600)
        m_flow = full_config['flow_config'].get("mass_flow_rate", 50)
        L = full_config['geometry_config'].get("length", 10.0)
        W = full_config['geometry_config'].get("width", 8.0)

        # Constants
        porosity = 0.7
        rho_gas = 0.4
        mu_gas = 5e-5
        k_gas = 0.08
        cp_gas = 1100
        Pr = 0.7
        A_cross = 60.0
        k_wall = 1.2
        A_wall = 200.0

        # --- GEOMETRY CALCULATIONS ---
        geometry_calcs = []

        # 1. Checker volume
        V_total = L * W * h
        V_checker = V_total * (1 - porosity)
        geometry_calcs.append(CalculationStepDetail(
            step_name="Objętość cegieł checker",
            formula="V = L × W × h × (1 - ε)",
            substitution=f"V = {L} × {W} × {h} × (1 - {porosity})",
            result=V_checker,
            unit="m³",
            explanation="Objętość wypełnienia pomniejszona o przestrzeń pustą (70% porowatość)"
        ))

        # 2. Surface area
        specific_surface = 400 / s
        A_surface = V_checker * specific_surface
        geometry_calcs.append(CalculationStepDetail(
            step_name="Powierzchnia wymiany ciepła",
            formula="A = V × (400 / s)",
            substitution=f"A = {V_checker:.2f} × (400 / {s})",
            result=A_surface,
            unit="m²",
            explanation="Całkowita powierzchnia kontaktu gazu z cegłami"
        ))

        # --- HEAT TRANSFER CALCULATIONS ---
        ht_calcs = []

        # 3. Velocity
        v = m_flow / (rho_gas * A_cross)
        ht_calcs.append(CalculationStepDetail(
            step_name="Prędkość gazu",
            formula="v = ṁ / (ρ × A)",
            substitution=f"v = {m_flow} / ({rho_gas} × {A_cross})",
            result=v,
            unit="m/s",
            explanation="Prędkość przepływu gazów spalinowych przez regenerator"
        ))

        # 4. Reynolds number
        Re = (rho_gas * v * s) / mu_gas
        ht_calcs.append(CalculationStepDetail(
            step_name="Liczba Reynoldsa",
            formula="Re = (ρ × v × d) / μ",
            substitution=f"Re = ({rho_gas} × {v:.2f} × {s}) / {mu_gas}",
            result=Re,
            unit="-",
            explanation="Stosunek sił bezwładności do lepkości - charakteryzuje przepływ"
        ))

        # 5. Nusselt number
        if Re < 10:
            Nu = 2.0 + 1.1 * (Re * Pr) ** 0.6
            Nu_formula = "Nu = 2.0 + 1.1 × (Re × Pr)^0.6"
        else:
            Nu = 2.0 + 0.6 * (Re ** 0.5) * (Pr ** 0.33)
            Nu_formula = "Nu = 2.0 + 0.6 × Re^0.5 × Pr^0.33"

        ht_calcs.append(CalculationStepDetail(
            step_name="Liczba Nusselta",
            formula=Nu_formula,
            substitution=f"Nu = ... (Re={Re:.1f}, Pr={Pr})",
            result=Nu,
            unit="-",
            explanation="Bezwymiarowy współczynnik wymiany ciepła konwekcyjnego"
        ))

        # 6. Heat transfer coefficient
        htc = (Nu * k_gas) / s
        ht_calcs.append(CalculationStepDetail(
            step_name="Współczynnik wymiany ciepła",
            formula="h = (Nu × k_gas) / d",
            substitution=f"h = ({Nu:.2f} × {k_gas}) / {s}",
            result=htc,
            unit="W/(m²·K)",
            explanation="Intensywność wymiany ciepła między gazem a cegłami"
        ))

        # 7. Heat capacity rate
        C_min = m_flow * cp_gas
        ht_calcs.append(CalculationStepDetail(
            step_name="Wydajność cieplna strumienia",
            formula="C = ṁ × cp",
            substitution=f"C = {m_flow} × {cp_gas}",
            result=C_min,
            unit="W/K",
            explanation="Zdolność strumienia gazu do przenoszenia ciepła"
        ))

        # 8. NTU
        NTU = (htc * A_surface) / C_min
        ht_calcs.append(CalculationStepDetail(
            step_name="Liczba jednostek transportu",
            formula="NTU = (h × A) / C",
            substitution=f"NTU = ({htc:.2f} × {A_surface:.2f}) / {C_min:.2f}",
            result=NTU,
            unit="-",
            explanation="Efektywność wymiennika - stosunek możliwości wymiany do przepływu"
        ))

        # 9. Effectiveness
        effectiveness = NTU / (1 + NTU)
        ht_calcs.append(CalculationStepDetail(
            step_name="Efektywność wymiennika",
            formula="ε = NTU / (1 + NTU)",
            substitution=f"ε = {NTU:.3f} / (1 + {NTU:.3f})",
            result=effectiveness,
            unit="-",
            explanation="Stosunek faktycznej wymiany ciepła do maksymalnej możliwej"
        ))

        # --- PERFORMANCE CALCULATIONS ---
        perf_calcs = []

        # 10. Available heat
        Q_available = C_min * (T_in - T_out)
        perf_calcs.append(CalculationStepDetail(
            step_name="Ciepło dostępne w gazach",
            formula="Q_avail = C × (T_in - T_out)",
            substitution=f"Q_avail = {C_min:.2f} × ({T_in} - {T_out})",
            result=Q_available,
            unit="W",
            explanation="Całkowite ciepło możliwe do odzyskania z gazów spalinowych"
        ))

        # 11. Actual heat transfer
        Q_actual = effectiveness * Q_available
        perf_calcs.append(CalculationStepDetail(
            step_name="Rzeczywisty transfer ciepła",
            formula="Q_actual = ε × Q_avail",
            substitution=f"Q_actual = {effectiveness:.3f} × {Q_available:.2f}",
            result=Q_actual,
            unit="W",
            explanation="Faktycznie odzyskane ciepło przez regenerator"
        ))

        # 12. Wall losses
        Q_wall = (k_wall * A_wall * (T_in - 50)) / w
        perf_calcs.append(CalculationStepDetail(
            step_name="Straty przez ściany",
            formula="Q_loss = (k × A × ΔT) / δ",
            substitution=f"Q_loss = ({k_wall} × {A_wall} × {T_in - 50}) / {w}",
            result=Q_wall,
            unit="W",
            explanation="Straty ciepła przez ściany ogniotrwałe regeneratora"
        ))

        # 13. Thermal efficiency
        eta_thermal = Q_actual / Q_available if Q_available > 0 else 0
        perf_calcs.append(CalculationStepDetail(
            step_name="Sprawność odzysku ciepła",
            formula="η = Q_actual / Q_avail",
            substitution=f"η = {Q_actual:.2f} / {Q_available:.2f}",
            result=eta_thermal,
            unit="-",
            explanation="Procent ciepła odzyskanego z gazów spalinowych"
        ))

        # 14. Net efficiency
        eta_net = eta_thermal - (Q_wall / max(Q_available, 1))
        eta_net = min(max(eta_net, 0.0), 1.0)
        perf_calcs.append(CalculationStepDetail(
            step_name="Sprawność netto",
            formula="η_net = η - (Q_loss / Q_avail)",
            substitution=f"η_net = {eta_thermal:.3f} - ({Q_wall:.2f} / {Q_available:.2f})",
            result=eta_net,
            unit="-",
            explanation="Sprawność skorygowana o straty przez ściany"
        ))

        # 15. Pressure drop
        f = 150 / Re + 1.75
        dp = f * (h / s) * 0.5 * rho_gas * (v ** 2)
        perf_calcs.append(CalculationStepDetail(
            step_name="Spadek ciśnienia",
            formula="Δp = f × (H/d) × 0.5 × ρ × v²",
            substitution=f"Δp = {f:.2f} × ({h}/{s}) × 0.5 × {rho_gas} × {v:.2f}²",
            result=dp,
            unit="Pa",
            explanation="Opór przepływu przez warstwę cegieł checker"
        ))

        # --- ECONOMIC CALCULATIONS ---
        econ_calcs = []

        # Baseline comparison (assume 80% baseline efficiency)
        baseline_efficiency = 0.80
        efficiency_improvement = ((eta_net - baseline_efficiency) / baseline_efficiency) * 100

        econ_calcs.append(CalculationStepDetail(
            step_name="Poprawa sprawności",
            formula="Δη = ((η_new - η_base) / η_base) × 100%",
            substitution=f"Δη = (({eta_net:.3f} - {baseline_efficiency}) / {baseline_efficiency}) × 100%",
            result=efficiency_improvement,
            unit="%",
            explanation="Procentowa poprawa względem bazowej sprawności 80%"
        ))

        # Fuel savings
        fuel_savings = efficiency_improvement
        econ_calcs.append(CalculationStepDetail(
            step_name="Oszczędność paliwa",
            formula="Fuel_savings ≈ Δη",
            substitution=f"Fuel_savings = {efficiency_improvement:.2f}%",
            result=fuel_savings,
            unit="%",
            explanation="Procentowa redukcja zużycia paliwa"
        ))

        # CO2 reduction
        co2_reduction = fuel_savings * 0.95
        econ_calcs.append(CalculationStepDetail(
            step_name="Redukcja CO₂",
            formula="CO₂_reduction = Fuel_savings × 0.95",
            substitution=f"CO₂ = {fuel_savings:.2f} × 0.95",
            result=co2_reduction,
            unit="%",
            explanation="Redukcja emisji CO₂ (nieco mniejsza niż oszczędność paliwa)"
        ))

        # Annual savings (assuming 50k€ base fuel cost)
        base_fuel_cost = 50000
        annual_savings = (fuel_savings / 100) * base_fuel_cost
        econ_calcs.append(CalculationStepDetail(
            step_name="Oszczędności roczne",
            formula="Savings = (Fuel_savings / 100) × Cost_base",
            substitution=f"Savings = ({fuel_savings:.2f} / 100) × {base_fuel_cost}€",
            result=annual_savings,
            unit="€/rok",
            explanation="Szacunkowe oszczędności przy bazowym koszcie paliwa 50 tys. €/rok"
        ))

        # --- FINAL METRICS ---
        final_metrics = {
            "thermal_efficiency": eta_net,
            "heat_transfer_rate": Q_actual,
            "pressure_drop": dp,
            "ntu_value": NTU,
            "effectiveness": effectiveness,
            "heat_transfer_coefficient": htc,
            "surface_area": A_surface,
            "wall_heat_loss": Q_wall,
            "reynolds_number": Re,
            "nusselt_number": Nu
        }

        # --- CONSTRAINTS CHECK ---
        constraints_check = {
            "pressure_drop": {
                "value": dp,
                "limit": 2000,
                "status": "OK" if dp < 2000 else "VIOLATED",
                "margin": 2000 - dp,
                "explanation": "Spadek ciśnienia musi być < 2000 Pa"
            },
            "thermal_efficiency": {
                "value": eta_net,
                "limit": 0.2,
                "status": "OK" if eta_net > 0.2 else "VIOLATED",
                "margin": eta_net - 0.2,
                "explanation": "Sprawność musi być > 20%"
            },
            "heat_transfer_coefficient": {
                "value": htc,
                "limit": 50,
                "status": "OK" if htc > 50 else "VIOLATED",
                "margin": htc - 50,
                "explanation": "Współczynnik HTC musi być > 50 W/(m²·K)"
            }
        }

        # --- OPERATING CONDITIONS & MATERIAL PROPERTIES ---
        operating_conditions = {
            "gas_temp_inlet": T_in,
            "gas_temp_outlet": T_out,
            "mass_flow_rate": m_flow,
            "cross_section_area": A_cross,
            "regenerator_length": L,
            "regenerator_width": W
        }

        material_properties = {
            "checker_conductivity": k_checker,
            "checker_specific_heat": cp_checker,
            "checker_density": rho_checker,
            "gas_density": rho_gas,
            "gas_viscosity": mu_gas,
            "gas_conductivity": k_gas,
            "gas_specific_heat": cp_gas,
            "prandtl_number": Pr
        }

        return OptimizationCalculationPreview(
            scenario_id=scenario_id,
            scenario_name=scenario.name,
            design_variables=design_vars,
            geometry_calculations=geometry_calcs,
            heat_transfer_calculations=ht_calcs,
            performance_calculations=perf_calcs,
            economic_calculations=econ_calcs,
            final_metrics=final_metrics,
            constraints_check=constraints_check,
            operating_conditions=operating_conditions,
            material_properties=material_properties
        )

    # Helper methods
    async def _get_scenario(self, scenario_id: str) -> Optional[OptimizationScenario]:
        """Get optimization scenario by ID."""
        stmt = select(OptimizationScenario).where(OptimizationScenario.id == scenario_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_configuration(self, config_id: str) -> Optional[RegeneratorConfiguration]:
        """Get regenerator configuration by ID."""
        stmt = select(RegeneratorConfiguration).where(RegeneratorConfiguration.id == config_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_job(self, job_id: str) -> Optional[OptimizationJob]:
        """Get optimization job by ID."""
        stmt = select(OptimizationJob).where(OptimizationJob.id == job_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _update_job_status(
        self,
        job_id: str,
        status: OptimizationStatus,
        error_message: Optional[str] = None
    ):
        """Update job status."""
        job = await self._get_job(job_id)
        if job:
            job.status = status
            if error_message:
                job.error_message = error_message
            if status == OptimizationStatus.RUNNING and not job.started_at:
                job.started_at = datetime.now(UTC)
            if status in [OptimizationStatus.COMPLETED, OptimizationStatus.FAILED]:
                job.completed_at = datetime.now(UTC)
                if job.started_at:
                    job.runtime_seconds = (job.completed_at - job.started_at).total_seconds()

            await self.db.commit()