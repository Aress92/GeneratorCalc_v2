using Fro.Domain.Enums;

namespace Fro.Application.DTOs.Optimization;

/// <summary>
/// Optimization job execution DTO.
/// </summary>
public class OptimizationJobDto
{
    public Guid Id { get; set; }
    public Guid ScenarioId { get; set; }
    public string? CeleryTaskId { get; set; }
    public OptimizationStatus Status { get; set; }
    public double Progress { get; set; }
    public int? CurrentIteration { get; set; }
    public double? CurrentObjectiveValue { get; set; }
    public double? BestObjectiveValue { get; set; }
    public string? BestSolution { get; set; }
    public string? ConvergenceHistory { get; set; }
    public string? Results { get; set; }
    public string? ErrorMessage { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? StartedAt { get; set; }
    public DateTime? CompletedAt { get; set; }
    public DateTime? EstimatedCompletionAt { get; set; }
    public double? RuntimeSeconds { get; set; }
}
