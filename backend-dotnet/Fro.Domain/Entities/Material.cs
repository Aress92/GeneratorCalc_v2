namespace Fro.Domain.Entities;

/// <summary>
/// Material entity for regenerator components.
/// Matches Python backend schema for materials library.
/// </summary>
public class Material : BaseEntity
{
    /// <summary>
    /// Material name (unique)
    /// </summary>
    public required string Name { get; set; }

    /// <summary>
    /// Material description
    /// </summary>
    public string? Description { get; set; }

    /// <summary>
    /// Manufacturer name
    /// </summary>
    public string? Manufacturer { get; set; }

    /// <summary>
    /// Manufacturer's material code
    /// </summary>
    public string? MaterialCode { get; set; }

    // Material classification
    /// <summary>
    /// Material type (refractory, insulation, checker, etc.)
    /// </summary>
    public required string MaterialType { get; set; }

    /// <summary>
    /// Material category
    /// </summary>
    public string? Category { get; set; }

    /// <summary>
    /// Application area (high_temp, medium_temp, insulation, etc.)
    /// </summary>
    public string? Application { get; set; }

    // Physical properties (stored as JSON for flexibility)
    /// <summary>
    /// All material properties as JSON
    /// </summary>
    public required string Properties { get; set; }

    // Standard properties (for easy querying)
    /// <summary>
    /// Density (kg/m³)
    /// </summary>
    public double? Density { get; set; }

    /// <summary>
    /// Thermal conductivity (W/(m·K))
    /// </summary>
    public double? ThermalConductivity { get; set; }

    /// <summary>
    /// Specific heat (kJ/(kg·K))
    /// </summary>
    public double? SpecificHeat { get; set; }

    /// <summary>
    /// Maximum operating temperature (°C)
    /// </summary>
    public double? MaxTemperature { get; set; }

    // Porosity and surface area
    /// <summary>
    /// Porosity (% 0-100)
    /// </summary>
    public double? Porosity { get; set; }

    /// <summary>
    /// Surface area (m²/m³)
    /// </summary>
    public double? SurfaceArea { get; set; }

    // Chemical composition
    /// <summary>
    /// Chemical composition (JSON)
    /// </summary>
    public string? ChemicalComposition { get; set; }

    // Cost and availability
    /// <summary>
    /// Cost per unit
    /// </summary>
    public double? CostPerUnit { get; set; }

    /// <summary>
    /// Cost unit (per kg, per m³, etc.)
    /// </summary>
    public string? CostUnit { get; set; }

    /// <summary>
    /// Availability status
    /// </summary>
    public string? Availability { get; set; }

    // Version control
    /// <summary>
    /// Material version (e.g., "1.0")
    /// </summary>
    public string Version { get; set; } = "1.0";

    /// <summary>
    /// ID of material that supersedes this one
    /// </summary>
    public Guid? SupersededById { get; set; }

    // Approval workflow
    /// <summary>
    /// Approval status (pending, approved, rejected)
    /// </summary>
    public string ApprovalStatus { get; set; } = "pending";

    /// <summary>
    /// User who approved the material
    /// </summary>
    public Guid? ApprovedByUserId { get; set; }

    /// <summary>
    /// Approval timestamp
    /// </summary>
    public DateTime? ApprovedAt { get; set; }

    // Status flags
    /// <summary>
    /// Whether material is active
    /// </summary>
    public bool IsActive { get; set; } = true;

    /// <summary>
    /// Whether material is standard industry material
    /// </summary>
    public bool IsStandard { get; set; } = false;

    // Creator information
    /// <summary>
    /// User who created the material
    /// </summary>
    public Guid? CreatedByUserId { get; set; }

    // Navigation properties
    public Material? SupersededBy { get; set; }
    public User? CreatedBy { get; set; }
    public User? ApprovedBy { get; set; }
}
