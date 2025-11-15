namespace Fro.Application.DTOs.Materials;

/// <summary>
/// Simplified material DTO for search results and lists.
/// </summary>
public class MaterialSearchDto
{
    public Guid Id { get; set; }
    public required string Name { get; set; }
    public string? Description { get; set; }
    public string? Manufacturer { get; set; }
    public string? MaterialCode { get; set; }
    public required string MaterialType { get; set; }
    public string? Category { get; set; }
    public string? Application { get; set; }

    // Key properties for quick reference
    public double? Density { get; set; }
    public double? ThermalConductivity { get; set; }
    public double? MaxTemperature { get; set; }

    // Cost
    public double? CostPerUnit { get; set; }
    public string? CostUnit { get; set; }

    // Status
    public string ApprovalStatus { get; set; } = "pending";
    public bool IsActive { get; set; }
    public bool IsStandard { get; set; }

    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
}
