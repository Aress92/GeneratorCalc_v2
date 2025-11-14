using Fro.Application.DTOs.Common;
using Fro.Domain.Enums;

namespace Fro.Application.DTOs.Users;

/// <summary>
/// Request for listing users with filters.
/// </summary>
public class UserListRequest : PaginatedRequest
{
    /// <summary>
    /// Filter by role
    /// </summary>
    public UserRole? Role { get; set; }

    /// <summary>
    /// Filter by active status
    /// </summary>
    public bool? IsActive { get; set; }

    /// <summary>
    /// Filter by verified status
    /// </summary>
    public bool? IsVerified { get; set; }
}
