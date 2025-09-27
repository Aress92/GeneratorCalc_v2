"""
Prometheus metrics for monitoring.

Metryki biznesowe i techniczne dla monitoringu systemu.
"""

from prometheus_client import Counter, Histogram, Gauge, Info
from typing import Dict, Any
import time

from app.core.config import settings


# Business metrics
optimization_jobs_total = Counter(
    "fro_optimization_jobs_total",
    "Total number of optimization jobs",
    ["status", "algorithm", "user_role"],
)

optimization_duration = Histogram(
    "fro_optimization_duration_seconds",
    "Time spent on optimization",
    ["algorithm", "scenario_type"],
    buckets=[10, 30, 60, 120, 300, 600, 1800, 3600],
)

active_optimization_jobs = Gauge(
    "fro_active_optimization_jobs",
    "Number of currently running optimizations",
)

fuel_savings_achieved = Histogram(
    "fro_fuel_savings_percent",
    "Fuel savings achieved in optimizations",
    ["scenario_type"],
    buckets=[0, 2, 5, 8, 10, 12, 15, 18, 20, 25],
)

# Technical metrics
api_requests_total = Counter(
    "fro_api_requests_total",
    "Total API requests",
    ["method", "endpoint", "status_code"],
)

api_request_duration = Histogram(
    "fro_api_request_duration_seconds",
    "API request duration",
    ["method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

database_connections = Gauge(
    "fro_database_connections",
    "Active database connections",
)

import_success_rate = Counter(
    "fro_import_operations_total",
    "Import operations",
    ["status", "file_type"],
)

export_generation_time = Histogram(
    "fro_export_generation_seconds",
    "Time to generate exports",
    ["export_type"],
    buckets=[1, 5, 10, 30, 60, 120, 300],
)

# User activity metrics
active_users_gauge = Gauge(
    "fro_active_users",
    "Number of active user sessions",
)

user_actions_total = Counter(
    "fro_user_actions_total",
    "Total user actions",
    ["action_type", "user_role"],
)

# System health metrics
memory_usage = Gauge(
    "fro_memory_usage_bytes",
    "Memory usage in bytes",
)

cpu_usage = Gauge(
    "fro_cpu_usage_percent",
    "CPU usage percentage",
)

# Application info
app_info = Info(
    "fro_application",
    "Application information",
)


def setup_metrics() -> None:
    """Initialize metrics with application info."""
    if settings.ENABLE_METRICS:
        app_info.info({
            "version": settings.VERSION,
            "name": settings.PROJECT_NAME,
            "debug": str(settings.DEBUG),
        })


class MetricsCollector:
    """Helper class for collecting metrics."""

    @staticmethod
    def track_optimization_job(
        status: str,
        algorithm: str,
        user_role: str,
        duration: float = None,
        fuel_savings: float = None,
        scenario_type: str = "standard",
    ) -> None:
        """Track optimization job metrics."""
        optimization_jobs_total.labels(
            status=status,
            algorithm=algorithm,
            user_role=user_role,
        ).inc()

        if duration is not None:
            optimization_duration.labels(
                algorithm=algorithm,
                scenario_type=scenario_type,
            ).observe(duration)

        if fuel_savings is not None:
            fuel_savings_achieved.labels(
                scenario_type=scenario_type,
            ).observe(fuel_savings)

    @staticmethod
    def track_api_request(
        method: str,
        endpoint: str,
        status_code: int,
        duration: float,
    ) -> None:
        """Track API request metrics."""
        api_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code),
        ).inc()

        api_request_duration.labels(
            method=method,
            endpoint=endpoint,
        ).observe(duration)

    @staticmethod
    def track_import_operation(
        status: str,
        file_type: str,
    ) -> None:
        """Track import operation metrics."""
        import_success_rate.labels(
            status=status,
            file_type=file_type,
        ).inc()

    @staticmethod
    def track_export_generation(
        export_type: str,
        duration: float,
    ) -> None:
        """Track export generation metrics."""
        export_generation_time.labels(
            export_type=export_type,
        ).observe(duration)

    @staticmethod
    def track_user_action(
        action_type: str,
        user_role: str,
    ) -> None:
        """Track user action metrics."""
        user_actions_total.labels(
            action_type=action_type,
            user_role=user_role,
        ).inc()

    @staticmethod
    def set_active_users(count: int) -> None:
        """Set number of active users."""
        active_users_gauge.set(count)

    @staticmethod
    def set_active_optimizations(count: int) -> None:
        """Set number of active optimizations."""
        active_optimization_jobs.set(count)

    @staticmethod
    def set_database_connections(count: int) -> None:
        """Set number of database connections."""
        database_connections.set(count)


# Create global metrics collector instance
metrics = MetricsCollector()