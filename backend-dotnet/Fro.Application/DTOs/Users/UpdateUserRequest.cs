using Fro.Domain.Enums;

namespace Fro.Application.DTOs.Users;

/// <summary>
/// Update user request.
/// </summary>
public class UpdateUserRequest
{
    /// <summary>
    /// Email address
    /// </summary>
    public string? Email { get; set; }

    /// <summary>
    /// Full name
    /// </summary>
    public string? FullName { get; set; }

    /// <summary>
    /// User role (admin only)
    /// </summary>
    public UserRole? Role { get; set; }

    /// <summary>
    /// Whether account is active (admin only)
    /// </summary>
    public bool? IsActive { get; set; }

    /// <summary>
    /// Whether email is verified (admin only)
    /// </summary>
    public bool? IsVerified { get; set; }
}
