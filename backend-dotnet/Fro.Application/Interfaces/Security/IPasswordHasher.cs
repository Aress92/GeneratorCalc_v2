namespace Fro.Application.Interfaces.Security;

/// <summary>
/// Interface for password hashing and validation.
/// </summary>
public interface IPasswordHasher
{
    /// <summary>
    /// Hash a password.
    /// </summary>
    string HashPassword(string password);

    /// <summary>
    /// Verify a password against a hash.
    /// </summary>
    bool VerifyPassword(string password, string hashedPassword);

    /// <summary>
    /// Validate password strength.
    /// </summary>
    (bool isValid, List<string> errors) ValidatePasswordStrength(string password);

    /// <summary>
    /// Generate a secure random reset token.
    /// </summary>
    string GenerateResetToken();
}
