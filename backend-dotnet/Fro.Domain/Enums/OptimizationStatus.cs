namespace Fro.Domain.Enums;

/// <summary>
/// Status of optimization job execution.
/// </summary>
public enum OptimizationStatus
{
    /// <summary>
    /// Job is queued and waiting to start
    /// </summary>
    Pending,

    /// <summary>
    /// Job is initializing (preparing data)
    /// </summary>
    Initializing,

    /// <summary>
    /// Job is actively running optimization
    /// </summary>
    Running,

    /// <summary>
    /// Job is in convergence phase
    /// </summary>
    Converging,

    /// <summary>
    /// Job completed successfully
    /// </summary>
    Completed,

    /// <summary>
    /// Job failed with error
    /// </summary>
    Failed,

    /// <summary>
    /// Job was cancelled by user
    /// </summary>
    Cancelled,

    /// <summary>
    /// Job exceeded maximum runtime
    /// </summary>
    Timeout
}
