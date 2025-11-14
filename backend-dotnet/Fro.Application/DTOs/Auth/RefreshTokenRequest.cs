namespace Fro.Application.DTOs.Auth;

/// <summary>
/// Refresh token request.
/// </summary>
public class RefreshTokenRequest
{
    /// <summary>
    /// Refresh token received from login
    /// </summary>
    public required string RefreshToken { get; set; }
}
