namespace Fro.Domain.Enums;

/// <summary>
/// Status of regenerator configuration.
/// </summary>
public enum ConfigurationStatus
{
    /// <summary>
    /// Configuration is in draft status, still being edited
    /// </summary>
    DRAFT,

    /// <summary>
    /// Configuration is validated and ready for optimization
    /// </summary>
    VALIDATED,

    /// <summary>
    /// Configuration is archived (not actively used)
    /// </summary>
    ARCHIVED,

    /// <summary>
    /// Configuration is marked as template for others to use
    /// </summary>
    TEMPLATE
}
