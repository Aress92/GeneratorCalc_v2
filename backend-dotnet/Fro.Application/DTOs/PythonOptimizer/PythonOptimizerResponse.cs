using System.Text.Json.Serialization;

namespace Fro.Application.DTOs.PythonOptimizer;

/// <summary>
/// Response from Python SLSQP optimizer microservice.
/// </summary>
public class PythonOptimizerResponse
{
    [JsonPropertyName("success")]
    public bool Success { get; set; }

    [JsonPropertyName("message")]
    public required string Message { get; set; }

    [JsonPropertyName("iterations")]
    public int Iterations { get; set; }

    [JsonPropertyName("final_objective_value")]
    public double FinalObjectiveValue { get; set; }

    [JsonPropertyName("optimized_design_variables")]
    public required Dictionary<string, double> OptimizedDesignVariables { get; set; }

    [JsonPropertyName("performance_metrics")]
    public required PerformanceMetrics PerformanceMetrics { get; set; }

    [JsonPropertyName("convergence_info")]
    public required ConvergenceInfo ConvergenceInfo { get; set; }

    [JsonPropertyName("constraints_satisfied")]
    public bool ConstraintsSatisfied { get; set; }

    [JsonPropertyName("constraint_violations")]
    public Dictionary<string, double>? ConstraintViolations { get; set; }
}

public class PerformanceMetrics
{
    [JsonPropertyName("thermal_efficiency")]
    public double ThermalEfficiency { get; set; }

    [JsonPropertyName("heat_transfer_rate")]
    public double HeatTransferRate { get; set; }

    [JsonPropertyName("pressure_drop")]
    public double PressureDrop { get; set; }

    [JsonPropertyName("ntu_value")]
    public double NtuValue { get; set; }

    [JsonPropertyName("effectiveness")]
    public double Effectiveness { get; set; }

    [JsonPropertyName("heat_transfer_coefficient")]
    public double HeatTransferCoefficient { get; set; }

    [JsonPropertyName("surface_area")]
    public double SurfaceArea { get; set; }

    [JsonPropertyName("wall_heat_loss")]
    public double WallHeatLoss { get; set; }

    [JsonPropertyName("reynolds_number")]
    public double ReynoldsNumber { get; set; }

    [JsonPropertyName("nusselt_number")]
    public double NusseltNumber { get; set; }
}

public class ConvergenceInfo
{
    [JsonPropertyName("converged")]
    public bool Converged { get; set; }

    [JsonPropertyName("status")]
    public int Status { get; set; }

    [JsonPropertyName("nfev")]
    public int NumberOfFunctionEvaluations { get; set; }

    [JsonPropertyName("njev")]
    public int NumberOfJacobianEvaluations { get; set; }

    [JsonPropertyName("nit")]
    public int NumberOfIterations { get; set; }
}

/// <summary>
/// Error response from Python optimizer.
/// </summary>
public class PythonOptimizerErrorResponse
{
    [JsonPropertyName("error")]
    public required string Error { get; set; }

    [JsonPropertyName("message")]
    public required string Message { get; set; }

    [JsonPropertyName("details")]
    public Dictionary<string, object>? Details { get; set; }
}
