using Microsoft.EntityFrameworkCore;
using Fro.Application.Interfaces.Repositories;
using Fro.Domain.Entities;
using Fro.Domain.Enums;
using Fro.Infrastructure.Data;

namespace Fro.Infrastructure.Repositories;

/// <summary>
/// Regenerator configuration repository implementation.
/// </summary>
public class RegeneratorConfigurationRepository : Repository<RegeneratorConfiguration>, IRegeneratorConfigurationRepository
{
    public RegeneratorConfigurationRepository(ApplicationDbContext context) : base(context)
    {
    }

    public async Task<List<RegeneratorConfiguration>> GetByUserIdAsync(Guid userId, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Where(r => r.UserId == userId)
            .OrderByDescending(r => r.UpdatedAt)
            .ToListAsync(cancellationToken);
    }

    public async Task<List<RegeneratorConfiguration>> GetByTypeAsync(RegeneratorType type, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Where(r => r.RegeneratorType == type)
            .OrderByDescending(r => r.UpdatedAt)
            .ToListAsync(cancellationToken);
    }

    public async Task<List<RegeneratorConfiguration>> GetByStatusAsync(ConfigurationStatus status, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Where(r => r.Status == status)
            .OrderByDescending(r => r.UpdatedAt)
            .ToListAsync(cancellationToken);
    }

    public async Task<List<RegeneratorConfiguration>> GetTemplatesAsync(CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Where(r => r.IsTemplate)
            .OrderBy(r => r.Name)
            .ToListAsync(cancellationToken);
    }

    public async Task<List<RegeneratorConfiguration>> GetValidatedAsync(CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Where(r => r.IsValidated)
            .OrderByDescending(r => r.ValidationScore)
            .ToListAsync(cancellationToken);
    }

    public async Task<List<RegeneratorConfiguration>> SearchAsync(string searchTerm, CancellationToken cancellationToken = default)
    {
        var lowerSearchTerm = searchTerm.ToLower();
        return await _dbSet
            .Where(r => r.Name.ToLower().Contains(lowerSearchTerm) ||
                       (r.Description != null && r.Description.ToLower().Contains(lowerSearchTerm)))
            .OrderByDescending(r => r.UpdatedAt)
            .ToListAsync(cancellationToken);
    }
}
