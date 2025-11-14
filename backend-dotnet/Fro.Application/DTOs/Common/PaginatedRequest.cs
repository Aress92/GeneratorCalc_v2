namespace Fro.Application.DTOs.Common;

/// <summary>
/// Base class for paginated requests.
/// </summary>
public class PaginatedRequest
{
    /// <summary>
    /// Page number (1-based)
    /// </summary>
    public int Page { get; set; } = 1;

    /// <summary>
    /// Number of items per page
    /// </summary>
    public int PageSize { get; set; } = 20;

    /// <summary>
    /// Field to sort by
    /// </summary>
    public string? SortBy { get; set; }

    /// <summary>
    /// Sort in descending order (default: false = ascending)
    /// </summary>
    public bool SortDescending { get; set; } = false;

    /// <summary>
    /// Search term for filtering
    /// </summary>
    public string? SearchTerm { get; set; }
}
