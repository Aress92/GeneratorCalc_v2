using Fro.Domain.Enums;

namespace Fro.Application.DTOs.Optimization;

/// <summary>
/// Optimization scenario DTO.
/// </summary>
public class OptimizationScenarioDto
{
    public Guid Id { get; set; }
    public Guid UserId { get; set; }
    public required string Name { get; set; }
    public string? Description { get; set; }
    public string ScenarioType { get; set; } = "baseline";
    public Guid BaseConfigurationId { get; set; }
    public string Objective { get; set; } = "minimize_fuel_consumption";
    public OptimizationAlgorithm Algorithm { get; set; }

    // Optimization parameters (JSON strings)
    public required string OptimizationConfig { get; set; }
    public string? ConstraintsConfig { get; set; }
    public string? BoundsConfig { get; set; }
    public required string DesignVariables { get; set; }
    public string? ObjectiveWeights { get; set; }

    // Termination criteria
    public int MaxIterations { get; set; }
    public int MaxFunctionEvaluations { get; set; }
    public double Tolerance { get; set; }
    public int MaxRuntimeMinutes { get; set; }

    // Status
    public string Status { get; set; } = "active";
    public bool IsActive { get; set; }
    public bool IsTemplate { get; set; }

    // Timestamps
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
}
