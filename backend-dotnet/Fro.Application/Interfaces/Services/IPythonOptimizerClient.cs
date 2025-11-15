using Fro.Application.DTOs.PythonOptimizer;

namespace Fro.Application.Interfaces.Services;

/// <summary>
/// Client for communicating with Python SLSQP optimizer microservice.
/// </summary>
public interface IPythonOptimizerClient
{
    /// <summary>
    /// Check if the Python optimizer service is healthy.
    /// </summary>
    Task<bool> IsHealthyAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Run optimization using the Python SLSQP optimizer.
    /// </summary>
    /// <param name="request">Optimization request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Optimization result</returns>
    /// <exception cref="HttpRequestException">Thrown when the service is unavailable</exception>
    /// <exception cref="InvalidOperationException">Thrown when the response is invalid</exception>
    Task<PythonOptimizerResponse> OptimizeAsync(
        PythonOptimizerRequest request,
        CancellationToken cancellationToken = default);
}
