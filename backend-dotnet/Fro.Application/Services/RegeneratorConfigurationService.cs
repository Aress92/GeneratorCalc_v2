using Fro.Application.DTOs.Common;
using Fro.Application.DTOs.Regenerators;
using Fro.Application.Interfaces.Repositories;
using Fro.Application.Interfaces.Services;
using Fro.Domain.Entities;
using Fro.Domain.Enums;

namespace Fro.Application.Services;

/// <summary>
/// Regenerator configuration management service implementation.
/// </summary>
public class RegeneratorConfigurationService : IRegeneratorConfigurationService
{
    private readonly IRegeneratorConfigurationRepository _configRepository;

    public RegeneratorConfigurationService(IRegeneratorConfigurationRepository configRepository)
    {
        _configRepository = configRepository;
    }

    /// <summary>
    /// Get regenerator configuration by ID.
    /// </summary>
    public async Task<RegeneratorConfigurationDto?> GetByIdAsync(Guid id, Guid userId)
    {
        var config = await _configRepository.GetByIdAsync(id);

        // Check ownership
        if (config == null || config.UserId != userId)
        {
            return null;
        }

        return MapToDto(config);
    }

    /// <summary>
    /// Get paginated list of regenerator configurations for a user.
    /// </summary>
    public async Task<PaginatedResponse<RegeneratorConfigurationDto>> GetUserConfigurationsAsync(
        Guid userId,
        RegeneratorListRequest request)
    {
        var allConfigs = await _configRepository.GetByUserIdAsync(userId);

        // Apply filters
        var query = allConfigs.AsQueryable();

        if (request.Status.HasValue)
        {
            query = query.Where(c => c.Status == request.Status.Value);
        }

        if (request.RegeneratorType.HasValue)
        {
            query = query.Where(c => c.RegeneratorType == request.RegeneratorType.Value);
        }

        if (!string.IsNullOrWhiteSpace(request.SearchTerm))
        {
            var searchLower = request.SearchTerm.ToLower();
            query = query.Where(c =>
                c.Name.ToLower().Contains(searchLower) ||
                (c.Description != null && c.Description.ToLower().Contains(searchLower))
            );
        }

        var totalCount = query.Count();

        // Apply sorting
        query = request.SortBy?.ToLower() switch
        {
            "name" => request.SortDescending ? query.OrderByDescending(c => c.Name) : query.OrderBy(c => c.Name),
            "status" => request.SortDescending ? query.OrderByDescending(c => c.Status) : query.OrderBy(c => c.Status),
            "type" => request.SortDescending ? query.OrderByDescending(c => c.RegeneratorType) : query.OrderBy(c => c.RegeneratorType),
            _ => query.OrderByDescending(c => c.UpdatedAt) // Default sort by updated date
        };

        // Apply pagination
        var configs = query
            .Skip((request.Page - 1) * request.PageSize)
            .Take(request.PageSize)
            .Select(MapToDto)
            .ToList();

        return new PaginatedResponse<RegeneratorConfigurationDto>
        {
            Items = configs,
            TotalCount = totalCount,
            Page = request.Page,
            PageSize = request.PageSize,
            TotalPages = (int)Math.Ceiling(totalCount / (double)request.PageSize)
        };
    }

    /// <summary>
    /// Create new regenerator configuration.
    /// </summary>
    public async Task<RegeneratorConfigurationDto> CreateConfigurationAsync(
        CreateRegeneratorRequest request,
        Guid userId)
    {
        var config = new RegeneratorConfiguration
        {
            Id = Guid.NewGuid(),
            Name = request.Name,
            Description = request.Description,
            RegeneratorType = request.RegeneratorType,
            Status = ConfigurationStatus.DRAFT,
            UserId = userId,
            GeometryConfig = "{}",  // JSON placeholder
            MaterialsConfig = "{}",
            ThermalConfig = "{}",
            FlowConfig = "{}",
            ConstraintsConfig = null,
            VisualizationConfig = null,
            ValidationResult = null,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };

        await _configRepository.AddAsync(config);
        return MapToDto(config);
    }

    /// <summary>
    /// Update existing regenerator configuration.
    /// </summary>
    public async Task<RegeneratorConfigurationDto> UpdateConfigurationAsync(
        Guid id,
        UpdateRegeneratorRequest request,
        Guid userId)
    {
        var config = await _configRepository.GetByIdAsync(id);

        if (config == null)
        {
            throw new KeyNotFoundException("Configuration not found");
        }

        // Check ownership
        if (config.UserId != userId)
        {
            throw new UnauthorizedAccessException("Not authorized to update this configuration");
        }

        // Update fields if provided
        if (request.Name != null)
        {
            config.Name = request.Name;
        }

        if (request.Description != null)
        {
            config.Description = request.Description;
        }

        if (request.Status.HasValue)
        {
            config.Status = request.Status.Value;
        }

        config.UpdatedAt = DateTime.UtcNow;
        await _configRepository.UpdateAsync(config);

        return MapToDto(config);
    }

    /// <summary>
    /// Delete regenerator configuration.
    /// </summary>
    public async Task DeleteConfigurationAsync(Guid id, Guid userId)
    {
        var config = await _configRepository.GetByIdAsync(id);

        if (config == null)
        {
            throw new KeyNotFoundException("Configuration not found");
        }

        // Check ownership
        if (config.UserId != userId)
        {
            throw new UnauthorizedAccessException("Not authorized to delete this configuration");
        }

        await _configRepository.DeleteByIdAsync(id);
    }

    /// <summary>
    /// Update configuration status.
    /// </summary>
    public async Task UpdateStatusAsync(Guid id, Fro.Domain.Enums.ConfigurationStatus newStatus, Guid userId)
    {
        var config = await _configRepository.GetByIdAsync(id);

        if (config == null)
        {
            throw new KeyNotFoundException("Configuration not found");
        }

        // Check ownership
        if (config.UserId != userId)
        {
            throw new UnauthorizedAccessException("Not authorized to update this configuration");
        }

        config.Status = newStatus;
        config.UpdatedAt = DateTime.UtcNow;
        await _configRepository.UpdateAsync(config);
    }

    /// <summary>
    /// Clone existing configuration.
    /// </summary>
    public async Task<RegeneratorConfigurationDto> CloneConfigurationAsync(Guid id, Guid userId, string newName)
    {
        var original = await _configRepository.GetByIdAsync(id);

        if (original == null)
        {
            throw new KeyNotFoundException("Configuration not found");
        }

        // Check ownership
        if (original.UserId != userId)
        {
            throw new UnauthorizedAccessException("Not authorized to clone this configuration");
        }

        var clone = new RegeneratorConfiguration
        {
            Id = Guid.NewGuid(),
            Name = newName,
            Description = $"Clone of {original.Name}",
            RegeneratorType = original.RegeneratorType,
            Status = ConfigurationStatus.DRAFT,
            UserId = userId,
            GeometryConfig = original.GeometryConfig,
            MaterialsConfig = original.MaterialsConfig,
            ThermalConfig = original.ThermalConfig,
            FlowConfig = original.FlowConfig,
            ConstraintsConfig = original.ConstraintsConfig,
            VisualizationConfig = original.VisualizationConfig,
            ValidationResult = null, // Reset validation for new config
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };

        await _configRepository.AddAsync(clone);
        return MapToDto(clone);
    }

    /// <summary>
    /// Validate configuration data.
    /// </summary>
    public async Task<ValidationResult> ValidateConfigurationAsync(Guid id)
    {
        var config = await _configRepository.GetByIdAsync(id);

        if (config == null)
        {
            throw new KeyNotFoundException("Configuration not found");
        }

        // TODO: Implement actual physics-based validation
        // This is a placeholder that would call validation logic
        var result = new ValidationResult
        {
            IsValid = true,
            Errors = new List<ValidationError>(),
            Warnings = new List<ValidationError>()
        };

        // Basic validation checks
        if (string.IsNullOrWhiteSpace(config.GeometryConfig) || config.GeometryConfig == "{}")
        {
            result.Warnings.Add(new ValidationError
            {
                Field = "GeometryConfig",
                Message = "Geometry configuration is empty",
                Severity = "warning"
            });
        }

        return result;
    }

    /// <summary>
    /// Map RegeneratorConfiguration entity to DTO.
    /// </summary>
    private static RegeneratorConfigurationDto MapToDto(RegeneratorConfiguration config)
    {
        return new RegeneratorConfigurationDto
        {
            Id = config.Id,
            Name = config.Name,
            Description = config.Description,
            RegeneratorType = config.RegeneratorType,
            Status = config.Status,
            UserId = config.UserId,
            CreatedAt = config.CreatedAt,
            UpdatedAt = config.UpdatedAt,
            // JSON configs
            GeometryConfig = config.GeometryConfig,
            MaterialsConfig = config.MaterialsConfig,
            ThermalConfig = config.ThermalConfig,
            FlowConfig = config.FlowConfig
        };
    }
}
