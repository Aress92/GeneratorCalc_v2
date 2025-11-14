"""
Test validation error handler for user-friendly 422 responses.
"""
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_missing_required_field():
    """Test that missing required fields return user-friendly error messages."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Try to create scenario without required 'name' field
        response = await client.post(
            "/api/v1/optimize/scenarios",
            json={
                "scenario_type": "geometry_optimization",
                "base_configuration_id": "test-uuid",
                "objective": "minimize_fuel_consumption",
                "design_variables": {"test": "value"}
            }
        )

        assert response.status_code == 422
        data = response.json()

        # Check structure
        assert "detail" in data
        assert "errors" in data
        assert "type" in data
        assert data["type"] == "validation_error"

        # Check Polish messages
        assert data["detail"] == "Błąd walidacji danych"
        assert isinstance(data["errors"], list)
        assert len(data["errors"]) > 0

        # Check error structure
        error = data["errors"][0]
        assert "field" in error
        assert "message" in error
        assert "type" in error

        # Check message is in Polish
        assert "Pole" in error["message"] or "pole" in error["message"]


@pytest.mark.asyncio
async def test_invalid_field_type():
    """Test that invalid field types return user-friendly error messages."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/optimize/scenarios",
            json={
                "name": "Test Scenario",
                "scenario_type": "geometry_optimization",
                "base_configuration_id": "test-uuid",
                "objective": "minimize_fuel_consumption",
                "design_variables": {"test": "value"},
                "max_iterations": "not_a_number"  # Should be int
            }
        )

        assert response.status_code == 422
        data = response.json()

        assert "errors" in data
        assert len(data["errors"]) > 0

        # Find the max_iterations error
        max_iter_error = next(
            (e for e in data["errors"] if "max_iterations" in e["field"]),
            None
        )
        assert max_iter_error is not None
        assert "typ" in max_iter_error["message"].lower()


@pytest.mark.asyncio
async def test_out_of_range_value():
    """Test that out-of-range values return user-friendly error messages."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/optimize/scenarios",
            json={
                "name": "Test Scenario",
                "scenario_type": "geometry_optimization",
                "base_configuration_id": "test-uuid",
                "objective": "minimize_fuel_consumption",
                "design_variables": {"test": "value"},
                "max_iterations": 50000  # Above max limit of 10000
            }
        )

        assert response.status_code == 422
        data = response.json()

        assert "errors" in data
        # Should contain error about max_iterations being too large
        assert any("max_iterations" in e["field"] for e in data["errors"])


@pytest.mark.asyncio
async def test_invalid_enum_value():
    """Test that invalid enum values return user-friendly error messages."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/optimize/scenarios",
            json={
                "name": "Test Scenario",
                "scenario_type": "invalid_type",  # Invalid enum value
                "base_configuration_id": "test-uuid",
                "objective": "minimize_fuel_consumption",
                "design_variables": {"test": "value"}
            }
        )

        assert response.status_code == 422
        data = response.json()

        assert "errors" in data
        # Should contain error about scenario_type with allowed values
        scenario_type_error = next(
            (e for e in data["errors"] if "scenario_type" in e["field"]),
            None
        )
        assert scenario_type_error is not None
        # Should list allowed values in Polish
        assert "wartości" in scenario_type_error["message"].lower() or "jedną z" in scenario_type_error["message"]


if __name__ == "__main__":
    import asyncio

    async def run_tests():
        print("Running validation error handler tests...")
        try:
            await test_missing_required_field()
            print("✅ test_missing_required_field")
        except AssertionError as e:
            print(f"❌ test_missing_required_field: {e}")

        try:
            await test_invalid_field_type()
            print("✅ test_invalid_field_type")
        except AssertionError as e:
            print(f"❌ test_invalid_field_type: {e}")

        try:
            await test_out_of_range_value()
            print("✅ test_out_of_range_value")
        except AssertionError as e:
            print(f"❌ test_out_of_range_value: {e}")

        try:
            await test_invalid_enum_value()
            print("✅ test_invalid_enum_value")
        except AssertionError as e:
            print(f"❌ test_invalid_enum_value: {e}")

    asyncio.run(run_tests())
