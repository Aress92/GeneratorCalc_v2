using System.Text.Json.Serialization;

namespace Fro.Application.DTOs.PythonOptimizer;

/// <summary>
/// Request to Python SLSQP optimizer microservice.
/// </summary>
public class PythonOptimizerRequest
{
    [JsonPropertyName("configuration")]
    public required RegeneratorConfiguration Configuration { get; set; }

    [JsonPropertyName("design_variables")]
    public required Dictionary<string, object> DesignVariables { get; set; }

    [JsonPropertyName("bounds")]
    public required Dictionary<string, BoundsConfig> Bounds { get; set; }

    [JsonPropertyName("initial_values")]
    public Dictionary<string, double>? InitialValues { get; set; }

    [JsonPropertyName("objective")]
    public string Objective { get; set; } = "maximize_efficiency";

    [JsonPropertyName("algorithm")]
    public string Algorithm { get; set; } = "SLSQP";

    [JsonPropertyName("max_iterations")]
    public int MaxIterations { get; set; } = 100;

    [JsonPropertyName("tolerance")]
    public double Tolerance { get; set; } = 1e-6;

    [JsonPropertyName("constraints")]
    public OptimizationConstraints? Constraints { get; set; }
}

public class RegeneratorConfiguration
{
    [JsonPropertyName("geometry_config")]
    public GeometryConfig? GeometryConfig { get; set; }

    [JsonPropertyName("thermal_config")]
    public ThermalConfig? ThermalConfig { get; set; }

    [JsonPropertyName("flow_config")]
    public FlowConfig? FlowConfig { get; set; }

    [JsonPropertyName("materials_config")]
    public Dictionary<string, object>? MaterialsConfig { get; set; }
}

public class GeometryConfig
{
    [JsonPropertyName("length")]
    public double Length { get; set; } = 10.0;

    [JsonPropertyName("width")]
    public double Width { get; set; } = 8.0;
}

public class ThermalConfig
{
    [JsonPropertyName("gas_temp_inlet")]
    public double GasTempInlet { get; set; } = 1600;

    [JsonPropertyName("gas_temp_outlet")]
    public double GasTempOutlet { get; set; } = 600;
}

public class FlowConfig
{
    [JsonPropertyName("mass_flow_rate")]
    public double MassFlowRate { get; set; } = 50;

    [JsonPropertyName("cycle_time")]
    public double CycleTime { get; set; } = 1200;
}

public class BoundsConfig
{
    [JsonPropertyName("min")]
    public required double Min { get; set; }

    [JsonPropertyName("max")]
    public required double Max { get; set; }
}

public class OptimizationConstraints
{
    [JsonPropertyName("max_pressure_drop")]
    public double MaxPressureDrop { get; set; } = 2000;

    [JsonPropertyName("min_thermal_efficiency")]
    public double MinThermalEfficiency { get; set; } = 0.2;

    [JsonPropertyName("min_heat_transfer_coefficient")]
    public double MinHeatTransferCoefficient { get; set; } = 50;
}
