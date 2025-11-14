using Fro.Domain.Entities;
using Fro.Domain.Enums;

namespace Fro.Application.Interfaces.Repositories;

/// <summary>
/// Regenerator configuration repository interface.
/// </summary>
public interface IRegeneratorConfigurationRepository : IRepository<RegeneratorConfiguration>
{
    /// <summary>
    /// Get configurations by user ID.
    /// </summary>
    Task<List<RegeneratorConfiguration>> GetByUserIdAsync(Guid userId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Get configurations by type.
    /// </summary>
    Task<List<RegeneratorConfiguration>> GetByTypeAsync(RegeneratorType type, CancellationToken cancellationToken = default);

    /// <summary>
    /// Get configurations by status.
    /// </summary>
    Task<List<RegeneratorConfiguration>> GetByStatusAsync(ConfigurationStatus status, CancellationToken cancellationToken = default);

    /// <summary>
    /// Get template configurations.
    /// </summary>
    Task<List<RegeneratorConfiguration>> GetTemplatesAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Get validated configurations.
    /// </summary>
    Task<List<RegeneratorConfiguration>> GetValidatedAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Search configurations by name or description.
    /// </summary>
    Task<List<RegeneratorConfiguration>> SearchAsync(string searchTerm, CancellationToken cancellationToken = default);
}
