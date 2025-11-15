using Microsoft.EntityFrameworkCore;
using Fro.Domain.Entities;
using Fro.Infrastructure.Data;

namespace Fro.Infrastructure.Repositories;

/// <summary>
/// Repository for materials CRUD operations.
/// </summary>
public interface IMaterialsRepository
{
    Task<Material?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default);
    Task<Material?> GetByNameAsync(string name, CancellationToken cancellationToken = default);
    Task<List<Material>> SearchAsync(
        string? search,
        string? materialType,
        string? category,
        bool? isActive,
        bool? isStandard,
        int limit,
        int offset,
        CancellationToken cancellationToken = default);
    Task<int> CountSearchResultsAsync(
        string? search,
        string? materialType,
        string? category,
        bool? isActive,
        bool? isStandard,
        CancellationToken cancellationToken = default);
    Task<List<Material>> GetByTypeAsync(string materialType, bool isActive = true, CancellationToken cancellationToken = default);
    Task<List<Material>> GetStandardMaterialsAsync(int limit = 20, CancellationToken cancellationToken = default);
    Task<Material> AddAsync(Material material, CancellationToken cancellationToken = default);
    Task UpdateAsync(Material material, CancellationToken cancellationToken = default);
    Task DeleteAsync(Guid id, CancellationToken cancellationToken = default);
    Task<bool> ExistsAsync(Guid id, CancellationToken cancellationToken = default);
}

/// <summary>
/// Materials repository implementation.
/// </summary>
public class MaterialsRepository : IMaterialsRepository
{
    private readonly ApplicationDbContext _context;

    public MaterialsRepository(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<Material?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default)
    {
        return await _context.Materials
            .Include(m => m.CreatedBy)
            .Include(m => m.ApprovedBy)
            .Include(m => m.SupersededBy)
            .FirstOrDefaultAsync(m => m.Id == id, cancellationToken);
    }

    public async Task<Material?> GetByNameAsync(string name, CancellationToken cancellationToken = default)
    {
        return await _context.Materials
            .FirstOrDefaultAsync(m => m.Name == name, cancellationToken);
    }

    public async Task<List<Material>> SearchAsync(
        string? search,
        string? materialType,
        string? category,
        bool? isActive,
        bool? isStandard,
        int limit,
        int offset,
        CancellationToken cancellationToken = default)
    {
        var query = _context.Materials.AsQueryable();

        if (!string.IsNullOrWhiteSpace(search))
        {
            query = query.Where(m =>
                m.Name.Contains(search) ||
                (m.Description != null && m.Description.Contains(search)) ||
                (m.Manufacturer != null && m.Manufacturer.Contains(search)) ||
                (m.MaterialCode != null && m.MaterialCode.Contains(search)));
        }

        if (!string.IsNullOrWhiteSpace(materialType))
        {
            query = query.Where(m => m.MaterialType == materialType);
        }

        if (!string.IsNullOrWhiteSpace(category))
        {
            query = query.Where(m => m.Category == category);
        }

        if (isActive.HasValue)
        {
            query = query.Where(m => m.IsActive == isActive.Value);
        }

        if (isStandard.HasValue)
        {
            query = query.Where(m => m.IsStandard == isStandard.Value);
        }

        return await query
            .OrderBy(m => m.Name)
            .Skip(offset)
            .Take(limit)
            .Include(m => m.CreatedBy)
            .ToListAsync(cancellationToken);
    }

    public async Task<int> CountSearchResultsAsync(
        string? search,
        string? materialType,
        string? category,
        bool? isActive,
        bool? isStandard,
        CancellationToken cancellationToken = default)
    {
        var query = _context.Materials.AsQueryable();

        if (!string.IsNullOrWhiteSpace(search))
        {
            query = query.Where(m =>
                m.Name.Contains(search) ||
                (m.Description != null && m.Description.Contains(search)) ||
                (m.Manufacturer != null && m.Manufacturer.Contains(search)) ||
                (m.MaterialCode != null && m.MaterialCode.Contains(search)));
        }

        if (!string.IsNullOrWhiteSpace(materialType))
        {
            query = query.Where(m => m.MaterialType == materialType);
        }

        if (!string.IsNullOrWhiteSpace(category))
        {
            query = query.Where(m => m.Category == category);
        }

        if (isActive.HasValue)
        {
            query = query.Where(m => m.IsActive == isActive.Value);
        }

        if (isStandard.HasValue)
        {
            query = query.Where(m => m.IsStandard == isStandard.Value);
        }

        return await query.CountAsync(cancellationToken);
    }

    public async Task<List<Material>> GetByTypeAsync(string materialType, bool isActive = true, CancellationToken cancellationToken = default)
    {
        return await _context.Materials
            .Where(m => m.MaterialType == materialType && m.IsActive == isActive)
            .OrderBy(m => m.Name)
            .ToListAsync(cancellationToken);
    }

    public async Task<List<Material>> GetStandardMaterialsAsync(int limit = 20, CancellationToken cancellationToken = default)
    {
        return await _context.Materials
            .Where(m => m.IsStandard && m.IsActive && m.ApprovalStatus == "approved")
            .OrderBy(m => m.Name)
            .Take(limit)
            .ToListAsync(cancellationToken);
    }

    public async Task<Material> AddAsync(Material material, CancellationToken cancellationToken = default)
    {
        _context.Materials.Add(material);
        await _context.SaveChangesAsync(cancellationToken);
        return material;
    }

    public async Task UpdateAsync(Material material, CancellationToken cancellationToken = default)
    {
        _context.Materials.Update(material);
        await _context.SaveChangesAsync(cancellationToken);
    }

    public async Task DeleteAsync(Guid id, CancellationToken cancellationToken = default)
    {
        var material = await GetByIdAsync(id, cancellationToken);
        if (material != null)
        {
            // Soft delete - just mark as inactive
            material.IsActive = false;
            await UpdateAsync(material, cancellationToken);
        }
    }

    public async Task<bool> ExistsAsync(Guid id, CancellationToken cancellationToken = default)
    {
        return await _context.Materials.AnyAsync(m => m.Id == id, cancellationToken);
    }
}
