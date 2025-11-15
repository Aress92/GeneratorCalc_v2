namespace Fro.Domain.Entities;

/// <summary>
/// Material entity for regenerator components (refractory materials library).
/// </summary>
/// <remarks>
/// Represents materials used in regenerator construction such as refractory bricks,
/// checker materials, insulation, etc. Includes thermal properties, composition,
/// and approval workflow for quality control.
/// </remarks>
public class Material : BaseEntity
{
    // ========================
    // Basic Information
    // ========================

    /// <summary>
    /// Material name (unique).
    /// </summary>
    public required string Name { get; set; }

    /// <summary>
    /// Material description.
    /// </summary>
    public string? Description { get; set; }

    /// <summary>
    /// Manufacturer name.
    /// </summary>
    public string? Manufacturer { get; set; }

    /// <summary>
    /// Manufacturer's material code/SKU.
    /// </summary>
    public string? MaterialCode { get; set; }

    // ========================
    // Classification
    // ========================

    /// <summary>
    /// Material type (refractory, insulation, checker, etc.).
    /// </summary>
    public required string MaterialType { get; set; }

    /// <summary>
    /// Material category for grouping.
    /// </summary>
    public string? Category { get; set; }

    /// <summary>
    /// Primary application (high_temp, medium_temp, insulation, etc.).
    /// </summary>
    public string? Application { get; set; }

    // ========================
    // Physical Properties (Core)
    // ========================

    /// <summary>
    /// Density (kg/m³).
    /// </summary>
    public double? Density { get; set; }

    /// <summary>
    /// Thermal conductivity (W/(m·K)).
    /// </summary>
    public double? ThermalConductivity { get; set; }

    /// <summary>
    /// Specific heat capacity (kJ/(kg·K)).
    /// </summary>
    public double? SpecificHeat { get; set; }

    /// <summary>
    /// Maximum operating temperature (°C).
    /// </summary>
    public double? MaxTemperature { get; set; }

    /// <summary>
    /// Porosity (% 0-100).
    /// </summary>
    public double? Porosity { get; set; }

    /// <summary>
    /// Specific surface area (m²/m³).
    /// </summary>
    public double? SurfaceArea { get; set; }

    // ========================
    // Extended Properties (JSON)
    // ========================

    /// <summary>
    /// All material properties as JSON.
    /// </summary>
    /// <remarks>
    /// Includes thermal expansion, compressive strength, thermal shock resistance,
    /// refractoriness, etc. Stored as JSON for flexibility.
    /// </remarks>
    public required string Properties { get; set; }  // JSON

    /// <summary>
    /// Chemical composition (e.g., {"Al2O3": 85, "SiO2": 12, "Fe2O3": 1}).
    /// </summary>
    public string? ChemicalComposition { get; set; }  // JSON

    // ========================
    // Cost and Availability
    // ========================

    /// <summary>
    /// Cost per unit.
    /// </summary>
    public double? CostPerUnit { get; set; }

    /// <summary>
    /// Cost unit (per_kg, per_m3, per_piece, etc.).
    /// </summary>
    public string? CostUnit { get; set; }

    /// <summary>
    /// Availability status (in_stock, limited, special_order, discontinued).
    /// </summary>
    public string? Availability { get; set; }

    // ========================
    // Version Control
    // ========================

    /// <summary>
    /// Material version (for tracking updates to material properties).
    /// </summary>
    public string Version { get; set; } = "1.0";

    /// <summary>
    /// ID of material that supersedes this one (if obsolete).
    /// </summary>
    public Guid? SupersededById { get; set; }

    // ========================
    // Approval Workflow
    // ========================

    /// <summary>
    /// Approval status (pending, approved, rejected).
    /// </summary>
    public string ApprovalStatus { get; set; } = "pending";

    /// <summary>
    /// User who approved/rejected the material.
    /// </summary>
    public Guid? ApprovedByUserId { get; set; }

    /// <summary>
    /// Approval/rejection timestamp.
    /// </summary>
    public DateTime? ApprovedAt { get; set; }

    // ========================
    // Status Flags
    // ========================

    /// <summary>
    /// Whether material is active and available for use.
    /// </summary>
    public bool IsActive { get; set; } = true;

    /// <summary>
    /// Whether this is a standard industry material (vs custom).
    /// </summary>
    public bool IsStandard { get; set; } = false;

    // ========================
    // Creator Information
    // ========================

    /// <summary>
    /// User who created this material entry.
    /// </summary>
    public Guid? CreatedByUserId { get; set; }

    // ========================
    // Navigation Properties
    // ========================

    public User? CreatedBy { get; set; }
    public User? ApprovedBy { get; set; }
    public Material? SupersededBy { get; set; }
}
