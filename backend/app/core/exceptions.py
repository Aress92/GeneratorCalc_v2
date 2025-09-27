"""
Custom exceptions for the Forglass Regenerator Optimizer.

Hierarchia wyjątków dla systemu optymalizacji regeneratorów.
"""


class FROptimizationError(Exception):
    """Base exception for optimization errors."""

    def __init__(self, message: str, details: dict = None) -> None:
        """Initialize optimization error."""
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(FROptimizationError):
    """Input validation failed."""

    pass


class ConvergenceError(FROptimizationError):
    """Algorithm failed to converge."""

    def __init__(self, message: str, iterations: int = None, objective_value: float = None) -> None:
        """Initialize convergence error."""
        super().__init__(message)
        self.iterations = iterations
        self.objective_value = objective_value


class ConfigurationError(FROptimizationError):
    """Invalid configuration parameters."""

    pass


class PhysicsError(FROptimizationError):
    """Physics calculation error."""

    pass


class ImportError(FROptimizationError):
    """Data import error."""

    def __init__(self, message: str, file_path: str = None, line_number: int = None) -> None:
        """Initialize import error."""
        super().__init__(message)
        self.file_path = file_path
        self.line_number = line_number


class ExportError(FROptimizationError):
    """Data export error."""

    pass


class AuthenticationError(FROptimizationError):
    """Authentication failed."""

    pass


class AuthorizationError(FROptimizationError):
    """Authorization failed."""

    pass


class ResourceNotFoundError(FROptimizationError):
    """Requested resource not found."""

    def __init__(self, resource_type: str, resource_id: str) -> None:
        """Initialize resource not found error."""
        message = f"{resource_type} with ID {resource_id} not found"
        super().__init__(message)
        self.resource_type = resource_type
        self.resource_id = resource_id


class ResourceConflictError(FROptimizationError):
    """Resource conflict (e.g., duplicate names)."""

    pass


class ServiceUnavailableError(FROptimizationError):
    """External service unavailable."""

    def __init__(self, service_name: str, details: str = None) -> None:
        """Initialize service unavailable error."""
        message = f"Service {service_name} is unavailable"
        if details:
            message += f": {details}"
        super().__init__(message)
        self.service_name = service_name


class RateLimitError(FROptimizationError):
    """Rate limit exceeded."""

    def __init__(self, limit: int, window: int) -> None:
        """Initialize rate limit error."""
        message = f"Rate limit of {limit} requests per {window} seconds exceeded"
        super().__init__(message)
        self.limit = limit
        self.window = window