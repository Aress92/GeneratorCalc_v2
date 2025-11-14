using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Fro.Application.DTOs.Common;
using Fro.Application.DTOs.Users;
using Fro.Application.Interfaces.Services;
using Fro.Domain.Enums;
using System.Security.Claims;

namespace Fro.Api.Controllers;

/// <summary>
/// User management controller for CRUD operations and user administration.
/// </summary>
[ApiController]
[Route("api/v1/[controller]")]
[Produces("application/json")]
[Authorize]
public class UsersController : ControllerBase
{
    private readonly IUserService _userService;
    private readonly ILogger<UsersController> _logger;

    public UsersController(
        IUserService userService,
        ILogger<UsersController> logger)
    {
        _userService = userService;
        _logger = logger;
    }

    /// <summary>
    /// Get paginated list of users.
    /// </summary>
    /// <param name="request">Pagination and filtering parameters</param>
    /// <returns>Paginated list of users</returns>
    /// <response code="200">Users retrieved successfully</response>
    /// <response code="401">Unauthorized</response>
    /// <response code="403">Forbidden - Admin only</response>
    [HttpGet]
    [Authorize(Roles = "ADMIN")]
    [ProducesResponseType(typeof(PaginatedResponse<UserDto>), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<ActionResult<PaginatedResponse<UserDto>>> GetUsers([FromQuery] UserListRequest request)
    {
        try
        {
            var result = await _userService.GetUsersAsync(request);
            return Ok(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving users");
            return StatusCode(500, new { message = "An error occurred while retrieving users" });
        }
    }

    /// <summary>
    /// Get user by ID.
    /// </summary>
    /// <param name="id">User ID</param>
    /// <returns>User information</returns>
    /// <response code="200">User found</response>
    /// <response code="404">User not found</response>
    /// <response code="401">Unauthorized</response>
    /// <response code="403">Forbidden - Admin only</response>
    [HttpGet("{id}")]
    [Authorize(Roles = "ADMIN")]
    [ProducesResponseType(typeof(UserDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<ActionResult<UserDto>> GetUserById(Guid id)
    {
        try
        {
            var user = await _userService.GetByIdAsync(id);
            if (user == null)
            {
                return NotFound(new { message = "User not found" });
            }
            return Ok(user);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving user {UserId}", id);
            return StatusCode(500, new { message = "An error occurred while retrieving user" });
        }
    }

    /// <summary>
    /// Get user by username.
    /// </summary>
    /// <param name="username">Username</param>
    /// <returns>User information</returns>
    /// <response code="200">User found</response>
    /// <response code="404">User not found</response>
    /// <response code="401">Unauthorized</response>
    /// <response code="403">Forbidden - Admin only</response>
    [HttpGet("username/{username}")]
    [Authorize(Roles = "ADMIN")]
    [ProducesResponseType(typeof(UserDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<ActionResult<UserDto>> GetUserByUsername(string username)
    {
        try
        {
            var user = await _userService.GetByUsernameAsync(username);
            if (user == null)
            {
                return NotFound(new { message = "User not found" });
            }
            return Ok(user);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving user by username {Username}", username);
            return StatusCode(500, new { message = "An error occurred while retrieving user" });
        }
    }

    /// <summary>
    /// Create new user.
    /// </summary>
    /// <param name="request">User creation data</param>
    /// <returns>Created user</returns>
    /// <response code="201">User created successfully</response>
    /// <response code="400">Invalid data or user already exists</response>
    /// <response code="401">Unauthorized</response>
    /// <response code="403">Forbidden - Admin only</response>
    [HttpPost]
    [Authorize(Roles = "ADMIN")]
    [ProducesResponseType(typeof(UserDto), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<ActionResult<UserDto>> CreateUser([FromBody] CreateUserRequest request)
    {
        try
        {
            var user = await _userService.CreateUserAsync(request);
            _logger.LogInformation("Admin created new user: {Username}", request.Username);
            return CreatedAtAction(nameof(GetUserById), new { id = user.Id }, user);
        }
        catch (InvalidOperationException ex)
        {
            _logger.LogWarning("User creation failed: {Message}", ex.Message);
            return BadRequest(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating user");
            return StatusCode(500, new { message = "An error occurred while creating user" });
        }
    }

    /// <summary>
    /// Update existing user.
    /// </summary>
    /// <param name="id">User ID</param>
    /// <param name="request">User update data</param>
    /// <returns>Updated user</returns>
    /// <response code="200">User updated successfully</response>
    /// <response code="400">Invalid data</response>
    /// <response code="404">User not found</response>
    /// <response code="401">Unauthorized</response>
    /// <response code="403">Forbidden - Admin only</response>
    [HttpPut("{id}")]
    [Authorize(Roles = "ADMIN")]
    [ProducesResponseType(typeof(UserDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<ActionResult<UserDto>> UpdateUser(Guid id, [FromBody] UpdateUserRequest request)
    {
        try
        {
            var user = await _userService.UpdateUserAsync(id, request);
            _logger.LogInformation("User {UserId} updated", id);
            return Ok(user);
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
            _logger.LogError(ex, "Error updating user {UserId}", id);
            return StatusCode(500, new { message = "An error occurred while updating user" });
        }
    }

    /// <summary>
    /// Delete user (soft delete).
    /// </summary>
    /// <param name="id">User ID</param>
    /// <returns>Success message</returns>
    /// <response code="200">User deleted successfully</response>
    /// <response code="404">User not found</response>
    /// <response code="401">Unauthorized</response>
    /// <response code="403">Forbidden - Admin only</response>
    [HttpDelete("{id}")]
    [Authorize(Roles = "ADMIN")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<IActionResult> DeleteUser(Guid id)
    {
        try
        {
            await _userService.DeleteUserAsync(id);
            _logger.LogInformation("User {UserId} deleted", id);
            return Ok(new { message = "User deleted successfully" });
        }
        catch (KeyNotFoundException ex)
        {
            return NotFound(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deleting user {UserId}", id);
            return StatusCode(500, new { message = "An error occurred while deleting user" });
        }
    }

    /// <summary>
    /// Activate user account.
    /// </summary>
    /// <param name="id">User ID</param>
    /// <returns>Success message</returns>
    /// <response code="200">User activated successfully</response>
    /// <response code="404">User not found</response>
    /// <response code="401">Unauthorized</response>
    /// <response code="403">Forbidden - Admin only</response>
    [HttpPost("{id}/activate")]
    [Authorize(Roles = "ADMIN")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<IActionResult> ActivateUser(Guid id)
    {
        try
        {
            await _userService.ActivateUserAsync(id);
            _logger.LogInformation("User {UserId} activated", id);
            return Ok(new { message = "User activated successfully" });
        }
        catch (KeyNotFoundException ex)
        {
            return NotFound(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error activating user {UserId}", id);
            return StatusCode(500, new { message = "An error occurred while activating user" });
        }
    }

    /// <summary>
    /// Deactivate user account.
    /// </summary>
    /// <param name="id">User ID</param>
    /// <returns>Success message</returns>
    /// <response code="200">User deactivated successfully</response>
    /// <response code="404">User not found</response>
    /// <response code="401">Unauthorized</response>
    /// <response code="403">Forbidden - Admin only</response>
    [HttpPost("{id}/deactivate")]
    [Authorize(Roles = "ADMIN")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<IActionResult> DeactivateUser(Guid id)
    {
        try
        {
            await _userService.DeactivateUserAsync(id);
            _logger.LogInformation("User {UserId} deactivated", id);
            return Ok(new { message = "User deactivated successfully" });
        }
        catch (KeyNotFoundException ex)
        {
            return NotFound(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deactivating user {UserId}", id);
            return StatusCode(500, new { message = "An error occurred while deactivating user" });
        }
    }

    /// <summary>
    /// Verify user email.
    /// </summary>
    /// <param name="id">User ID</param>
    /// <returns>Success message</returns>
    /// <response code="200">Email verified successfully</response>
    /// <response code="404">User not found</response>
    /// <response code="401">Unauthorized</response>
    /// <response code="403">Forbidden - Admin only</response>
    [HttpPost("{id}/verify")]
    [Authorize(Roles = "ADMIN")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<IActionResult> VerifyUser(Guid id)
    {
        try
        {
            await _userService.VerifyEmailAsync(id);
            _logger.LogInformation("User {UserId} email verified", id);
            return Ok(new { message = "Email verified successfully" });
        }
        catch (KeyNotFoundException ex)
        {
            return NotFound(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error verifying user {UserId}", id);
            return StatusCode(500, new { message = "An error occurred while verifying email" });
        }
    }

    /// <summary>
    /// Update user role.
    /// </summary>
    /// <param name="id">User ID</param>
    /// <param name="request">Role update request</param>
    /// <returns>Success message</returns>
    /// <response code="200">Role updated successfully</response>
    /// <response code="400">Invalid role</response>
    /// <response code="404">User not found</response>
    /// <response code="401">Unauthorized</response>
    /// <response code="403">Forbidden - Admin only</response>
    [HttpPut("{id}/role")]
    [Authorize(Roles = "ADMIN")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<IActionResult> UpdateUserRole(Guid id, [FromBody] UpdateUserRoleRequest request)
    {
        try
        {
            await _userService.UpdateUserRoleAsync(id, request.Role);
            _logger.LogInformation("User {UserId} role updated to {Role}", id, request.Role);
            return Ok(new { message = "User role updated successfully" });
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
            _logger.LogError(ex, "Error updating role for user {UserId}", id);
            return StatusCode(500, new { message = "An error occurred while updating user role" });
        }
    }

    /// <summary>
    /// Get user statistics for admin dashboard.
    /// </summary>
    /// <returns>User statistics</returns>
    /// <response code="200">Statistics retrieved successfully</response>
    /// <response code="401">Unauthorized</response>
    /// <response code="403">Forbidden - Admin only</response>
    [HttpGet("statistics")]
    [Authorize(Roles = "ADMIN")]
    [ProducesResponseType(typeof(UserStatistics), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<ActionResult<UserStatistics>> GetStatistics()
    {
        try
        {
            var statistics = await _userService.GetUserStatisticsAsync();
            return Ok(statistics);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving user statistics");
            return StatusCode(500, new { message = "An error occurred while retrieving statistics" });
        }
    }
}

/// <summary>
/// Request model for updating user role.
/// </summary>
public class UpdateUserRoleRequest
{
    public UserRole Role { get; set; }
}
