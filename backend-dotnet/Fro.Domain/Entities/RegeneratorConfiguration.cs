using Fro.Domain.Enums;

namespace Fro.Domain.Entities;

/// <summary>
/// Regenerator configuration entity.
/// </summary>
public class RegeneratorConfiguration : BaseEntity
{
    /// <summary>
    /// Owner user ID
    /// </summary>
    public Guid UserId { get; set; }

    /// <summary>
    /// Configuration name (max 255 characters)
    /// </summary>
    public required string Name { get; set; }

    /// <summary>
    /// Description of the configuration
    /// </summary>
    public string? Description { get; set; }

    /// <summary>
    /// Type of regenerator
    /// </summary>
    public RegeneratorType RegeneratorType { get; set; }

    /// <summary>
    /// Configuration version (e.g., "1.0")
    /// </summary>
    public string ConfigurationVersion { get; set; } = "1.0";

    /// <summary>
    /// Current status of the configuration
    /// </summary>
    public ConfigurationStatus Status { get; set; } = ConfigurationStatus.DRAFT;

    /// <summary>
    /// Current wizard step (1-based)
    /// </summary>
    public int CurrentStep { get; set; } = 1;

    /// <summary>
    /// Total number of wizard steps
    /// </summary>
    public int TotalSteps { get; set; } = 7;

    /// <summary>
    /// List of completed step numbers (stored as JSON string)
    /// </summary>
    public string? CompletedSteps { get; set; }

    // Configuration data (stored as JSON)
    public string? GeometryConfig { get; set; }
    public string? MaterialsConfig { get; set; }
    public string? ThermalConfig { get; set; }
    public string? FlowConfig { get; set; }
    public string? ConstraintsConfig { get; set; }
    public string? VisualizationConfig { get; set; }

    // 3D model data (stored as JSON)
    public string? ModelGeometry { get; set; }
    public string? ModelMaterials { get; set; }

    // Validation
    public bool IsValidated { get; set; } = false;
    public double? ValidationScore { get; set; }
    public string? ValidationResult { get; set; }
    public string? ValidationErrors { get; set; }
    public string? ValidationWarnings { get; set; }

    // Template information
    public Guid? BasedOnTemplateId { get; set; }
    public bool IsTemplate { get; set; } = false;
    public DateTime? CompletedAt { get; set; }

    // Navigation properties
    public User? User { get; set; }
    public ConfigurationTemplate? Template { get; set; }
    public ICollection<OptimizationScenario> OptimizationScenarios { get; set; } = new List<OptimizationScenario>();
}

/// <summary>
/// Pre-defined configuration template.
/// Matches Python backend schema for configuration templates.
/// </summary>
public class ConfigurationTemplate : BaseEntity
{
    public required string Name { get; set; }
    public string? Description { get; set; }
    public RegeneratorType RegeneratorType { get; set; }
    public string? Category { get; set; }

    // Python-style consolidated template configuration (JSON)
    public string? TemplateConfig { get; set; }
    public string? DefaultValues { get; set; }
    public string? RequiredFields { get; set; }

    // .NET-style detailed configuration data (stored as JSON)
    public string? DefaultGeometryConfig { get; set; }
    public string? DefaultMaterialsConfig { get; set; }
    public string? DefaultThermalConfig { get; set; }
    public string? DefaultFlowConfig { get; set; }
    public string? DefaultConstraintsConfig { get; set; }

    // Usage and status
    public bool IsActive { get; set; } = true;
    public bool IsPublic { get; set; } = true;
    public int UsageCount { get; set; } = 0;

    // Creator information
    public Guid? CreatedByUserId { get; set; }

    // Navigation properties
    public User? CreatedBy { get; set; }
    public ICollection<RegeneratorConfiguration> Configurations { get; set; } = new List<RegeneratorConfiguration>();
}
