"""
Tests for core exception handling.

Testy dla obsługi wyjątków.
"""

import pytest
from app.core.exceptions import (
    FROptimizationError,
    ValidationError,
    ConfigurationError,
    ImportError,
    ConvergenceError,
    PhysicsError,
    AuthenticationError,
    AuthorizationError,
    ResourceNotFoundError
)


class TestCustomExceptions:
    """Test custom exception classes."""

    def test_fr_optimization_error(self):
        """Test FROptimizationError exception."""
        message = "Optimization failed due to invalid parameters"
        error = FROptimizationError(message)

        assert str(error) == message
        assert isinstance(error, Exception)

        # Test with additional context
        error_with_code = FROptimizationError(message, error_code="OPT001")
        assert str(error_with_code) == message
        assert hasattr(error_with_code, 'error_code')

    def test_validation_error(self):
        """Test ValidationError exception."""
        message = "Validation failed for field 'temperature'"
        field = "temperature"
        value = -300

        error = ValidationError(message, field=field, value=value)

        assert str(error) == message
        assert error.field == field
        assert error.value == value

    def test_configuration_error(self):
        """Test ConfigurationError exception."""
        message = "Invalid regenerator configuration"
        config_section = "geometry"

        error = ConfigurationError(message, section=config_section)

        assert str(error) == message
        assert error.section == config_section

    def test_import_error(self):
        """Test ImportError exception."""
        message = "Failed to import XLSX file"
        filename = "regenerators.xlsx"
        row_number = 5

        error = ImportError(message, filename=filename, row=row_number)

        assert str(error) == message
        assert error.filename == filename
        assert error.row == row_number

    def test_convergence_error(self):
        """Test ConvergenceError exception."""
        message = "SLSQP algorithm failed to converge"

        error = ConvergenceError(message)

        assert str(error) == message
        assert isinstance(error, FROptimizationError)

    def test_physics_error(self):
        """Test PhysicsError exception."""
        message = "Invalid physics calculation"

        error = PhysicsError(message)

        assert str(error) == message
        assert isinstance(error, FROptimizationError)

    def test_authentication_error(self):
        """Test AuthenticationError exception."""
        message = "Invalid credentials"
        username = "testuser"

        error = AuthenticationError(message, username=username)

        assert str(error) == message
        assert error.username == username

    def test_authorization_error(self):
        """Test AuthorizationError exception."""
        message = "Insufficient permissions for this operation"

        error = AuthorizationError(message)

        assert str(error) == message
        assert isinstance(error, FROptimizationError)

    def test_resource_not_found_error(self):
        """Test ResourceNotFoundError exception."""
        message = "Resource not found"

        error = ResourceNotFoundError(message)

        assert str(error) == message
        assert isinstance(error, FROptimizationError)

    def test_exception_chaining(self):
        """Test exception chaining with cause."""
        original_error = ValueError("Original error")

        # Chain exceptions
        try:
            raise original_error
        except ValueError as e:
            try:
                raise FROptimizationError("Optimization failed") from e
            except FROptimizationError as wrapped_error:
                assert wrapped_error.__cause__ == original_error

    def test_exception_with_multiple_args(self):
        """Test exceptions with multiple arguments."""
        error = ValidationError(
            "Multiple validation errors occurred",
            field="geometry",
            value={"length": -5, "width": 0},
            errors=["Length cannot be negative", "Width cannot be zero"]
        )

        assert "Multiple validation errors occurred" in str(error)
        assert error.field == "geometry"
        assert len(error.errors) == 2

    def test_exception_inheritance(self):
        """Test exception inheritance hierarchy."""
        # All custom exceptions should inherit from Exception
        assert issubclass(FROptimizationError, Exception)
        assert issubclass(ValidationError, FROptimizationError)
        assert issubclass(ConfigurationError, FROptimizationError)
        assert issubclass(ImportError, FROptimizationError)
        assert issubclass(ConvergenceError, FROptimizationError)

    def test_exception_repr(self):
        """Test exception string representation."""
        error = ValidationError("Test error")

        repr_str = repr(error)
        assert "ValidationError" in repr_str
        assert "Test error" in repr_str

    def test_exception_args(self):
        """Test exception args property."""
        message = "Test message"
        error = FROptimizationError(message)

        assert error.args == (message,)
        assert error.args[0] == message

    def test_basic_exception_functionality(self):
        """Test basic exception functionality."""
        # Test basic ValidationError
        validation_error = ValidationError("Validation failed")
        assert str(validation_error) == "Validation failed"
        assert isinstance(validation_error, FROptimizationError)

        # Test basic ImportError
        import_error = ImportError("Import failed")
        assert str(import_error) == "Import failed"
        assert isinstance(import_error, FROptimizationError)

        # Test basic ConfigurationError
        config_error = ConfigurationError("Configuration invalid")
        assert str(config_error) == "Configuration invalid"
        assert isinstance(config_error, FROptimizationError)

    def test_exception_serialization(self):
        """Test exception serialization for API responses."""
        error = ValidationError("Temperature out of range")

        # Convert to dict for JSON serialization
        error_dict = {
            "type": error.__class__.__name__,
            "message": str(error)
        }

        assert error_dict["type"] == "ValidationError"
        assert error_dict["message"] == "Temperature out of range"

    def test_exception_context_managers(self):
        """Test exceptions within context managers."""
        errors_caught = []

        # Test catching specific exceptions
        try:
            raise ValidationError("Test validation error", field="test")
        except FROptimizationError as e:
            errors_caught.append(type(e).__name__)

        try:
            raise ConfigurationError("Test config error")
        except FROptimizationError as e:
            errors_caught.append(type(e).__name__)

        assert "ValidationError" in errors_caught
        assert "ConfigurationError" in errors_caught

    def test_exception_with_traceback_info(self):
        """Test exception with additional traceback information."""
        def inner_function():
            raise ValueError("Inner error")

        def outer_function():
            try:
                inner_function()
            except ValueError as e:
                raise OptimizationError("Outer optimization error") from e

        with pytest.raises(OptimizationError) as exc_info:
            outer_function()

        assert exc_info.value.__cause__.__class__.__name__ == "ValueError"
        assert str(exc_info.value.__cause__) == "Inner error"