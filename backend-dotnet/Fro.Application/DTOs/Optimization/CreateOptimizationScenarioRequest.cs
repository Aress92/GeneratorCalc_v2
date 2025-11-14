using Fro.Domain.Enums;

namespace Fro.Application.DTOs.Optimization;

/// <summary>
/// Create optimization scenario request.
/// </summary>
public class CreateOptimizationScenarioRequest
{
    public required string Name { get; set; }
    public string? Description { get; set; }
    public string ScenarioType { get; set; } = "baseline";
    public Guid BaseConfigurationId { get; set; }
    public string Objective { get; set; } = "minimize_fuel_consumption";
    public OptimizationAlgorithm Algorithm { get; set; } = OptimizationAlgorithm.SLSQP;

    // Optimization parameters (JSON strings)
    public required string OptimizationConfig { get; set; }
    public string? ConstraintsConfig { get; set; }
    public string? BoundsConfig { get; set; }
    public required string DesignVariables { get; set; }
    public string? ObjectiveWeights { get; set; }

    // Termination criteria
    public int MaxIterations { get; set; } = 1000;
    public int MaxFunctionEvaluations { get; set; } = 5000;
    public double Tolerance { get; set; } = 1e-6;
    public int MaxRuntimeMinutes { get; set; } = 120;
}
