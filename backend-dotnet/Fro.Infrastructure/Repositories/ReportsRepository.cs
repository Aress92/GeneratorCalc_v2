using Microsoft.EntityFrameworkCore;
using Fro.Domain.Entities;
using Fro.Infrastructure.Data;

namespace Fro.Infrastructure.Repositories;

/// <summary>
/// Repository for reports CRUD operations (simplified placeholder).
/// </summary>
public interface IReportsRepository
{
    Task<Report?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default);
    Task<List<Report>> GetByUserIdAsync(Guid userId, int limit, int offset, string? reportType = null, string? status = null, CancellationToken cancellationToken = default);
    Task<int> CountByUserIdAsync(Guid userId, string? reportType = null, string? status = null, CancellationToken cancellationToken = default);
    Task<Report> AddAsync(Report report, CancellationToken cancellationToken = default);
    Task UpdateAsync(Report report, CancellationToken cancellationToken = default);
    Task DeleteAsync(Guid id, CancellationToken cancellationToken = default);
}

/// <summary>
/// Reports repository implementation.
/// </summary>
public class ReportsRepository : IReportsRepository
{
    private readonly ApplicationDbContext _context;

    public ReportsRepository(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<Report?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default)
    {
        return await _context.Reports
            .Include(r => r.User)
            .FirstOrDefaultAsync(r => r.Id == id, cancellationToken);
    }

    public async Task<List<Report>> GetByUserIdAsync(
        Guid userId,
        int limit,
        int offset,
        string? reportType = null,
        string? status = null,
        CancellationToken cancellationToken = default)
    {
        var query = _context.Reports.Where(r => r.UserId == userId);

        if (!string.IsNullOrWhiteSpace(reportType))
        {
            query = query.Where(r => r.ReportType == reportType);
        }

        if (!string.IsNullOrWhiteSpace(status))
        {
            query = query.Where(r => r.Status == status);
        }

        return await query
            .OrderByDescending(r => r.CreatedAt)
            .Skip(offset)
            .Take(limit)
            .ToListAsync(cancellationToken);
    }

    public async Task<int> CountByUserIdAsync(
        Guid userId,
        string? reportType = null,
        string? status = null,
        CancellationToken cancellationToken = default)
    {
        var query = _context.Reports.Where(r => r.UserId == userId);

        if (!string.IsNullOrWhiteSpace(reportType))
        {
            query = query.Where(r => r.ReportType == reportType);
        }

        if (!string.IsNullOrWhiteSpace(status))
        {
            query = query.Where(r => r.Status == status);
        }

        return await query.CountAsync(cancellationToken);
    }

    public async Task<Report> AddAsync(Report report, CancellationToken cancellationToken = default)
    {
        _context.Reports.Add(report);
        await _context.SaveChangesAsync(cancellationToken);
        return report;
    }

    public async Task UpdateAsync(Report report, CancellationToken cancellationToken = default)
    {
        _context.Reports.Update(report);
        await _context.SaveChangesAsync(cancellationToken);
    }

    public async Task DeleteAsync(Guid id, CancellationToken cancellationToken = default)
    {
        var report = await GetByIdAsync(id, cancellationToken);
        if (report != null)
        {
            _context.Reports.Remove(report);
            await _context.SaveChangesAsync(cancellationToken);
        }
    }
}
