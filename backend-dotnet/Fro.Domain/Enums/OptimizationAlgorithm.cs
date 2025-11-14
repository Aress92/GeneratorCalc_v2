namespace Fro.Domain.Enums;

/// <summary>
/// Available optimization algorithms.
/// </summary>
public enum OptimizationAlgorithm
{
    /// <summary>
    /// Sequential Least Squares Programming (gradient-based)
    /// </summary>
    SLSQP,

    /// <summary>
    /// Genetic Algorithm (evolutionary)
    /// </summary>
    Genetic,

    /// <summary>
    /// Differential Evolution (evolutionary)
    /// </summary>
    DifferentialEvolution,

    /// <summary>
    /// Particle Swarm Optimization (swarm intelligence)
    /// </summary>
    ParticleSwarm,

    /// <summary>
    /// Simulated Annealing (probabilistic)
    /// </summary>
    SimulatedAnnealing
}
