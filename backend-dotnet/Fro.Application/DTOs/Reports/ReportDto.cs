namespace Fro.Application.DTOs.Reports;

/// <summary>
/// Report data transfer object for API responses.
/// </summary>
public class ReportDto
{
    public Guid Id { get; set; }
    public Guid UserId { get; set; }
    public string? Username { get; set; }  // Denormalized

    // Basic Information
    public required string Title { get; set; }
    public string? Description { get; set; }
    public required string ReportType { get; set; }

    // Configuration
    public required string ReportConfig { get; set; }
    public string? DateRange { get; set; }
    public string? Filters { get; set; }

    // Generation Settings
    public string Format { get; set; } = "pdf";
    public string Frequency { get; set; } = "on_demand";

    // Status and Progress
    public string Status { get; set; } = "pending";
    public double Progress { get; set; } = 0.0;

    // Generation Tracking
    public DateTime? GeneratedAt { get; set; }
    public double? GenerationTimeSeconds { get; set; }
    public long? FileSizeBytes { get; set; }

    // File Storage
    public string? FilePath { get; set; }
    public string? DownloadUrl { get; set; }
    public DateTime? ExpiresAt { get; set; }

    // Error Handling
    public string? ErrorMessage { get; set; }

    // Timestamps
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
}
