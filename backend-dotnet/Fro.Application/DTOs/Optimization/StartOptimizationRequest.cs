namespace Fro.Application.DTOs.Optimization;

/// <summary>
/// Start optimization job request.
/// </summary>
public class StartOptimizationRequest
{
    /// <summary>
    /// Optimization scenario ID
    /// </summary>
    public Guid ScenarioId { get; set; }

    /// <summary>
    /// Optional: Override max iterations
    /// </summary>
    public int? MaxIterations { get; set; }

    /// <summary>
    /// Optional: Override max runtime in minutes
    /// </summary>
    public int? MaxRuntimeMinutes { get; set; }

    /// <summary>
    /// Optional: Priority (1-10, default 5)
    /// </summary>
    public int Priority { get; set; } = 5;
}
