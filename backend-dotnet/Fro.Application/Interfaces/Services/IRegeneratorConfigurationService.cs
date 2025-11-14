using Fro.Application.DTOs.Common;
using Fro.Application.DTOs.Regenerators;
using Fro.Domain.Enums;

namespace Fro.Application.Interfaces.Services;

/// <summary>
/// Service interface for regenerator configuration management.
/// </summary>
public interface IRegeneratorConfigurationService
{
    /// <summary>
    /// Get regenerator configuration by ID.
    /// </summary>
    Task<RegeneratorConfigurationDto?> GetByIdAsync(Guid id, Guid userId);

    /// <summary>
    /// Get paginated list of regenerator configurations for a user.
    /// </summary>
    Task<PaginatedResponse<RegeneratorConfigurationDto>> GetUserConfigurationsAsync(
        Guid userId,
        RegeneratorListRequest request);

    /// <summary>
    /// Create new regenerator configuration.
    /// </summary>
    Task<RegeneratorConfigurationDto> CreateConfigurationAsync(
        CreateRegeneratorRequest request,
        Guid userId);

    /// <summary>
    /// Update existing regenerator configuration.
    /// </summary>
    Task<RegeneratorConfigurationDto> UpdateConfigurationAsync(
        Guid id,
        UpdateRegeneratorRequest request,
        Guid userId);

    /// <summary>
    /// Delete regenerator configuration.
    /// </summary>
    Task DeleteConfigurationAsync(Guid id, Guid userId);

    /// <summary>
    /// Update configuration status.
    /// </summary>
    Task UpdateStatusAsync(Guid id, Fro.Domain.Enums.ConfigurationStatus newStatus, Guid userId);

    /// <summary>
    /// Clone existing configuration.
    /// </summary>
    Task<RegeneratorConfigurationDto> CloneConfigurationAsync(Guid id, Guid userId, string newName);

    /// <summary>
    /// Validate configuration data.
    /// </summary>
    Task<ValidationResult> ValidateConfigurationAsync(Guid id);
}

/// <summary>
/// Validation result for regenerator configuration.
/// </summary>
public class ValidationResult
{
    public bool IsValid { get; set; }
    public List<ValidationError> Errors { get; set; } = new();
    public List<ValidationError> Warnings { get; set; } = new();
}

/// <summary>
/// Validation error or warning.
/// </summary>
public class ValidationError
{
    public required string Field { get; set; }
    public required string Message { get; set; }
    public string Severity { get; set; } = "error"; // "error" or "warning"
}
