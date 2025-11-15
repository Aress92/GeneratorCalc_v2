using Microsoft.Extensions.DependencyInjection;
using Fro.Application.Interfaces.Repositories;
using Fro.Application.Interfaces.Security;
using Fro.Infrastructure.Repositories;
using Fro.Infrastructure.Security;
using Fro.Infrastructure.Data;

namespace Fro.Infrastructure;

/// <summary>
/// Dependency injection configuration for Infrastructure layer.
/// </summary>
public static class DependencyInjection
{
    /// <summary>
    /// Register Infrastructure services and repositories.
    /// </summary>
    public static IServiceCollection AddInfrastructure(this IServiceCollection services)
    {
        // Register repositories
        services.AddScoped(typeof(IRepository<>), typeof(Repository<>));
        services.AddScoped<IUserRepository, UserRepository>();
        services.AddScoped<IRegeneratorConfigurationRepository, RegeneratorConfigurationRepository>();
        services.AddScoped<IOptimizationScenarioRepository, OptimizationScenarioRepository>();
        services.AddScoped<IOptimizationJobRepository, OptimizationJobRepository>();
        services.AddScoped<IMaterialsRepository, MaterialsRepository>();

        // Register security services
        services.AddSingleton<IJwtTokenService, JwtTokenService>();
        services.AddSingleton<IPasswordHasher, PasswordHasher>();

        // Register database seeder
        services.AddScoped<DatabaseSeeder>();

        return services;
    }
}
