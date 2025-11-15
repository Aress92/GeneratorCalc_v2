"""
Physics model for regenerator thermal calculations.
Extracted from backend/app/services/optimization_service.py

Model fizyczny regeneratora dla obliczeń termicznych.
"""

from typing import Dict, Any


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
