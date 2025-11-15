using Fro.Application.DTOs.Reports;
using Fro.Application.DTOs.Common;

namespace Fro.Application.Interfaces;

/// <summary>
/// Service interface for reporting and analytics (simplified placeholder).
/// </summary>
public interface IReportingService
{
    /// <summary>
    /// Get dashboard metrics for user.
    /// </summary>
    Task<DashboardMetricsDto> GetDashboardMetricsAsync(Guid userId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Create new report.
    /// </summary>
    Task<ReportDto> CreateReportAsync(CreateReportDto dto, Guid userId, CancellationToken cancellationToken = default);

    /// <summary>
    /// List reports for user.
    /// </summary>
    Task<PaginatedResponse<ReportListDto>> ListReportsAsync(
        Guid userId,
        int limit,
        int offset,
        string? reportType = null,
        string? status = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Get report by ID.
    /// </summary>
    Task<ReportDto?> GetReportByIdAsync(Guid id, Guid userId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Delete report.
    /// </summary>
    Task DeleteReportAsync(Guid id, Guid userId, CancellationToken cancellationToken = default);
}
