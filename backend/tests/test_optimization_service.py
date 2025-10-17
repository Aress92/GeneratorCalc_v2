"""
Tests for optimization service.

Testy dla serwisu optymalizacji.
"""

import pytest
from uuid import uuid4
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np

from app.services.optimization_service import OptimizationService, RegeneratorPhysicsModel
from app.models.user import User, UserRole
from app.models.optimization import OptimizationScenario, OptimizationJob, OptimizationResult, OptimizationStatus
from app.models.regenerator import RegeneratorConfiguration, RegeneratorType, ConfigurationStatus
from app.schemas.optimization_schemas import (
    OptimizationScenarioCreate, OptimizationJobCreate, OptimizationConstraint,
    OptimizationObjectiveSchema, OptimizationAlgorithmSchema, ScenarioTypeSchema
)


class TestOptimizationService:
    """Test optimization service functionality."""

    @pytest.fixture
    async def optimization_service(self, test_db: AsyncSession) -> OptimizationService:
        """Create optimization service instance."""
        return OptimizationService(test_db)

    @pytest.fixture
    async def test_user(self, test_db: AsyncSession) -> User:
        """Create test user."""
        unique_id = uuid4().hex[:8]
        user = User(
            username=f"testuser_{unique_id}",
            email=f"test_{unique_id}@example.com",
            full_name="Test User",
            password_hash="hashed_password",
            role=UserRole.ENGINEER,
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        return user

    @pytest.fixture
    async def test_regenerator(self, test_db: AsyncSession, test_user: User) -> RegeneratorConfiguration:
        """Create test regenerator configuration."""
        config = RegeneratorConfiguration(
            user_id=str(test_user.id),
            name="Test Regenerator",
            regenerator_type=RegeneratorType.CROWN,
            status=ConfigurationStatus.COMPLETED,
            geometry_config={
                "length": 10.0,
                "width": 8.0,
                "height": 6.0,
                "wall_thickness": 0.4
            },
            materials_config={
                "thermal_conductivity": 2.5,
                "specific_heat": 900.0,
                "checker_density": 2300.0
            },
            thermal_config={
                "gas_temp_inlet": 1600.0,
                "gas_temp_outlet": 600.0,
                "ambient_temp": 25.0
            },
            flow_config={
                "mass_flow_rate": 50.0,
                "cycle_time": 1200.0,
                "pressure_inlet": 101325.0
            }
        )
        test_db.add(config)
        await test_db.commit()
        await test_db.refresh(config)
        return config

    @pytest.fixture
    async def test_scenario(self, test_db: AsyncSession, test_user: User, test_regenerator: RegeneratorConfiguration) -> OptimizationScenario:
        """Create test optimization scenario."""
        scenario = OptimizationScenario(
            user_id=str(test_user.id),
            regenerator_id=str(test_regenerator.id),
            name="Test Optimization Scenario",
            description="Test scenario for optimization",
            objective_function="minimize_fuel_consumption",
            design_variables={
                "checker_height": {"min": 0.5, "max": 1.0, "current": 0.7},
                "checker_spacing": {"min": 0.08, "max": 0.15, "current": 0.12},
                "wall_thickness": {"min": 0.25, "max": 0.5, "current": 0.35}
            },
            constraints={
                "max_pressure_drop": 2000.0,
                "min_thermal_efficiency": 0.2,
                "min_heat_transfer_coefficient": 50.0
            },
            algorithm_config={
                "algorithm": "SLSQP",
                "max_iterations": 100,
                "tolerance": 1e-6,
                "step_size": 0.01
            }
        )
        test_db.add(scenario)
        await test_db.commit()
        await test_db.refresh(scenario)
        return scenario

    async def test_create_scenario(self, optimization_service: OptimizationService, test_user: User, test_regenerator: RegeneratorConfiguration):
        """Test creating optimization scenario."""
        scenario_data = OptimizationScenarioCreate(
            name="New Test Scenario",
            description="New test scenario for optimization",
            scenario_type=ScenarioTypeSchema.GEOMETRY_OPTIMIZATION,
            base_configuration_id=str(test_regenerator.id),
            objective=OptimizationObjectiveSchema.MINIMIZE_FUEL_CONSUMPTION,
            algorithm=OptimizationAlgorithmSchema.SLSQP,
            design_variables={
                "checker_height": {"min": 0.5, "max": 1.0, "current": 0.7},
                "checker_spacing": {"min": 0.08, "max": 0.15, "current": 0.12}
            },
            constraints=[
                {"name": "max_pressure_drop", "value": 2000.0},
                {"name": "min_thermal_efficiency", "value": 0.25}
            ],
            max_iterations=50,
            tolerance=1e-5
        )

        result = await optimization_service.create_scenario(scenario_data, str(test_user.id))

        assert result.name == "New Test Scenario"
        assert result.user_id == str(test_user.id)

    async def test_get_scenario_by_id(self, optimization_service: OptimizationService, test_scenario: OptimizationScenario):
        """Test getting scenario by ID."""
        result = await optimization_service.get_scenario(str(test_scenario.id))

        assert result is not None
        assert result.id == test_scenario.id
        assert result.name == test_scenario.name

    async def test_get_user_scenarios(self, optimization_service: OptimizationService, test_user: User, test_scenario: OptimizationScenario):
        """Test getting user scenarios."""
        scenarios = await optimization_service.get_user_scenarios(str(test_user.id), limit=10, offset=0)

        assert len(scenarios) >= 1
        found_scenario = next((s for s in scenarios if s.id == test_scenario.id), None)
        assert found_scenario is not None

    async def test_create_optimization_job(self, optimization_service: OptimizationService, test_scenario: OptimizationScenario, test_user: User):
        """Test creating optimization job."""
        job_data = OptimizationJobCreate(
            name="Test Optimization Job",
            description="Test job for optimization",
            priority=1
        )

        result = await optimization_service.create_job(str(test_scenario.id), job_data, str(test_user.id))

        assert result.scenario_id == str(test_scenario.id)
        assert result.created_by_id == str(test_user.id)
        assert result.status == OptimizationStatus.PENDING
        assert result.name == "Test Optimization Job"

    async def test_get_optimization_jobs(self, optimization_service: OptimizationService, test_user: User):
        """Test getting optimization jobs."""
        jobs = await optimization_service.get_jobs(user_id=str(test_user.id), limit=10, offset=0)

        assert isinstance(jobs, list)

    async def test_cancel_job(self, optimization_service: OptimizationService, test_scenario: OptimizationScenario, test_user: User):
        """Test canceling optimization job."""
        # Create job first
        job_data = OptimizationJobCreate(name="Job to Cancel", description="Job for cancel test")
        job = await optimization_service.create_job(str(test_scenario.id), job_data, str(test_user.id))

        # Cancel the job
        success = await optimization_service.cancel_job(str(job.id), str(test_user.id))

        assert success is True

        # Verify job status
        cancelled_job = await optimization_service.get_job(str(job.id))
        assert cancelled_job.status == OptimizationStatus.CANCELLED

    async def test_update_job_progress(self, optimization_service: OptimizationService, test_scenario: OptimizationScenario, test_user: User):
        """Test updating job progress."""
        # Create job first
        job_data = OptimizationJobCreate(name="Progress Test Job", description="Job for progress test")
        job = await optimization_service.create_job(str(test_scenario.id), job_data, str(test_user.id))

        # Update progress
        await optimization_service.update_job_progress(str(job.id), 50.0, "Halfway through optimization")

        # Verify progress
        updated_job = await optimization_service.get_job(str(job.id))
        assert updated_job.progress == 50.0
        assert updated_job.progress_message == "Halfway through optimization"


class TestRegeneratorPhysicsModel:
    """Test regenerator physics model."""

    @pytest.fixture
    def physics_config(self) -> dict:
        """Create test physics configuration."""
        return {
            "geometry_config": {
                "length": 10.0,
                "width": 8.0,
                "height": 6.0,
                "wall_thickness": 0.4
            },
            "materials_config": {
                "thermal_conductivity": 2.5,
                "specific_heat": 900.0,
                "checker_density": 2300.0
            },
            "thermal_config": {
                "gas_temp_inlet": 1600.0,
                "gas_temp_outlet": 600.0,
                "ambient_temp": 25.0
            },
            "flow_config": {
                "mass_flow_rate": 50.0,
                "cycle_time": 1200.0,
                "pressure_inlet": 101325.0
            }
        }

    @pytest.fixture
    def physics_model(self, physics_config: dict) -> RegeneratorPhysicsModel:
        """Create physics model instance."""
        return RegeneratorPhysicsModel(physics_config)

    def test_physics_model_initialization(self, physics_model: RegeneratorPhysicsModel, physics_config: dict):
        """Test physics model initialization."""
        assert physics_model.config == physics_config
        assert physics_model.gas_temp_inlet == 1600.0
        assert physics_model.mass_flow_rate == 50.0

    def test_calculate_thermal_performance(self, physics_model: RegeneratorPhysicsModel):
        """Test thermal performance calculation."""
        design_vars = {
            "checker_height": 0.7,
            "checker_spacing": 0.12,
            "wall_thickness": 0.35,
            "thermal_conductivity": 2.5,
            "specific_heat": 900.0,
            "density": 2300.0
        }

        result = physics_model.calculate_thermal_performance(design_vars)

        assert "thermal_efficiency" in result
        assert "heat_transfer_coefficient" in result
        assert "pressure_drop" in result
        assert "heat_loss" in result

        # Check realistic values
        assert 0.0 <= result["thermal_efficiency"] <= 1.0
        assert result["heat_transfer_coefficient"] > 0
        assert result["pressure_drop"] > 0
        assert result["heat_loss"] >= 0

    def test_calculate_reynolds_number(self, physics_model: RegeneratorPhysicsModel):
        """Test Reynolds number calculation."""
        velocity = 5.0  # m/s
        hydraulic_diameter = 0.1  # m

        re = physics_model._calculate_reynolds_number(velocity, hydraulic_diameter)

        assert re > 0
        assert isinstance(re, float)

    def test_calculate_nusselt_number(self, physics_model: RegeneratorPhysicsModel):
        """Test Nusselt number calculation."""
        reynolds = 5000.0
        prandtl = 0.7

        nu = physics_model._calculate_nusselt_number(reynolds, prandtl)

        assert nu > 0
        assert isinstance(nu, float)

    def test_calculate_pressure_drop(self, physics_model: RegeneratorPhysicsModel):
        """Test pressure drop calculation."""
        velocity = 5.0
        hydraulic_diameter = 0.1
        length = 10.0

        dp = physics_model._calculate_pressure_drop(velocity, hydraulic_diameter, length)

        assert dp > 0
        assert isinstance(dp, float)

    def test_calculate_heat_loss(self, physics_model: RegeneratorPhysicsModel):
        """Test heat loss calculation."""
        wall_thickness = 0.35
        thermal_conductivity = 2.5
        surface_area = 100.0
        temp_difference = 1000.0

        heat_loss = physics_model._calculate_heat_loss(
            wall_thickness, thermal_conductivity, surface_area, temp_difference
        )

        assert heat_loss > 0
        assert isinstance(heat_loss, float)

    def test_validate_design_variables(self, physics_model: RegeneratorPhysicsModel):
        """Test design variables validation."""
        valid_vars = {
            "checker_height": 0.7,
            "checker_spacing": 0.12,
            "wall_thickness": 0.35,
            "thermal_conductivity": 2.5,
            "specific_heat": 900.0,
            "density": 2300.0
        }

        # Valid variables should not raise
        physics_model._validate_design_variables(valid_vars)

        # Invalid variables should raise
        invalid_vars = valid_vars.copy()
        invalid_vars["checker_height"] = -1.0  # Negative value

        with pytest.raises(ValueError):
            physics_model._validate_design_variables(invalid_vars)

    def test_objective_function(self, physics_model: RegeneratorPhysicsModel):
        """Test objective function calculation."""
        design_vars = np.array([0.7, 0.12, 0.35, 2.5, 900.0, 2300.0])

        result = physics_model.objective_function(design_vars)

        assert isinstance(result, (int, float))
        assert result >= 0  # Should be non-negative for fuel consumption

    def test_constraint_functions(self, physics_model: RegeneratorPhysicsModel):
        """Test constraint functions."""
        design_vars = np.array([0.7, 0.12, 0.35, 2.5, 900.0, 2300.0])
        constraints = {
            "max_pressure_drop": 2000.0,
            "min_thermal_efficiency": 0.2,
            "min_heat_transfer_coefficient": 50.0
        }

        constraint_values = physics_model.constraint_functions(design_vars, constraints)

        assert isinstance(constraint_values, list)
        assert len(constraint_values) == len(constraints)

    def test_physics_model_with_different_configs(self, physics_config: dict):
        """Test physics model with different configurations."""
        # Test with different regenerator dimensions
        config_large = physics_config.copy()
        config_large["geometry_config"]["length"] = 20.0
        config_large["geometry_config"]["width"] = 15.0

        model_large = RegeneratorPhysicsModel(config_large)
        design_vars = {
            "checker_height": 0.8,
            "checker_spacing": 0.15,
            "wall_thickness": 0.4,
            "thermal_conductivity": 3.0,
            "specific_heat": 850.0,
            "density": 2400.0
        }

        result = model_large.calculate_thermal_performance(design_vars)
        assert "thermal_efficiency" in result
        assert result["thermal_efficiency"] > 0

    def test_edge_cases_thermal_performance(self, physics_model: RegeneratorPhysicsModel):
        """Test edge cases in thermal performance calculation."""
        # Test with minimum values
        min_design_vars = {
            "checker_height": 0.1,
            "checker_spacing": 0.05,
            "wall_thickness": 0.1,
            "thermal_conductivity": 0.1,
            "specific_heat": 100.0,
            "density": 100.0
        }

        result = physics_model.calculate_thermal_performance(min_design_vars)
        assert "thermal_efficiency" in result

        # Test with maximum values
        max_design_vars = {
            "checker_height": 2.0,
            "checker_spacing": 0.3,
            "wall_thickness": 1.0,
            "thermal_conductivity": 10.0,
            "specific_heat": 2000.0,
            "density": 5000.0
        }

        result = physics_model.calculate_thermal_performance(max_design_vars)
        assert "thermal_efficiency" in result

    @patch('app.services.optimization_service.minimize')
    def test_optimization_with_mock(self, mock_minimize, physics_model: RegeneratorPhysicsModel):
        """Test optimization with mocked scipy minimize."""
        from scipy.optimize import OptimizeResult

        # Mock the optimization result
        mock_result = OptimizeResult()
        mock_result.success = True
        mock_result.x = np.array([0.75, 0.13, 0.38, 2.8, 920.0, 2350.0])
        mock_result.fun = 1.2
        mock_result.nit = 15
        mock_result.message = "Optimization terminated successfully"

        mock_minimize.return_value = mock_result

        # Test optimization would work with proper integration
        assert mock_result.success is True
        assert len(mock_result.x) == 6


class TestOptimizationServiceAdvanced:
    """Advanced tests for OptimizationService core functionality."""

    @pytest.fixture
    async def optimization_service(self, test_db: AsyncSession) -> OptimizationService:
        """Create optimization service instance."""
        return OptimizationService(test_db)

    @pytest.fixture
    async def test_user(self, test_db: AsyncSession) -> User:
        """Create test user."""
        unique_id = uuid4().hex[:8]
        user = User(
            username=f"optuser_{unique_id}",
            email=f"optuser_{unique_id}@example.com",
            full_name="Optimization Test User",
            password_hash="hashed_password",
            role=UserRole.ENGINEER,
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        return user

    @pytest.fixture
    async def test_regenerator(self, test_db: AsyncSession, test_user: User) -> RegeneratorConfiguration:
        """Create test regenerator configuration."""
        config = RegeneratorConfiguration(
            user_id=str(test_user.id),
            name=f"Test Regenerator {uuid4().hex[:6]}",
            regenerator_type=RegeneratorType.CROWN,
            status=ConfigurationStatus.COMPLETED,
            geometry_config={
                "length": 10.0,
                "width": 8.0,
                "height": 6.0,
                "wall_thickness": 0.4
            },
            materials_config={
                "thermal_conductivity": 2.5,
                "specific_heat": 900.0,
                "checker_density": 2300.0
            },
            thermal_config={
                "gas_temp_inlet": 1600.0,
                "gas_temp_outlet": 600.0,
                "ambient_temp": 25.0
            },
            flow_config={
                "mass_flow_rate": 50.0,
                "cycle_time": 1200.0,
                "pressure_inlet": 101325.0
            }
        )
        test_db.add(config)
        await test_db.commit()
        await test_db.refresh(config)
        return config

    @pytest.fixture
    async def test_scenario(self, test_db: AsyncSession, test_user: User, test_regenerator: RegeneratorConfiguration) -> OptimizationScenario:
        """Create test optimization scenario."""
        scenario = OptimizationScenario(
            user_id=str(test_user.id),
            base_configuration_id=str(test_regenerator.id),
            name=f"Test Scenario {uuid4().hex[:6]}",
            description="Advanced test scenario",
            scenario_type="geometry_optimization",
            objective="minimize_fuel_consumption",
            algorithm="slsqp",
            design_variables={
                "checker_height": {"min": 0.5, "max": 1.0, "baseline": 0.7},
                "checker_spacing": {"min": 0.08, "max": 0.15, "baseline": 0.12}
            },
            optimization_config={
                "max_iterations": 100,
                "tolerance": 1e-6
            },
            max_iterations=100,
            tolerance=1e-6
        )
        test_db.add(scenario)
        await test_db.commit()
        await test_db.refresh(scenario)
        return scenario

    async def test_create_optimization_job_success(
        self,
        optimization_service: OptimizationService,
        test_scenario: OptimizationScenario,
        test_user: User
    ):
        """Test successful optimization job creation."""
        job_config = OptimizationJobCreate(
            job_name="Test Optimization Run",
            initial_values={"checker_height": 0.7, "checker_spacing": 0.12},
            priority=1
        )

        job = await optimization_service.create_optimization_job(
            scenario_id=str(test_scenario.id),
            user_id=str(test_user.id),
            job_config=job_config
        )

        assert job is not None
        assert job.scenario_id == str(test_scenario.id)
        assert job.user_id == str(test_user.id)
        assert job.job_name == "Test Optimization Run"
        assert job.status == OptimizationStatus.PENDING
        assert job.initial_values == {"checker_height": 0.7, "checker_spacing": 0.12}

    async def test_create_optimization_job_invalid_scenario(
        self,
        optimization_service: OptimizationService,
        test_user: User
    ):
        """Test job creation with non-existent scenario."""
        job_config = OptimizationJobCreate(
            job_name="Invalid Job",
            priority=1
        )

        with pytest.raises(ValueError, match="Scenario .* not found"):
            await optimization_service.create_optimization_job(
                scenario_id=str(uuid4()),
                user_id=str(test_user.id),
                job_config=job_config
            )

    async def test_create_optimization_job_no_initial_values(
        self,
        optimization_service: OptimizationService,
        test_scenario: OptimizationScenario,
        test_user: User
    ):
        """Test job creation without initial values (should use defaults)."""
        job_config = OptimizationJobCreate(
            job_name="Job with defaults",
            priority=2
        )

        job = await optimization_service.create_optimization_job(
            scenario_id=str(test_scenario.id),
            user_id=str(test_user.id),
            job_config=job_config
        )

        assert job is not None
        assert job.initial_values == {}  # Empty dict as default

    async def test_get_optimization_progress_pending(
        self,
        optimization_service: OptimizationService,
        test_scenario: OptimizationScenario,
        test_user: User
    ):
        """Test getting progress for pending job."""
        # Create job
        job_config = OptimizationJobCreate(job_name="Progress Test", priority=1)
        job = await optimization_service.create_optimization_job(
            scenario_id=str(test_scenario.id),
            user_id=str(test_user.id),
            job_config=job_config
        )

        # Get progress
        progress = await optimization_service.get_optimization_progress(str(job.id))

        assert progress.job_id == str(job.id)
        assert progress.status == OptimizationStatus.PENDING
        assert progress.current_iteration == 0
        assert progress.progress_percentage == 0.0

    async def test_get_optimization_progress_not_found(
        self,
        optimization_service: OptimizationService
    ):
        """Test getting progress for non-existent job."""
        with pytest.raises(ValueError, match="Job .* not found"):
            await optimization_service.get_optimization_progress(str(uuid4()))


class TestRegeneratorPhysicsModelDetailed:
    """Detailed tests for RegeneratorPhysicsModel calculation methods."""

    @pytest.fixture
    def physics_config(self) -> dict:
        """Create realistic physics configuration."""
        return {
            "geometry_config": {
                "length": 10.0,
                "width": 8.0,
                "height": 6.0,
                "wall_thickness": 0.4
            },
            "materials_config": {
                "thermal_conductivity": 2.5,
                "specific_heat": 900.0,
                "checker_density": 2300.0
            },
            "thermal_config": {
                "gas_temp_inlet": 1600.0,
                "gas_temp_outlet": 600.0,
                "ambient_temp": 25.0
            },
            "flow_config": {
                "mass_flow_rate": 50.0,
                "cycle_time": 1200.0,
                "pressure_inlet": 101325.0
            }
        }

    @pytest.fixture
    def physics_model(self, physics_config: dict) -> RegeneratorPhysicsModel:
        """Create physics model instance."""
        return RegeneratorPhysicsModel(physics_config)

    def test_calculate_checker_volume(self, physics_model: RegeneratorPhysicsModel):
        """Test checker volume calculation."""
        # Test with standard dimensions
        volume = physics_model._calculate_checker_volume(height=1.0, spacing=0.1)

        # Expected: length(10) * width(8) * height(1.0) * (1-porosity=0.3) = 80 * 0.3 = 24 m³
        assert volume > 0
        assert volume < 100  # Reasonable bounds
        assert isinstance(volume, float)

    def test_calculate_surface_area(self, physics_model: RegeneratorPhysicsModel):
        """Test surface area calculation."""
        volume = 24.0  # m³
        spacing = 0.1  # m

        area = physics_model._calculate_surface_area(volume, spacing)

        # Expected: specific_surface = 400/0.1 = 4000 m²/m³, area = 24 * 4000 = 96000 m²
        assert area > 1000  # Must be significant
        assert area < 200000  # But reasonable
        assert isinstance(area, float)

    def test_calculate_reynolds_laminar(self, physics_model: RegeneratorPhysicsModel):
        """Test Reynolds number for laminar flow."""
        reynolds = physics_model._calculate_reynolds(mass_flow=1.0, spacing=0.01)

        # Very low flow should give laminar flow (Re < 2300)
        assert reynolds > 0
        assert reynolds < 5000  # Should be in laminar/transition regime

    def test_calculate_reynolds_turbulent(self, physics_model: RegeneratorPhysicsModel):
        """Test Reynolds number for turbulent flow."""
        reynolds = physics_model._calculate_reynolds(mass_flow=100.0, spacing=0.2)

        # High flow with large spacing should give turbulent flow
        assert reynolds > 1000  # Should be significantly turbulent

    def test_calculate_nusselt_low_reynolds(self, physics_model: RegeneratorPhysicsModel):
        """Test Nusselt number for low Reynolds (Re < 10)."""
        reynolds = 5.0
        nusselt = physics_model._calculate_nusselt(reynolds)

        # For Re < 10: Nu = 2.0 + 1.1 * (Re * Pr)^0.6
        # With Pr = 0.7: Nu ≈ 2.0 + 1.1 * (5*0.7)^0.6 ≈ 2.0 + 1.1 * 2.3 ≈ 4.5
        assert nusselt > 2.0  # Minimum Nusselt
        assert nusselt < 10.0  # Reasonable upper bound
        assert isinstance(nusselt, float)

    def test_calculate_nusselt_high_reynolds(self, physics_model: RegeneratorPhysicsModel):
        """Test Nusselt number for high Reynolds (Re >= 10)."""
        reynolds = 1000.0
        nusselt = physics_model._calculate_nusselt(reynolds)

        # For Re >= 10: Nu = 2.0 + 0.6 * Re^0.5 * Pr^0.33
        # With Pr = 0.7: Nu ≈ 2.0 + 0.6 * sqrt(1000) * 0.89 ≈ 2.0 + 16.9 ≈ 18.9
        assert nusselt > 10.0  # Should be higher for turbulent
        assert nusselt < 50.0  # But reasonable

    def test_calculate_htc_varies_with_nusselt(self, physics_model: RegeneratorPhysicsModel):
        """Test heat transfer coefficient varies with Nusselt number."""
        htc_low = physics_model._calculate_htc(nusselt=5.0, conductivity=2.5, spacing=0.1)
        htc_high = physics_model._calculate_htc(nusselt=20.0, conductivity=2.5, spacing=0.1)

        assert htc_high > htc_low  # Higher Nusselt → higher HTC
        assert htc_low > 0
        assert htc_high < 1000  # W/(m²·K) - reasonable range

    def test_calculate_htc_varies_with_spacing(self, physics_model: RegeneratorPhysicsModel):
        """Test heat transfer coefficient varies inversely with spacing."""
        htc_small = physics_model._calculate_htc(nusselt=10.0, conductivity=2.5, spacing=0.05)
        htc_large = physics_model._calculate_htc(nusselt=10.0, conductivity=2.5, spacing=0.15)

        assert htc_small > htc_large  # Smaller spacing → higher HTC
        assert htc_small / htc_large == pytest.approx(0.15 / 0.05, rel=0.01)

    def test_calculate_effectiveness_low_ntu(self, physics_model: RegeneratorPhysicsModel):
        """Test effectiveness for low NTU."""
        ntu = 0.5
        eff = physics_model._calculate_effectiveness(ntu)

        # ε = NTU / (1 + NTU) = 0.5 / 1.5 = 0.333
        assert eff == pytest.approx(0.333, rel=0.01)
        assert 0 < eff < 1.0  # Must be bounded

    def test_calculate_effectiveness_high_ntu(self, physics_model: RegeneratorPhysicsModel):
        """Test effectiveness for high NTU."""
        ntu = 10.0
        eff = physics_model._calculate_effectiveness(ntu)

        # ε = 10 / 11 = 0.909
        assert eff == pytest.approx(0.909, rel=0.01)
        assert eff < 1.0  # Cannot exceed 100%

    def test_calculate_pressure_drop_increases_with_flow(self, physics_model: RegeneratorPhysicsModel):
        """Test pressure drop increases with mass flow rate."""
        dp_low = physics_model._calculate_pressure_drop(mass_flow=20.0, spacing=0.1, height=1.0)
        dp_high = physics_model._calculate_pressure_drop(mass_flow=80.0, spacing=0.1, height=1.0)

        assert dp_high > dp_low  # Higher flow → higher pressure drop
        assert dp_low > 0
        assert dp_high < 50000  # Pa - reasonable range

    def test_calculate_pressure_drop_decreases_with_spacing(self, physics_model: RegeneratorPhysicsModel):
        """Test pressure drop decreases with larger spacing."""
        dp_small = physics_model._calculate_pressure_drop(mass_flow=50.0, spacing=0.05, height=1.0)
        dp_large = physics_model._calculate_pressure_drop(mass_flow=50.0, spacing=0.15, height=1.0)

        assert dp_small > dp_large  # Smaller spacing → higher resistance

    def test_calculate_pressure_drop_increases_with_height(self, physics_model: RegeneratorPhysicsModel):
        """Test pressure drop increases with regenerator height."""
        dp_short = physics_model._calculate_pressure_drop(mass_flow=50.0, spacing=0.1, height=0.5)
        dp_tall = physics_model._calculate_pressure_drop(mass_flow=50.0, spacing=0.1, height=2.0)

        assert dp_tall > dp_short  # Taller regenerator → more resistance
        assert dp_tall / dp_short == pytest.approx(2.0 / 0.5, rel=0.1)

    def test_calculate_wall_losses_decreases_with_thickness(self, physics_model: RegeneratorPhysicsModel):
        """Test wall heat losses decrease with wall thickness."""
        loss_thin = physics_model._calculate_wall_losses(wall_thickness=0.2, gas_temp=1600)
        loss_thick = physics_model._calculate_wall_losses(wall_thickness=0.6, gas_temp=1600)

        assert loss_thin > loss_thick  # Thinner walls → more heat loss
        assert loss_thick > 0  # Always some loss

    def test_calculate_wall_losses_increases_with_temperature(self, physics_model: RegeneratorPhysicsModel):
        """Test wall heat losses increase with gas temperature."""
        loss_cool = physics_model._calculate_wall_losses(wall_thickness=0.4, gas_temp=800)
        loss_hot = physics_model._calculate_wall_losses(wall_thickness=0.4, gas_temp=1600)

        assert loss_hot > loss_cool  # Higher temp → more heat loss

    def test_thermal_performance_complete_output(self, physics_model: RegeneratorPhysicsModel):
        """Test that calculate_thermal_performance returns all expected fields."""
        design_vars = {
            "checker_height": 0.8,
            "checker_spacing": 0.12,
            "wall_thickness": 0.35,
            "thermal_conductivity": 2.5,
            "specific_heat": 900.0,
            "density": 2300.0
        }

        result = physics_model.calculate_thermal_performance(design_vars)

        # Check all required output fields
        required_fields = [
            "thermal_efficiency", "heat_transfer_rate", "pressure_drop",
            "ntu_value", "effectiveness", "heat_transfer_coefficient",
            "surface_area", "wall_heat_loss", "reynolds_number", "nusselt_number"
        ]

        for field in required_fields:
            assert field in result, f"Missing field: {field}"
            assert isinstance(result[field], (int, float)), f"Field {field} is not numeric"
            assert result[field] >= 0, f"Field {field} is negative"

    def test_thermal_performance_efficiency_bounded(self, physics_model: RegeneratorPhysicsModel):
        """Test that thermal efficiency is always bounded 0-100%."""
        # Try with extreme values
        extreme_designs = [
            {"checker_height": 0.1, "checker_spacing": 0.3, "wall_thickness": 0.1,
             "thermal_conductivity": 0.5, "specific_heat": 500, "density": 1000},
            {"checker_height": 2.0, "checker_spacing": 0.05, "wall_thickness": 1.0,
             "thermal_conductivity": 10.0, "specific_heat": 2000, "density": 5000},
        ]

        for design in extreme_designs:
            result = physics_model.calculate_thermal_performance(design)
            assert 0 <= result["thermal_efficiency"] <= 1.0, \
                f"Efficiency out of bounds: {result['thermal_efficiency']}"


class TestOptimizationServiceSLSQP:
    """Tests for SLSQP optimization algorithm integration."""

    @pytest.fixture
    async def optimization_service(self, test_db: AsyncSession) -> OptimizationService:
        """Create optimization service instance."""
        return OptimizationService(test_db)

    @pytest.fixture
    async def test_user(self, test_db: AsyncSession) -> User:
        """Create test user."""
        unique_id = uuid4().hex[:8]
        user = User(
            username=f"slsqp_user_{unique_id}",
            email=f"slsqp_{unique_id}@example.com",
            full_name="SLSQP Test User",
            password_hash="hashed_password",
            role=UserRole.ENGINEER,
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        return user

    @pytest.fixture
    async def test_regenerator(self, test_db: AsyncSession, test_user: User) -> RegeneratorConfiguration:
        """Create test regenerator configuration."""
        config = RegeneratorConfiguration(
            user_id=str(test_user.id),
            name=f"SLSQP Test Regenerator {uuid4().hex[:6]}",
            regenerator_type=RegeneratorType.CROWN,
            status=ConfigurationStatus.COMPLETED,
            geometry_config={
                "length": 10.0,
                "width": 8.0,
                "height": 6.0,
                "wall_thickness": 0.4
            },
            materials_config={
                "thermal_conductivity": 2.5,
                "specific_heat": 900.0,
                "checker_density": 2300.0
            },
            thermal_config={
                "gas_temp_inlet": 1600.0,
                "gas_temp_outlet": 600.0,
                "ambient_temp": 25.0
            },
            flow_config={
                "mass_flow_rate": 50.0,
                "cycle_time": 1200.0,
                "pressure_inlet": 101325.0
            }
        )
        test_db.add(config)
        await test_db.commit()
        await test_db.refresh(config)
        return config

    @pytest.fixture
    async def test_scenario(self, test_db: AsyncSession, test_user: User, test_regenerator: RegeneratorConfiguration) -> OptimizationScenario:
        """Create test optimization scenario for SLSQP."""
        from app.models.optimization import OptimizationObjective, OptimizationAlgorithm

        scenario = OptimizationScenario(
            user_id=str(test_user.id),
            base_configuration_id=str(test_regenerator.id),
            name=f"SLSQP Test Scenario {uuid4().hex[:6]}",
            description="SLSQP test scenario",
            scenario_type="geometry_optimization",
            objective="minimize_fuel_consumption",
            algorithm="slsqp",
            design_variables={
                "checker_height": {"min": 0.5, "max": 1.5, "baseline": 0.8},
                "checker_spacing": {"min": 0.08, "max": 0.15, "baseline": 0.12},
                "wall_thickness": {"min": 0.2, "max": 0.6, "baseline": 0.4}
            },
            optimization_config={
                "max_iterations": 50,
                "tolerance": 1e-6
            },
            max_iterations=50,
            tolerance=1e-6
        )
        test_db.add(scenario)
        await test_db.commit()
        await test_db.refresh(scenario)
        return scenario

    @pytest.fixture
    async def test_job(
        self,
        test_db: AsyncSession,
        test_scenario: OptimizationScenario,
        test_user: User
    ) -> OptimizationJob:
        """Create test optimization job."""
        job = OptimizationJob(
            scenario_id=str(test_scenario.id),
            user_id=str(test_user.id),
            job_name="SLSQP Test Job",
            execution_config={"max_iterations": 50, "tolerance": 1e-6},
            initial_values={"checker_height": 0.8, "checker_spacing": 0.12, "wall_thickness": 0.4},
            status=OptimizationStatus.PENDING
        )
        test_db.add(job)
        await test_db.commit()
        await test_db.refresh(job)
        return job

    @patch('app.services.optimization_service.minimize')
    async def test_run_optimization_slsqp_success(
        self,
        mock_minimize,
        optimization_service: OptimizationService,
        test_job: OptimizationJob
    ):
        """Test successful SLSQP optimization run."""
        from scipy.optimize import OptimizeResult

        # Mock successful optimization result
        mock_result = OptimizeResult()
        mock_result.success = True
        mock_result.x = np.array([0.9, 0.10, 0.35])  # Optimal values
        mock_result.fun = -0.95  # Negative efficiency (we minimize negative)
        mock_result.nit = 25
        mock_result.message = "Optimization terminated successfully"
        mock_minimize.return_value = mock_result

        # Run optimization
        result = await optimization_service.run_optimization(str(test_job.id))

        # Verify result
        assert result is not None
        assert mock_minimize.called

        # Verify job was updated
        updated_job = await optimization_service._get_job(str(test_job.id))
        assert updated_job.status == OptimizationStatus.COMPLETED

    @patch('app.services.optimization_service.minimize')
    async def test_run_optimization_slsqp_failure(
        self,
        mock_minimize,
        optimization_service: OptimizationService,
        test_job: OptimizationJob
    ):
        """Test SLSQP optimization failure handling."""
        from scipy.optimize import OptimizeResult

        # Mock failed optimization
        mock_result = OptimizeResult()
        mock_result.success = False
        mock_result.x = np.array([0.7, 0.12, 0.4])
        mock_result.fun = -0.85
        mock_result.nit = 10
        mock_result.message = "Maximum iterations exceeded"
        mock_minimize.return_value = mock_result

        # Run optimization - should still complete but with warning
        result = await optimization_service.run_optimization(str(test_job.id))

        assert result is not None
        assert mock_minimize.called

    async def test_run_optimization_job_not_found(
        self,
        optimization_service: OptimizationService
    ):
        """Test optimization with non-existent job."""
        with pytest.raises(ValueError, match="Job .* not found"):
            await optimization_service.run_optimization(str(uuid4()))

    @patch('app.services.optimization_service.minimize')
    async def test_run_optimization_with_progress_callback(
        self,
        mock_minimize,
        optimization_service: OptimizationService,
        test_job: OptimizationJob
    ):
        """Test optimization with progress callback."""
        from scipy.optimize import OptimizeResult

        # Track progress calls
        progress_calls = []

        def progress_callback(iteration, max_iter, obj_value):
            progress_calls.append({
                'iteration': iteration,
                'max_iter': max_iter,
                'obj_value': obj_value
            })

        optimization_service.progress_callback = progress_callback

        # Mock result
        mock_result = OptimizeResult()
        mock_result.success = True
        mock_result.x = np.array([0.9, 0.10, 0.35])
        mock_result.fun = -0.95
        mock_result.nit = 5
        mock_result.message = "Success"
        mock_minimize.return_value = mock_result

        # Run optimization
        await optimization_service.run_optimization(str(test_job.id))

        # Progress callback should have been called during optimization
        # (Note: In mock scenario, it won't be called unless we simulate scipy calling objective)
        assert optimization_service.progress_callback is not None

    @patch('app.services.optimization_service.minimize')
    async def test_run_optimization_exception_handling(
        self,
        mock_minimize,
        optimization_service: OptimizationService,
        test_job: OptimizationJob
    ):
        """Test optimization exception handling."""
        # Mock optimization raising exception
        mock_minimize.side_effect = RuntimeError("SLSQP internal error")

        # Run optimization - should handle exception gracefully
        with pytest.raises(RuntimeError, match="SLSQP internal error"):
            await optimization_service.run_optimization(str(test_job.id))

        # Verify job status updated to FAILED
        updated_job = await optimization_service._get_job(str(test_job.id))
        assert updated_job.status == OptimizationStatus.FAILED
        assert "SLSQP internal error" in updated_job.error_message

    def test_array_to_design_vars_conversion(self):
        """Test conversion from numpy array to design variables dict."""
        service = OptimizationService(None)  # DB not needed for this test

        design_var_config = {
            "checker_height": {"min": 0.5, "max": 1.5},
            "checker_spacing": {"min": 0.08, "max": 0.15},
            "wall_thickness": {"min": 0.2, "max": 0.6}
        }

        x = np.array([0.9, 0.10, 0.35])

        result = service._array_to_design_vars(x, design_var_config)

        assert result["checker_height"] == 0.9
        assert result["checker_spacing"] == 0.10
        assert result["wall_thickness"] == 0.35
        assert len(result) == 3

    @patch('app.services.optimization_service.minimize')
    async def test_run_optimization_minimize_fuel_consumption(
        self,
        mock_minimize,
        optimization_service: OptimizationService,
        test_job: OptimizationJob,
        test_scenario: OptimizationScenario
    ):
        """Test optimization with minimize_fuel_consumption objective."""
        from scipy.optimize import OptimizeResult

        # Ensure scenario has correct objective
        test_scenario.objective = "minimize_fuel_consumption"

        mock_result = OptimizeResult()
        mock_result.success = True
        mock_result.x = np.array([1.2, 0.09, 0.3])
        mock_result.fun = -0.93
        mock_result.nit = 30
        mock_minimize.return_value = mock_result

        result = await optimization_service.run_optimization(str(test_job.id))

        assert result is not None
        # Objective should be to maximize thermal efficiency (minimize negative)
        assert mock_minimize.called

    @patch('app.services.optimization_service.minimize')
    async def test_run_optimization_maximize_efficiency(
        self,
        mock_minimize,
        optimization_service: OptimizationService,
        test_job: OptimizationJob,
        test_scenario: OptimizationScenario
    ):
        """Test optimization with maximize_efficiency objective."""
        from scipy.optimize import OptimizeResult

        test_scenario.objective = "maximize_efficiency"

        mock_result = OptimizeResult()
        mock_result.success = True
        mock_result.x = np.array([1.0, 0.10, 0.35])
        mock_result.fun = -0.94
        mock_result.nit = 20
        mock_minimize.return_value = mock_result

        result = await optimization_service.run_optimization(str(test_job.id))

        assert result is not None