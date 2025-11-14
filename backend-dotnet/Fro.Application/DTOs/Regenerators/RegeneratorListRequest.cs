using Fro.Application.DTOs.Common;
using Fro.Domain.Enums;

namespace Fro.Application.DTOs.Regenerators;

/// <summary>
/// List regenerators with filters.
/// </summary>
public class RegeneratorListRequest : PaginatedRequest
{
    /// <summary>
    /// Filter by regenerator type
    /// </summary>
    public RegeneratorType? RegeneratorType { get; set; }

    /// <summary>
    /// Filter by configuration status
    /// </summary>
    public ConfigurationStatus? Status { get; set; }

    /// <summary>
    /// Filter by validation status
    /// </summary>
    public bool? IsValidated { get; set; }

    /// <summary>
    /// Filter by template flag
    /// </summary>
    public bool? IsTemplate { get; set; }

    /// <summary>
    /// Filter by user ID (admin can see all)
    /// </summary>
    public Guid? UserId { get; set; }
}
