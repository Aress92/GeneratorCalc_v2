using Fro.Domain.Enums;

namespace Fro.Application.DTOs.Auth;

/// <summary>
/// Login response with JWT token.
/// </summary>
public class LoginResponse
{
    /// <summary>
    /// JWT access token
    /// </summary>
    public required string AccessToken { get; set; }

    /// <summary>
    /// Token type (always "Bearer")
    /// </summary>
    public string TokenType { get; set; } = "Bearer";

    /// <summary>
    /// Token expiration time in seconds
    /// </summary>
    public int ExpiresIn { get; set; }

    /// <summary>
    /// Refresh token for obtaining new access token
    /// </summary>
    public string? RefreshToken { get; set; }

    /// <summary>
    /// User information
    /// </summary>
    public required UserInfo User { get; set; }
}

/// <summary>
/// User information in login response.
/// </summary>
public class UserInfo
{
    public Guid Id { get; set; }
    public required string Username { get; set; }
    public required string Email { get; set; }
    public string? FullName { get; set; }
    public UserRole Role { get; set; }
    public bool IsActive { get; set; }
    public bool IsVerified { get; set; }
}
