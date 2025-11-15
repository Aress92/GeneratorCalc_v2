namespace Fro.Application.DTOs.Reports;

/// <summary>
/// Dashboard metrics DTO for system overview.
/// </summary>
public class DashboardMetricsDto
{
    public int TotalConfigurations { get; set; }
    public int TotalOptimizations { get; set; }
    public int TotalReports { get; set; }
    public int ActiveUsers { get; set; }

    // Recent activity
    public List<RecentActivityDto> RecentActivity { get; set; } = new();

    // Statistics
    public double AverageOptimizationTime { get; set; }
    public double TotalFuelSavingsPercent { get; set; }
    public double TotalCO2ReductionPercent { get; set; }
}

/// <summary>
/// Recent activity item.
/// </summary>
public class RecentActivityDto
{
    public required string Type { get; set; }  // configuration, optimization, report
    public required string Description { get; set; }
    public required string Username { get; set; }
    public DateTime Timestamp { get; set; }
}
