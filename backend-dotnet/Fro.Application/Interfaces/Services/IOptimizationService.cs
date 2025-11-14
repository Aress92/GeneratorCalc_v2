using Fro.Application.DTOs.Common;
using Fro.Application.DTOs.Optimization;
using Fro.Domain.Enums;

namespace Fro.Application.Interfaces.Services;

/// <summary>
/// Service interface for optimization scenario and job management.
/// </summary>
public interface IOptimizationService
{
    /// <summary>
    /// Get optimization scenario by ID.
    /// </summary>
    Task<OptimizationScenarioDto?> GetScenarioByIdAsync(Guid id, Guid userId);

    /// <summary>
    /// Get paginated list of optimization scenarios for a user.
    /// </summary>
    Task<PaginatedResponse<OptimizationScenarioDto>> GetUserScenariosAsync(
        Guid userId,
        OptimizationListRequest request);

    /// <summary>
    /// Create new optimization scenario.
    /// </summary>
    Task<OptimizationScenarioDto> CreateScenarioAsync(
        CreateOptimizationScenarioRequest request,
        Guid userId);

    /// <summary>
    /// Start optimization job for a scenario.
    /// </summary>
    Task<OptimizationJobDto> StartOptimizationAsync(
        StartOptimizationRequest request,
        Guid userId);

    /// <summary>
    /// Get optimization job by ID.
    /// </summary>
    Task<OptimizationJobDto?> GetJobByIdAsync(Guid jobId, Guid userId);

    /// <summary>
    /// Get all jobs for a scenario.
    /// </summary>
    Task<List<OptimizationJobDto>> GetScenarioJobsAsync(Guid scenarioId, Guid userId);

    /// <summary>
    /// Cancel running optimization job.
    /// </summary>
    Task CancelJobAsync(Guid jobId, Guid userId);

    /// <summary>
    /// Get job progress.
    /// </summary>
    Task<JobProgress> GetJobProgressAsync(Guid jobId);
}

/// <summary>
/// Job progress information.
/// </summary>
public class JobProgress
{
    public OptimizationStatus Status { get; set; }
    public int CurrentIteration { get; set; }
    public int MaxIterations { get; set; }
    public double? CurrentObjectiveValue { get; set; }
    public double ProgressPercentage { get; set; }
    public string? StatusMessage { get; set; }
}
