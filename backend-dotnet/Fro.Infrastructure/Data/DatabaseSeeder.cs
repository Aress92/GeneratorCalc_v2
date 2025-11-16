using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using Fro.Domain.Entities;
using Fro.Domain.Enums;
using Fro.Application.Interfaces.Security;
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

            // Seed materials (optional - development only)
            // await SeedMaterialsAsync();

            // Seed configuration templates (optional)
            // await SeedConfigurationTemplatesAsync();

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
    /// Seed materials library (optional - development/testing).
    /// </summary>
    private async Task SeedMaterialsAsync()
    {
        if (await _context.Materials.AnyAsync())
        {
            _logger.LogInformation("Materials already exist, skipping material seeding");
            return;
        }

        _logger.LogInformation("Seeding materials...");

        var materials = new List<Material>
        {
            new Material
            {
                Id = Guid.NewGuid(),
                Name = "Silica Brick Grade A",
                Description = "High-quality silica brick for regenerator crowns",
                Manufacturer = "Forglass Materials",
                MaterialCode = "SIL-A-001",
                MaterialType = "refractory",
                Category = "high_temperature",
                Application = "crown",
                Density = 2300,
                ThermalConductivity = 2.5,
                SpecificHeat = 950,
                MaxTemperature = 1650,
                MinTemperature = 200,
                Properties = "{}",
                IsActive = true,
                IsStandard = true,
                CreatedAt = DateTime.UtcNow,
                UpdatedAt = DateTime.UtcNow
            },

            new Material
            {
                Id = Guid.NewGuid(),
                Name = "Mullite Checker Brick",
                Description = "Standard mullite checker brick",
                Manufacturer = "Forglass Materials",
                MaterialCode = "MUL-C-001",
                MaterialType = "checker",
                Category = "medium_temperature",
                Application = "checker_packing",
                Density = 2100,
                ThermalConductivity = 2.0,
                SpecificHeat = 900,
                MaxTemperature = 1500,
                MinTemperature = 200,
                Properties = "{}",
                IsActive = true,
                IsStandard = true,
                CreatedAt = DateTime.UtcNow,
                UpdatedAt = DateTime.UtcNow
            },

            new Material
            {
                Id = Guid.NewGuid(),
                Name = "Ceramic Fiber Insulation",
                Description = "Lightweight ceramic fiber for insulation",
                Manufacturer = "Forglass Materials",
                MaterialCode = "INS-CF-001",
                MaterialType = "insulation",
                Category = "insulation",
                Application = "wall_insulation",
                Density = 128,
                ThermalConductivity = 0.12,
                SpecificHeat = 1000,
                MaxTemperature = 1260,
                MinTemperature = 0,
                Properties = "{}",
                IsActive = true,
                IsStandard = true,
                CreatedAt = DateTime.UtcNow,
                UpdatedAt = DateTime.UtcNow
            }
        };

        await _context.Materials.AddRangeAsync(materials);
        _logger.LogInformation($"Seeded {materials.Count} materials");
    }

    /// <summary>
    /// Seed configuration templates (optional).
    /// </summary>
    private async Task SeedConfigurationTemplatesAsync()
    {
        if (await _context.ConfigurationTemplates.AnyAsync())
        {
            _logger.LogInformation("Templates already exist, skipping template seeding");
            return;
        }

        _logger.LogInformation("Seeding configuration templates...");

        var adminUser = await _context.Users.FirstOrDefaultAsync(u => u.Role == UserRole.ADMIN);

        if (adminUser == null)
        {
            _logger.LogWarning("Admin user not found, skipping template seeding");
            return;
        }

        var templates = new List<ConfigurationTemplate>
        {
            new ConfigurationTemplate
            {
                Id = Guid.NewGuid(),
                Name = "Standard End-Port Regenerator",
                Description = "Standard configuration for end-port regenerators",
                RegeneratorType = RegeneratorType.EndPort,
                Category = "standard",
                DefaultGeometryConfig = @"{
                    ""length"": 10.0,
                    ""width"": 8.0,
                    ""height"": 12.0,
                    ""checkerHeight"": 0.5,
                    ""checkerSpacing"": 0.1
                }",
                DefaultThermalConfig = @"{
                    ""gasTempInlet"": 1600,
                    ""gasTempOutlet"": 600,
                    ""operatingTemperature"": 1450
                }",
                DefaultFlowConfig = @"{
                    ""massFlowRate"": 50,
                    ""cycleTime"": 1200
                }",
                UsageCount = 0,
                IsActive = true,
                IsPublic = true,
                CreatedByUserId = adminUser.Id,
                CreatedAt = DateTime.UtcNow,
                UpdatedAt = DateTime.UtcNow
            },

            new ConfigurationTemplate
            {
                Id = Guid.NewGuid(),
                Name = "High-Temperature Crown Regenerator",
                Description = "Template for high-temperature crown regenerators",
                RegeneratorType = RegeneratorType.Crown,
                Category = "high_temperature",
                DefaultGeometryConfig = @"{
                    ""length"": 12.0,
                    ""width"": 10.0,
                    ""height"": 15.0,
                    ""checkerHeight"": 0.6,
                    ""checkerSpacing"": 0.12
                }",
                DefaultThermalConfig = @"{
                    ""gasTempInlet"": 1700,
                    ""gasTempOutlet"": 700,
                    ""operatingTemperature"": 1550
                }",
                DefaultFlowConfig = @"{
                    ""massFlowRate"": 60,
                    ""cycleTime"": 1800
                }",
                UsageCount = 0,
                IsActive = true,
                IsPublic = true,
                CreatedByUserId = adminUser.Id,
                CreatedAt = DateTime.UtcNow,
                UpdatedAt = DateTime.UtcNow
            }
        };

        await _context.ConfigurationTemplates.AddRangeAsync(templates);
        _logger.LogInformation($"Seeded {templates.Count} configuration templates");
    }
}
