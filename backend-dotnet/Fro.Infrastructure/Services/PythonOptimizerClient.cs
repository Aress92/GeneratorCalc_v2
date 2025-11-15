using System.Net.Http.Json;
using System.Text;
using System.Text.Json;
using Fro.Application.DTOs.PythonOptimizer;
using Fro.Application.Interfaces.Services;
using Microsoft.Extensions.Logging;

namespace Fro.Infrastructure.Services;

/// <summary>
/// HTTP client for Python SLSQP optimizer microservice.
/// </summary>
public class PythonOptimizerClient : IPythonOptimizerClient
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<PythonOptimizerClient> _logger;
    private readonly JsonSerializerOptions _jsonOptions;

    public PythonOptimizerClient(
        HttpClient httpClient,
        ILogger<PythonOptimizerClient> logger)
    {
        _httpClient = httpClient;
        _logger = logger;

        // Configure JSON serialization to match Python snake_case
        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
            WriteIndented = false
        };
    }

    /// <summary>
    /// Check if the Python optimizer service is healthy.
    /// </summary>
    public async Task<bool> IsHealthyAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogDebug("Checking Python optimizer service health");

            var response = await _httpClient.GetAsync("/health", cancellationToken);

            if (!response.IsSuccessStatusCode)
            {
                _logger.LogWarning("Python optimizer health check returned status {StatusCode}", response.StatusCode);
                return false;
            }

            var healthResponse = await response.Content.ReadFromJsonAsync<HealthCheckResponse>(cancellationToken);

            var isHealthy = healthResponse?.Status == "healthy" && healthResponse.ScipyAvailable;

            _logger.LogInformation(
                "Python optimizer health check: Status={Status}, SciPy={ScipyAvailable}, Version={Version}",
                healthResponse?.Status,
                healthResponse?.ScipyAvailable,
                healthResponse?.Version
            );

            return isHealthy;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error checking Python optimizer health");
            return false;
        }
    }

    /// <summary>
    /// Run optimization using the Python SLSQP optimizer with retry logic.
    /// </summary>
    public async Task<PythonOptimizerResponse> OptimizeAsync(
        PythonOptimizerRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation(
            "Starting optimization: Objective={Objective}, Algorithm={Algorithm}, MaxIterations={MaxIterations}",
            request.Objective,
            request.Algorithm,
            request.MaxIterations
        );

        const int maxRetries = 3;
        var retryDelays = new[] { TimeSpan.FromSeconds(1), TimeSpan.FromSeconds(2), TimeSpan.FromSeconds(4) };

        for (int attempt = 0; attempt <= maxRetries; attempt++)
        {
            try
            {
                // Serialize request
                var jsonContent = JsonSerializer.Serialize(request, _jsonOptions);
                var httpContent = new StringContent(jsonContent, Encoding.UTF8, "application/json");

                _logger.LogDebug("Sending optimization request (attempt {Attempt}/{MaxAttempts})", attempt + 1, maxRetries + 1);

                // Send request
                var response = await _httpClient.PostAsync("/optimize", httpContent, cancellationToken);

                // Handle different status codes
                if (response.IsSuccessStatusCode)
                {
                    var result = await response.Content.ReadFromJsonAsync<PythonOptimizerResponse>(cancellationToken);

                    if (result == null)
                    {
                        throw new InvalidOperationException("Received null response from Python optimizer");
                    }

                    _logger.LogInformation(
                        "Optimization completed: Success={Success}, Iterations={Iterations}, Objective={ObjectiveValue}",
                        result.Success,
                        result.Iterations,
                        result.FinalObjectiveValue
                    );

                    return result;
                }

                // Handle error responses
                var statusCode = (int)response.StatusCode;

                if (statusCode == 422)
                {
                    // Validation error - don't retry
                    var errorResponse = await response.Content.ReadFromJsonAsync<PythonOptimizerErrorResponse>(cancellationToken);
                    var errorMessage = errorResponse?.Message ?? "Validation error";

                    _logger.LogError("Validation error from Python optimizer: {ErrorMessage}", errorMessage);

                    throw new InvalidOperationException($"Validation error: {errorMessage}");
                }

                if (statusCode == 503)
                {
                    // Service unavailable - retry
                    _logger.LogWarning("Python optimizer service unavailable (503)");

                    if (attempt < maxRetries)
                    {
                        await Task.Delay(retryDelays[attempt], cancellationToken);
                        continue;
                    }

                    throw new HttpRequestException("Python optimizer service unavailable after retries");
                }

                if (statusCode >= 500)
                {
                    // Server error - try to parse error response
                    var errorResponse = await response.Content.ReadFromJsonAsync<PythonOptimizerErrorResponse>(cancellationToken);
                    var errorMessage = errorResponse?.Message ?? $"Server error: {statusCode}";

                    _logger.LogError("Server error from Python optimizer: {ErrorMessage}", errorMessage);

                    if (attempt < maxRetries)
                    {
                        await Task.Delay(retryDelays[attempt], cancellationToken);
                        continue;
                    }

                    throw new HttpRequestException($"Python optimizer error: {errorMessage}");
                }

                // Other errors
                var content = await response.Content.ReadAsStringAsync(cancellationToken);
                _logger.LogError("Unexpected response from Python optimizer: {StatusCode} - {Content}", statusCode, content);

                throw new HttpRequestException($"Unexpected response: {statusCode}");
            }
            catch (HttpRequestException) when (attempt < maxRetries)
            {
                // Network error - retry
                _logger.LogWarning("Network error on attempt {Attempt}, retrying...", attempt + 1);
                await Task.Delay(retryDelays[attempt], cancellationToken);
                continue;
            }
            catch (TaskCanceledException) when (!cancellationToken.IsCancellationRequested && attempt < maxRetries)
            {
                // Timeout - retry
                _logger.LogWarning("Timeout on attempt {Attempt}, retrying...", attempt + 1);
                await Task.Delay(retryDelays[attempt], cancellationToken);
                continue;
            }
        }

        // Should never reach here, but just in case
        throw new HttpRequestException("Failed to communicate with Python optimizer after all retries");
    }

    /// <summary>
    /// Health check response from Python service.
    /// </summary>
    private class HealthCheckResponse
    {
        public string? Status { get; set; }
        public string? Version { get; set; }
        public bool ScipyAvailable { get; set; }
    }
}
