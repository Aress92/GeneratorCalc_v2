using System.Runtime.Serialization;

namespace Fro.Domain.Enums;

/// <summary>
/// Status of regenerator configuration.
/// Matches Python backend: draft, in_progress, completed, validated, archived
/// </summary>
public enum ConfigurationStatus
{
    /// <summary>
    /// Configuration is in draft status, still being edited
    /// </summary>
    [EnumMember(Value = "draft")]
    DRAFT,

    /// <summary>
    /// Configuration is in progress
    /// </summary>
    [EnumMember(Value = "in_progress")]
    IN_PROGRESS,

    /// <summary>
    /// Configuration is completed
    /// </summary>
    [EnumMember(Value = "completed")]
    COMPLETED,

    /// <summary>
    /// Configuration is validated and ready for optimization
    /// </summary>
    [EnumMember(Value = "validated")]
    VALIDATED,

    /// <summary>
    /// Configuration is archived (not actively used)
    /// </summary>
    [EnumMember(Value = "archived")]
    ARCHIVED
}
