namespace Fro.Application.DTOs.Reports;

/// <summary>
/// Data transfer object for creating a new report.
/// </summary>
public class CreateReportDto
{
    public required string Title { get; set; }
    public string? Description { get; set; }
    public required string ReportType { get; set; }

    // Configuration
    public required string ReportConfig { get; set; }  // JSON
    public string? DateRange { get; set; }  // JSON
    public string? Filters { get; set; }  // JSON

    // Generation Settings
    public string Format { get; set; } = "pdf";
    public string Frequency { get; set; } = "on_demand";
}
