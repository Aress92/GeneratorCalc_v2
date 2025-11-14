using Fro.Application.DTOs.Auth;
using Fro.Domain.Entities;

namespace Fro.Application.Interfaces.Services;

/// <summary>
/// Service interface for authentication and user management.
/// </summary>
public interface IAuthenticationService
{
    /// <summary>
    /// Authenticate user and generate JWT tokens.
    /// </summary>
    Task<LoginResponse> LoginAsync(LoginRequest request);

    /// <summary>
    /// Register a new user.
    /// </summary>
    Task<UserInfo> RegisterAsync(RegisterRequest request);

    /// <summary>
    /// Refresh access token using refresh token.
    /// </summary>
    Task<LoginResponse> RefreshTokenAsync(RefreshTokenRequest request);

    /// <summary>
    /// Change user password.
    /// </summary>
    Task ChangePasswordAsync(Guid userId, ChangePasswordRequest request);

    /// <summary>
    /// Request password reset.
    /// </summary>
    Task RequestPasswordResetAsync(string email);

    /// <summary>
    /// Reset password with reset token.
    /// </summary>
    Task ResetPasswordAsync(string token, string newPassword);

    /// <summary>
    /// Verify user from JWT token.
    /// </summary>
    Task<User?> GetCurrentUserAsync(string token);
}
