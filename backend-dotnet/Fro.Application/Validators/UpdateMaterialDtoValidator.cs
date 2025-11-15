using FluentValidation;
using Fro.Application.DTOs.Materials;

namespace Fro.Application.Validators;

/// <summary>
/// Validator for UpdateMaterialDto.
/// </summary>
public class UpdateMaterialDtoValidator : AbstractValidator<UpdateMaterialDto>
{
    public UpdateMaterialDtoValidator()
    {
        // Basic Information
        RuleFor(x => x.Name)
            .NotEmpty().WithMessage("Material name cannot be empty")
            .MaximumLength(255).WithMessage("Material name must not exceed 255 characters")
            .When(x => x.Name != null);

        RuleFor(x => x.Description)
            .MaximumLength(2000).WithMessage("Description must not exceed 2000 characters")
            .When(x => x.Description != null);

        RuleFor(x => x.Manufacturer)
            .MaximumLength(255).WithMessage("Manufacturer name must not exceed 255 characters")
            .When(x => x.Manufacturer != null);

        RuleFor(x => x.MaterialCode)
            .MaximumLength(100).WithMessage("Material code must not exceed 100 characters")
            .When(x => x.MaterialCode != null);

        // Classification
        RuleFor(x => x.MaterialType)
            .NotEmpty().WithMessage("Material type cannot be empty")
            .MaximumLength(50).WithMessage("Material type must not exceed 50 characters")
            .Must(BeValidMaterialType).WithMessage("Invalid material type. Valid types: refractory, insulation, checker, structural, coating")
            .When(x => x.MaterialType != null);

        RuleFor(x => x.Category)
            .MaximumLength(100).WithMessage("Category must not exceed 100 characters")
            .When(x => x.Category != null);

        RuleFor(x => x.Application)
            .MaximumLength(100).WithMessage("Application must not exceed 100 characters")
            .When(x => x.Application != null);

        // Physical Properties Validation
        RuleFor(x => x.Density)
            .GreaterThan(0).WithMessage("Density must be greater than 0")
            .LessThanOrEqualTo(10000).WithMessage("Density must be less than or equal to 10000 kg/m³")
            .When(x => x.Density.HasValue);

        RuleFor(x => x.ThermalConductivity)
            .GreaterThanOrEqualTo(0).WithMessage("Thermal conductivity must be non-negative")
            .LessThanOrEqualTo(1000).WithMessage("Thermal conductivity must be less than or equal to 1000 W/(m·K)")
            .When(x => x.ThermalConductivity.HasValue);

        RuleFor(x => x.SpecificHeat)
            .GreaterThan(0).WithMessage("Specific heat must be greater than 0")
            .LessThanOrEqualTo(10).WithMessage("Specific heat must be less than or equal to 10 kJ/(kg·K)")
            .When(x => x.SpecificHeat.HasValue);

        RuleFor(x => x.MaxTemperature)
            .GreaterThan(0).WithMessage("Max temperature must be greater than 0")
            .LessThanOrEqualTo(3000).WithMessage("Max temperature must be less than or equal to 3000°C")
            .When(x => x.MaxTemperature.HasValue);

        RuleFor(x => x.Porosity)
            .GreaterThanOrEqualTo(0).WithMessage("Porosity must be between 0 and 100")
            .LessThanOrEqualTo(100).WithMessage("Porosity must be between 0 and 100")
            .When(x => x.Porosity.HasValue);

        RuleFor(x => x.SurfaceArea)
            .GreaterThanOrEqualTo(0).WithMessage("Surface area must be non-negative")
            .LessThanOrEqualTo(10000).WithMessage("Surface area must be less than or equal to 10000 m²/m³")
            .When(x => x.SurfaceArea.HasValue);

        // Extended Properties (JSON)
        RuleFor(x => x.Properties)
            .Must(BeValidJson).WithMessage("Properties must be valid JSON")
            .When(x => x.Properties != null);

        RuleFor(x => x.ChemicalComposition)
            .Must(BeValidJson).WithMessage("Chemical composition must be valid JSON")
            .When(x => x.ChemicalComposition != null);

        // Cost
        RuleFor(x => x.CostPerUnit)
            .GreaterThanOrEqualTo(0).WithMessage("Cost per unit must be non-negative")
            .When(x => x.CostPerUnit.HasValue);

        RuleFor(x => x.CostUnit)
            .MaximumLength(20).WithMessage("Cost unit must not exceed 20 characters")
            .When(x => x.CostUnit != null);

        RuleFor(x => x.Availability)
            .MaximumLength(50).WithMessage("Availability must not exceed 50 characters")
            .When(x => x.Availability != null);

        // Version Control
        RuleFor(x => x.Version)
            .MaximumLength(20).WithMessage("Version must not exceed 20 characters")
            .When(x => x.Version != null);

        // At least one field must be provided for update
        RuleFor(x => x)
            .Must(x => !IsEmpty(x))
            .WithMessage("At least one field must be provided for update");
    }

    private static bool BeValidMaterialType(string materialType)
    {
        var validTypes = new[] { "refractory", "insulation", "checker", "structural", "coating", "sealant", "other" };
        return validTypes.Contains(materialType.ToLowerInvariant());
    }

    private static bool BeValidJson(string json)
    {
        if (string.IsNullOrWhiteSpace(json))
            return false;

        try
        {
            System.Text.Json.JsonDocument.Parse(json);
            return true;
        }
        catch
        {
            return false;
        }
    }

    private static bool IsEmpty(UpdateMaterialDto dto)
    {
        return dto.Name == null
            && dto.Description == null
            && dto.Manufacturer == null
            && dto.MaterialCode == null
            && dto.MaterialType == null
            && dto.Category == null
            && dto.Application == null
            && dto.Density == null
            && dto.ThermalConductivity == null
            && dto.SpecificHeat == null
            && dto.MaxTemperature == null
            && dto.Porosity == null
            && dto.SurfaceArea == null
            && dto.Properties == null
            && dto.ChemicalComposition == null
            && dto.CostPerUnit == null
            && dto.CostUnit == null
            && dto.Availability == null
            && dto.Version == null
            && dto.SupersededById == null
            && dto.IsActive == null
            && dto.IsStandard == null;
    }
}
