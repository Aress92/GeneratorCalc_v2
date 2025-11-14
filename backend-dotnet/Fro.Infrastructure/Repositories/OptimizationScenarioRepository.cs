using Microsoft.EntityFrameworkCore;
using Fro.Application.Interfaces.Repositories;
using Fro.Domain.Entities;
using Fro.Domain.Enums;
using Fro.Infrastructure.Data;

namespace Fro.Infrastructure.Repositories;

/// <summary>
/// Optimization scenario repository implementation.
/// </summary>
public class OptimizationScenarioRepository : Repository<OptimizationScenario>, IOptimizationScenarioRepository
{
    public OptimizationScenarioRepository(ApplicationDbContext context) : base(context)
    {
    }

    public async Task<List<OptimizationScenario>> GetByUserIdAsync(Guid userId, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Where(s => s.UserId == userId)
            .OrderByDescending(s => s.UpdatedAt)
            .ToListAsync(cancellationToken);
    }

    public async Task<List<OptimizationScenario>> GetByConfigurationIdAsync(Guid configurationId, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Where(s => s.BaseConfigurationId == configurationId)
            .OrderByDescending(s => s.UpdatedAt)
            .ToListAsync(cancellationToken);
    }

    public async Task<List<OptimizationScenario>> GetByAlgorithmAsync(OptimizationAlgorithm algorithm, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Where(s => s.Algorithm == algorithm)
            .OrderByDescending(s => s.UpdatedAt)
            .ToListAsync(cancellationToken);
    }

    public async Task<List<OptimizationScenario>> GetActiveByUserIdAsync(Guid userId, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Where(s => s.UserId == userId && s.IsActive)
            .OrderByDescending(s => s.UpdatedAt)
            .ToListAsync(cancellationToken);
    }
}

/// <summary>
/// Optimization job repository implementation.
/// </summary>
public class OptimizationJobRepository : Repository<OptimizationJob>, IOptimizationJobRepository
{
    public OptimizationJobRepository(ApplicationDbContext context) : base(context)
    {
    }

    public async Task<List<OptimizationJob>> GetByScenarioIdAsync(Guid scenarioId, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Where(j => j.ScenarioId == scenarioId)
            .OrderByDescending(j => j.CreatedAt)
            .ToListAsync(cancellationToken);
    }

    public async Task<OptimizationJob?> GetByCeleryTaskIdAsync(string taskId, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .FirstOrDefaultAsync(j => j.CeleryTaskId == taskId, cancellationToken);
    }

    public async Task<List<OptimizationJob>> GetActiveJobsByUserIdAsync(Guid userId, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Include(j => j.Scenario)
            .Where(j => j.Scenario!.UserId == userId &&
                       (j.Status == OptimizationStatus.Pending ||
                        j.Status == OptimizationStatus.Initializing ||
                        j.Status == OptimizationStatus.Running ||
                        j.Status == OptimizationStatus.Converging))
            .OrderByDescending(j => j.CreatedAt)
            .ToListAsync(cancellationToken);
    }

    public async Task<int> GetRunningJobsCountAsync(Guid userId, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Include(j => j.Scenario)
            .CountAsync(j => j.Scenario!.UserId == userId &&
                            (j.Status == OptimizationStatus.Running ||
                             j.Status == OptimizationStatus.Converging),
                        cancellationToken);
    }

    public async Task<OptimizationJob?> GetLatestByScenarioIdAsync(Guid scenarioId, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Where(j => j.ScenarioId == scenarioId)
            .OrderByDescending(j => j.CreatedAt)
            .FirstOrDefaultAsync(cancellationToken);
    }
}
