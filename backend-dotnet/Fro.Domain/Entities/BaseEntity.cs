namespace Fro.Domain.Entities;

/// <summary>
/// Base entity with common properties for all domain entities.
/// </summary>
public abstract class BaseEntity
{
    /// <summary>
    /// Unique identifier (GUID stored as string for MySQL compatibility)
    /// </summary>
    public Guid Id { get; set; } = Guid.NewGuid();

    /// <summary>
    /// When the entity was created (UTC)
    /// </summary>
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// When the entity was last updated (UTC)
    /// </summary>
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}
