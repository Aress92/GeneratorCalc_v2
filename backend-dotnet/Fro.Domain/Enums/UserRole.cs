namespace Fro.Domain.Enums;

/// <summary>
/// User roles for RBAC (Role-Based Access Control).
/// </summary>
public enum UserRole
{
    /// <summary>
    /// Administrator with full system access
    /// </summary>
    ADMIN,

    /// <summary>
    /// Engineer who can create and manage optimization scenarios
    /// </summary>
    ENGINEER,

    /// <summary>
    /// Viewer with read-only access
    /// </summary>
    VIEWER
}
