using Hangfire;
using Hangfire.Server;
using Microsoft.Extensions.Logging;
using Fro.Application.Interfaces.Repositories;
using Fro.Domain.Entities;
using Fro.Domain.Enums;

namespace Fro.Infrastructure.Jobs;

/// <summary>
/// Hangfire background job for running optimization algorithms.
/// </summary>
/// <remarks>
/// This job orchestrates the optimization process:
/// 1. Fetch scenario and job configuration
/// 2. Call Python optimizer service (or C# implementation)
/// 3. Update job status and progress
/// 4. Save optimization results
///
/// TODO: Implement Python optimizer service integration (see SLSQP_OPTIMIZER_INTEGRATION_STRATEGY.md)
/// </remarks>
public class OptimizationJob
{
    private readonly IOptimizationJobRepository _jobRepository;
    private readonly IOptimizationScenarioRepository _scenarioRepository;
    private readonly IRegeneratorConfigurationRepository _configRepository;
    private readonly ILogger<OptimizationJob> _logger;

    public OptimizationJob(
        IOptimizationJobRepository jobRepository,
        IOptimizationScenarioRepository scenarioRepository,
        IRegeneratorConfigurationRepository configRepository,
        ILogger<OptimizationJob> logger)
    {
        _jobRepository = jobRepository;
        _scenarioRepository = scenarioRepository;
        _configRepository = configRepository;
        _logger = logger;
    }

    /// <summary>
    /// Execute optimization job in background.
    /// </summary>
    /// <param name="jobId">Optimization job ID</param>
    /// <param name="performContext">Hangfire execution context for progress tracking</param>
    [AutomaticRetry(Attempts = 0)] // Don't retry failed optimizations automatically
    [Queue("optimization")] // Use dedicated queue for long-running optimizations
    public async Task ExecuteAsync(Guid jobId, PerformContext performContext)
    {
        _logger.LogInformation("Starting optimization job {JobId}", jobId);

        try
        {
            // 1. Fetch job and scenario
            var job = await _jobRepository.GetByIdAsync(jobId);
            if (job == null)
            {
                _logger.LogError("Optimization job {JobId} not found", jobId);
                throw new InvalidOperationException($"Job {jobId} not found");
            }

            var scenario = await _scenarioRepository.GetByIdAsync(job.ScenarioId);
            if (scenario == null)
            {
                _logger.LogError("Optimization scenario {ScenarioId} not found for job {JobId}",
                    job.ScenarioId, jobId);
                throw new InvalidOperationException($"Scenario {job.ScenarioId} not found");
            }

            var baseConfig = await _configRepository.GetByIdAsync(scenario.BaseConfigurationId);
            if (baseConfig == null)
            {
                _logger.LogError("Base configuration {ConfigId} not found for scenario {ScenarioId}",
                    scenario.BaseConfigurationId, scenario.Id);
                throw new InvalidOperationException($"Configuration {scenario.BaseConfigurationId} not found");
            }

            // 2. Update job status to RUNNING
            job.Status = OptimizationStatus.Running;
            job.StartedAt = DateTime.UtcNow;
            job.HangfireJobId = performContext.BackgroundJob.Id;
            await _jobRepository.UpdateAsync(job);

            // 3. Report initial progress
            performContext.SetJobParameter("progress", 0);
            performContext.SetJobParameter("status", "Initializing");

            // 4. Build optimization request
            // TODO: Implement IOptimizerService and call Python optimizer microservice
            // For now, this is a placeholder that simulates optimization

            _logger.LogInformation(
                "Job {JobId}: Scenario={ScenarioId}, Algorithm={Algorithm}, MaxIterations={MaxIter}",
                jobId, scenario.Id, scenario.Algorithm, scenario.MaxIterations);

            // Placeholder: Simulate optimization progress
            await SimulateOptimizationAsync(job, scenario, performContext);

            // 5. Update job status to COMPLETED
            job.Status = OptimizationStatus.Completed;
            job.CompletedAt = DateTime.UtcNow;
            job.Progress = 100;

            // TODO: Save actual optimization results from optimizer service
            job.Results = System.Text.Json.JsonSerializer.Serialize(new Dictionary<string, object>
            {
                { "thermal_efficiency", 0.85 },
                { "heat_transfer_rate", 125000.0 },
                { "pressure_drop", 1450.0 },
                { "iterations", 47 },
                { "converged", true },
                { "message", "Placeholder optimization completed (TODO: integrate Python service)" }
            });

            await _jobRepository.UpdateAsync(job);

            performContext.SetJobParameter("progress", 100);
            performContext.SetJobParameter("status", "Completed");

            _logger.LogInformation("Optimization job {JobId} completed successfully", jobId);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Optimization job {JobId} failed", jobId);

            // Update job status to FAILED
            var job = await _jobRepository.GetByIdAsync(jobId);
            if (job != null)
            {
                job.Status = OptimizationStatus.Failed;
                job.CompletedAt = DateTime.UtcNow;
                job.ErrorMessage = ex.Message;
                await _jobRepository.UpdateAsync(job);
            }

            performContext.SetJobParameter("status", "Failed");
            performContext.SetJobParameter("error", ex.Message);

            throw; // Re-throw to mark Hangfire job as failed
        }
    }

    /// <summary>
    /// Simulate optimization progress for testing (placeholder).
    /// TODO: Replace with actual Python optimizer service integration.
    /// </summary>
    private async Task SimulateOptimizationAsync(
        Domain.Entities.OptimizationJob job,
        OptimizationScenario scenario,
        PerformContext performContext)
    {
        var maxIterations = scenario.MaxIterations > 0 ? scenario.MaxIterations : 100;
        var iterationsPerUpdate = Math.Max(1, maxIterations / 20); // Update 20 times

        for (int i = 0; i <= maxIterations; i++)
        {
            // Simulate optimization work
            await Task.Delay(50); // Simulate 50ms per iteration

            // Update progress periodically
            if (i % iterationsPerUpdate == 0 || i == maxIterations)
            {
                var progress = (int)((i / (double)maxIterations) * 100);
                job.Progress = progress;
                await _jobRepository.UpdateAsync(job);

                performContext.SetJobParameter("progress", progress);
                performContext.SetJobParameter("current_iteration", i);
                performContext.SetJobParameter("max_iterations", maxIterations);

                _logger.LogDebug("Job {JobId} progress: {Progress}% ({Iteration}/{MaxIter})",
                    job.Id, progress, i, maxIterations);
            }

            // Check for cancellation
            if (performContext.CancellationToken.ShutdownToken.IsCancellationRequested)
            {
                _logger.LogWarning("Optimization job {JobId} was cancelled", job.Id);
                throw new OperationCanceledException("Optimization cancelled by user or shutdown");
            }
        }
    }
}
