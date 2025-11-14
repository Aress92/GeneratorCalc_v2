using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Fro.Application.DTOs.Common;
using Fro.Application.DTOs.Regenerators;
using Fro.Application.Interfaces.Services;
using Fro.Domain.Enums;
using System.Security.Claims;

namespace Fro.Api.Controllers;

/// <summary>
/// Regenerator configuration management controller.
/// </summary>
[ApiController]
[Route("api/v1/[controller]")]
[Produces("application/json")]
[Authorize]
public class RegeneratorsController : ControllerBase
{
    private readonly IRegeneratorConfigurationService _configService;
    private readonly ILogger<RegeneratorsController> _logger;

    public RegeneratorsController(
        IRegeneratorConfigurationService configService,
        ILogger<RegeneratorsController> logger)
    {
        _configService = configService;
        _logger = logger;
    }

    /// <summary>
    /// Get current user ID from JWT token.
    /// </summary>
    private Guid GetCurrentUserId()
    {
        var userIdClaim = User.FindFirst("sub")?.Value;
        if (string.IsNullOrEmpty(userIdClaim) || !Guid.TryParse(userIdClaim, out var userId))
        {
            throw new UnauthorizedAccessException("Invalid user token");
        }
        return userId;
    }

    /// <summary>
    /// Get paginated list of regenerator configurations for current user.
    /// </summary>
    /// <param name="request">Pagination and filtering parameters</param>
    /// <returns>Paginated list of configurations</returns>
    /// <response code="200">Configurations retrieved successfully</response>
    /// <response code="401">Unauthorized</response>
    [HttpGet]
    [ProducesResponseType(typeof(PaginatedResponse<RegeneratorConfigurationDto>), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<ActionResult<PaginatedResponse<RegeneratorConfigurationDto>>> GetConfigurations(
        [FromQuery] RegeneratorListRequest request)
    {
        try
        {
            var userId = GetCurrentUserId();
            var result = await _configService.GetUserConfigurationsAsync(userId, request);
            return Ok(result);
        }
        catch (UnauthorizedAccessException ex)
        {
            return Unauthorized(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving configurations");
            return StatusCode(500, new { message = "An error occurred while retrieving configurations" });
        }
    }

    /// <summary>
    /// Get regenerator configuration by ID.
    /// </summary>
    /// <param name="id">Configuration ID</param>
    /// <returns>Configuration details</returns>
    /// <response code="200">Configuration found</response>
    /// <response code="404">Configuration not found</response>
    /// <response code="401">Unauthorized</response>
    [HttpGet("{id}")]
    [ProducesResponseType(typeof(RegeneratorConfigurationDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<ActionResult<RegeneratorConfigurationDto>> GetConfigurationById(Guid id)
    {
        try
        {
            var userId = GetCurrentUserId();
            var config = await _configService.GetByIdAsync(id, userId);

            if (config == null)
            {
                return NotFound(new { message = "Configuration not found or access denied" });
            }

            return Ok(config);
        }
        catch (UnauthorizedAccessException ex)
        {
            return Unauthorized(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving configuration {ConfigId}", id);
            return StatusCode(500, new { message = "An error occurred while retrieving configuration" });
        }
    }

    /// <summary>
    /// Create new regenerator configuration.
    /// </summary>
    /// <param name="request">Configuration creation data</param>
    /// <returns>Created configuration</returns>
    /// <response code="201">Configuration created successfully</response>
    /// <response code="400">Invalid data</response>
    /// <response code="401">Unauthorized</response>
    [HttpPost]
    [ProducesResponseType(typeof(RegeneratorConfigurationDto), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<ActionResult<RegeneratorConfigurationDto>> CreateConfiguration(
        [FromBody] CreateRegeneratorRequest request)
    {
        try
        {
            var userId = GetCurrentUserId();
            var config = await _configService.CreateConfigurationAsync(request, userId);

            _logger.LogInformation("User {UserId} created configuration {ConfigId}", userId, config.Id);
            return CreatedAtAction(nameof(GetConfigurationById), new { id = config.Id }, config);
        }
        catch (UnauthorizedAccessException ex)
        {
            return Unauthorized(new { message = ex.Message });
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating configuration");
            return StatusCode(500, new { message = "An error occurred while creating configuration" });
        }
    }

    /// <summary>
    /// Update existing regenerator configuration.
    /// </summary>
    /// <param name="id">Configuration ID</param>
    /// <param name="request">Configuration update data</param>
    /// <returns>Updated configuration</returns>
    /// <response code="200">Configuration updated successfully</response>
    /// <response code="400">Invalid data</response>
    /// <response code="404">Configuration not found</response>
    /// <response code="401">Unauthorized</response>
    /// <response code="403">Access denied</response>
    [HttpPut("{id}")]
    [ProducesResponseType(typeof(RegeneratorConfigurationDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<ActionResult<RegeneratorConfigurationDto>> UpdateConfiguration(
        Guid id,
        [FromBody] UpdateRegeneratorRequest request)
    {
        try
        {
            var userId = GetCurrentUserId();
            var config = await _configService.UpdateConfigurationAsync(id, request, userId);

            _logger.LogInformation("User {UserId} updated configuration {ConfigId}", userId, id);
            return Ok(config);
        }
        catch (UnauthorizedAccessException ex)
        {
            return StatusCode(403, new { message = ex.Message });
        }
        catch (KeyNotFoundException ex)
        {
            return NotFound(new { message = ex.Message });
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating configuration {ConfigId}", id);
            return StatusCode(500, new { message = "An error occurred while updating configuration" });
        }
    }

    /// <summary>
    /// Delete regenerator configuration.
    /// </summary>
    /// <param name="id">Configuration ID</param>
    /// <returns>Success message</returns>
    /// <response code="200">Configuration deleted successfully</response>
    /// <response code="404">Configuration not found</response>
    /// <response code="401">Unauthorized</response>
    /// <response code="403">Access denied</response>
    [HttpDelete("{id}")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<IActionResult> DeleteConfiguration(Guid id)
    {
        try
        {
            var userId = GetCurrentUserId();
            await _configService.DeleteConfigurationAsync(id, userId);

            _logger.LogInformation("User {UserId} deleted configuration {ConfigId}", userId, id);
            return Ok(new { message = "Configuration deleted successfully" });
        }
        catch (UnauthorizedAccessException ex)
        {
            return StatusCode(403, new { message = ex.Message });
        }
        catch (KeyNotFoundException ex)
        {
            return NotFound(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deleting configuration {ConfigId}", id);
            return StatusCode(500, new { message = "An error occurred while deleting configuration" });
        }
    }

    /// <summary>
    /// Update configuration status.
    /// </summary>
    /// <param name="id">Configuration ID</param>
    /// <param name="request">Status update request</param>
    /// <returns>Success message</returns>
    /// <response code="200">Status updated successfully</response>
    /// <response code="400">Invalid status</response>
    /// <response code="404">Configuration not found</response>
    /// <response code="401">Unauthorized</response>
    /// <response code="403">Access denied</response>
    [HttpPut("{id}/status")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<IActionResult> UpdateStatus(Guid id, [FromBody] UpdateStatusRequest request)
    {
        try
        {
            var userId = GetCurrentUserId();
            await _configService.UpdateStatusAsync(id, request.Status, userId);

            _logger.LogInformation("User {UserId} updated configuration {ConfigId} status to {Status}",
                userId, id, request.Status);
            return Ok(new { message = "Configuration status updated successfully" });
        }
        catch (UnauthorizedAccessException ex)
        {
            return StatusCode(403, new { message = ex.Message });
        }
        catch (KeyNotFoundException ex)
        {
            return NotFound(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating configuration {ConfigId} status", id);
            return StatusCode(500, new { message = "An error occurred while updating status" });
        }
    }

    /// <summary>
    /// Clone existing configuration.
    /// </summary>
    /// <param name="id">Configuration ID to clone</param>
    /// <param name="request">Clone request with new name</param>
    /// <returns>Cloned configuration</returns>
    /// <response code="201">Configuration cloned successfully</response>
    /// <response code="404">Configuration not found</response>
    /// <response code="401">Unauthorized</response>
    /// <response code="403">Access denied</response>
    [HttpPost("{id}/clone")]
    [ProducesResponseType(typeof(RegeneratorConfigurationDto), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<ActionResult<RegeneratorConfigurationDto>> CloneConfiguration(
        Guid id,
        [FromBody] CloneConfigurationRequest request)
    {
        try
        {
            var userId = GetCurrentUserId();
            var config = await _configService.CloneConfigurationAsync(id, userId, request.NewName);

            _logger.LogInformation("User {UserId} cloned configuration {ConfigId} to {NewConfigId}",
                userId, id, config.Id);
            return CreatedAtAction(nameof(GetConfigurationById), new { id = config.Id }, config);
        }
        catch (UnauthorizedAccessException ex)
        {
            return StatusCode(403, new { message = ex.Message });
        }
        catch (KeyNotFoundException ex)
        {
            return NotFound(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error cloning configuration {ConfigId}", id);
            return StatusCode(500, new { message = "An error occurred while cloning configuration" });
        }
    }

    /// <summary>
    /// Validate configuration data.
    /// </summary>
    /// <param name="id">Configuration ID</param>
    /// <returns>Validation result</returns>
    /// <response code="200">Validation completed</response>
    /// <response code="404">Configuration not found</response>
    /// <response code="401">Unauthorized</response>
    [HttpPost("{id}/validate")]
    [ProducesResponseType(typeof(ValidationResult), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<ActionResult<ValidationResult>> ValidateConfiguration(Guid id)
    {
        try
        {
            var result = await _configService.ValidateConfigurationAsync(id);

            _logger.LogInformation("Configuration {ConfigId} validated. IsValid: {IsValid}",
                id, result.IsValid);
            return Ok(result);
        }
        catch (KeyNotFoundException ex)
        {
            return NotFound(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error validating configuration {ConfigId}", id);
            return StatusCode(500, new { message = "An error occurred while validating configuration" });
        }
    }
}

/// <summary>
/// Request model for updating configuration status.
/// </summary>
public class UpdateStatusRequest
{
    public ConfigurationStatus Status { get; set; }
}

/// <summary>
/// Request model for cloning configuration.
/// </summary>
public class CloneConfigurationRequest
{
    public required string NewName { get; set; }
}
