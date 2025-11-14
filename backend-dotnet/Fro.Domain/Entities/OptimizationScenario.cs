using Fro.Domain.Enums;

namespace Fro.Domain.Entities;

/// <summary>
/// Optimization scenario configuration.
/// </summary>
public class OptimizationScenario : BaseEntity
{
    /// <summary>
    /// Owner user ID
    /// </summary>
    public Guid UserId { get; set; }

    /// <summary>
    /// Scenario name
    /// </summary>
    public required string Name { get; set; }

    /// <summary>
    /// Description of the scenario
    /// </summary>
    public string? Description { get; set; }

    /// <summary>
    /// Type of scenario (baseline, geometry_optimization, etc.)
    /// </summary>
    public string ScenarioType { get; set; } = "baseline";

    /// <summary>
    /// Source regenerator configuration ID
    /// </summary>
    public Guid BaseConfigurationId { get; set; }

    /// <summary>
    /// Optimization objective (minimize_fuel_consumption, etc.)
    /// </summary>
    public string Objective { get; set; } = "minimize_fuel_consumption";

    /// <summary>
    /// Optimization algorithm to use
    /// </summary>
    public OptimizationAlgorithm Algorithm { get; set; } = OptimizationAlgorithm.SLSQP;

    // Optimization parameters (stored as JSON)
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

    // Status
    public string Status { get; set; } = "active";
    public bool IsActive { get; set; } = true;
    public bool IsTemplate { get; set; } = false;

    // Navigation properties
    public User? User { get; set; }
    public RegeneratorConfiguration? BaseConfiguration { get; set; }
    public ICollection<OptimizationJob> OptimizationJobs { get; set; } = new List<OptimizationJob>();
}

/// <summary>
/// Optimization job execution record.
/// </summary>
public class OptimizationJob : BaseEntity
{
    /// <summary>
    /// Parent scenario ID
    /// </summary>
    public Guid ScenarioId { get; set; }

    /// <summary>
    /// Celery/Hangfire job ID (nullable until job is enqueued)
    /// </summary>
    public string? CeleryTaskId { get; set; }

    /// <summary>
    /// Hangfire job ID (for .NET backend)
    /// </summary>
    public string? HangfireJobId { get; set; }

    /// <summary>
    /// Current status of the optimization job
    /// </summary>
    public OptimizationStatus Status { get; set; } = OptimizationStatus.Pending;

    /// <summary>
    /// Progress percentage (0-100)
    /// </summary>
    public double Progress { get; set; } = 0.0;

    /// <summary>
    /// Current iteration number
    /// </summary>
    public int? CurrentIteration { get; set; }

    /// <summary>
    /// Current objective function value
    /// </summary>
    public double? CurrentObjectiveValue { get; set; }

    /// <summary>
    /// Best objective value found so far
    /// </summary>
    public double? BestObjectiveValue { get; set; }

    /// <summary>
    /// Best solution found (JSON)
    /// </summary>
    public string? BestSolution { get; set; }

    /// <summary>
    /// Convergence history (JSON array of objective values)
    /// </summary>
    public string? ConvergenceHistory { get; set; }

    /// <summary>
    /// Final optimization results (JSON)
    /// </summary>
    public string? Results { get; set; }

    /// <summary>
    /// Error message if job failed
    /// </summary>
    public string? ErrorMessage { get; set; }

    /// <summary>
    /// Error traceback for debugging
    /// </summary>
    public string? ErrorTraceback { get; set; }

    // Timestamps
    public DateTime? StartedAt { get; set; }
    public DateTime? CompletedAt { get; set; }
    public DateTime? EstimatedCompletionAt { get; set; }

    /// <summary>
    /// Actual runtime in seconds
    /// </summary>
    public double? RuntimeSeconds { get; set; }

    // Navigation properties
    public OptimizationScenario? Scenario { get; set; }
}
