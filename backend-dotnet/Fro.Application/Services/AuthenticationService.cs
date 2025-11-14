using Microsoft.Extensions.Configuration;
using Fro.Application.DTOs.Auth;
using Fro.Application.Interfaces.Repositories;
using Fro.Application.Interfaces.Services;
using Fro.Application.Interfaces.Security;
using Fro.Domain.Entities;

namespace Fro.Application.Services;

/// <summary>
/// Authentication service implementation.
/// </summary>
public class AuthenticationService : IAuthenticationService
{
    private readonly IUserRepository _userRepository;
    private readonly IJwtTokenService _jwtTokenService;
    private readonly IPasswordHasher _passwordHasher;
    private readonly IConfiguration _configuration;

    public AuthenticationService(
        IUserRepository userRepository,
        IJwtTokenService jwtTokenService,
        IPasswordHasher passwordHasher,
        IConfiguration configuration)
    {
        _userRepository = userRepository;
        _jwtTokenService = jwtTokenService;
        _passwordHasher = passwordHasher;
        _configuration = configuration;
    }

    /// <summary>
    /// Authenticate user and generate JWT tokens.
    /// </summary>
    public async Task<LoginResponse> LoginAsync(LoginRequest request)
    {
        // Find user by username
        var user = await _userRepository.GetByUsernameAsync(request.Username.ToLower());
        if (user == null)
        {
            throw new UnauthorizedAccessException("Incorrect username or password");
        }

        // Check if user is active
        if (!user.IsActive)
        {
            throw new UnauthorizedAccessException("User account is deactivated");
        }

        // Verify password
        if (!_passwordHasher.VerifyPassword(request.Password, user.PasswordHash))
        {
            throw new UnauthorizedAccessException("Incorrect username or password");
        }

        // Update last login timestamp
        user.LastLogin = DateTime.UtcNow;
        await _userRepository.UpdateAsync(user);

        // Generate JWT tokens
        var accessToken = _jwtTokenService.GenerateAccessToken(
            user.Id.ToString(),
            user.Username,
            user.Role.ToString(),
            user.IsVerified
        );

        var refreshToken = _jwtTokenService.GenerateRefreshToken(
            user.Id.ToString(),
            user.Username
        );

        var expirationMinutes = _configuration.GetValue<int>("JwtSettings:ExpirationMinutes", 1440);

        return new LoginResponse
        {
            AccessToken = accessToken,
            TokenType = "Bearer",
            ExpiresIn = expirationMinutes * 60,
            RefreshToken = refreshToken,
            User = new UserInfo
            {
                Id = user.Id,
                Username = user.Username,
                Email = user.Email,
                FullName = user.FullName,
                Role = user.Role,
                IsActive = user.IsActive,
                IsVerified = user.IsVerified
            }
        };
    }

    /// <summary>
    /// Register a new user.
    /// </summary>
    public async Task<UserInfo> RegisterAsync(RegisterRequest request)
    {
        // Check if username already exists
        var existingUser = await _userRepository.GetByUsernameAsync(request.Username.ToLower());
        if (existingUser != null)
        {
            throw new InvalidOperationException("Username already registered");
        }

        // Check if email already exists
        var existingEmail = await _userRepository.GetByEmailAsync(request.Email.ToLower());
        if (existingEmail != null)
        {
            throw new InvalidOperationException("Email already registered");
        }

        // Validate password strength
        var (isValid, errors) = _passwordHasher.ValidatePasswordStrength(request.Password);
        if (!isValid)
        {
            throw new InvalidOperationException($"Password validation failed: {string.Join("; ", errors)}");
        }

        // Hash password
        var passwordHash = _passwordHasher.HashPassword(request.Password);

        // Create user entity
        var user = new User
        {
            Id = Guid.NewGuid(),
            Username = request.Username.ToLower(),
            Email = request.Email.ToLower(),
            FullName = request.FullName,
            PasswordHash = passwordHash,
            Role = request.Role,
            IsActive = true,
            IsVerified = false, // Admin needs to verify users
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };

        await _userRepository.AddAsync(user);

        return new UserInfo
        {
            Id = user.Id,
            Username = user.Username,
            Email = user.Email,
            FullName = user.FullName,
            Role = user.Role,
            IsActive = user.IsActive,
            IsVerified = user.IsVerified
        };
    }

    /// <summary>
    /// Refresh access token using refresh token.
    /// </summary>
    public async Task<LoginResponse> RefreshTokenAsync(RefreshTokenRequest request)
    {
        // Validate refresh token
        var principal = _jwtTokenService.ValidateToken(request.RefreshToken);
        if (principal == null)
        {
            throw new UnauthorizedAccessException("Invalid refresh token");
        }

        // Get user ID from token
        var userId = principal.FindFirst("sub")?.Value;
        if (userId == null || !Guid.TryParse(userId, out var userGuid))
        {
            throw new UnauthorizedAccessException("Invalid token claims");
        }

        // Get user
        var user = await _userRepository.GetByIdAsync(userGuid);
        if (user == null || !user.IsActive)
        {
            throw new UnauthorizedAccessException("User not found or inactive");
        }

        // Generate new tokens
        var accessToken = _jwtTokenService.GenerateAccessToken(
            user.Id.ToString(),
            user.Username,
            user.Role.ToString(),
            user.IsVerified
        );

        var refreshToken = _jwtTokenService.GenerateRefreshToken(
            user.Id.ToString(),
            user.Username
        );

        var expirationMinutes = _configuration.GetValue<int>("JwtSettings:ExpirationMinutes", 1440);

        return new LoginResponse
        {
            AccessToken = accessToken,
            TokenType = "Bearer",
            ExpiresIn = expirationMinutes * 60,
            RefreshToken = refreshToken,
            User = new UserInfo
            {
                Id = user.Id,
                Username = user.Username,
                Email = user.Email,
                FullName = user.FullName,
                Role = user.Role,
                IsActive = user.IsActive,
                IsVerified = user.IsVerified
            }
        };
    }

    /// <summary>
    /// Change user password.
    /// </summary>
    public async Task ChangePasswordAsync(Guid userId, ChangePasswordRequest request)
    {
        var user = await _userRepository.GetByIdAsync(userId);
        if (user == null)
        {
            throw new KeyNotFoundException("User not found");
        }

        // Verify current password
        if (!_passwordHasher.VerifyPassword(request.CurrentPassword, user.PasswordHash))
        {
            throw new UnauthorizedAccessException("Current password is incorrect");
        }

        // Validate new password
        var (isValid, errors) = _passwordHasher.ValidatePasswordStrength(request.NewPassword);
        if (!isValid)
        {
            throw new InvalidOperationException($"New password validation failed: {string.Join("; ", errors)}");
        }

        // Update password
        user.PasswordHash = _passwordHasher.HashPassword(request.NewPassword);
        user.UpdatedAt = DateTime.UtcNow;

        await _userRepository.UpdateAsync(user);
    }

    /// <summary>
    /// Request password reset.
    /// </summary>
    public async Task RequestPasswordResetAsync(string email)
    {
        var user = await _userRepository.GetByEmailAsync(email.ToLower());
        if (user == null)
        {
            // Don't reveal if email exists for security
            return;
        }

        // Generate reset token
        var resetToken = _passwordHasher.GenerateResetToken();
        var expiresAt = DateTime.UtcNow.AddHours(1); // 1 hour expiry

        user.ResetToken = resetToken;
        user.ResetTokenExpires = expiresAt;
        user.UpdatedAt = DateTime.UtcNow;

        await _userRepository.UpdateAsync(user);

        // TODO: Send email with reset link
        // sendPasswordResetEmail(user.Email, resetToken);
    }

    /// <summary>
    /// Reset password with reset token.
    /// </summary>
    public async Task ResetPasswordAsync(string token, string newPassword)
    {
        // Find user with reset token
        var users = await _userRepository.GetAllAsync();
        var user = users.FirstOrDefault(u => u.ResetToken == token);

        if (user == null || user.ResetTokenExpires == null)
        {
            throw new InvalidOperationException("Invalid or expired reset token");
        }

        // Check token expiration
        if (DateTime.UtcNow > user.ResetTokenExpires)
        {
            throw new InvalidOperationException("Reset token has expired");
        }

        // Validate new password
        var (isValid, errors) = _passwordHasher.ValidatePasswordStrength(newPassword);
        if (!isValid)
        {
            throw new InvalidOperationException($"Password validation failed: {string.Join("; ", errors)}");
        }

        // Update password and clear reset token
        user.PasswordHash = _passwordHasher.HashPassword(newPassword);
        user.ResetToken = null;
        user.ResetTokenExpires = null;
        user.UpdatedAt = DateTime.UtcNow;

        await _userRepository.UpdateAsync(user);
    }

    /// <summary>
    /// Verify user from JWT token.
    /// </summary>
    public async Task<User?> GetCurrentUserAsync(string token)
    {
        var userId = _jwtTokenService.GetUserIdFromToken(token);
        if (userId == null || !Guid.TryParse(userId, out var userGuid))
        {
            return null;
        }

        return await _userRepository.GetByIdAsync(userGuid);
    }
}
