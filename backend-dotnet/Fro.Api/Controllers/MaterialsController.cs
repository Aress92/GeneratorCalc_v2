using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Fro.Application.Interfaces;
using Fro.Application.DTOs.Materials;
using System.Security.Claims;

namespace Fro.Api.Controllers;

/// <summary>
/// Materials library management controller.
/// </summary>
[ApiController]
[Route("api/v1/[controller]")]
[Produces("application/json")]
[Authorize]
public class MaterialsController : ControllerBase
{
    private readonly IMaterialsService _materialsService;
    private readonly ILogger<MaterialsController> _logger;

    public MaterialsController(
        IMaterialsService materialsService,
        ILogger<MaterialsController> logger)
    {
        _materialsService = materialsService;
        _logger = logger;
    }

    /// <summary>
    /// Search and filter materials.
    /// </summary>
    /// <param name="search">Search term</param>
    /// <param name="materialType">Filter by material type</param>
    /// <param name="category">Filter by category</param>
    /// <param name="isActive">Filter by active status</param>
    /// <param name="isStandard">Filter by standard materials</param>
    /// <param name="limit">Maximum number of results</param>
    /// <param name="offset">Number of results to skip</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of materials</returns>
    /// <response code="200">Materials retrieved successfully</response>
    /// <response code="401">Unauthorized</response>
    [HttpGet]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<IActionResult> SearchMaterials(
        [FromQuery] string? search = null,
        [FromQuery] string? materialType = null,
        [FromQuery] string? category = null,
        [FromQuery] bool? isActive = true,
        [FromQuery] bool? isStandard = null,
        [FromQuery] int limit = 50,
        [FromQuery] int offset = 0,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var result = await _materialsService.SearchMaterialsAsync(
                search, materialType, category, isActive, isStandard, limit, offset, cancellationToken);

            return Ok(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error searching materials");
            return StatusCode(500, new { message = "An error occurred while searching materials" });
        }
    }

    /// <summary>
    /// Get material by ID.
    /// </summary>
    /// <param name="id">Material ID</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Material details</returns>
    /// <response code="200">Material found</response>
    /// <response code="404">Material not found</response>
    /// <response code="401">Unauthorized</response>
    [HttpGet("{id}")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<IActionResult> GetMaterial(Guid id, CancellationToken cancellationToken = default)
    {
        try
        {
            var material = await _materialsService.GetMaterialByIdAsync(id, cancellationToken);

            if (material == null)
            {
                return NotFound(new { message = $"Material with ID {id} not found" });
            }

            return Ok(material);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting material {MaterialId}", id);
            return StatusCode(500, new { message = "An error occurred while retrieving the material" });
        }
    }

    /// <summary>
    /// Create new material.
    /// </summary>
    /// <param name="request">Material creation data</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Created material</returns>
    /// <response code="201">Material created successfully</response>
    /// <response code="400">Invalid data</response>
    /// <response code="401">Unauthorized</response>
    /// <response code="403">Forbidden - Engineer or Admin role required</response>
    [HttpPost]
    [Authorize(Roles = "ENGINEER,ADMIN")]
    [ProducesResponseType(StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<IActionResult> CreateMaterial(
        [FromBody] CreateMaterialDto request,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var userId = GetCurrentUserId();

            var material = await _materialsService.CreateMaterialAsync(request, userId, cancellationToken);

            return CreatedAtAction(nameof(GetMaterial), new { id = material.Id }, material);
        }
        catch (InvalidOperationException ex)
        {
            _logger.LogWarning(ex, "Invalid operation when creating material");
            return BadRequest(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating material");
            return StatusCode(500, new { message = "An error occurred while creating the material" });
        }
    }

    /// <summary>
    /// Update existing material.
    /// </summary>
    /// <param name="id">Material ID</param>
    /// <param name="request">Material update data</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Updated material</returns>
    /// <response code="200">Material updated successfully</response>
    /// <response code="400">Invalid data</response>
    /// <response code="404">Material not found</response>
    /// <response code="401">Unauthorized</response>
    /// <response code="403">Forbidden - Engineer or Admin role required</response>
    [HttpPut("{id}")]
    [Authorize(Roles = "ENGINEER,ADMIN")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<IActionResult> UpdateMaterial(
        Guid id,
        [FromBody] UpdateMaterialDto request,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var material = await _materialsService.UpdateMaterialAsync(id, request, cancellationToken);

            return Ok(material);
        }
        catch (KeyNotFoundException ex)
        {
            _logger.LogWarning(ex, "Material not found: {MaterialId}", id);
            return NotFound(new { message = ex.Message });
        }
        catch (InvalidOperationException ex)
        {
            _logger.LogWarning(ex, "Invalid operation when updating material");
            return BadRequest(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating material {MaterialId}", id);
            return StatusCode(500, new { message = "An error occurred while updating the material" });
        }
    }

    /// <summary>
    /// Delete material (soft delete).
    /// </summary>
    /// <param name="id">Material ID</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Success message</returns>
    /// <response code="200">Material deleted successfully</response>
    /// <response code="404">Material not found</response>
    /// <response code="401">Unauthorized</response>
    /// <response code="403">Forbidden - Engineer or Admin role required</response>
    [HttpDelete("{id}")]
    [Authorize(Roles = "ENGINEER,ADMIN")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<IActionResult> DeleteMaterial(Guid id, CancellationToken cancellationToken = default)
    {
        try
        {
            await _materialsService.DeleteMaterialAsync(id, cancellationToken);

            return Ok(new { message = "Material deleted successfully (soft delete)" });
        }
        catch (KeyNotFoundException ex)
        {
            _logger.LogWarning(ex, "Material not found: {MaterialId}", id);
            return NotFound(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deleting material {MaterialId}", id);
            return StatusCode(500, new { message = "An error occurred while deleting the material" });
        }
    }

    /// <summary>
    /// Get materials by type.
    /// </summary>
    /// <param name="materialType">Material type</param>
    /// <param name="isActive">Filter by active status</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of materials</returns>
    /// <response code="200">Materials retrieved successfully</response>
    /// <response code="401">Unauthorized</response>
    [HttpGet("types/{materialType}")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<IActionResult> GetMaterialsByType(
        string materialType,
        [FromQuery] bool isActive = true,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var materials = await _materialsService.GetMaterialsByTypeAsync(materialType, isActive, cancellationToken);

            return Ok(new
            {
                materialType,
                isActive,
                totalCount = materials.Count,
                materials
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting materials by type {MaterialType}", materialType);
            return StatusCode(500, new { message = "An error occurred while retrieving materials" });
        }
    }

    /// <summary>
    /// Get popular/standard materials.
    /// </summary>
    /// <param name="limit">Maximum number of results</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of popular materials</returns>
    /// <response code="200">Materials retrieved successfully</response>
    /// <response code="401">Unauthorized</response>
    [HttpGet("popular/standard")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<IActionResult> GetPopularMaterials(
        [FromQuery] int limit = 20,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var materials = await _materialsService.GetPopularMaterialsAsync(limit, cancellationToken);

            return Ok(new
            {
                totalCount = materials.Count,
                materials
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting popular materials");
            return StatusCode(500, new { message = "An error occurred while retrieving popular materials" });
        }
    }

    /// <summary>
    /// Approve or reject a material.
    /// </summary>
    /// <param name="id">Material ID</param>
    /// <param name="approvalStatus">Approval status (approved/rejected)</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Updated material</returns>
    /// <response code="200">Material approval status updated</response>
    /// <response code="400">Invalid approval status</response>
    /// <response code="404">Material not found</response>
    /// <response code="401">Unauthorized</response>
    /// <response code="403">Forbidden - Admin only</response>
    [HttpPost("{id}/approve")]
    [Authorize(Roles = "ADMIN")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<IActionResult> ApproveMaterial(
        Guid id,
        [FromQuery] string approvalStatus,
        CancellationToken cancellationToken = default)
    {
        if (approvalStatus != "approved" && approvalStatus != "rejected")
        {
            return BadRequest(new { message = "Invalid approval status. Must be 'approved' or 'rejected'" });
        }

        try
        {
            var userId = GetCurrentUserId();

            var material = await _materialsService.ApproveMaterialAsync(id, approvalStatus, userId, cancellationToken);

            return Ok(material);
        }
        catch (KeyNotFoundException ex)
        {
            _logger.LogWarning(ex, "Material not found: {MaterialId}", id);
            return NotFound(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error approving material {MaterialId}", id);
            return StatusCode(500, new { message = "An error occurred while approving the material" });
        }
    }

    /// <summary>
    /// Initialize standard industry materials.
    /// </summary>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Success message with count</returns>
    /// <response code="200">Standard materials initialized</response>
    /// <response code="401">Unauthorized</response>
    /// <response code="403">Forbidden - Admin only</response>
    [HttpPost("initialize/standard")]
    [Authorize(Roles = "ADMIN")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<IActionResult> InitializeStandardMaterials(CancellationToken cancellationToken = default)
    {
        try
        {
            var count = await _materialsService.InitializeStandardMaterialsAsync(cancellationToken);

            return Ok(new
            {
                message = "Standard materials initialized successfully",
                materialsCreated = count
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error initializing standard materials");
            return StatusCode(500, new { message = "An error occurred while initializing standard materials" });
        }
    }

    // ========================
    // Private Helper Methods
    // ========================

    private Guid GetCurrentUserId()
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (string.IsNullOrEmpty(userIdClaim))
        {
            throw new UnauthorizedAccessException("User ID not found in token");
        }

        return Guid.Parse(userIdClaim);
    }
}
