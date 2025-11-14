using Fro.Domain.Enums;

namespace Fro.Domain.Entities;

/// <summary>
/// User entity for authentication and authorization.
/// </summary>
public class User : BaseEntity
{
    /// <summary>
    /// Unique username (max 50 characters)
    /// </summary>
    public required string Username { get; set; }

    /// <summary>
    /// Email address (max 255 characters)
    /// </summary>
    public required string Email { get; set; }

    /// <summary>
    /// Full name of the user
    /// </summary>
    public string? FullName { get; set; }

    /// <summary>
    /// Hashed password (bcrypt)
    /// </summary>
    public required string PasswordHash { get; set; }

    /// <summary>
    /// User role for RBAC
    /// </summary>
    public UserRole Role { get; set; } = UserRole.VIEWER;

    /// <summary>
    /// Whether the account is active
    /// </summary>
    public bool IsActive { get; set; } = true;

    /// <summary>
    /// Whether the email is verified
    /// </summary>
    public bool IsVerified { get; set; } = false;

    /// <summary>
    /// Last login timestamp
    /// </summary>
    public DateTime? LastLogin { get; set; }

    /// <summary>
    /// Password reset token
    /// </summary>
    public string? ResetToken { get; set; }

    /// <summary>
    /// Password reset token expiration
    /// </summary>
    public DateTime? ResetTokenExpires { get; set; }

    // Business logic properties
    public bool IsAdmin => Role == UserRole.ADMIN;
    public bool IsEngineer => Role == UserRole.ENGINEER;
    public bool CanCreateScenarios => Role is UserRole.ADMIN or UserRole.ENGINEER;
    public bool CanManageUsers => Role == UserRole.ADMIN;
    public bool CanViewAllScenarios => Role == UserRole.ADMIN;

    // Navigation properties
    public ICollection<RegeneratorConfiguration> Configurations { get; set; } = new List<RegeneratorConfiguration>();
    public ICollection<OptimizationScenario> OptimizationScenarios { get; set; } = new List<OptimizationScenario>();
}
