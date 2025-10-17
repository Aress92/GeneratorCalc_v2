"""
Optimization models for regenerator optimization engine.

Modele optymalizacji dla silnika optymalizacji regeneratorów.
"""

from datetime import datetime, UTC
from enum import Enum
from typing import Dict, List, Optional
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, Integer, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR

from app.core.database import Base


class OptimizationStatus(str, Enum):
    """Status of optimization job."""
    PENDING = "pending"
    INITIALIZING = "initializing"
    RUNNING = "running"
    CONVERGING = "converging"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class OptimizationObjective(str, Enum):
    """Optimization objectives."""
    MINIMIZE_FUEL_CONSUMPTION = "minimize_fuel_consumption"
    MINIMIZE_CO2_EMISSIONS = "minimize_co2_emissions"
    MAXIMIZE_EFFICIENCY = "maximize_efficiency"
    MINIMIZE_COST = "minimize_cost"
    MULTI_OBJECTIVE = "multi_objective"


class OptimizationAlgorithm(str, Enum):
    """Available optimization algorithms."""
    SLSQP = "slsqp"
    GENETIC = "genetic"
    DIFFERENTIAL_EVOLUTION = "differential_evolution"
    PSO = "particle_swarm"
    SIMULATED_ANNEALING = "simulated_annealing"


class ScenarioType(str, Enum):
    """Types of optimization scenarios."""
    BASELINE = "baseline"
    GEOMETRY_OPTIMIZATION = "geometry_optimization"
    MATERIAL_OPTIMIZATION = "material_optimization"
    OPERATING_CONDITIONS = "operating_conditions"
    COMPREHENSIVE = "comprehensive"


class OptimizationScenario(Base):
    """Optimization scenario configuration."""

    __tablename__ = "optimization_scenarios"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)

    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    scenario_type = Column(String(50), nullable=False)

    # Source regenerator configuration
    base_configuration_id = Column(CHAR(36), ForeignKey("regenerator_configurations.id"), nullable=False)

    # Optimization configuration
    objective = Column(String(50), nullable=False)
    algorithm = Column(String(50), nullable=False, default=OptimizationAlgorithm.SLSQP)

    # Optimization parameters
    optimization_config = Column(JSON, nullable=False)  # Algorithm-specific parameters
    constraints_config = Column(JSON, nullable=True)    # Optimization constraints
    bounds_config = Column(JSON, nullable=True)         # Variable bounds

    # Variables to optimize
    design_variables = Column(JSON, nullable=False)     # Variables and their ranges
    objective_weights = Column(JSON, nullable=True)     # Multi-objective weights

    # Termination criteria
    max_iterations = Column(Integer, default=1000)
    max_function_evaluations = Column(Integer, default=5000)
    tolerance = Column(Float, default=1e-6)
    max_runtime_minutes = Column(Integer, default=120)

    # Status and progress
    status = Column(String(20), nullable=False, default="active")  # active, archived, deleted
    is_active = Column(Boolean, default=True)
    is_template = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    user = relationship("User")
    base_configuration = relationship("RegeneratorConfiguration")
    optimization_jobs = relationship("OptimizationJob", back_populates="scenario")


class OptimizationJob(Base):
    """Individual optimization job execution."""

    __tablename__ = "optimization_jobs"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scenario_id = Column(CHAR(36), ForeignKey("optimization_scenarios.id"), nullable=False)
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)

    # Job metadata
    job_name = Column(String(255), nullable=True)
    celery_task_id = Column(String(255), nullable=True, unique=True)

    # Execution parameters (snapshot from scenario at execution time)
    execution_config = Column(JSON, nullable=False)
    initial_values = Column(JSON, nullable=False)

    # Progress tracking
    status = Column(String(20), nullable=False, default=OptimizationStatus.PENDING)
    current_iteration = Column(Integer, default=0)
    current_function_evaluations = Column(Integer, default=0)
    progress_percentage = Column(Float, default=0.0)

    # Execution times
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    estimated_completion_at = Column(DateTime, nullable=True)
    runtime_seconds = Column(Float, nullable=True)

    # Results summary
    final_objective_value = Column(Float, nullable=True)
    convergence_achieved = Column(Boolean, default=False)
    convergence_criteria = Column(JSON, nullable=True)

    # Error handling
    error_message = Column(Text, nullable=True)
    error_traceback = Column(Text, nullable=True)
    warning_messages = Column(JSON, default=list)

    # Resource usage
    memory_usage_mb = Column(Float, nullable=True)
    cpu_usage_percentage = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    scenario = relationship("OptimizationScenario", back_populates="optimization_jobs")
    user = relationship("User")
    results = relationship("OptimizationResult", back_populates="job", cascade="all, delete-orphan")
    iterations = relationship("OptimizationIteration", back_populates="job", cascade="all, delete-orphan")


class OptimizationResult(Base):
    """Final optimization results."""

    __tablename__ = "optimization_results"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(CHAR(36), ForeignKey("optimization_jobs.id"), nullable=False)

    # Optimized configuration
    optimized_configuration = Column(JSON, nullable=False)  # Final optimized parameters
    design_variables_final = Column(JSON, nullable=False)   # Final variable values

    # Objective function results
    objective_value = Column(Float, nullable=False)
    objective_components = Column(JSON, nullable=True)      # Multi-objective breakdown
    constraint_violations = Column(JSON, nullable=True)     # Any constraint violations

    # Performance improvements
    baseline_metrics = Column(JSON, nullable=False)         # Original performance
    optimized_metrics = Column(JSON, nullable=False)        # Improved performance
    improvement_percentages = Column(JSON, nullable=False)  # % improvements

    # Economic analysis
    fuel_savings_percentage = Column(Float, nullable=True)
    co2_reduction_percentage = Column(Float, nullable=True)
    annual_cost_savings = Column(Float, nullable=True)
    payback_period_months = Column(Float, nullable=True)

    # Technical validation
    thermal_efficiency = Column(Float, nullable=True)       # %
    pressure_drop = Column(Float, nullable=True)            # Pa
    heat_transfer_coefficient = Column(Float, nullable=True) # W/m²K
    ntu_value = Column(Float, nullable=True)                # Number of Transfer Units

    # Geometry results (if geometry optimization)
    optimized_geometry = Column(JSON, nullable=True)
    volume_changes = Column(JSON, nullable=True)
    surface_area_changes = Column(JSON, nullable=True)

    # Material results (if material optimization)
    material_recommendations = Column(JSON, nullable=True)
    material_cost_impact = Column(JSON, nullable=True)

    # Sensitivity analysis
    sensitivity_analysis = Column(JSON, nullable=True)      # Variable sensitivity
    robustness_metrics = Column(JSON, nullable=True)        # Solution robustness

    # Quality metrics
    solution_feasibility = Column(Float, nullable=True)     # 0-1 score
    optimization_confidence = Column(Float, nullable=True)  # 0-1 score

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    job = relationship("OptimizationJob", back_populates="results")


class OptimizationIteration(Base):
    """Individual optimization iteration data for tracking progress."""

    __tablename__ = "optimization_iterations"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(CHAR(36), ForeignKey("optimization_jobs.id"), nullable=False)

    # Iteration metadata
    iteration_number = Column(Integer, nullable=False)
    function_evaluation = Column(Integer, nullable=False)

    # Variable values at this iteration
    design_variables = Column(JSON, nullable=False)

    # Objective function value
    objective_value = Column(Float, nullable=False)
    objective_components = Column(JSON, nullable=True)

    # Constraint values
    constraint_values = Column(JSON, nullable=True)
    constraint_violations = Column(JSON, nullable=True)

    # Algorithm-specific data
    gradient = Column(JSON, nullable=True)
    step_size = Column(Float, nullable=True)
    convergence_metrics = Column(JSON, nullable=True)

    # Performance metrics at this iteration
    performance_metrics = Column(JSON, nullable=True)

    # Computation time
    evaluation_time_seconds = Column(Float, nullable=True)

    # Flags
    is_feasible = Column(Boolean, default=True)
    is_improvement = Column(Boolean, default=False)

    # Timestamp
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    job = relationship("OptimizationJob", back_populates="iterations")


class OptimizationTemplate(Base):
    """Pre-configured optimization templates."""

    __tablename__ = "optimization_templates"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Template metadata
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    template_type = Column(String(50), nullable=False)
    regenerator_type = Column(String(50), nullable=True)    # crown, end-port, cross-fired

    # Template configuration
    template_config = Column(JSON, nullable=False)          # Complete scenario template
    default_parameters = Column(JSON, nullable=True)        # Default parameter values

    # Usage and popularity
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, nullable=True)             # % of successful optimizations
    average_improvement = Column(Float, nullable=True)      # Average fuel savings %

    # Status
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)            # Engineering validated

    # Creator information
    created_by_user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    created_by = relationship("User")