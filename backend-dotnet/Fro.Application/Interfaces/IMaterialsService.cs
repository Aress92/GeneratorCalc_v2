using Fro.Application.DTOs.Materials;
using Fro.Application.DTOs.Common;

namespace Fro.Application.Interfaces;

/// <summary>
/// Service interface for materials management.
/// </summary>
public interface IMaterialsService
{
    /// <summary>
    /// Search and filter materials.
    /// </summary>
    Task<PaginatedResponse<MaterialSearchDto>> SearchMaterialsAsync(
        string? search,
        string? materialType,
        string? category,
        bool? isActive,
        bool? isStandard,
        int limit,
        int offset,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Get material by ID.
    /// </summary>
    Task<MaterialDto?> GetMaterialByIdAsync(Guid id, CancellationToken cancellationToken = default);

    /// <summary>
    /// Create new material.
    /// </summary>
    Task<MaterialDto> CreateMaterialAsync(CreateMaterialDto dto, Guid userId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Update existing material.
    /// </summary>
    Task<MaterialDto> UpdateMaterialAsync(Guid id, UpdateMaterialDto dto, CancellationToken cancellationToken = default);

    /// <summary>
    /// Delete material (soft delete).
    /// </summary>
    Task DeleteMaterialAsync(Guid id, CancellationToken cancellationToken = default);

    /// <summary>
    /// Get materials by type.
    /// </summary>
    Task<List<MaterialSearchDto>> GetMaterialsByTypeAsync(string materialType, bool isActive = true, CancellationToken cancellationToken = default);

    /// <summary>
    /// Get popular/standard materials.
    /// </summary>
    Task<List<MaterialSearchDto>> GetPopularMaterialsAsync(int limit = 20, CancellationToken cancellationToken = default);

    /// <summary>
    /// Approve or reject a material.
    /// </summary>
    Task<MaterialDto> ApproveMaterialAsync(Guid id, string approvalStatus, Guid approvedByUserId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Initialize standard industry materials (103 materials).
    /// </summary>
    Task<int> InitializeStandardMaterialsAsync(CancellationToken cancellationToken = default);
}
