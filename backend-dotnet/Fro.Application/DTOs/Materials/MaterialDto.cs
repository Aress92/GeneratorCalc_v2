namespace Fro.Application.DTOs.Materials;

/// <summary>
/// Material data transfer object for API responses.
/// </summary>
public class MaterialDto
{
    public Guid Id { get; set; }

    // Basic Information
    public required string Name { get; set; }
    public string? Description { get; set; }
    public string? Manufacturer { get; set; }
    public string? MaterialCode { get; set; }

    // Classification
    public required string MaterialType { get; set; }
    public string? Category { get; set; }
    public string? Application { get; set; }

    // Physical Properties
    public double? Density { get; set; }
    public double? ThermalConductivity { get; set; }
    public double? SpecificHeat { get; set; }
    public double? MaxTemperature { get; set; }
    public double? Porosity { get; set; }
    public double? SurfaceArea { get; set; }

    // Extended Properties (JSON as string for API)
    public required string Properties { get; set; }
    public string? ChemicalComposition { get; set; }

    // Cost and Availability
    public double? CostPerUnit { get; set; }
    public string? CostUnit { get; set; }
    public string? Availability { get; set; }

    // Version Control
    public string Version { get; set; } = "1.0";
    public Guid? SupersededById { get; set; }
    public string? SupersededByName { get; set; }  // Denormalized for convenience

    // Approval Workflow
    public string ApprovalStatus { get; set; } = "pending";
    public Guid? ApprovedByUserId { get; set; }
    public string? ApprovedByUsername { get; set; }  // Denormalized
    public DateTime? ApprovedAt { get; set; }

    // Status
    public bool IsActive { get; set; }
    public bool IsStandard { get; set; }

    // Creator
    public Guid? CreatedByUserId { get; set; }
    public string? CreatedByUsername { get; set; }  // Denormalized

    // Timestamps
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
}
