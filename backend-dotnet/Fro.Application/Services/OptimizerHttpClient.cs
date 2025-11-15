using System.Net.Http.Json;
using System.Text.Json;
using Microsoft.Extensions.Logging;
using Fro.Application.DTOs.Optimization;

namespace Fro.Application.Services;

/// <summary>
/// HTTP client for communicating with Python SLSQP Optimizer microservice.
/// </summary>
public class OptimizerHttpClient
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<OptimizerHttpClient> _logger;
    private readonly string _baseUrl;

    public OptimizerHttpClient(HttpClient httpClient, ILogger<OptimizerHttpClient> logger, string baseUrl)
    {
        _httpClient = httpClient ?? throw new ArgumentNullException(nameof(httpClient));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        _baseUrl = baseUrl ?? throw new ArgumentNullException(nameof(baseUrl));

        _httpClient.BaseAddress = new Uri(_baseUrl);
        _httpClient.Timeout = TimeSpan.FromMinutes(10); // Long timeout for optimization
    }

    /// <summary>
    /// Check if optimizer service is healthy.
    /// </summary>
    public async Task<bool> IsHealthyAsync()
    {
        try
        {
            var response = await _httpClient.GetAsync("/health");
            return response.IsSuccessStatusCode;
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to check optimizer service health");
            return false;
        }
    }

    /// <summary>
    /// Run SLSQP optimization via Python microservice with retry logic.
    /// </summary>
    public async Task<OptimizerResult> OptimizeAsync(OptimizerRequest request)
    {
        const int maxRetries = 3;
        var retryDelays = new[] { TimeSpan.FromSeconds(1), TimeSpan.FromSeconds(2), TimeSpan.FromSeconds(4) };

        for (int attempt = 0; attempt <= maxRetries; attempt++)
        {
            try
            {
                _logger.LogInformation("Sending optimization request to Python service (attempt {Attempt}/{MaxAttempts}): {BaseUrl}/optimize",
                    attempt + 1, maxRetries + 1, _baseUrl);

                // Use /optimize endpoint (new Python microservice)
                var response = await _httpClient.PostAsJsonAsync("/optimize", request);

                if (response.IsSuccessStatusCode)
                {
                    var result = await response.Content.ReadFromJsonAsync<OptimizerResult>();
                    if (result == null)
                    {
                        throw new InvalidOperationException("Failed to deserialize optimizer response");
                    }

                    _logger.LogInformation("Optimization completed: Success={Success}, Iterations={Iterations}, Objective={Objective}",
                        result.Success, result.Iterations, result.ObjectiveValue);

                    return result;
                }

                // Handle error responses
                var statusCode = (int)response.StatusCode;
                var errorContent = await response.Content.ReadAsStringAsync();

                if (statusCode == 422)
                {
                    // Validation error - don't retry
                    _logger.LogError("Validation error from optimizer service: {Error}", errorContent);
                    throw new InvalidOperationException($"Validation error: {errorContent}");
                }

                if (statusCode == 503)
                {
                    // Service unavailable - retry
                    _logger.LogWarning("Optimizer service unavailable (503) on attempt {Attempt}", attempt + 1);

                    if (attempt < maxRetries)
                    {
                        await Task.Delay(retryDelays[attempt]);
                        continue;
                    }

                    throw new HttpRequestException("Optimizer service unavailable after retries");
                }

                if (statusCode >= 500)
                {
                    // Server error - retry
                    _logger.LogWarning("Server error from optimizer service (attempt {Attempt}): {StatusCode} - {Error}",
                        attempt + 1, statusCode, errorContent);

                    if (attempt < maxRetries)
                    {
                        await Task.Delay(retryDelays[attempt]);
                        continue;
                    }

                    throw new HttpRequestException($"Optimizer service error: {statusCode} - {errorContent}");
                }

                // Other errors
                _logger.LogError("Unexpected response from optimizer service: {StatusCode} - {Error}", statusCode, errorContent);
                throw new HttpRequestException($"Unexpected response: {statusCode}");
            }
            catch (HttpRequestException) when (attempt < maxRetries)
            {
                // Network error - retry
                _logger.LogWarning("Network error on attempt {Attempt}, retrying...", attempt + 1);
                await Task.Delay(retryDelays[attempt]);
                continue;
            }
            catch (TaskCanceledException) when (attempt < maxRetries)
            {
                // Timeout - retry
                _logger.LogWarning("Timeout on attempt {Attempt}, retrying...", attempt + 1);
                await Task.Delay(retryDelays[attempt]);
                continue;
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError(ex, "HTTP error communicating with optimizer service at {Url}", _baseUrl);
                throw new InvalidOperationException($"Failed to communicate with optimizer service: {ex.Message}", ex);
            }
            catch (TaskCanceledException ex)
            {
                _logger.LogError(ex, "Optimization request timed out");
                throw new TimeoutException("Optimization request timed out. Consider increasing timeout or max_iterations.", ex);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Unexpected error during optimization");
                throw;
            }
        }

        // Should never reach here, but just in case
        throw new HttpRequestException("Failed to communicate with optimizer after all retries");
    }

    /// <summary>
    /// Calculate performance metrics without optimization.
    /// </summary>
    public async Task<OptimizerPerformanceMetrics> CalculatePerformanceAsync(OptimizerPerformanceRequest request)
    {
        try
        {
            _logger.LogInformation("Sending performance calculation request to Python service");

            var response = await _httpClient.PostAsJsonAsync("/api/v1/performance", request);

            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                _logger.LogError("Optimizer service returned error: {StatusCode} - {Error}",
                    response.StatusCode, errorContent);
                throw new HttpRequestException($"Optimizer service error: {response.StatusCode}");
            }

            var result = await response.Content.ReadFromJsonAsync<OptimizerPerformanceMetrics>();
            if (result == null)
            {
                throw new InvalidOperationException("Failed to deserialize performance response");
            }

            return result;
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "HTTP error communicating with optimizer service");
            throw new InvalidOperationException($"Failed to communicate with optimizer service: {ex.Message}", ex);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unexpected error during performance calculation");
            throw;
        }
    }
}

/// <summary>
/// Request model for Python optimizer service.
/// </summary>
public class OptimizerRequest
{
    public required OptimizerConfiguration Configuration { get; set; }
    public required OptimizerDesignVariables InitialGuess { get; set; }
    public OptimizerBounds? Bounds { get; set; }
    public string ObjectiveType { get; set; } = "minimize_fuel_consumption";
    public int MaxIterations { get; set; } = 100;
    public double Tolerance { get; set; } = 1e-6;
}

/// <summary>
/// Configuration for optimizer (maps to Python RegeneratorConfiguration).
/// </summary>
public class OptimizerConfiguration
{
    public required GeometryConfig GeometryConfig { get; set; }
    public required ThermalConfig ThermalConfig { get; set; }
    public required FlowConfig FlowConfig { get; set; }
    public Dictionary<string, object>? MaterialsConfig { get; set; }
}

public class GeometryConfig
{
    public double Length { get; set; }
    public double Width { get; set; }
}

public class ThermalConfig
{
    public double GasTempInlet { get; set; }
    public double GasTempOutlet { get; set; }
}

public class FlowConfig
{
    public double MassFlowRate { get; set; }
    public double CycleTime { get; set; }
}

/// <summary>
/// Design variables for optimization.
/// </summary>
public class OptimizerDesignVariables
{
    public double CheckerHeight { get; set; }
    public double CheckerSpacing { get; set; }
    public double WallThickness { get; set; }
    public double? ThermalConductivity { get; set; }
    public double? SpecificHeat { get; set; }
    public double? Density { get; set; }
}

/// <summary>
/// Bounds for design variables.
/// </summary>
public class OptimizerBounds
{
    public (double, double) CheckerHeight { get; set; } = (0.3, 2.0);
    public (double, double) CheckerSpacing { get; set; } = (0.05, 0.3);
    public (double, double) WallThickness { get; set; } = (0.2, 0.8);
    public (double, double) ThermalConductivity { get; set; } = (1.0, 5.0);
    public (double, double) SpecificHeat { get; set; } = (700, 1200);
    public (double, double) Density { get; set; } = (1800, 2800);
}

/// <summary>
/// Result from Python optimizer service.
/// </summary>
public class OptimizerResult
{
    public required bool Success { get; set; }
    public required string Message { get; set; }
    public required OptimizerDesignVariables FinalDesignVariables { get; set; }
    public required OptimizerPerformanceMetrics FinalPerformance { get; set; }
    public required double ObjectiveValue { get; set; }
    public required int Iterations { get; set; }
    public required bool ConvergenceReached { get; set; }
    public required double ComputationTimeSeconds { get; set; }
}

/// <summary>
/// Performance metrics from physics calculations.
/// </summary>
public class OptimizerPerformanceMetrics
{
    public required double ThermalEfficiency { get; set; }
    public required double HeatTransferRate { get; set; }
    public required double PressureDrop { get; set; }
    public required double NtuValue { get; set; }
    public required double Effectiveness { get; set; }
    public required double HeatTransferCoefficient { get; set; }
    public required double SurfaceArea { get; set; }
    public required double WallHeatLoss { get; set; }
    public required double ReynoldsNumber { get; set; }
    public required double NusseltNumber { get; set; }
}

/// <summary>
/// Request for performance calculation only.
/// </summary>
public class OptimizerPerformanceRequest
{
    public required OptimizerConfiguration Configuration { get; set; }
    public required OptimizerDesignVariables DesignVariables { get; set; }
}
