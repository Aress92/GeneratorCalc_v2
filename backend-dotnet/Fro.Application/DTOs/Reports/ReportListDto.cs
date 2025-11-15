namespace Fro.Application.DTOs.Reports;

/// <summary>
/// Simplified report DTO for list views.
/// </summary>
public class ReportListDto
{
    public Guid Id { get; set; }
    public required string Title { get; set; }
    public string? Description { get; set; }
    public required string ReportType { get; set; }
    public string Format { get; set; } = "pdf";
    public string Status { get; set; } = "pending";
    public double Progress { get; set; } = 0.0;
    public DateTime? GeneratedAt { get; set; }
    public long? FileSizeBytes { get; set; }
    public DateTime CreatedAt { get; set; }
}
