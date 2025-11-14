namespace Fro.Application.DTOs.Auth;

/// <summary>
/// User registration request.
/// </summary>
public class RegisterRequest
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
    /// Password confirmation (must match password)
    /// </summary>
    public required string PasswordConfirm { get; set; }

    /// <summary>
    /// User role (default: VIEWER)
    /// </summary>
    public Fro.Domain.Enums.UserRole Role { get; set; } = Fro.Domain.Enums.UserRole.VIEWER;
}
