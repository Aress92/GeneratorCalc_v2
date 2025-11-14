using System.Security.Cryptography;
using System.Text;
using Fro.Application.Interfaces.Security;

namespace Fro.Infrastructure.Security;

/// <summary>
/// Service for hashing and verifying passwords using BCrypt.
/// </summary>
public class PasswordHasher : IPasswordHasher
{
    private const int WorkFactor = 12; // BCrypt work factor (higher = more secure but slower)

    /// <summary>
    /// Hash a password using BCrypt.
    /// </summary>
    /// <param name="password">Plain text password</param>
    /// <returns>BCrypt hashed password</returns>
    public string HashPassword(string password)
    {
        return BCrypt.Net.BCrypt.HashPassword(password, WorkFactor);
    }

    /// <summary>
    /// Verify a password against a BCrypt hash.
    /// </summary>
    /// <param name="password">Plain text password</param>
    /// <param name="hashedPassword">BCrypt hashed password</param>
    /// <returns>True if password matches, false otherwise</returns>
    public bool VerifyPassword(string password, string hashedPassword)
    {
        try
        {
            return BCrypt.Net.BCrypt.Verify(password, hashedPassword);
        }
        catch
        {
            return false;
        }
    }

    /// <summary>
    /// Validate password strength.
    /// </summary>
    /// <param name="password">Password to validate</param>
    /// <returns>Tuple of (isValid, list of error messages)</returns>
    public (bool isValid, List<string> errors) ValidatePasswordStrength(string password)
    {
        var errors = new List<string>();

        if (string.IsNullOrWhiteSpace(password))
        {
            errors.Add("Password cannot be empty");
            return (false, errors);
        }

        if (password.Length < 8)
        {
            errors.Add("Password must be at least 8 characters long");
        }

        if (!password.Any(char.IsUpper))
        {
            errors.Add("Password must contain at least one uppercase letter");
        }

        if (!password.Any(char.IsLower))
        {
            errors.Add("Password must contain at least one lowercase letter");
        }

        if (!password.Any(char.IsDigit))
        {
            errors.Add("Password must contain at least one digit");
        }

        if (!password.Any(ch => !char.IsLetterOrDigit(ch)))
        {
            errors.Add("Password must contain at least one special character");
        }

        return (errors.Count == 0, errors);
    }

    /// <summary>
    /// Generate a secure random reset token.
    /// </summary>
    /// <returns>Random token string</returns>
    public string GenerateResetToken()
    {
        var randomBytes = new byte[32];
        using (var rng = RandomNumberGenerator.Create())
        {
            rng.GetBytes(randomBytes);
        }
        return Convert.ToBase64String(randomBytes);
    }
}
