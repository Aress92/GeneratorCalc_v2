namespace Fro.Application.DTOs.Auth;

/// <summary>
/// Change password request.
/// </summary>
public class ChangePasswordRequest
{
    /// <summary>
    /// Current password
    /// </summary>
    public required string CurrentPassword { get; set; }

    /// <summary>
    /// New password (min 8 characters)
    /// </summary>
    public required string NewPassword { get; set; }

    /// <summary>
    /// New password confirmation
    /// </summary>
    public required string NewPasswordConfirm { get; set; }
}
