using Fro.Application.DTOs.Common;
using Fro.Application.DTOs.Users;
using Fro.Domain.Enums;

namespace Fro.Application.Interfaces.Services;

/// <summary>
/// Service interface for user management.
/// </summary>
public interface IUserService
{
    /// <summary>
    /// Get user by ID.
    /// </summary>
    Task<UserDto?> GetByIdAsync(Guid id);

    /// <summary>
    /// Get user by username.
    /// </summary>
    Task<UserDto?> GetByUsernameAsync(string username);

    /// <summary>
    /// Get paginated list of users.
    /// </summary>
    Task<PaginatedResponse<UserDto>> GetUsersAsync(UserListRequest request);

    /// <summary>
    /// Create new user.
    /// </summary>
    Task<UserDto> CreateUserAsync(CreateUserRequest request);

    /// <summary>
    /// Update existing user.
    /// </summary>
    Task<UserDto> UpdateUserAsync(Guid id, UpdateUserRequest request);

    /// <summary>
    /// Delete user (soft delete).
    /// </summary>
    Task DeleteUserAsync(Guid id);

    /// <summary>
    /// Activate user account.
    /// </summary>
    Task ActivateUserAsync(Guid id);

    /// <summary>
    /// Deactivate user account.
    /// </summary>
    Task DeactivateUserAsync(Guid id);

    /// <summary>
    /// Verify user email.
    /// </summary>
    Task VerifyEmailAsync(Guid id);

    /// <summary>
    /// Update user role.
    /// </summary>
    Task UpdateUserRoleAsync(Guid id, UserRole newRole);

    /// <summary>
    /// Get user statistics.
    /// </summary>
    Task<UserStatistics> GetUserStatisticsAsync();
}

/// <summary>
/// User statistics for admin dashboard.
/// </summary>
public class UserStatistics
{
    public int TotalUsers { get; set; }
    public int ActiveUsers { get; set; }
    public int VerifiedUsers { get; set; }
    public int AdminUsers { get; set; }
    public int EngineerUsers { get; set; }
    public int ViewerUsers { get; set; }
    public int RecentRegistrations { get; set; }
    public int RecentLogins { get; set; }
}
