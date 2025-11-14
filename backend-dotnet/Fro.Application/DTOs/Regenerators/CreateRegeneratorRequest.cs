using Fro.Domain.Enums;

namespace Fro.Application.DTOs.Regenerators;

/// <summary>
/// Create new regenerator configuration.
/// </summary>
public class CreateRegeneratorRequest
{
    /// <summary>
    /// Configuration name (required)
    /// </summary>
    public required string Name { get; set; }

    /// <summary>
    /// Description
    /// </summary>
    public string? Description { get; set; }

    /// <summary>
    /// Type of regenerator
    /// </summary>
    public RegeneratorType RegeneratorType { get; set; }

    /// <summary>
    /// Optional template ID to base configuration on
    /// </summary>
    public Guid? BasedOnTemplateId { get; set; }
}
