using System.Runtime.Serialization;

namespace Fro.Domain.Enums;

/// <summary>
/// Status of optimization job execution.
/// Matches Python backend: pending, initializing, running, converging, completed, failed, cancelled, timeout
/// </summary>
public enum OptimizationStatus
{
    /// <summary>
    /// Job is queued and waiting to start
    /// </summary>
    [EnumMember(Value = "pending")]
    Pending,

    /// <summary>
    /// Job is initializing (preparing data)
    /// </summary>
    [EnumMember(Value = "initializing")]
    Initializing,

    /// <summary>
    /// Job is actively running optimization
    /// </summary>
    [EnumMember(Value = "running")]
    Running,

    /// <summary>
    /// Job is in convergence phase
    /// </summary>
    [EnumMember(Value = "converging")]
    Converging,

    /// <summary>
    /// Job completed successfully
    /// </summary>
    [EnumMember(Value = "completed")]
    Completed,

    /// <summary>
    /// Job failed with error
    /// </summary>
    [EnumMember(Value = "failed")]
    Failed,

    /// <summary>
    /// Job was cancelled by user
    /// </summary>
    [EnumMember(Value = "cancelled")]
    Cancelled,

    /// <summary>
    /// Job exceeded maximum runtime
    /// </summary>
    [EnumMember(Value = "timeout")]
    Timeout
}
