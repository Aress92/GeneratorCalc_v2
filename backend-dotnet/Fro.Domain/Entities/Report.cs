namespace Fro.Domain.Entities;

/// <summary>
/// Report entity for system performance and analytics (simplified placeholder).
/// </summary>
/// <remarks>
/// This is a simplified version. Full implementation will include:
/// - PDF/Excel generation
/// - Chart and graph generation
/// - Scheduled reports
/// - Email delivery
/// - Advanced analytics
/// </remarks>
public class Report : BaseEntity
{
    // ========================
    // Basic Information
    // ========================

    /// <summary>
    /// User who requested the report.
    /// </summary>
    public Guid UserId { get; set; }

    /// <summary>
    /// Report title.
    /// </summary>
    public required string Title { get; set; }

    /// <summary>
    /// Report description.
    /// </summary>
    public string? Description { get; set; }

    /// <summary>
    /// Report type (optimization_summary, fuel_savings, technical_metrics, etc.).
    /// </summary>
    public required string ReportType { get; set; }

    // ========================
    // Configuration
    // ========================

    /// <summary>
    /// Report parameters and filters as JSON.
    /// </summary>
    public required string ReportConfig { get; set; }  // JSON

    /// <summary>
    /// Date range filters as JSON.
    /// </summary>
    public string? DateRange { get; set; }  // JSON

    /// <summary>
    /// Additional filters as JSON.
    /// </summary>
    public string? Filters { get; set; }  // JSON

    // ========================
    // Generation Settings
    // ========================

    /// <summary>
    /// Output format (pdf, excel, csv, json, html).
    /// </summary>
    public string Format { get; set; } = "pdf";

    /// <summary>
    /// Generation frequency (on_demand, daily, weekly, monthly).
    /// </summary>
    public string Frequency { get; set; } = "on_demand";

    // ========================
    // Status and Progress
    // ========================

    /// <summary>
    /// Report generation status (pending, generating, completed, failed).
    /// </summary>
    public string Status { get; set; } = "pending";

    /// <summary>
    /// Progress percentage (0-100).
    /// </summary>
    public double Progress { get; set; } = 0.0;

    // ========================
    // Generation Tracking
    // ========================

    /// <summary>
    /// When report was generated.
    /// </summary>
    public DateTime? GeneratedAt { get; set; }

    /// <summary>
    /// Time taken to generate report (seconds).
    /// </summary>
    public double? GenerationTimeSeconds { get; set; }

    /// <summary>
    /// File size in bytes.
    /// </summary>
    public long? FileSizeBytes { get; set; }

    // ========================
    // File Storage
    // ========================

    /// <summary>
    /// Path to generated file on server.
    /// </summary>
    public string? FilePath { get; set; }

    /// <summary>
    /// Download URL for the report.
    /// </summary>
    public string? DownloadUrl { get; set; }

    /// <summary>
    /// When the download link expires.
    /// </summary>
    public DateTime? ExpiresAt { get; set; }

    // ========================
    // Error Handling
    // ========================

    /// <summary>
    /// Error message if generation failed.
    /// </summary>
    public string? ErrorMessage { get; set; }

    // ========================
    // Navigation Properties
    // ========================

    public User? User { get; set; }
}
