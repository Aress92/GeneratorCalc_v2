using Fro.Application.DTOs.Common;
using Fro.Application.DTOs.Users;
using Fro.Application.Interfaces.Repositories;
using Fro.Application.Interfaces.Services;
using Fro.Application.Interfaces.Security;
using Fro.Domain.Entities;
using Fro.Domain.Enums;

namespace Fro.Application.Services;

/// <summary>
/// User management service implementation.
/// </summary>
public class UserService : IUserService
{
    private readonly IUserRepository _userRepository;
    private readonly IPasswordHasher _passwordHasher;

    public UserService(IUserRepository userRepository, IPasswordHasher passwordHasher)
    {
        _userRepository = userRepository;
        _passwordHasher = passwordHasher;
    }

    /// <summary>
    /// Get user by ID.
    /// </summary>
    public async Task<UserDto?> GetByIdAsync(Guid id)
    {
        var user = await _userRepository.GetByIdAsync(id);
        return user == null ? null : MapToDto(user);
    }

    /// <summary>
    /// Get user by username.
    /// </summary>
    public async Task<UserDto?> GetByUsernameAsync(string username)
    {
        var user = await _userRepository.GetByUsernameAsync(username.ToLower());
        return user == null ? null : MapToDto(user);
    }

    /// <summary>
    /// Get paginated list of users.
    /// </summary>
    public async Task<PaginatedResponse<UserDto>> GetUsersAsync(UserListRequest request)
    {
        var allUsers = await _userRepository.GetAllAsync();

        // Apply filters
        var query = allUsers.AsQueryable();

        if (request.Role.HasValue)
        {
            query = query.Where(u => u.Role == request.Role.Value);
        }

        if (request.IsActive.HasValue)
        {
            query = query.Where(u => u.IsActive == request.IsActive.Value);
        }

        if (request.IsVerified.HasValue)
        {
            query = query.Where(u => u.IsVerified == request.IsVerified.Value);
        }

        if (!string.IsNullOrWhiteSpace(request.SearchTerm))
        {
            var searchLower = request.SearchTerm.ToLower();
            query = query.Where(u =>
                u.Username.Contains(searchLower) ||
                u.Email.Contains(searchLower) ||
                (u.FullName != null && u.FullName.Contains(searchLower))
            );
        }

        var totalCount = query.Count();

        // Apply sorting
        query = request.SortBy?.ToLower() switch
        {
            "username" => request.SortDescending ? query.OrderByDescending(u => u.Username) : query.OrderBy(u => u.Username),
            "email" => request.SortDescending ? query.OrderByDescending(u => u.Email) : query.OrderBy(u => u.Email),
            "role" => request.SortDescending ? query.OrderByDescending(u => u.Role) : query.OrderBy(u => u.Role),
            "lastlogin" => request.SortDescending ? query.OrderByDescending(u => u.LastLogin) : query.OrderBy(u => u.LastLogin),
            _ => query.OrderByDescending(u => u.CreatedAt) // Default sort by created date
        };

        // Apply pagination
        var users = query
            .Skip((request.Page - 1) * request.PageSize)
            .Take(request.PageSize)
            .Select(MapToDto)
            .ToList();

        return new PaginatedResponse<UserDto>
        {
            Items = users,
            TotalCount = totalCount,
            Page = request.Page,
            PageSize = request.PageSize,
            TotalPages = (int)Math.Ceiling(totalCount / (double)request.PageSize)
        };
    }

    /// <summary>
    /// Create new user.
    /// </summary>
    public async Task<UserDto> CreateUserAsync(CreateUserRequest request)
    {
        // Check if username already exists
        var existingUser = await _userRepository.GetByUsernameAsync(request.Username.ToLower());
        if (existingUser != null)
        {
            throw new InvalidOperationException("Username already exists");
        }

        // Check if email already exists
        var existingEmail = await _userRepository.GetByEmailAsync(request.Email.ToLower());
        if (existingEmail != null)
        {
            throw new InvalidOperationException("Email already exists");
        }

        // Validate password strength
        var (isValid, errors) = _passwordHasher.ValidatePasswordStrength(request.Password);
        if (!isValid)
        {
            throw new InvalidOperationException($"Password validation failed: {string.Join("; ", errors)}");
        }

        // Create user entity
        var user = new User
        {
            Id = Guid.NewGuid(),
            Username = request.Username.ToLower(),
            Email = request.Email.ToLower(),
            FullName = request.FullName,
            PasswordHash = _passwordHasher.HashPassword(request.Password),
            Role = request.Role,
            IsActive = request.IsActive,
            IsVerified = request.IsVerified,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };

        await _userRepository.AddAsync(user);
        return MapToDto(user);
    }

    /// <summary>
    /// Update existing user.
    /// </summary>
    public async Task<UserDto> UpdateUserAsync(Guid id, UpdateUserRequest request)
    {
        var user = await _userRepository.GetByIdAsync(id);
        if (user == null)
        {
            throw new KeyNotFoundException("User not found");
        }

        // Update fields if provided
        if (request.Email != null)
        {
            var emailLower = request.Email.ToLower();
            // Check if email already exists for another user
            var existingEmail = await _userRepository.GetByEmailAsync(emailLower);
            if (existingEmail != null && existingEmail.Id != id)
            {
                throw new InvalidOperationException("Email already exists");
            }
            user.Email = emailLower;
        }

        if (request.FullName != null)
        {
            user.FullName = request.FullName;
        }

        if (request.Role.HasValue)
        {
            user.Role = request.Role.Value;
        }

        if (request.IsActive.HasValue)
        {
            user.IsActive = request.IsActive.Value;
        }

        if (request.IsVerified.HasValue)
        {
            user.IsVerified = request.IsVerified.Value;
        }

        user.UpdatedAt = DateTime.UtcNow;
        await _userRepository.UpdateAsync(user);

        return MapToDto(user);
    }

    /// <summary>
    /// Delete user (soft delete).
    /// </summary>
    public async Task DeleteUserAsync(Guid id)
    {
        var user = await _userRepository.GetByIdAsync(id);
        if (user == null)
        {
            throw new KeyNotFoundException("User not found");
        }

        // Soft delete - just deactivate
        user.IsActive = false;
        user.UpdatedAt = DateTime.UtcNow;
        await _userRepository.UpdateAsync(user);
    }

    /// <summary>
    /// Activate user account.
    /// </summary>
    public async Task ActivateUserAsync(Guid id)
    {
        var user = await _userRepository.GetByIdAsync(id);
        if (user == null)
        {
            throw new KeyNotFoundException("User not found");
        }

        user.IsActive = true;
        user.UpdatedAt = DateTime.UtcNow;
        await _userRepository.UpdateAsync(user);
    }

    /// <summary>
    /// Deactivate user account.
    /// </summary>
    public async Task DeactivateUserAsync(Guid id)
    {
        var user = await _userRepository.GetByIdAsync(id);
        if (user == null)
        {
            throw new KeyNotFoundException("User not found");
        }

        user.IsActive = false;
        user.UpdatedAt = DateTime.UtcNow;
        await _userRepository.UpdateAsync(user);
    }

    /// <summary>
    /// Verify user email.
    /// </summary>
    public async Task VerifyEmailAsync(Guid id)
    {
        var user = await _userRepository.GetByIdAsync(id);
        if (user == null)
        {
            throw new KeyNotFoundException("User not found");
        }

        user.IsVerified = true;
        user.UpdatedAt = DateTime.UtcNow;
        await _userRepository.UpdateAsync(user);
    }

    /// <summary>
    /// Update user role.
    /// </summary>
    public async Task UpdateUserRoleAsync(Guid id, UserRole newRole)
    {
        var user = await _userRepository.GetByIdAsync(id);
        if (user == null)
        {
            throw new KeyNotFoundException("User not found");
        }

        user.Role = newRole;
        user.UpdatedAt = DateTime.UtcNow;
        await _userRepository.UpdateAsync(user);
    }

    /// <summary>
    /// Get user statistics.
    /// </summary>
    public async Task<UserStatistics> GetUserStatisticsAsync()
    {
        var allUsers = await _userRepository.GetAllAsync();

        var totalUsers = allUsers.Count();
        var activeUsers = allUsers.Count(u => u.IsActive);
        var verifiedUsers = allUsers.Count(u => u.IsVerified);
        var adminUsers = allUsers.Count(u => u.Role == UserRole.ADMIN);
        var engineerUsers = allUsers.Count(u => u.Role == UserRole.ENGINEER);
        var viewerUsers = allUsers.Count(u => u.Role == UserRole.VIEWER);

        // Recent registrations (last 30 days)
        var thirtyDaysAgo = DateTime.UtcNow.AddDays(-30);
        var recentRegistrations = allUsers.Count(u => u.CreatedAt >= thirtyDaysAgo);

        // Recent logins (last 24 hours)
        var twentyFourHoursAgo = DateTime.UtcNow.AddHours(-24);
        var recentLogins = allUsers.Count(u => u.LastLogin.HasValue && u.LastLogin >= twentyFourHoursAgo);

        return new UserStatistics
        {
            TotalUsers = totalUsers,
            ActiveUsers = activeUsers,
            VerifiedUsers = verifiedUsers,
            AdminUsers = adminUsers,
            EngineerUsers = engineerUsers,
            ViewerUsers = viewerUsers,
            RecentRegistrations = recentRegistrations,
            RecentLogins = recentLogins
        };
    }

    /// <summary>
    /// Map User entity to UserDto.
    /// </summary>
    private static UserDto MapToDto(User user)
    {
        return new UserDto
        {
            Id = user.Id,
            Username = user.Username,
            Email = user.Email,
            FullName = user.FullName,
            Role = user.Role,
            IsActive = user.IsActive,
            IsVerified = user.IsVerified,
            CreatedAt = user.CreatedAt,
            LastLogin = user.LastLogin
        };
    }
}
