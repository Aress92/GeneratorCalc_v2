using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using Fro.Domain.Entities;
using Fro.Domain.Enums;
using Fro.Infrastructure.Security;

namespace Fro.Infrastructure.Data;

/// <summary>
/// Database seeder for initial data.
/// Seeds admin user and test data for development.
/// </summary>
public class DatabaseSeeder
{
    private readonly ApplicationDbContext _context;
    private readonly IPasswordHasher _passwordHasher;
    private readonly ILogger<DatabaseSeeder> _logger;

    public DatabaseSeeder(
        ApplicationDbContext context,
        IPasswordHasher passwordHasher,
        ILogger<DatabaseSeeder> logger)
    {
        _context = context;
        _passwordHasher = passwordHasher;
        _logger = logger;
    }

    /// <summary>
    /// Seed database with initial data.
    /// </summary>
    public async Task SeedAsync()
    {
        try
        {
            _logger.LogInformation("Starting database seeding...");

            // Seed users
            await SeedUsersAsync();

            // Seed configuration templates
            await SeedConfigurationTemplatesAsync();

            // Seed test configuration (optional - development only)
            await SeedTestConfigurationAsync();

            await _context.SaveChangesAsync();

            _logger.LogInformation("Database seeding completed successfully");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during database seeding");
            throw;
        }
    }

    /// <summary>
    /// Seed users (admin, engineer, viewer).
    /// </summary>
    private async Task SeedUsersAsync()
    {
        // Check if users already exist
        if (await _context.Users.AnyAsync())
        {
            _logger.LogInformation("Users already exist, skipping user seeding");
            return;
        }

        _logger.LogInformation("Seeding users...");

        var users = new List<User>
        {
            // Admin user
            new User
            {
                Id = Guid.NewGuid(),
                Username = "admin",
                Email = "admin@forglass.com",
                FullName = "System Administrator",
                PasswordHash = _passwordHasher.HashPassword("admin"), // CHANGE IN PRODUCTION!
                Role = UserRole.ADMIN,
                IsActive = true,
                IsVerified = true,
                CreatedAt = DateTime.UtcNow,
                UpdatedAt = DateTime.UtcNow
            },

            // Engineer user
            new User
            {
                Id = Guid.NewGuid(),
                Username = "engineer",
                Email = "engineer@forglass.com",
                FullName = "Test Engineer",
                PasswordHash = _passwordHasher.HashPassword("engineer123"),
                Role = UserRole.ENGINEER,
                IsActive = true,
                IsVerified = true,
                CreatedAt = DateTime.UtcNow,
                UpdatedAt = DateTime.UtcNow
            },

            // Viewer user
            new User
            {
                Id = Guid.NewGuid(),
                Username = "viewer",
                Email = "viewer@forglass.com",
                FullName = "Test Viewer",
                PasswordHash = _passwordHasher.HashPassword("viewer123"),
                Role = UserRole.VIEWER,
                IsActive = true,
                IsVerified = true,
                CreatedAt = DateTime.UtcNow,
                UpdatedAt = DateTime.UtcNow
            }
        };

        await _context.Users.AddRangeAsync(users);
        _logger.LogInformation($"Seeded {users.Count} users");
    }

    /// <summary>
    /// Seed test configuration for development (optional).
    /// </summary>
    private async Task SeedTestConfigurationAsync()
    {
        if (await _context.RegeneratorConfigurations.AnyAsync())
        {
            _logger.LogInformation("Configurations already exist, skipping test configuration seeding");
            return;
        }

        _logger.LogInformation("Seeding test configuration...");

        var adminUser = await _context.Users.FirstOrDefaultAsync(u => u.Role == UserRole.ADMIN);

        if (adminUser == null)
        {
            _logger.LogWarning("Admin user not found, skipping test configuration seeding");
            return;
        }

        var testConfig = new RegeneratorConfiguration
        {
            Id = Guid.NewGuid(),
            UserId = adminUser.Id,
            Name = "Test Regenerator Configuration",
            Description = "Sample configuration for testing purposes",
            RegeneratorType = RegeneratorType.EndPort,
            Status = ConfigurationStatus.Draft,
            CurrentStep = 1,
            TotalSteps = 8,
            CompletedSteps = new List<int> { 1 },
            GeometryConfig = @"{""length"": 10.0, ""width"": 8.0, ""height"": 12.0}",
            ThermalConfig = @"{""gasTempInlet"": 1600, ""gasTempOutlet"": 600}",
            FlowConfig = @"{""massFlowRate"": 50, ""cycleTime"": 1200}",
            IsValidated = false,
            IsTemplate = false,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };

        await _context.RegeneratorConfigurations.AddAsync(testConfig);
        _logger.LogInformation("Seeded 1 test configuration");
    }

    /// <summary>
    /// Seed configuration templates.
    /// </summary>
    private async Task SeedConfigurationTemplatesAsync()
    {
        if (await _context.ConfigurationTemplates.AnyAsync())
        {
            _logger.LogInformation("Templates already exist, skipping template seeding");
            return;
        }

        _logger.LogInformation("Seeding configuration templates...");

        var templates = new List<ConfigurationTemplate>
        {
            new ConfigurationTemplate
            {
                Id = Guid.NewGuid(),
                Name = "Standard End-Port Regenerator",
                Description = "Standard configuration for end-port regenerators",
                RegeneratorType = RegeneratorType.EndPort,
                IsActive = true,
                CreatedAt = DateTime.UtcNow
            },

            new ConfigurationTemplate
            {
                Id = Guid.NewGuid(),
                Name = "High-Temperature Crown Regenerator",
                Description = "Template for high-temperature crown regenerators",
                RegeneratorType = RegeneratorType.Crown,
                IsActive = true,
                CreatedAt = DateTime.UtcNow
            },

            new ConfigurationTemplate
            {
                Id = Guid.NewGuid(),
                Name = "Side-Port Regenerator",
                Description = "Template for side-port regenerators",
                RegeneratorType = RegeneratorType.SidePort,
                IsActive = true,
                CreatedAt = DateTime.UtcNow
            }
        };

        await _context.ConfigurationTemplates.AddRangeAsync(templates);
        _logger.LogInformation($"Seeded {templates.Count} configuration templates");
    }
}
