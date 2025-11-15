using Fro.Application.DTOs.Materials;
using Fro.Application.DTOs.Common;
using Fro.Application.Interfaces;
using Fro.Domain.Entities;
using Fro.Infrastructure.Repositories;
using Microsoft.Extensions.Logging;

namespace Fro.Application.Services;

/// <summary>
/// Materials management service implementation.
/// </summary>
public class MaterialsService : IMaterialsService
{
    private readonly IMaterialsRepository _materialsRepository;
    private readonly ILogger<MaterialsService> _logger;

    public MaterialsService(
        IMaterialsRepository materialsRepository,
        ILogger<MaterialsService> logger)
    {
        _materialsRepository = materialsRepository;
        _logger = logger;
    }

    public async Task<PaginatedResponse<MaterialSearchDto>> SearchMaterialsAsync(
        string? search,
        string? materialType,
        string? category,
        bool? isActive,
        bool? isStandard,
        int limit,
        int offset,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation(
            "Searching materials: search={Search}, type={Type}, category={Category}, active={Active}, standard={Standard}",
            search, materialType, category, isActive, isStandard);

        var materials = await _materialsRepository.SearchAsync(
            search, materialType, category, isActive, isStandard, limit, offset, cancellationToken);

        var totalCount = await _materialsRepository.CountSearchResultsAsync(
            search, materialType, category, isActive, isStandard, cancellationToken);

        var dtos = materials.Select(MapToSearchDto).ToList();

        return new PaginatedResponse<MaterialSearchDto>
        {
            Items = dtos,
            TotalCount = totalCount,
            Page = (offset / limit) + 1,
            PerPage = limit,
            TotalPages = (int)Math.Ceiling((double)totalCount / limit)
        };
    }

    public async Task<MaterialDto?> GetMaterialByIdAsync(Guid id, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting material by ID: {MaterialId}", id);

        var material = await _materialsRepository.GetByIdAsync(id, cancellationToken);

        return material == null ? null : MapToDto(material);
    }

    public async Task<MaterialDto> CreateMaterialAsync(CreateMaterialDto dto, Guid userId, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Creating material: {MaterialName} by user {UserId}", dto.Name, userId);

        // Check if material with same name already exists
        var existing = await _materialsRepository.GetByNameAsync(dto.Name, cancellationToken);
        if (existing != null)
        {
            throw new InvalidOperationException($"Material with name '{dto.Name}' already exists");
        }

        var material = new Material
        {
            Id = Guid.NewGuid(),
            Name = dto.Name,
            Description = dto.Description,
            Manufacturer = dto.Manufacturer,
            MaterialCode = dto.MaterialCode,
            MaterialType = dto.MaterialType,
            Category = dto.Category,
            Application = dto.Application,
            Density = dto.Density,
            ThermalConductivity = dto.ThermalConductivity,
            SpecificHeat = dto.SpecificHeat,
            MaxTemperature = dto.MaxTemperature,
            Porosity = dto.Porosity,
            SurfaceArea = dto.SurfaceArea,
            Properties = dto.Properties,
            ChemicalComposition = dto.ChemicalComposition,
            CostPerUnit = dto.CostPerUnit,
            CostUnit = dto.CostUnit,
            Availability = dto.Availability,
            Version = "1.0",
            ApprovalStatus = "pending",
            IsActive = true,
            IsStandard = dto.IsStandard,
            CreatedByUserId = userId,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };

        var created = await _materialsRepository.AddAsync(material, cancellationToken);

        _logger.LogInformation("Material created successfully: {MaterialId}", created.Id);

        return MapToDto(created);
    }

    public async Task<MaterialDto> UpdateMaterialAsync(Guid id, UpdateMaterialDto dto, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Updating material: {MaterialId}", id);

        var material = await _materialsRepository.GetByIdAsync(id, cancellationToken);
        if (material == null)
        {
            throw new KeyNotFoundException($"Material with ID {id} not found");
        }

        // Update only provided fields
        if (dto.Name != null && dto.Name != material.Name)
        {
            // Check if new name conflicts
            var existing = await _materialsRepository.GetByNameAsync(dto.Name, cancellationToken);
            if (existing != null && existing.Id != id)
            {
                throw new InvalidOperationException($"Material with name '{dto.Name}' already exists");
            }
            material.Name = dto.Name;
        }

        if (dto.Description != null) material.Description = dto.Description;
        if (dto.Manufacturer != null) material.Manufacturer = dto.Manufacturer;
        if (dto.MaterialCode != null) material.MaterialCode = dto.MaterialCode;
        if (dto.MaterialType != null) material.MaterialType = dto.MaterialType;
        if (dto.Category != null) material.Category = dto.Category;
        if (dto.Application != null) material.Application = dto.Application;
        if (dto.Density.HasValue) material.Density = dto.Density;
        if (dto.ThermalConductivity.HasValue) material.ThermalConductivity = dto.ThermalConductivity;
        if (dto.SpecificHeat.HasValue) material.SpecificHeat = dto.SpecificHeat;
        if (dto.MaxTemperature.HasValue) material.MaxTemperature = dto.MaxTemperature;
        if (dto.Porosity.HasValue) material.Porosity = dto.Porosity;
        if (dto.SurfaceArea.HasValue) material.SurfaceArea = dto.SurfaceArea;
        if (dto.Properties != null) material.Properties = dto.Properties;
        if (dto.ChemicalComposition != null) material.ChemicalComposition = dto.ChemicalComposition;
        if (dto.CostPerUnit.HasValue) material.CostPerUnit = dto.CostPerUnit;
        if (dto.CostUnit != null) material.CostUnit = dto.CostUnit;
        if (dto.Availability != null) material.Availability = dto.Availability;
        if (dto.Version != null) material.Version = dto.Version;
        if (dto.SupersededById.HasValue) material.SupersededById = dto.SupersededById;
        if (dto.IsActive.HasValue) material.IsActive = dto.IsActive.Value;
        if (dto.IsStandard.HasValue) material.IsStandard = dto.IsStandard.Value;

        material.UpdatedAt = DateTime.UtcNow;

        await _materialsRepository.UpdateAsync(material, cancellationToken);

        _logger.LogInformation("Material updated successfully: {MaterialId}", id);

        return MapToDto(material);
    }

    public async Task DeleteMaterialAsync(Guid id, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Deleting material: {MaterialId}", id);

        var material = await _materialsRepository.GetByIdAsync(id, cancellationToken);
        if (material == null)
        {
            throw new KeyNotFoundException($"Material with ID {id} not found");
        }

        await _materialsRepository.DeleteAsync(id, cancellationToken);

        _logger.LogInformation("Material deleted (soft delete): {MaterialId}", id);
    }

    public async Task<List<MaterialSearchDto>> GetMaterialsByTypeAsync(string materialType, bool isActive = true, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting materials by type: {MaterialType}", materialType);

        var materials = await _materialsRepository.GetByTypeAsync(materialType, isActive, cancellationToken);

        return materials.Select(MapToSearchDto).ToList();
    }

    public async Task<List<MaterialSearchDto>> GetPopularMaterialsAsync(int limit = 20, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting popular/standard materials");

        var materials = await _materialsRepository.GetStandardMaterialsAsync(limit, cancellationToken);

        return materials.Select(MapToSearchDto).ToList();
    }

    public async Task<MaterialDto> ApproveMaterialAsync(Guid id, string approvalStatus, Guid approvedByUserId, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Approving material {MaterialId} with status {Status} by user {UserId}",
            id, approvalStatus, approvedByUserId);

        if (approvalStatus != "approved" && approvalStatus != "rejected")
        {
            throw new ArgumentException("Approval status must be 'approved' or 'rejected'", nameof(approvalStatus));
        }

        var material = await _materialsRepository.GetByIdAsync(id, cancellationToken);
        if (material == null)
        {
            throw new KeyNotFoundException($"Material with ID {id} not found");
        }

        material.ApprovalStatus = approvalStatus;
        material.ApprovedByUserId = approvedByUserId;
        material.ApprovedAt = DateTime.UtcNow;
        material.UpdatedAt = DateTime.UtcNow;

        await _materialsRepository.UpdateAsync(material, cancellationToken);

        _logger.LogInformation("Material approval status updated: {MaterialId} -> {Status}", id, approvalStatus);

        return MapToDto(material);
    }

    public async Task<int> InitializeStandardMaterialsAsync(CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Initializing standard industry materials");

        // This is a simplified version. In production, this would load from a JSON file or database seed.
        var standardMaterials = GetStandardMaterialsData();

        int count = 0;
        foreach (var materialData in standardMaterials)
        {
            // Check if material already exists
            var existing = await _materialsRepository.GetByNameAsync(materialData.Name, cancellationToken);
            if (existing == null)
            {
                var material = new Material
                {
                    Id = Guid.NewGuid(),
                    Name = materialData.Name,
                    Description = materialData.Description,
                    Manufacturer = materialData.Manufacturer,
                    MaterialCode = materialData.MaterialCode,
                    MaterialType = materialData.MaterialType,
                    Category = materialData.Category,
                    Application = materialData.Application,
                    Density = materialData.Density,
                    ThermalConductivity = materialData.ThermalConductivity,
                    SpecificHeat = materialData.SpecificHeat,
                    MaxTemperature = materialData.MaxTemperature,
                    Porosity = materialData.Porosity,
                    SurfaceArea = materialData.SurfaceArea,
                    Properties = materialData.Properties,
                    ChemicalComposition = materialData.ChemicalComposition,
                    CostPerUnit = materialData.CostPerUnit,
                    CostUnit = materialData.CostUnit,
                    Availability = "in_stock",
                    Version = "1.0",
                    ApprovalStatus = "approved",
                    IsActive = true,
                    IsStandard = true,
                    ApprovedAt = DateTime.UtcNow,
                    CreatedAt = DateTime.UtcNow,
                    UpdatedAt = DateTime.UtcNow
                };

                await _materialsRepository.AddAsync(material, cancellationToken);
                count++;
            }
        }

        _logger.LogInformation("Initialized {Count} standard materials", count);

        return count;
    }

    // ========================
    // Private Helper Methods
    // ========================

    private static MaterialDto MapToDto(Material material)
    {
        return new MaterialDto
        {
            Id = material.Id,
            Name = material.Name,
            Description = material.Description,
            Manufacturer = material.Manufacturer,
            MaterialCode = material.MaterialCode,
            MaterialType = material.MaterialType,
            Category = material.Category,
            Application = material.Application,
            Density = material.Density,
            ThermalConductivity = material.ThermalConductivity,
            SpecificHeat = material.SpecificHeat,
            MaxTemperature = material.MaxTemperature,
            Porosity = material.Porosity,
            SurfaceArea = material.SurfaceArea,
            Properties = material.Properties,
            ChemicalComposition = material.ChemicalComposition,
            CostPerUnit = material.CostPerUnit,
            CostUnit = material.CostUnit,
            Availability = material.Availability,
            Version = material.Version,
            SupersededById = material.SupersededById,
            SupersededByName = material.SupersededBy?.Name,
            ApprovalStatus = material.ApprovalStatus,
            ApprovedByUserId = material.ApprovedByUserId,
            ApprovedByUsername = material.ApprovedBy?.Username,
            ApprovedAt = material.ApprovedAt,
            IsActive = material.IsActive,
            IsStandard = material.IsStandard,
            CreatedByUserId = material.CreatedByUserId,
            CreatedByUsername = material.CreatedBy?.Username,
            CreatedAt = material.CreatedAt,
            UpdatedAt = material.UpdatedAt
        };
    }

    private static MaterialSearchDto MapToSearchDto(Material material)
    {
        return new MaterialSearchDto
        {
            Id = material.Id,
            Name = material.Name,
            Description = material.Description,
            Manufacturer = material.Manufacturer,
            MaterialCode = material.MaterialCode,
            MaterialType = material.MaterialType,
            Category = material.Category,
            Application = material.Application,
            Density = material.Density,
            ThermalConductivity = material.ThermalConductivity,
            MaxTemperature = material.MaxTemperature,
            CostPerUnit = material.CostPerUnit,
            CostUnit = material.CostUnit,
            ApprovalStatus = material.ApprovalStatus,
            IsActive = material.IsActive,
            IsStandard = material.IsStandard,
            CreatedAt = material.CreatedAt,
            UpdatedAt = material.UpdatedAt
        };
    }

    private static List<Material> GetStandardMaterialsData()
    {
        // Simplified standard materials data
        // In production, this would be loaded from a JSON file or external data source
        // Returning a subset of the 103 standard materials for demonstration
        return new List<Material>
        {
            new Material
            {
                Name = "High Alumina Brick 85%",
                Description = "High alumina refractory brick with 85% Al2O3 content",
                Manufacturer = "Standard Refractories Inc.",
                MaterialCode = "HAB-85",
                MaterialType = "refractory",
                Category = "high_alumina",
                Application = "high_temp",
                Density = 2800,
                ThermalConductivity = 2.5,
                SpecificHeat = 1.05,
                MaxTemperature = 1650,
                Porosity = 18,
                SurfaceArea = 150,
                Properties = "{\"compressive_strength\": 120, \"thermal_expansion\": 8.0, \"refractoriness\": 1790}",
                ChemicalComposition = "{\"Al2O3\": 85, \"SiO2\": 12, \"Fe2O3\": 1.5}",
                CostPerUnit = 450.0,
                CostUnit = "per_ton"
            },
            new Material
            {
                Name = "Silica Brick 94%",
                Description = "High purity silica refractory brick",
                Manufacturer = "Standard Refractories Inc.",
                MaterialCode = "SB-94",
                MaterialType = "refractory",
                Category = "silica",
                Application = "high_temp",
                Density = 1900,
                ThermalConductivity = 1.8,
                SpecificHeat = 1.2,
                MaxTemperature = 1680,
                Porosity = 20,
                SurfaceArea = 120,
                Properties = "{\"compressive_strength\": 60, \"thermal_expansion\": 1.5, \"refractoriness\": 1710}",
                ChemicalComposition = "{\"SiO2\": 94, \"Al2O3\": 1.5, \"Fe2O3\": 0.8}",
                CostPerUnit = 380.0,
                CostUnit = "per_ton"
            },
            new Material
            {
                Name = "Ceramic Fiber Blanket 1260°C",
                Description = "High temperature ceramic fiber insulation",
                Manufacturer = "Insultech Ltd.",
                MaterialCode = "CFB-1260",
                MaterialType = "insulation",
                Category = "ceramic_fiber",
                Application = "insulation",
                Density = 128,
                ThermalConductivity = 0.12,
                SpecificHeat = 1.08,
                MaxTemperature = 1260,
                Porosity = 95,
                SurfaceArea = 2500,
                Properties = "{\"thermal_shrinkage\": 3.5, \"shot_content\": 5}",
                ChemicalComposition = "{\"Al2O3\": 48, \"SiO2\": 52}",
                CostPerUnit = 12.5,
                CostUnit = "per_m2"
            }
            // Add remaining 100 materials here in production
        };
    }
}
