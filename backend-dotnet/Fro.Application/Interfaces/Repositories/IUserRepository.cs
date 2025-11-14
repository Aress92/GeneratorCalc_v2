using Fro.Domain.Entities;

namespace Fro.Application.Interfaces.Repositories;

/// <summary>
/// User repository interface with specific methods.
/// </summary>
public interface IUserRepository : IRepository<User>
{
    /// <summary>
    /// Get user by username.
    /// </summary>
    Task<User?> GetByUsernameAsync(string username, CancellationToken cancellationToken = default);

    /// <summary>
    /// Get user by email.
    /// </summary>
    Task<User?> GetByEmailAsync(string email, CancellationToken cancellationToken = default);

    /// <summary>
    /// Check if username exists.
    /// </summary>
    Task<bool> UsernameExistsAsync(string username, CancellationToken cancellationToken = default);

    /// <summary>
    /// Check if email exists.
    /// </summary>
    Task<bool> EmailExistsAsync(string email, CancellationToken cancellationToken = default);

    /// <summary>
    /// Update user's last login timestamp.
    /// </summary>
    Task UpdateLastLoginAsync(Guid userId, CancellationToken cancellationToken = default);
}
