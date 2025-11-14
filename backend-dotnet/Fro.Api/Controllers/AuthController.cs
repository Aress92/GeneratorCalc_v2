using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Fro.Application.DTOs.Auth;
using Fro.Application.Interfaces.Services;

namespace Fro.Api.Controllers;

/// <summary>
/// Authentication controller for user login, registration, and password management.
/// </summary>
[ApiController]
[Route("api/v1/[controller]")]
[Produces("application/json")]
public class AuthController : ControllerBase
{
    private readonly IAuthenticationService _authService;
    private readonly ILogger<AuthController> _logger;

    public AuthController(
        IAuthenticationService authService,
        ILogger<AuthController> logger)
    {
        _authService = authService;
        _logger = logger;
    }

    /// <summary>
    /// User login endpoint.
    /// </summary>
    /// <param name="request">Login credentials</param>
    /// <returns>JWT token and user information</returns>
    /// <response code="200">Login successful</response>
    /// <response code="401">Invalid credentials</response>
    [HttpPost("login")]
    [AllowAnonymous]
    [ProducesResponseType(typeof(LoginResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<ActionResult<LoginResponse>> Login([FromBody] LoginRequest request)
    {
        try
        {
            var response = await _authService.LoginAsync(request);
            _logger.LogInformation("User {Username} logged in successfully", request.Username);
            return Ok(response);
        }
        catch (UnauthorizedAccessException ex)
        {
            _logger.LogWarning("Failed login attempt for {Username}: {Message}", request.Username, ex.Message);
            return Unauthorized(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during login for {Username}", request.Username);
            return StatusCode(500, new { message = "An error occurred during login" });
        }
    }

    /// <summary>
    /// User registration endpoint.
    /// </summary>
    /// <param name="request">Registration data</param>
    /// <returns>Created user information</returns>
    /// <response code="201">Registration successful</response>
    /// <response code="400">Invalid data or user already exists</response>
    [HttpPost("register")]
    [AllowAnonymous]
    [ProducesResponseType(typeof(UserInfo), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<ActionResult<UserInfo>> Register([FromBody] RegisterRequest request)
    {
        try
        {
            var user = await _authService.RegisterAsync(request);
            _logger.LogInformation("New user registered: {Username}", request.Username);
            return CreatedAtAction(nameof(Register), new { id = user.Id }, user);
        }
        catch (InvalidOperationException ex)
        {
            _logger.LogWarning("Registration failed for {Username}: {Message}", request.Username, ex.Message);
            return BadRequest(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during registration for {Username}", request.Username);
            return StatusCode(500, new { message = "An error occurred during registration" });
        }
    }

    /// <summary>
    /// Refresh access token.
    /// </summary>
    /// <param name="request">Refresh token</param>
    /// <returns>New access token</returns>
    /// <response code="200">Token refreshed successfully</response>
    /// <response code="401">Invalid refresh token</response>
    [HttpPost("refresh")]
    [AllowAnonymous]
    [ProducesResponseType(typeof(LoginResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<ActionResult<LoginResponse>> RefreshToken([FromBody] RefreshTokenRequest request)
    {
        try
        {
            var response = await _authService.RefreshTokenAsync(request);
            return Ok(response);
        }
        catch (UnauthorizedAccessException ex)
        {
            _logger.LogWarning("Invalid refresh token attempt: {Message}", ex.Message);
            return Unauthorized(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during token refresh");
            return StatusCode(500, new { message = "An error occurred during token refresh" });
        }
    }

    /// <summary>
    /// Change user password.
    /// </summary>
    /// <param name="request">Password change data</param>
    /// <returns>Success message</returns>
    /// <response code="200">Password changed successfully</response>
    /// <response code="400">Invalid data</response>
    /// <response code="401">Unauthorized</response>
    [HttpPost("change-password")]
    [Authorize]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<IActionResult> ChangePassword([FromBody] ChangePasswordRequest request)
    {
        try
        {
            var userIdClaim = User.FindFirst("sub")?.Value;
            if (string.IsNullOrEmpty(userIdClaim) || !Guid.TryParse(userIdClaim, out var userId))
            {
                return Unauthorized(new { message = "Invalid user token" });
            }

            await _authService.ChangePasswordAsync(userId, request);
            _logger.LogInformation("User {UserId} changed password", userId);
            return Ok(new { message = "Password changed successfully" });
        }
        catch (UnauthorizedAccessException ex)
        {
            return BadRequest(new { message = ex.Message });
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during password change");
            return StatusCode(500, new { message = "An error occurred during password change" });
        }
    }

    /// <summary>
    /// Request password reset.
    /// </summary>
    /// <param name="email">User email</param>
    /// <returns>Success message</returns>
    /// <response code="200">Reset email sent (or email not found)</response>
    [HttpPost("request-password-reset")]
    [AllowAnonymous]
    [ProducesResponseType(StatusCodes.Status200OK)]
    public async Task<IActionResult> RequestPasswordReset([FromBody] string email)
    {
        try
        {
            await _authService.RequestPasswordResetAsync(email);
            return Ok(new { message = "If the email exists, a password reset link has been sent" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during password reset request");
            // Don't reveal if email exists
            return Ok(new { message = "If the email exists, a password reset link has been sent" });
        }
    }

    /// <summary>
    /// Reset password with token.
    /// </summary>
    /// <param name="token">Reset token</param>
    /// <param name="newPassword">New password</param>
    /// <returns>Success message</returns>
    /// <response code="200">Password reset successfully</response>
    /// <response code="400">Invalid token or password</response>
    [HttpPost("reset-password")]
    [AllowAnonymous]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> ResetPassword([FromQuery] string token, [FromBody] string newPassword)
    {
        try
        {
            await _authService.ResetPasswordAsync(token, newPassword);
            _logger.LogInformation("Password reset successfully with token");
            return Ok(new { message = "Password reset successfully" });
        }
        catch (InvalidOperationException ex)
        {
            _logger.LogWarning("Invalid password reset attempt: {Message}", ex.Message);
            return BadRequest(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during password reset");
            return StatusCode(500, new { message = "An error occurred during password reset" });
        }
    }

    /// <summary>
    /// Get current user information.
    /// </summary>
    /// <returns>Current user information</returns>
    /// <response code="200">User information</response>
    /// <response code="401">Unauthorized</response>
    [HttpGet("me")]
    [Authorize]
    [ProducesResponseType(typeof(UserInfo), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<ActionResult<UserInfo>> GetCurrentUser()
    {
        try
        {
            var token = Request.Headers["Authorization"].ToString().Replace("Bearer ", "");
            var user = await _authService.GetCurrentUserAsync(token);

            if (user == null)
            {
                return Unauthorized(new { message = "User not found" });
            }

            return Ok(new UserInfo
            {
                Id = user.Id,
                Username = user.Username,
                Email = user.Email,
                FullName = user.FullName,
                Role = user.Role,
                IsActive = user.IsActive,
                IsVerified = user.IsVerified
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting current user");
            return StatusCode(500, new { message = "An error occurred" });
        }
    }
}
