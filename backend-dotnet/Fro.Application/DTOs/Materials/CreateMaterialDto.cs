namespace Fro.Application.DTOs.Materials;

/// <summary>
/// Data transfer object for creating a new material.
/// </summary>
public class CreateMaterialDto
{
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

    // Extended Properties (JSON)
    public required string Properties { get; set; }
    public string? ChemicalComposition { get; set; }

    // Cost and Availability
    public double? CostPerUnit { get; set; }
    public string? CostUnit { get; set; }
    public string? Availability { get; set; }

    // Status
    public bool IsStandard { get; set; } = false;
}
