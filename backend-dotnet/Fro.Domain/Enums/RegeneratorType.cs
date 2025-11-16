using System.Runtime.Serialization;

namespace Fro.Domain.Enums;

/// <summary>
/// Types of glass furnace regenerators.
/// Matches Python backend: crown, end-port, cross-fired
/// </summary>
public enum RegeneratorType
{
    /// <summary>
    /// Crown regenerator
    /// </summary>
    [EnumMember(Value = "crown")]
    Crown,

    /// <summary>
    /// End-port regenerator
    /// </summary>
    [EnumMember(Value = "end-port")]
    EndPort,

    /// <summary>
    /// Cross-fired regenerator
    /// </summary>
    [EnumMember(Value = "cross-fired")]
    CrossFired
}
