namespace Fro.Application.DTOs.Auth;

/// <summary>
/// Login request DTO.
/// </summary>
public class LoginRequest
{
    /// <summary>
    /// Username (email or username)
    /// </summary>
    public required string Username { get; set; }

    /// <summary>
    /// Password (plain text, will be hashed)
    /// </summary>
    public required string Password { get; set; }

    /// <summary>
    /// Remember me flag (extends token expiration)
    /// </summary>
    public bool RememberMe { get; set; } = false;
}
