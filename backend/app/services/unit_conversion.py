"""
Unit conversion service for handling metric/imperial conversions.

Serwis konwersji jednostek obsługujący konwersje metryczne/imperialne.
"""

from typing import Dict, Optional, List
from enum import Enum
import structlog

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.import_job import UnitConversion
from app.schemas.import_schemas import UnitConversionCreate, UnitConversionResponse


logger = structlog.get_logger(__name__)


class UnitType(str, Enum):
    """Types of units for conversion."""
    TEMPERATURE = "temperature"
    LENGTH = "length"
    AREA = "area"
    VOLUME = "volume"
    PRESSURE = "pressure"
    FLOW_RATE = "flow_rate"
    THERMAL_CONDUCTIVITY = "thermal_conductivity"
    SPECIFIC_HEAT = "specific_heat"
    DENSITY = "density"
    POWER = "power"
    ENERGY = "energy"


class UnitConversionService:
    """Service for handling unit conversions."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._initialize_default_conversions()

    def _initialize_default_conversions(self):
        """Initialize standard conversion definitions."""

        # Temperature conversions
        self.temperature_conversions = {
            ("celsius", "fahrenheit"): lambda c: c * 9/5 + 32,
            ("fahrenheit", "celsius"): lambda f: (f - 32) * 5/9,
            ("celsius", "kelvin"): lambda c: c + 273.15,
            ("kelvin", "celsius"): lambda k: k - 273.15,
            ("fahrenheit", "kelvin"): lambda f: (f - 32) * 5/9 + 273.15,
            ("kelvin", "fahrenheit"): lambda k: (k - 273.15) * 9/5 + 32,
        }

        # Length conversions (to meters)
        self.length_conversions = {
            ("mm", "m"): 0.001,
            ("cm", "m"): 0.01,
            ("m", "mm"): 1000.0,
            ("m", "cm"): 100.0,
            ("ft", "m"): 0.3048,
            ("m", "ft"): 3.28084,
            ("in", "m"): 0.0254,
            ("m", "in"): 39.3701,
            ("in", "mm"): 25.4,
            ("mm", "in"): 0.0393701,
        }

        # Area conversions (to m²)
        self.area_conversions = {
            ("mm2", "m2"): 1e-6,
            ("cm2", "m2"): 1e-4,
            ("m2", "mm2"): 1e6,
            ("m2", "cm2"): 1e4,
            ("ft2", "m2"): 0.092903,
            ("m2", "ft2"): 10.7639,
            ("in2", "m2"): 0.00064516,
            ("m2", "in2"): 1550.0,
        }

        # Volume conversions (to m³)
        self.volume_conversions = {
            ("l", "m3"): 0.001,
            ("m3", "l"): 1000.0,
            ("ft3", "m3"): 0.0283168,
            ("m3", "ft3"): 35.3147,
            ("gal", "m3"): 0.00378541,  # US gallon
            ("m3", "gal"): 264.172,
        }

        # Pressure conversions (to Pascal)
        self.pressure_conversions = {
            ("bar", "pa"): 100000.0,
            ("pa", "bar"): 1e-5,
            ("psi", "pa"): 6894.76,
            ("pa", "psi"): 0.000145038,
            ("atm", "pa"): 101325.0,
            ("pa", "atm"): 9.8692e-6,
            ("kpa", "pa"): 1000.0,
            ("pa", "kpa"): 0.001,
            ("mpa", "pa"): 1e6,
            ("pa", "mpa"): 1e-6,
        }

        # Flow rate conversions (to m³/h)
        self.flow_rate_conversions = {
            ("scfm", "m3h"): 1.69901,
            ("m3h", "scfm"): 0.588578,
            ("l/s", "m3h"): 3.6,
            ("m3h", "l/s"): 0.277778,
            ("cfm", "m3h"): 1.69901,
            ("m3h", "cfm"): 0.588578,
        }

        # Thermal conductivity (to W/(m·K))
        self.thermal_conductivity_conversions = {
            ("btu_ft_hr_f", "w_m_k"): 1.73073,
            ("w_m_k", "btu_ft_hr_f"): 0.577789,
            ("cal_cm_s_c", "w_m_k"): 418.4,
            ("w_m_k", "cal_cm_s_c"): 0.00239006,
        }

        # Specific heat (to kJ/(kg·K))
        self.specific_heat_conversions = {
            ("btu_lb_f", "kj_kg_k"): 4.184,
            ("kj_kg_k", "btu_lb_f"): 0.238846,
            ("cal_g_c", "kj_kg_k"): 4.184,
            ("kj_kg_k", "cal_g_c"): 0.238846,
        }

        # Density conversions (to kg/m³)
        self.density_conversions = {
            ("lb_ft3", "kg_m3"): 16.0185,
            ("kg_m3", "lb_ft3"): 0.0624279,
            ("g_cm3", "kg_m3"): 1000.0,
            ("kg_m3", "g_cm3"): 0.001,
        }

        # Power conversions (to Watts)
        self.power_conversions = {
            ("btu_h", "w"): 0.293071,
            ("w", "btu_h"): 3.41214,
            ("hp", "w"): 745.7,
            ("w", "hp"): 0.00134102,
            ("kw", "w"): 1000.0,
            ("w", "kw"): 0.001,
            ("mw", "w"): 1e6,
            ("w", "mw"): 1e-6,
        }

        # Energy conversions (to Joules)
        self.energy_conversions = {
            ("btu", "j"): 1055.06,
            ("j", "btu"): 0.000947817,
            ("kwh", "j"): 3.6e6,
            ("j", "kwh"): 2.77778e-7,
            ("cal", "j"): 4.184,
            ("j", "cal"): 0.238846,
            ("kj", "j"): 1000.0,
            ("j", "kj"): 0.001,
        }

    async def convert_value(
        self,
        value: float,
        from_unit: str,
        to_unit: str,
        unit_type: UnitType
    ) -> float:
        """
        Convert a value from one unit to another.

        Args:
            value: Value to convert
            from_unit: Source unit
            to_unit: Target unit
            unit_type: Type of unit conversion

        Returns:
            Converted value

        Raises:
            ValueError: If conversion is not supported
        """
        if from_unit.lower() == to_unit.lower():
            return value

        # Check database for custom conversions first
        db_conversion = await self._get_database_conversion(from_unit, to_unit, unit_type)
        if db_conversion:
            return (value * db_conversion.conversion_factor) + db_conversion.conversion_offset

        # Use built-in conversions
        conversion_key = (from_unit.lower(), to_unit.lower())

        if unit_type == UnitType.TEMPERATURE:
            if conversion_key in self.temperature_conversions:
                return self.temperature_conversions[conversion_key](value)

        elif unit_type == UnitType.LENGTH:
            factor = self.length_conversions.get(conversion_key)
            if factor:
                return value * factor

        elif unit_type == UnitType.AREA:
            factor = self.area_conversions.get(conversion_key)
            if factor:
                return value * factor

        elif unit_type == UnitType.VOLUME:
            factor = self.volume_conversions.get(conversion_key)
            if factor:
                return value * factor

        elif unit_type == UnitType.PRESSURE:
            factor = self.pressure_conversions.get(conversion_key)
            if factor:
                return value * factor

        elif unit_type == UnitType.FLOW_RATE:
            factor = self.flow_rate_conversions.get(conversion_key)
            if factor:
                return value * factor

        elif unit_type == UnitType.THERMAL_CONDUCTIVITY:
            factor = self.thermal_conductivity_conversions.get(conversion_key)
            if factor:
                return value * factor

        elif unit_type == UnitType.SPECIFIC_HEAT:
            factor = self.specific_heat_conversions.get(conversion_key)
            if factor:
                return value * factor

        elif unit_type == UnitType.DENSITY:
            factor = self.density_conversions.get(conversion_key)
            if factor:
                return value * factor

        elif unit_type == UnitType.POWER:
            factor = self.power_conversions.get(conversion_key)
            if factor:
                return value * factor

        elif unit_type == UnitType.ENERGY:
            factor = self.energy_conversions.get(conversion_key)
            if factor:
                return value * factor

        # If no conversion found, raise error
        raise ValueError(f"Conversion not supported: {from_unit} to {to_unit} for {unit_type}")

    async def get_supported_units(self, unit_type: UnitType) -> List[str]:
        """
        Get list of supported units for a unit type.

        Args:
            unit_type: Type of units to get

        Returns:
            List of supported unit names
        """
        supported_units = set()

        # Get from built-in conversions
        conversion_map = {
            UnitType.TEMPERATURE: self.temperature_conversions,
            UnitType.LENGTH: self.length_conversions,
            UnitType.AREA: self.area_conversions,
            UnitType.VOLUME: self.volume_conversions,
            UnitType.PRESSURE: self.pressure_conversions,
            UnitType.FLOW_RATE: self.flow_rate_conversions,
            UnitType.THERMAL_CONDUCTIVITY: self.thermal_conductivity_conversions,
            UnitType.SPECIFIC_HEAT: self.specific_heat_conversions,
            UnitType.DENSITY: self.density_conversions,
            UnitType.POWER: self.power_conversions,
            UnitType.ENERGY: self.energy_conversions,
        }

        if unit_type in conversion_map:
            for from_unit, to_unit in conversion_map[unit_type].keys():
                supported_units.add(from_unit)
                supported_units.add(to_unit)

        # Add from database
        result = await self.db.execute(
            select(UnitConversion).where(
                UnitConversion.unit_type == unit_type,
                UnitConversion.is_active == True
            )
        )
        db_conversions = result.scalars().all()

        for conversion in db_conversions:
            supported_units.add(conversion.from_unit)
            supported_units.add(conversion.to_unit)

        return sorted(list(supported_units))

    async def create_conversion_rule(
        self,
        conversion_data: UnitConversionCreate
    ) -> UnitConversion:
        """
        Create a new unit conversion rule.

        Args:
            conversion_data: Conversion rule data

        Returns:
            Created conversion rule
        """
        conversion = UnitConversion(**conversion_data.model_dump())
        self.db.add(conversion)
        await self.db.commit()
        await self.db.refresh(conversion)

        logger.info(
            "Unit conversion rule created",
            from_unit=conversion.from_unit,
            to_unit=conversion.to_unit,
            unit_type=conversion.unit_type
        )

        return conversion

    async def get_conversion_rules(
        self,
        unit_type: Optional[UnitType] = None,
        is_active: bool = True
    ) -> List[UnitConversion]:
        """
        Get conversion rules from database.

        Args:
            unit_type: Filter by unit type
            is_active: Filter by active status

        Returns:
            List of conversion rules
        """
        query = select(UnitConversion).where(UnitConversion.is_active == is_active)

        if unit_type:
            query = query.where(UnitConversion.unit_type == unit_type)

        result = await self.db.execute(query.order_by(UnitConversion.unit_type, UnitConversion.from_unit))
        return result.scalars().all()

    async def _get_database_conversion(
        self,
        from_unit: str,
        to_unit: str,
        unit_type: UnitType
    ) -> Optional[UnitConversion]:
        """Get conversion rule from database."""
        result = await self.db.execute(
            select(UnitConversion).where(
                UnitConversion.from_unit == from_unit.lower(),
                UnitConversion.to_unit == to_unit.lower(),
                UnitConversion.unit_type == unit_type,
                UnitConversion.is_active == True
            )
        )
        return result.scalar_one_or_none()

    def get_conversion_examples(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Get examples of supported conversions for documentation.

        Returns:
            Dictionary with conversion examples by unit type
        """
        return {
            "temperature": [
                {"from": "celsius", "to": "fahrenheit", "example": "25°C → 77°F"},
                {"from": "fahrenheit", "to": "celsius", "example": "100°F → 37.8°C"},
                {"from": "celsius", "to": "kelvin", "example": "0°C → 273.15K"},
            ],
            "length": [
                {"from": "mm", "to": "m", "example": "1000mm → 1m"},
                {"from": "ft", "to": "m", "example": "3.28ft → 1m"},
                {"from": "in", "to": "mm", "example": "1in → 25.4mm"},
            ],
            "pressure": [
                {"from": "bar", "to": "pa", "example": "1bar → 100000Pa"},
                {"from": "psi", "to": "pa", "example": "1psi → 6894.76Pa"},
                {"from": "atm", "to": "pa", "example": "1atm → 101325Pa"},
            ],
            "flow_rate": [
                {"from": "scfm", "to": "m3h", "example": "1scfm → 1.699m³/h"},
                {"from": "l/s", "to": "m3h", "example": "1l/s → 3.6m³/h"},
            ],
            "thermal_conductivity": [
                {"from": "btu_ft_hr_f", "to": "w_m_k", "example": "1BTU/(ft·hr·°F) → 1.73W/(m·K)"},
            ],
            "power": [
                {"from": "btu_h", "to": "w", "example": "1BTU/h → 0.293W"},
                {"from": "hp", "to": "w", "example": "1hp → 745.7W"},
            ]
        }