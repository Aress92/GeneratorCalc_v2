using Fro.Application.DTOs.Common;
using Fro.Domain.Enums;

namespace Fro.Application.DTOs.Optimization;

/// <summary>
/// List optimization scenarios with filters.
/// </summary>
public class OptimizationListRequest : PaginatedRequest
{
    /// <summary>
    /// Filter by scenario type
    /// </summary>
    public string? ScenarioType { get; set; }

    /// <summary>
    /// Filter by optimization algorithm
    /// </summary>
    public OptimizationAlgorithm? Algorithm { get; set; }

    /// <summary>
    /// Filter by scenario status (active, archived, etc.)
    /// </summary>
    public string? Status { get; set; }

    /// <summary>
    /// Filter by active status
    /// </summary>
    public bool? IsActive { get; set; }

    /// <summary>
    /// Filter by user ID
    /// </summary>
    public Guid? UserId { get; set; }

    /// <summary>
    /// Filter by base configuration ID
    /// </summary>
    public Guid? BaseConfigurationId { get; set; }
}
