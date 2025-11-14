using Fro.Application.DTOs.Common;
using Fro.Application.DTOs.Optimization;
using Fro.Application.Interfaces.Repositories;
using Fro.Application.Interfaces.Services;
using Fro.Domain.Entities;
using Fro.Domain.Enums;

namespace Fro.Application.Services;

/// <summary>
/// Optimization service implementation.
/// </summary>
public class OptimizationService : IOptimizationService
{
    private readonly IOptimizationScenarioRepository _scenarioRepository;
    private readonly IOptimizationJobRepository _jobRepository;
    private readonly IRegeneratorConfigurationRepository _configRepository;

    public OptimizationService(
        IOptimizationScenarioRepository scenarioRepository,
        IOptimizationJobRepository jobRepository,
        IRegeneratorConfigurationRepository configRepository)
    {
        _scenarioRepository = scenarioRepository;
        _jobRepository = jobRepository;
        _configRepository = configRepository;
    }

    /// <summary>
    /// Get optimization scenario by ID.
    /// </summary>
    public async Task<OptimizationScenarioDto?> GetScenarioByIdAsync(Guid id, Guid userId)
    {
        var scenario = await _scenarioRepository.GetByIdAsync(id);

        if (scenario == null)
        {
            return null;
        }

        // Verify ownership through base configuration
        var config = await _configRepository.GetByIdAsync(scenario.BaseConfigurationId);
        if (config == null || config.UserId != userId)
        {
            return null;
        }

        return MapScenarioToDto(scenario);
    }

    /// <summary>
    /// Get paginated list of optimization scenarios for a user.
    /// </summary>
    public async Task<PaginatedResponse<OptimizationScenarioDto>> GetUserScenariosAsync(
        Guid userId,
        OptimizationListRequest request)
    {
        var allScenarios = await _scenarioRepository.GetAllAsync();

        // Filter by user ownership through configurations
        var userConfigs = await _configRepository.GetByUserIdAsync(userId);
        var userConfigIds = userConfigs.Select(c => c.Id).ToHashSet();

        var query = allScenarios
            .Where(s => userConfigIds.Contains(s.BaseConfigurationId))
            .AsQueryable();

        // Apply filters
        if (!string.IsNullOrWhiteSpace(request.Status))
        {
            query = query.Where(s => s.Status == request.Status);
        }

        if (!string.IsNullOrWhiteSpace(request.SearchTerm))
        {
            var searchLower = request.SearchTerm.ToLower();
            query = query.Where(s =>
                s.Name.ToLower().Contains(searchLower) ||
                (s.Description != null && s.Description.ToLower().Contains(searchLower))
            );
        }

        var totalCount = query.Count();

        // Apply sorting
        query = request.SortBy?.ToLower() switch
        {
            "name" => request.SortDescending ? query.OrderByDescending(s => s.Name) : query.OrderBy(s => s.Name),
            "status" => request.SortDescending ? query.OrderByDescending(s => s.Status) : query.OrderBy(s => s.Status),
            _ => query.OrderByDescending(s => s.UpdatedAt) // Default sort
        };

        // Apply pagination
        var scenarios = query
            .Skip((request.Page - 1) * request.PageSize)
            .Take(request.PageSize)
            .Select(MapScenarioToDto)
            .ToList();

        return new PaginatedResponse<OptimizationScenarioDto>
        {
            Items = scenarios,
            TotalCount = totalCount,
            Page = request.Page,
            PageSize = request.PageSize,
            TotalPages = (int)Math.Ceiling(totalCount / (double)request.PageSize)
        };
    }

    /// <summary>
    /// Create new optimization scenario.
    /// </summary>
    public async Task<OptimizationScenarioDto> CreateScenarioAsync(
        CreateOptimizationScenarioRequest request,
        Guid userId)
    {
        // Verify base configuration exists and user has access
        var config = await _configRepository.GetByIdAsync(request.BaseConfigurationId);
        if (config == null || config.UserId != userId)
        {
            throw new UnauthorizedAccessException("Base configuration not found or access denied");
        }

        var scenario = new OptimizationScenario
        {
            Id = Guid.NewGuid(),
            Name = request.Name,
            Description = request.Description,
            ScenarioType = request.ScenarioType,
            BaseConfigurationId = request.BaseConfigurationId,
            Status = "active",
            Objective = request.Objective,
            Algorithm = request.Algorithm,
            OptimizationConfig = request.OptimizationConfig,
            ConstraintsConfig = request.ConstraintsConfig,
            BoundsConfig = request.BoundsConfig,
            DesignVariables = request.DesignVariables,
            ObjectiveWeights = request.ObjectiveWeights,
            MaxIterations = request.MaxIterations,
            MaxFunctionEvaluations = request.MaxFunctionEvaluations,
            Tolerance = request.Tolerance,
            MaxRuntimeMinutes = request.MaxRuntimeMinutes,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };

        await _scenarioRepository.AddAsync(scenario);
        return MapScenarioToDto(scenario);
    }

    /// <summary>
    /// Start optimization job for a scenario.
    /// </summary>
    public async Task<OptimizationJobDto> StartOptimizationAsync(
        StartOptimizationRequest request,
        Guid userId)
    {
        var scenario = await _scenarioRepository.GetByIdAsync(request.ScenarioId);
        if (scenario == null)
        {
            throw new KeyNotFoundException("Scenario not found");
        }

        // Verify ownership
        var config = await _configRepository.GetByIdAsync(scenario.BaseConfigurationId);
        if (config == null || config.UserId != userId)
        {
            throw new UnauthorizedAccessException("Not authorized to start this optimization");
        }

        // Create optimization job
        var job = new OptimizationJob
        {
            Id = Guid.NewGuid(),
            ScenarioId = request.ScenarioId,
            Status = OptimizationStatus.Pending,
            HangfireJobId = null, // Will be set when Hangfire job is enqueued
            CurrentIteration = 0,
            StartedAt = DateTime.UtcNow,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };

        await _jobRepository.AddAsync(job);

        // TODO: Enqueue Hangfire job here
        // var hangfireJobId = BackgroundJob.Enqueue(() => RunOptimization(job.Id));
        // job.HangfireJobId = hangfireJobId;
        // await _jobRepository.UpdateAsync(job);

        return MapJobToDto(job);
    }

    /// <summary>
    /// Get optimization job by ID.
    /// </summary>
    public async Task<OptimizationJobDto?> GetJobByIdAsync(Guid jobId, Guid userId)
    {
        var job = await _jobRepository.GetByIdAsync(jobId);
        if (job == null)
        {
            return null;
        }

        // Verify ownership through scenario and configuration
        var scenario = await _scenarioRepository.GetByIdAsync(job.ScenarioId);
        if (scenario == null)
        {
            return null;
        }

        var config = await _configRepository.GetByIdAsync(scenario.BaseConfigurationId);
        if (config == null || config.UserId != userId)
        {
            return null;
        }

        return MapJobToDto(job);
    }

    /// <summary>
    /// Get all jobs for a scenario.
    /// </summary>
    public async Task<List<OptimizationJobDto>> GetScenarioJobsAsync(Guid scenarioId, Guid userId)
    {
        var scenario = await _scenarioRepository.GetByIdAsync(scenarioId);
        if (scenario == null)
        {
            throw new KeyNotFoundException("Scenario not found");
        }

        // Verify ownership
        var config = await _configRepository.GetByIdAsync(scenario.BaseConfigurationId);
        if (config == null || config.UserId != userId)
        {
            throw new UnauthorizedAccessException("Not authorized to view these jobs");
        }

        var jobs = await _jobRepository.GetByScenarioIdAsync(scenarioId);
        return jobs.Select(MapJobToDto).ToList();
    }

    /// <summary>
    /// Cancel running optimization job.
    /// </summary>
    public async Task CancelJobAsync(Guid jobId, Guid userId)
    {
        var job = await _jobRepository.GetByIdAsync(jobId);
        if (job == null)
        {
            throw new KeyNotFoundException("Job not found");
        }

        // Verify ownership
        var scenario = await _scenarioRepository.GetByIdAsync(job.ScenarioId);
        if (scenario != null)
        {
            var config = await _configRepository.GetByIdAsync(scenario.BaseConfigurationId);
            if (config == null || config.UserId != userId)
            {
                throw new UnauthorizedAccessException("Not authorized to cancel this job");
            }
        }

        // Update job status
        job.Status = OptimizationStatus.Failed;
        job.CompletedAt = DateTime.UtcNow;
        job.UpdatedAt = DateTime.UtcNow;

        await _jobRepository.UpdateAsync(job);

        // TODO: Cancel Hangfire job
        // if (!string.IsNullOrEmpty(job.HangfireJobId))
        // {
        //     BackgroundJob.Delete(job.HangfireJobId);
        // }
    }

    /// <summary>
    /// Get job progress.
    /// </summary>
    public async Task<JobProgress> GetJobProgressAsync(Guid jobId)
    {
        var job = await _jobRepository.GetByIdAsync(jobId);
        if (job == null)
        {
            throw new KeyNotFoundException("Job not found");
        }

        // Get scenario to get max iterations
        var scenario = await _scenarioRepository.GetByIdAsync(job.ScenarioId);
        var maxIterations = scenario?.MaxIterations ?? 1000;

        var progressPercentage = maxIterations > 0
            ? (double)(job.CurrentIteration ?? 0) / maxIterations * 100
            : 0;

        return new JobProgress
        {
            Status = job.Status,
            CurrentIteration = job.CurrentIteration ?? 0,
            MaxIterations = maxIterations,
            CurrentObjectiveValue = job.BestObjectiveValue,
            ProgressPercentage = progressPercentage,
            StatusMessage = job.ErrorMessage
        };
    }

    /// <summary>
    /// Map OptimizationScenario entity to DTO.
    /// </summary>
    private static OptimizationScenarioDto MapScenarioToDto(OptimizationScenario scenario)
    {
        return new OptimizationScenarioDto
        {
            Id = scenario.Id,
            Name = scenario.Name,
            Description = scenario.Description,
            ScenarioType = scenario.ScenarioType,
            BaseConfigurationId = scenario.BaseConfigurationId,
            Status = scenario.Status,
            Objective = scenario.Objective,
            Algorithm = scenario.Algorithm,
            OptimizationConfig = scenario.OptimizationConfig,
            ConstraintsConfig = scenario.ConstraintsConfig,
            BoundsConfig = scenario.BoundsConfig,
            DesignVariables = scenario.DesignVariables,
            ObjectiveWeights = scenario.ObjectiveWeights,
            MaxIterations = scenario.MaxIterations,
            MaxFunctionEvaluations = scenario.MaxFunctionEvaluations,
            Tolerance = scenario.Tolerance,
            MaxRuntimeMinutes = scenario.MaxRuntimeMinutes,
            CreatedAt = scenario.CreatedAt,
            UpdatedAt = scenario.UpdatedAt
        };
    }

    /// <summary>
    /// Map OptimizationJob entity to DTO.
    /// </summary>
    private static OptimizationJobDto MapJobToDto(OptimizationJob job)
    {
        return new OptimizationJobDto
        {
            Id = job.Id,
            ScenarioId = job.ScenarioId,
            Status = job.Status,
            CurrentIteration = job.CurrentIteration,
            BestObjectiveValue = job.BestObjectiveValue,
            StartedAt = job.StartedAt,
            CompletedAt = job.CompletedAt,
            ErrorMessage = job.ErrorMessage,
            CreatedAt = job.CreatedAt
        };
    }
}
