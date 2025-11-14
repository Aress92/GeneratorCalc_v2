using System.Net;
using System.Text.Json;
using FluentValidation;

namespace Fro.Api.Middleware;

/// <summary>
/// Global exception handler middleware for consistent error responses.
/// </summary>
/// <remarks>
/// Catches all unhandled exceptions and returns standardized error responses:
/// - 400 Bad Request: Validation errors (FluentValidation)
/// - 401 Unauthorized: Authentication errors
/// - 403 Forbidden: Authorization errors
/// - 404 Not Found: Resource not found (KeyNotFoundException)
/// - 422 Unprocessable Entity: Business logic validation errors
/// - 500 Internal Server Error: Unexpected errors
/// </remarks>
public class GlobalExceptionHandlerMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<GlobalExceptionHandlerMiddleware> _logger;
    private readonly IHostEnvironment _environment;

    public GlobalExceptionHandlerMiddleware(
        RequestDelegate next,
        ILogger<GlobalExceptionHandlerMiddleware> logger,
        IHostEnvironment environment)
    {
        _next = next;
        _logger = logger;
        _environment = environment;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        try
        {
            await _next(context);
        }
        catch (Exception ex)
        {
            await HandleExceptionAsync(context, ex);
        }
    }

    private async Task HandleExceptionAsync(HttpContext context, Exception exception)
    {
        _logger.LogError(exception, "Unhandled exception occurred: {Message}", exception.Message);

        var response = context.Response;
        response.ContentType = "application/json";

        var errorResponse = exception switch
        {
            // FluentValidation errors (400 Bad Request)
            ValidationException validationEx => new ErrorResponse
            {
                StatusCode = (int)HttpStatusCode.BadRequest,
                Message = "Validation failed",
                Errors = validationEx.Errors.Select(e => new ValidationError
                {
                    Field = e.PropertyName,
                    Message = e.ErrorMessage,
                    Code = e.ErrorCode
                }).ToList(),
                TraceId = context.TraceIdentifier
            },

            // Resource not found (404 Not Found)
            KeyNotFoundException notFoundEx => new ErrorResponse
            {
                StatusCode = (int)HttpStatusCode.NotFound,
                Message = notFoundEx.Message ?? "Resource not found",
                TraceId = context.TraceIdentifier
            },

            // Authentication errors (401 Unauthorized)
            UnauthorizedAccessException unauthorizedEx => new ErrorResponse
            {
                StatusCode = (int)HttpStatusCode.Unauthorized,
                Message = unauthorizedEx.Message ?? "Unauthorized access",
                TraceId = context.TraceIdentifier
            },

            // Business logic validation errors (422 Unprocessable Entity)
            InvalidOperationException invalidOpEx => new ErrorResponse
            {
                StatusCode = (int)HttpStatusCode.UnprocessableEntity,
                Message = invalidOpEx.Message ?? "Invalid operation",
                TraceId = context.TraceIdentifier
            },

            // Argument validation errors (400 Bad Request)
            ArgumentException argEx => new ErrorResponse
            {
                StatusCode = (int)HttpStatusCode.BadRequest,
                Message = argEx.Message ?? "Invalid argument",
                TraceId = context.TraceIdentifier
            },

            // Generic errors (500 Internal Server Error)
            _ => new ErrorResponse
            {
                StatusCode = (int)HttpStatusCode.InternalServerError,
                Message = _environment.IsDevelopment()
                    ? exception.Message
                    : "An internal server error occurred. Please contact support.",
                Details = _environment.IsDevelopment() ? exception.StackTrace : null,
                TraceId = context.TraceIdentifier
            }
        };

        response.StatusCode = errorResponse.StatusCode;

        var jsonOptions = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            WriteIndented = _environment.IsDevelopment()
        };

        await response.WriteAsync(JsonSerializer.Serialize(errorResponse, jsonOptions));
    }
}

/// <summary>
/// Standard error response model.
/// </summary>
public class ErrorResponse
{
    /// <summary>
    /// HTTP status code.
    /// </summary>
    public int StatusCode { get; set; }

    /// <summary>
    /// Error message.
    /// </summary>
    public required string Message { get; set; }

    /// <summary>
    /// Detailed error information (only in Development mode).
    /// </summary>
    public string? Details { get; set; }

    /// <summary>
    /// List of validation errors (for 400/422 responses).
    /// </summary>
    public List<ValidationError>? Errors { get; set; }

    /// <summary>
    /// Request trace identifier for debugging.
    /// </summary>
    public string? TraceId { get; set; }

    /// <summary>
    /// Timestamp of the error.
    /// </summary>
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
}

/// <summary>
/// Validation error detail.
/// </summary>
public class ValidationError
{
    /// <summary>
    /// Field name that failed validation.
    /// </summary>
    public required string Field { get; set; }

    /// <summary>
    /// Validation error message.
    /// </summary>
    public required string Message { get; set; }

    /// <summary>
    /// Error code (e.g., "NotEmptyValidator", "EmailValidator").
    /// </summary>
    public string? Code { get; set; }
}

/// <summary>
/// Extension methods for registering the middleware.
/// </summary>
public static class GlobalExceptionHandlerMiddlewareExtensions
{
    /// <summary>
    /// Add global exception handler middleware to the pipeline.
    /// </summary>
    public static IApplicationBuilder UseGlobalExceptionHandler(this IApplicationBuilder app)
    {
        return app.UseMiddleware<GlobalExceptionHandlerMiddleware>();
    }
}
