using System.Runtime.Serialization;

namespace Fro.Domain.Enums;

/// <summary>
/// Available optimization algorithms.
/// Matches Python backend: slsqp, genetic, differential_evolution, particle_swarm, simulated_annealing
/// </summary>
public enum OptimizationAlgorithm
{
    /// <summary>
    /// Sequential Least Squares Programming (gradient-based)
    /// </summary>
    [EnumMember(Value = "slsqp")]
    SLSQP,

    /// <summary>
    /// Genetic Algorithm (evolutionary)
    /// </summary>
    [EnumMember(Value = "genetic")]
    Genetic,

    /// <summary>
    /// Differential Evolution (evolutionary)
    /// </summary>
    [EnumMember(Value = "differential_evolution")]
    DifferentialEvolution,

    /// <summary>
    /// Particle Swarm Optimization (swarm intelligence)
    /// </summary>
    [EnumMember(Value = "particle_swarm")]
    ParticleSwarm,

    /// <summary>
    /// Simulated Annealing (probabilistic)
    /// </summary>
    [EnumMember(Value = "simulated_annealing")]
    SimulatedAnnealing
}
