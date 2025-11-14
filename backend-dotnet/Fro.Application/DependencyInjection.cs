using FluentValidation;
using Microsoft.Extensions.DependencyInjection;
using Fro.Application.Interfaces.Services;
using Fro.Application.Services;

namespace Fro.Application;

/// <summary>
/// Dependency injection configuration for Application layer.
/// </summary>
public static class DependencyInjection
{
    /// <summary>
    /// Register Application services, validators, and mappings.
    /// </summary>
    public static IServiceCollection AddApplication(this IServiceCollection services)
    {
        // Register application services
        services.AddScoped<IAuthenticationService, AuthenticationService>();
        services.AddScoped<IUserService, UserService>();
        services.AddScoped<IRegeneratorConfigurationService, RegeneratorConfigurationService>();
        services.AddScoped<IOptimizationService, OptimizationService>();

        // Register FluentValidation validators from this assembly
        services.AddValidatorsFromAssembly(typeof(DependencyInjection).Assembly);

        return services;
    }
}
