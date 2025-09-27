"""
Physical data validation service for regenerator properties.

Serwis walidacji fizycznej danych właściwości regeneratorów.
"""

from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import math
import structlog

from app.schemas.import_schemas import ValidationError
from app.services.unit_conversion import UnitConversionService, UnitType


logger = structlog.get_logger(__name__)


class ValidationSeverity(str, Enum):
    """Validation severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class RegeneratorPhysicsValidator:
    """Validator for regenerator physics and engineering constraints."""

    def __init__(self, unit_converter: Optional[UnitConversionService] = None):
        self.unit_converter = unit_converter
        self.validation_errors = []

    async def validate_regenerator_data(
        self,
        data: Dict[str, Any],
        row_index: int = 0
    ) -> List[ValidationError]:
        """
        Validate complete regenerator data for physical consistency.

        Args:
            data: Regenerator data dictionary
            row_index: Row index for error reporting

        Returns:
            List of validation errors and warnings
        """
        self.validation_errors = []

        # Validate individual fields
        await self._validate_geometric_properties(data, row_index)
        await self._validate_thermal_properties(data, row_index)
        await self._validate_flow_properties(data, row_index)
        await self._validate_material_properties(data, row_index)
        await self._validate_performance_metrics(data, row_index)

        # Cross-field validations
        await self._validate_physical_consistency(data, row_index)
        await self._validate_engineering_constraints(data, row_index)

        return self.validation_errors

    async def _validate_geometric_properties(self, data: Dict[str, Any], row_index: int):
        """Validate geometric dimensions and constraints."""

        # Required geometric fields
        required_fields = ["length", "width", "height"]
        for field in required_fields:
            if field not in data or data[field] is None:
                self._add_error(
                    row_index, field,
                    f"Required geometric field '{field}' is missing",
                    ValidationSeverity.ERROR
                )
                continue

            value = data[field]

            # Check for positive values
            if not isinstance(value, (int, float)) or value <= 0:
                self._add_error(
                    row_index, field,
                    f"Geometric dimension must be positive: {value}",
                    ValidationSeverity.ERROR
                )
                continue

            # Check reasonable ranges (in meters)
            if field == "length":
                if value < 0.5 or value > 50.0:
                    self._add_error(
                        row_index, field,
                        f"Regenerator length {value}m is outside typical range (0.5-50m)",
                        ValidationSeverity.WARNING
                    )
            elif field == "width":
                if value < 0.5 or value > 30.0:
                    self._add_error(
                        row_index, field,
                        f"Regenerator width {value}m is outside typical range (0.5-30m)",
                        ValidationSeverity.WARNING
                    )
            elif field == "height":
                if value < 0.3 or value > 15.0:
                    self._add_error(
                        row_index, field,
                        f"Regenerator height {value}m is outside typical range (0.3-15m)",
                        ValidationSeverity.WARNING
                    )

        # Calculate and validate volume
        if all(field in data for field in required_fields):
            calculated_volume = data["length"] * data["width"] * data["height"]

            if "volume" in data and data["volume"] is not None:
                provided_volume = data["volume"]
                volume_diff = abs(calculated_volume - provided_volume) / calculated_volume

                if volume_diff > 0.05:  # 5% tolerance
                    self._add_error(
                        row_index, "volume",
                        f"Provided volume {provided_volume:.2f}m³ differs from calculated volume {calculated_volume:.2f}m³ by {volume_diff:.1%}",
                        ValidationSeverity.WARNING
                    )

        # Aspect ratio checks
        if "length" in data and "width" in data:
            aspect_ratio = max(data["length"], data["width"]) / min(data["length"], data["width"])
            if aspect_ratio > 10:
                self._add_error(
                    row_index, "length",
                    f"Extreme aspect ratio {aspect_ratio:.1f} may cause flow distribution issues",
                    ValidationSeverity.WARNING
                )

    async def _validate_thermal_properties(self, data: Dict[str, Any], row_index: int):
        """Validate thermal properties and temperature constraints."""

        # Design temperature validation
        if "design_temperature" in data:
            design_temp = data["design_temperature"]
            if design_temp is not None:
                if not isinstance(design_temp, (int, float)):
                    self._add_error(
                        row_index, "design_temperature",
                        f"Design temperature must be numeric: {design_temp}",
                        ValidationSeverity.ERROR
                    )
                elif design_temp < 200 or design_temp > 1800:
                    self._add_error(
                        row_index, "design_temperature",
                        f"Design temperature {design_temp}°C is outside typical range (200-1800°C)",
                        ValidationSeverity.WARNING
                    )

        # Maximum temperature validation
        if "max_temperature" in data:
            max_temp = data["max_temperature"]
            if max_temp is not None:
                if not isinstance(max_temp, (int, float)):
                    self._add_error(
                        row_index, "max_temperature",
                        f"Maximum temperature must be numeric: {max_temp}",
                        ValidationSeverity.ERROR
                    )
                elif max_temp < 250 or max_temp > 2000:
                    self._add_error(
                        row_index, "max_temperature",
                        f"Maximum temperature {max_temp}°C is outside typical range (250-2000°C)",
                        ValidationSeverity.WARNING
                    )

        # Temperature relationship validation
        if ("design_temperature" in data and "max_temperature" in data and
            data["design_temperature"] is not None and data["max_temperature"] is not None):

            design_temp = data["design_temperature"]
            max_temp = data["max_temperature"]

            if max_temp <= design_temp:
                self._add_error(
                    row_index, "max_temperature",
                    f"Maximum temperature {max_temp}°C must be higher than design temperature {design_temp}°C",
                    ValidationSeverity.ERROR
                )
            elif (max_temp - design_temp) < 50:
                self._add_error(
                    row_index, "max_temperature",
                    f"Small temperature margin ({max_temp - design_temp}°C) between design and maximum temperature",
                    ValidationSeverity.WARNING
                )

    async def _validate_flow_properties(self, data: Dict[str, Any], row_index: int):
        """Validate flow rates and pressure properties."""

        # Pressure validation
        if "working_pressure" in data and data["working_pressure"] is not None:
            pressure = data["working_pressure"]
            if not isinstance(pressure, (int, float)):
                self._add_error(
                    row_index, "working_pressure",
                    f"Working pressure must be numeric: {pressure}",
                    ValidationSeverity.ERROR
                )
            elif pressure < -1000 or pressure > 1000000:  # Pa
                self._add_error(
                    row_index, "working_pressure",
                    f"Working pressure {pressure} Pa is outside typical range (-1000 to 1000000 Pa)",
                    ValidationSeverity.WARNING
                )

        # Flow rate validation
        flow_fields = ["air_flow_rate", "gas_flow_rate"]
        for field in flow_fields:
            if field in data and data[field] is not None:
                flow_rate = data[field]
                if not isinstance(flow_rate, (int, float)):
                    self._add_error(
                        row_index, field,
                        f"Flow rate must be numeric: {flow_rate}",
                        ValidationSeverity.ERROR
                    )
                elif flow_rate <= 0:
                    self._add_error(
                        row_index, field,
                        f"Flow rate must be positive: {flow_rate}",
                        ValidationSeverity.ERROR
                    )
                elif flow_rate > 1000000:  # m³/h
                    self._add_error(
                        row_index, field,
                        f"Flow rate {flow_rate} m³/h seems unusually high",
                        ValidationSeverity.WARNING
                    )

        # Pressure drop validation
        if "pressure_drop" in data and data["pressure_drop"] is not None:
            pressure_drop = data["pressure_drop"]
            if not isinstance(pressure_drop, (int, float)):
                self._add_error(
                    row_index, "pressure_drop",
                    f"Pressure drop must be numeric: {pressure_drop}",
                    ValidationSeverity.ERROR
                )
            elif pressure_drop < 0:
                self._add_error(
                    row_index, "pressure_drop",
                    f"Pressure drop cannot be negative: {pressure_drop}",
                    ValidationSeverity.ERROR
                )
            elif pressure_drop > 10000:  # Pa
                self._add_error(
                    row_index, "pressure_drop",
                    f"Pressure drop {pressure_drop} Pa seems unusually high",
                    ValidationSeverity.WARNING
                )

    async def _validate_material_properties(self, data: Dict[str, Any], row_index: int):
        """Validate material selections and properties."""

        # Material name validation
        material_fields = ["checker_material", "insulation_material", "refractory_material"]
        for field in material_fields:
            if field in data and data[field] is not None:
                material = data[field]
                if not isinstance(material, str) or len(material.strip()) == 0:
                    self._add_error(
                        row_index, field,
                        f"Material name must be non-empty string: {material}",
                        ValidationSeverity.ERROR
                    )
                elif len(material) > 255:
                    self._add_error(
                        row_index, field,
                        f"Material name too long ({len(material)} chars, max 255)",
                        ValidationSeverity.ERROR
                    )

        # Check for common material naming issues
        if "checker_material" in data and data["checker_material"]:
            checker_material = data["checker_material"].lower()
            common_checker_materials = [
                "firebrick", "alumina", "silica", "magnesia", "chrome", "carbon",
                "refractory brick", "ceramic", "cordierite"
            ]
            if not any(mat in checker_material for mat in common_checker_materials):
                self._add_error(
                    row_index, "checker_material",
                    f"Unusual checker material '{data['checker_material']}' - verify material selection",
                    ValidationSeverity.INFO
                )

    async def _validate_performance_metrics(self, data: Dict[str, Any], row_index: int):
        """Validate performance metrics and efficiency values."""

        # Efficiency validation
        efficiency_fields = ["thermal_efficiency", "heat_recovery_rate"]
        for field in efficiency_fields:
            if field in data and data[field] is not None:
                efficiency = data[field]
                if not isinstance(efficiency, (int, float)):
                    self._add_error(
                        row_index, field,
                        f"Efficiency must be numeric: {efficiency}",
                        ValidationSeverity.ERROR
                    )
                elif efficiency < 0 or efficiency > 100:
                    self._add_error(
                        row_index, field,
                        f"Efficiency must be between 0-100%: {efficiency}%",
                        ValidationSeverity.ERROR
                    )
                elif efficiency < 20:
                    self._add_error(
                        row_index, field,
                        f"Efficiency {efficiency}% is unusually low",
                        ValidationSeverity.WARNING
                    )
                elif efficiency > 95:
                    self._add_error(
                        row_index, field,
                        f"Efficiency {efficiency}% is unusually high",
                        ValidationSeverity.WARNING
                    )

        # Fuel consumption validation
        if "fuel_consumption" in data and data["fuel_consumption"] is not None:
            fuel_consumption = data["fuel_consumption"]
            if not isinstance(fuel_consumption, (int, float)):
                self._add_error(
                    row_index, "fuel_consumption",
                    f"Fuel consumption must be numeric: {fuel_consumption}",
                    ValidationSeverity.ERROR
                )
            elif fuel_consumption <= 0:
                self._add_error(
                    row_index, "fuel_consumption",
                    f"Fuel consumption must be positive: {fuel_consumption}",
                    ValidationSeverity.ERROR
                )

    async def _validate_physical_consistency(self, data: Dict[str, Any], row_index: int):
        """Validate physical consistency between different parameters."""

        # Flow velocity check
        if all(field in data and data[field] is not None for field in
               ["air_flow_rate", "length", "width", "height"]):

            flow_rate = data["air_flow_rate"]  # m³/h
            cross_section = data["width"] * data["height"]  # m²

            # Convert flow rate to m³/s
            flow_rate_ms = flow_rate / 3600.0

            # Calculate velocity
            velocity = flow_rate_ms / cross_section  # m/s

            if velocity < 0.1:
                self._add_error(
                    row_index, "air_flow_rate",
                    f"Very low gas velocity {velocity:.2f} m/s may cause poor heat transfer",
                    ValidationSeverity.WARNING
                )
            elif velocity > 20:
                self._add_error(
                    row_index, "air_flow_rate",
                    f"Very high gas velocity {velocity:.2f} m/s may cause excessive pressure drop",
                    ValidationSeverity.WARNING
                )

        # Heat transfer consistency
        if all(field in data and data[field] is not None for field in
               ["thermal_efficiency", "design_temperature", "air_flow_rate"]):

            efficiency = data["thermal_efficiency"]
            temp = data["design_temperature"]
            flow = data["air_flow_rate"]

            # Rough check for heat transfer correlation
            # Higher temperatures and flows should generally correlate with efficiency
            if temp > 1000 and flow > 10000 and efficiency < 50:
                self._add_error(
                    row_index, "thermal_efficiency",
                    f"Low efficiency {efficiency}% unexpected for high temperature {temp}°C and flow rate {flow} m³/h",
                    ValidationSeverity.WARNING
                )

    async def _validate_engineering_constraints(self, data: Dict[str, Any], row_index: int):
        """Validate engineering and operational constraints."""

        # Regenerator type specific validations
        if "regenerator_type" in data and data["regenerator_type"]:
            regen_type = data["regenerator_type"].lower()

            if regen_type == "crown":
                # Crown regenerators typically have height constraints
                if "height" in data and data["height"] and data["height"] < 2.0:
                    self._add_error(
                        row_index, "height",
                        f"Crown regenerator height {data['height']}m may be insufficient for proper heat exchange",
                        ValidationSeverity.WARNING
                    )

            elif regen_type == "end-port":
                # End-port regenerators have different flow patterns
                if "length" in data and "width" in data and data["length"] and data["width"]:
                    if data["length"] / data["width"] < 2:
                        self._add_error(
                            row_index, "length",
                            f"End-port regenerator may need higher length/width ratio for optimal flow distribution",
                            ValidationSeverity.INFO
                        )

        # Structural constraints
        if all(field in data and data[field] is not None for field in ["length", "width", "height"]):
            volume = data["length"] * data["width"] * data["height"]

            # Very large regenerators may have structural issues
            if volume > 5000:  # m³
                self._add_error(
                    row_index, "volume",
                    f"Large regenerator volume {volume:.1f}m³ requires careful structural design",
                    ValidationSeverity.INFO
                )

    def _add_error(
        self,
        row: int,
        column: str,
        message: str,
        severity: ValidationSeverity,
        value: Any = None
    ):
        """Add validation error to the list."""
        error = ValidationError(
            row=row,
            column=column,
            message=message,
            severity=severity.value,
            value=value
        )
        self.validation_errors.append(error)

    async def get_validation_rules_summary(self) -> Dict[str, Any]:
        """
        Get summary of all validation rules for documentation.

        Returns:
            Dictionary with validation rules by category
        """
        return {
            "geometric_constraints": {
                "length": {"min": 0.5, "max": 50.0, "unit": "m"},
                "width": {"min": 0.5, "max": 30.0, "unit": "m"},
                "height": {"min": 0.3, "max": 15.0, "unit": "m"},
                "aspect_ratio": {"max": 10.0, "warning_level": True}
            },
            "thermal_constraints": {
                "design_temperature": {"min": 200, "max": 1800, "unit": "°C"},
                "max_temperature": {"min": 250, "max": 2000, "unit": "°C"},
                "temperature_margin": {"min": 50, "unit": "°C"}
            },
            "flow_constraints": {
                "working_pressure": {"min": -1000, "max": 1000000, "unit": "Pa"},
                "pressure_drop": {"min": 0, "max": 10000, "unit": "Pa"},
                "gas_velocity": {"min": 0.1, "max": 20.0, "unit": "m/s"}
            },
            "performance_constraints": {
                "thermal_efficiency": {"min": 0, "max": 100, "typical_min": 20, "typical_max": 95, "unit": "%"},
                "heat_recovery_rate": {"min": 0, "max": 100, "typical_min": 20, "typical_max": 95, "unit": "%"},
                "fuel_consumption": {"min": 0, "unit": "kW"}
            },
            "engineering_rules": {
                "crown_regenerator_min_height": {"value": 2.0, "unit": "m"},
                "end_port_aspect_ratio": {"min": 2.0},
                "large_volume_threshold": {"value": 5000, "unit": "m³"}
            }
        }