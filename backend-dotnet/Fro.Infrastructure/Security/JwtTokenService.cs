using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using Microsoft.Extensions.Configuration;
using Microsoft.IdentityModel.Tokens;
using Fro.Application.Interfaces.Security;

namespace Fro.Infrastructure.Security;

/// <summary>
/// Service for generating and validating JWT tokens.
/// </summary>
public class JwtTokenService : IJwtTokenService
{
    private readonly IConfiguration _configuration;
    private readonly string _secret;
    private readonly string _issuer;
    private readonly string _audience;
    private readonly int _expirationMinutes;

    public JwtTokenService(IConfiguration configuration)
    {
        _configuration = configuration;
        _secret = configuration["JwtSettings:Secret"]
            ?? throw new InvalidOperationException("JWT Secret is not configured");
        _issuer = configuration["JwtSettings:Issuer"]
            ?? throw new InvalidOperationException("JWT Issuer is not configured");
        _audience = configuration["JwtSettings:Audience"]
            ?? throw new InvalidOperationException("JWT Audience is not configured");
        _expirationMinutes = configuration.GetValue<int>("JwtSettings:ExpirationMinutes", 1440);
    }

    /// <summary>
    /// Generate JWT access token for a user.
    /// </summary>
    /// <param name="userId">User ID (GUID as string)</param>
    /// <param name="username">Username</param>
    /// <param name="role">User role</param>
    /// <param name="isVerified">Whether user email is verified</param>
    /// <returns>JWT token string</returns>
    public string GenerateAccessToken(string userId, string username, string role, bool isVerified)
    {
        var claims = new List<Claim>
        {
            new Claim(JwtRegisteredClaimNames.Sub, userId),
            new Claim(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString()),
            new Claim(JwtRegisteredClaimNames.Iat, DateTimeOffset.UtcNow.ToUnixTimeSeconds().ToString(), ClaimValueTypes.Integer64),
            new Claim("username", username),
            new Claim(ClaimTypes.Role, role),
            new Claim("role", role), // Both formats for compatibility
            new Claim("is_verified", isVerified.ToString().ToLower()),
            new Claim("type", "access")
        };

        return GenerateToken(claims, _expirationMinutes);
    }

    /// <summary>
    /// Generate refresh token for a user.
    /// </summary>
    /// <param name="userId">User ID (GUID as string)</param>
    /// <param name="username">Username</param>
    /// <returns>JWT refresh token string</returns>
    public string GenerateRefreshToken(string userId, string username)
    {
        var refreshExpirationDays = _configuration.GetValue<int>("JwtSettings:RefreshTokenExpirationDays", 7);

        var claims = new List<Claim>
        {
            new Claim(JwtRegisteredClaimNames.Sub, userId),
            new Claim(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString()),
            new Claim("username", username),
            new Claim("type", "refresh")
        };

        return GenerateToken(claims, refreshExpirationDays * 24 * 60);
    }

    /// <summary>
    /// Validate and decode JWT token.
    /// </summary>
    /// <param name="token">JWT token string</param>
    /// <returns>ClaimsPrincipal if valid, null otherwise</returns>
    public ClaimsPrincipal? ValidateToken(string token)
    {
        try
        {
            var tokenHandler = new JwtSecurityTokenHandler();
            var key = Encoding.UTF8.GetBytes(_secret);

            var validationParameters = new TokenValidationParameters
            {
                ValidateIssuer = true,
                ValidateAudience = true,
                ValidateLifetime = true,
                ValidateIssuerSigningKey = true,
                ValidIssuer = _issuer,
                ValidAudience = _audience,
                IssuerSigningKey = new SymmetricSecurityKey(key),
                ClockSkew = TimeSpan.Zero
            };

            var principal = tokenHandler.ValidateToken(token, validationParameters, out var validatedToken);
            return principal;
        }
        catch
        {
            return null;
        }
    }

    /// <summary>
    /// Extract user ID from token.
    /// </summary>
    /// <param name="token">JWT token string</param>
    /// <returns>User ID if valid, null otherwise</returns>
    public string? GetUserIdFromToken(string token)
    {
        var principal = ValidateToken(token);
        return principal?.FindFirst(JwtRegisteredClaimNames.Sub)?.Value;
    }

    /// <summary>
    /// Generate JWT token with specified claims and expiration.
    /// </summary>
    private string GenerateToken(IEnumerable<Claim> claims, int expirationMinutes)
    {
        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_secret));
        var credentials = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);
        var expires = DateTime.UtcNow.AddMinutes(expirationMinutes);

        var token = new JwtSecurityToken(
            issuer: _issuer,
            audience: _audience,
            claims: claims,
            expires: expires,
            signingCredentials: credentials
        );

        return new JwtSecurityTokenHandler().WriteToken(token);
    }
}
