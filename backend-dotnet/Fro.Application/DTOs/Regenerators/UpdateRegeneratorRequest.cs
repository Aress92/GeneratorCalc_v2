using Fro.Domain.Enums;

namespace Fro.Application.DTOs.Regenerators;

/// <summary>
/// Update regenerator configuration.
/// </summary>
public class UpdateRegeneratorRequest
{
    public string? Name { get; set; }
    public string? Description { get; set; }
    public ConfigurationStatus? Status { get; set; }

    // Wizard progress
    public int? CurrentStep { get; set; }
    public List<int>? CompletedSteps { get; set; }

    // Configuration data (JSON strings)
    public string? GeometryConfig { get; set; }
    public string? MaterialsConfig { get; set; }
    public string? ThermalConfig { get; set; }
    public string? FlowConfig { get; set; }
    public string? ConstraintsConfig { get; set; }
    public string? VisualizationConfig { get; set; }

    // 3D model
    public string? ModelGeometry { get; set; }
    public string? ModelMaterials { get; set; }
}
