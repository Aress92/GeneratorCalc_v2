using Fro.Domain.Entities;
using Fro.Domain.Enums;

namespace Fro.Application.Interfaces.Repositories;

/// <summary>
/// Optimization scenario repository interface.
/// </summary>
public interface IOptimizationScenarioRepository : IRepository<OptimizationScenario>
{
    /// <summary>
    /// Get scenarios by user ID.
    /// </summary>
    Task<List<OptimizationScenario>> GetByUserIdAsync(Guid userId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Get scenarios by base configuration ID.
    /// </summary>
    Task<List<OptimizationScenario>> GetByConfigurationIdAsync(Guid configurationId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Get scenarios by algorithm.
    /// </summary>
    Task<List<OptimizationScenario>> GetByAlgorithmAsync(OptimizationAlgorithm algorithm, CancellationToken cancellationToken = default);

    /// <summary>
    /// Get active scenarios for a user.
    /// </summary>
    Task<List<OptimizationScenario>> GetActiveByUserIdAsync(Guid userId, CancellationToken cancellationToken = default);
}

/// <summary>
/// Optimization job repository interface.
/// </summary>
public interface IOptimizationJobRepository : IRepository<OptimizationJob>
{
    /// <summary>
    /// Get jobs by scenario ID.
    /// </summary>
    Task<List<OptimizationJob>> GetByScenarioIdAsync(Guid scenarioId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Get job by Celery task ID.
    /// </summary>
    Task<OptimizationJob?> GetByCeleryTaskIdAsync(string taskId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Get active jobs for a user.
    /// </summary>
    Task<List<OptimizationJob>> GetActiveJobsByUserIdAsync(Guid userId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Get running jobs count for a user.
    /// </summary>
    Task<int> GetRunningJobsCountAsync(Guid userId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Get latest job for a scenario.
    /// </summary>
    Task<OptimizationJob?> GetLatestByScenarioIdAsync(Guid scenarioId, CancellationToken cancellationToken = default);
}
