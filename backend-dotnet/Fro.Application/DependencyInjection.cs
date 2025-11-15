using FluentValidation;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Fro.Application.Interfaces;
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
    public static IServiceCollection AddApplication(this IServiceCollection services, IConfiguration configuration)
    {
        // Register application services
        services.AddScoped<IAuthenticationService, AuthenticationService>();
        services.AddScoped<IUserService, UserService>();
        services.AddScoped<IRegeneratorConfigurationService, RegeneratorConfigurationService>();
        services.AddScoped<IOptimizationService, OptimizationService>();
        services.AddScoped<IMaterialsService, MaterialsService>();

        // Register Python Optimizer HTTP client
        var optimizerBaseUrl = configuration["OptimizerService:BaseUrl"] ?? "http://localhost:7000";
        var timeoutSeconds = configuration.GetValue<int>("OptimizerService:TimeoutSeconds", 600); // 10 minutes for optimization

        services.AddHttpClient<OptimizerHttpClient>()
            .ConfigureHttpClient(client =>
            {
                client.BaseAddress = new Uri(optimizerBaseUrl);
                client.Timeout = TimeSpan.FromSeconds(timeoutSeconds);
                client.DefaultRequestHeaders.Add("Accept", "application/json");
            });

        services.AddScoped(sp =>
        {
            var httpClientFactory = sp.GetRequiredService<IHttpClientFactory>();
            var httpClient = httpClientFactory.CreateClient(nameof(OptimizerHttpClient));
            var logger = sp.GetRequiredService<ILogger<OptimizerHttpClient>>();
            return new OptimizerHttpClient(httpClient, logger, optimizerBaseUrl);
        });

        // Register FluentValidation validators from this assembly
        services.AddValidatorsFromAssembly(typeof(DependencyInjection).Assembly);

        return services;
    }
}
