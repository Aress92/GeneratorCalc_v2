using System.Security.Claims;

namespace Fro.Application.Interfaces.Security;

/// <summary>
/// Interface for JWT token generation and validation.
/// </summary>
public interface IJwtTokenService
{
    /// <summary>
    /// Generate JWT access token for a user.
    /// </summary>
    string GenerateAccessToken(string userId, string username, string role, bool isVerified);

    /// <summary>
    /// Generate refresh token for a user.
    /// </summary>
    string GenerateRefreshToken(string userId, string username);

    /// <summary>
    /// Validate and decode JWT token.
    /// </summary>
    ClaimsPrincipal? ValidateToken(string token);

    /// <summary>
    /// Extract user ID from token.
    /// </summary>
    string? GetUserIdFromToken(string token);
}
