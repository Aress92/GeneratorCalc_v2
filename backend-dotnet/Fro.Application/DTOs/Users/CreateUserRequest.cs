using Fro.Domain.Enums;

namespace Fro.Application.DTOs.Users;

/// <summary>
/// Create user request (admin only).
/// </summary>
public class CreateUserRequest
{
    /// <summary>
    /// Unique username (3-50 characters)
    /// </summary>
    public required string Username { get; set; }

    /// <summary>
    /// Email address
    /// </summary>
    public required string Email { get; set; }

    /// <summary>
    /// Full name
    /// </summary>
    public string? FullName { get; set; }

    /// <summary>
    /// Password (min 8 characters)
    /// </summary>
    public required string Password { get; set; }

    /// <summary>
    /// User role (default: VIEWER)
    /// </summary>
    public UserRole Role { get; set; } = UserRole.VIEWER;

    /// <summary>
    /// Whether account is active
    /// </summary>
    public bool IsActive { get; set; } = true;

    /// <summary>
    /// Whether email is verified
    /// </summary>
    public bool IsVerified { get; set; } = false;
}
