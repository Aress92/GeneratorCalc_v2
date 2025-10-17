"""
Tests for regenerator service.

Testy dla serwisu regeneratorów.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.services.regenerator_service import RegeneratorService
from app.models.user import User, UserRole
from app.models.regenerator import RegeneratorConfiguration, RegeneratorType, ConfigurationStatus
from app.schemas.regenerator_schemas import RegeneratorConfigurationCreate, RegeneratorConfigurationUpdate


class TestRegeneratorService:
    """Test regenerator service functionality."""

    @pytest.fixture
    async def regenerator_service(self, test_db: AsyncSession) -> RegeneratorService:
        """Create regenerator service instance."""
        return RegeneratorService(test_db)

    @pytest.fixture
    async def test_user(self, test_db: AsyncSession) -> User:
        """Create test user."""
        unique_id = str(uuid4())[:8]
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
            description="Test regenerator for testing",
            geometry_config={
                "length": 10.0,
                "width": 8.0,
                "height": 6.0,
                "wall_thickness": 0.4,
                "checker_height": 0.7,
                "checker_spacing": 0.12
            },
            materials_config={
                "wall_material_id": "test-wall-material",
                "checker_material_id": "test-checker-material",
                "thermal_conductivity": 2.5,
                "specific_heat": 900.0,
                "checker_density": 2300.0,
                "wall_density": 2500.0
            },
            thermal_config={
                "gas_temp_inlet": 1600.0,
                "gas_temp_outlet": 600.0,
                "ambient_temp": 25.0,
                "heat_duty": 15000.0
            },
            flow_config={
                "mass_flow_rate": 50.0,
                "cycle_time": 1200.0,
                "pressure_inlet": 101325.0,
                "pressure_outlet": 101000.0
            }
        )
        test_db.add(config)
        await test_db.commit()
        await test_db.refresh(config)
        return config

    async def test_create_regenerator(self, regenerator_service: RegeneratorService, test_user: User):
        """Test creating a new regenerator configuration."""
        regenerator_data = RegeneratorConfigurationCreate(
            name="New Test Regenerator",
            regenerator_type=RegeneratorType.END_PORT,
            description="New test regenerator configuration",
            geometry_config={
                "length": 12.0,
                "width": 10.0,
                "height": 7.0,
                "wall_thickness": 0.5,
                "checker_height": 0.8,
                "checker_spacing": 0.15
            },
            materials_config={
                "wall_material_id": "new-wall-material",
                "checker_material_id": "new-checker-material",
                "thermal_conductivity": 3.0,
                "specific_heat": 850.0,
                "checker_density": 2400.0
            },
            thermal_config={
                "gas_temp_inlet": 1700.0,
                "gas_temp_outlet": 650.0,
                "ambient_temp": 30.0
            },
            flow_config={
                "mass_flow_rate": 60.0,
                "cycle_time": 1800.0,
                "pressure_inlet": 102000.0
            }
        )

        result = await regenerator_service.create_regenerator(regenerator_data, str(test_user.id))

        assert result.name == "New Test Regenerator"
        assert result.regenerator_type == RegeneratorType.END_PORT
        assert result.user_id == str(test_user.id)
        assert result.status == ConfigurationStatus.DRAFT
        assert result.geometry_config["length"] == 12.0

    async def test_get_regenerator_by_id(self, regenerator_service: RegeneratorService, test_regenerator: RegeneratorConfiguration, test_user: User):
        """Test getting regenerator by ID."""
        result = await regenerator_service.get_regenerator(str(test_regenerator.id), str(test_user.id))

        assert result is not None
        assert result.id == test_regenerator.id
        assert result.name == test_regenerator.name
        assert result.regenerator_type == test_regenerator.regenerator_type

    async def test_get_regenerator_not_found(self, regenerator_service: RegeneratorService, test_user: User):
        """Test getting non-existent regenerator."""
        result = await regenerator_service.get_regenerator("non-existent-id", str(test_user.id))
        assert result is None

    async def test_update_regenerator(self, regenerator_service: RegeneratorService, test_regenerator: RegeneratorConfiguration, test_user: User):
        """Test updating regenerator configuration."""
        update_data = RegeneratorConfigurationUpdate(
            name="Updated Regenerator Name",
            description="Updated description",
            geometry_config={
                "length": 15.0,
                "width": 12.0,
                "height": 8.0,
                "wall_thickness": 0.6
            },
            thermal_config={
                "gas_temp_inlet": 1800.0,
                "gas_temp_outlet": 700.0
            }
        )

        result = await regenerator_service.update_regenerator(str(test_regenerator.id), update_data, str(test_user.id))

        assert result is not None
        assert result.name == "Updated Regenerator Name"
        assert result.description == "Updated description"
        assert result.geometry_config["length"] == 15.0
        assert result.thermal_config["gas_temp_inlet"] == 1800.0

    async def test_delete_regenerator(self, regenerator_service: RegeneratorService, test_regenerator: RegeneratorConfiguration, test_user: User):
        """Test deleting regenerator configuration."""
        success = await regenerator_service.delete_regenerator(str(test_regenerator.id), str(test_user.id))

        assert success is True

        # Verify regenerator is deleted
        deleted_regenerator = await regenerator_service.get_regenerator(str(test_regenerator.id), str(test_user.id))
        assert deleted_regenerator is None

    async def test_get_user_regenerators(self, regenerator_service: RegeneratorService, test_user: User, test_regenerator: RegeneratorConfiguration):
        """Test getting user's regenerator configurations."""
        regenerators = await regenerator_service.list_user_regenerators(str(test_user.id), skip=0, limit=10)

        assert len(regenerators) >= 1
        found_regenerator = next((r for r in regenerators if r.id == test_regenerator.id), None)
        assert found_regenerator is not None

    async def test_validate_regenerator_config(self, regenerator_service: RegeneratorService):
        """Test regenerator configuration validation."""
        valid_config = {
            "name": "Valid Regenerator",
            "regenerator_type": RegeneratorType.CROWN,
            "geometry_config": {
                "length": 10.0,
                "width": 8.0,
                "height": 6.0,
                "wall_thickness": 0.4
            },
            "thermal_config": {
                "gas_temp_inlet": 1600.0,
                "gas_temp_outlet": 600.0
            },
            "flow_config": {
                "mass_flow_rate": 50.0,
                "cycle_time": 1200.0
            }
        }

        # Valid config should not raise
        result = await regenerator_service.validate_configuration(valid_config)
        assert result["is_valid"] is True

    async def test_get_regenerator_templates(self, regenerator_service: RegeneratorService):
        """Test getting regenerator templates."""
        templates = await regenerator_service.get_configuration_templates()

        assert isinstance(templates, list)
        # Should contain predefined templates
        template_names = [t["name"] for t in templates]
        assert "Crown Regenerator" in template_names
        assert "End-Port Regenerator" in template_names

    async def test_regenerator_pagination(self, regenerator_service: RegeneratorService, test_user: User, test_regenerator: RegeneratorConfiguration):
        """Test regenerator pagination."""
        # Test first page
        page1 = await regenerator_service.list_user_regenerators(str(test_user.id), skip=0, limit=1)
        assert len(page1) <= 1

        # Test second page
        page2 = await regenerator_service.list_user_regenerators(str(test_user.id), skip=1, limit=1)
        assert len(page2) <= 1

    async def test_regenerator_ownership_validation(self, regenerator_service: RegeneratorService, test_regenerator: RegeneratorConfiguration, test_db: AsyncSession):
        """Test regenerator ownership validation."""
        # Create another user
        other_user = User(
            username="otheruser",
            email="other@example.com",
            full_name="Other User",
            password_hash="hashed_password",
            role=UserRole.ENGINEER,
            is_active=True,
            is_verified=True
        )
        test_db.add(other_user)
        await test_db.commit()
        await test_db.refresh(other_user)

        # Try to get regenerator with different user - should fail
        result = await regenerator_service.get_regenerator(str(test_regenerator.id), str(other_user.id))
        assert result is None  # Should fail due to ownership validation