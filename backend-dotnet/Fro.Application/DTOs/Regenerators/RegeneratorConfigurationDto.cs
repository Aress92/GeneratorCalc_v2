using Fro.Domain.Enums;

namespace Fro.Application.DTOs.Regenerators;

/// <summary>
/// Regenerator configuration DTO.
/// </summary>
public class RegeneratorConfigurationDto
{
    public Guid Id { get; set; }
    public Guid UserId { get; set; }
    public required string Name { get; set; }
    public string? Description { get; set; }
    public RegeneratorType RegeneratorType { get; set; }
    public string ConfigurationVersion { get; set; } = "1.0";
    public ConfigurationStatus Status { get; set; } = ConfigurationStatus.DRAFT;

    // Wizard progress
    public int CurrentStep { get; set; }
    public int TotalSteps { get; set; }
    public List<int> CompletedSteps { get; set; } = new();

    // Configuration data (as JSON strings)
    public string? GeometryConfig { get; set; }
    public string? MaterialsConfig { get; set; }
    public string? ThermalConfig { get; set; }
    public string? FlowConfig { get; set; }
    public string? ConstraintsConfig { get; set; }
    public string? VisualizationConfig { get; set; }

    // 3D model
    public string? ModelGeometry { get; set; }
    public string? ModelMaterials { get; set; }

    // Validation
    public bool IsValidated { get; set; }
    public double? ValidationScore { get; set; }
    public List<string> ValidationErrors { get; set; } = new();
    public List<string> ValidationWarnings { get; set; } = new();

    // Template
    public Guid? BasedOnTemplateId { get; set; }
    public bool IsTemplate { get; set; }

    // Timestamps
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    public DateTime? CompletedAt { get; set; }
}
