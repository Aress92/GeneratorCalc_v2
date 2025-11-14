using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Design;
using Microsoft.Extensions.Configuration;

namespace Fro.Infrastructure.Data;

/// <summary>
/// Factory for creating ApplicationDbContext instances at design time (for migrations).
/// </summary>
public class ApplicationDbContextFactory : IDesignTimeDbContextFactory<ApplicationDbContext>
{
    public ApplicationDbContext CreateDbContext(string[] args)
    {
        Console.WriteLine($"[Factory] CreateDbContext called");
        Console.WriteLine($"[Factory] Current directory: {Directory.GetCurrentDirectory()}");
        Console.WriteLine($"[Factory] Args: {string.Join(", ", args)}");

        // Try to find appsettings.json in multiple locations
        string? basePath = null;
        var currentDir = Directory.GetCurrentDirectory();

        // Try ../Fro.Api (when running from Infrastructure)
        var apiPath1 = Path.Combine(currentDir, "..", "Fro.Api");
        Console.WriteLine($"[Factory] Trying path: {apiPath1}");
        if (Directory.Exists(apiPath1))
        {
            basePath = apiPath1;
            Console.WriteLine($"[Factory] Found Fro.Api at: {basePath}");
        }
        // Try ../../Fro.Api (when running from Infrastructure/bin/Debug)
        else
        {
            var apiPath2 = Path.Combine(currentDir, "..", "..", "Fro.Api");
            Console.WriteLine($"[Factory] Trying path: {apiPath2}");
            if (Directory.Exists(apiPath2))
            {
                basePath = apiPath2;
                Console.WriteLine($"[Factory] Found Fro.Api at: {basePath}");
            }
        }

        // Build configuration (or use default connection string if no config found)
        string? connectionString = null;

        if (basePath != null)
        {
            try
            {
                var configuration = new ConfigurationBuilder()
                    .SetBasePath(basePath)
                    .AddJsonFile("appsettings.json", optional: true)
                    .AddJsonFile("appsettings.Development.json", optional: true)
                    .Build();

                connectionString = configuration.GetConnectionString("DefaultConnection");
            }
            catch
            {
                // If configuration fails, use default connection string
                connectionString = null;
            }
        }

        // Fallback to default connection string if not found in config
        connectionString ??= "Server=localhost;Port=3306;Database=fro_db;User=fro_user;Password=fro_password;";
        Console.WriteLine($"[Factory] Using connection string: {connectionString?.Substring(0, Math.Min(50, connectionString.Length))}...");

        // Configure DbContext options
        Console.WriteLine($"[Factory] Creating DbContextOptionsBuilder...");
        var optionsBuilder = new DbContextOptionsBuilder<ApplicationDbContext>();
        var serverVersion = new MySqlServerVersion(new Version(8, 0, 33));
        Console.WriteLine($"[Factory] MySQL server version: {serverVersion}");

        Console.WriteLine($"[Factory] Configuring UseMySql...");
        optionsBuilder.UseMySql(
            connectionString,
            serverVersion,
            mysqlOptions =>
            {
                mysqlOptions.EnableRetryOnFailure(
                    maxRetryCount: 3,
                    maxRetryDelay: TimeSpan.FromSeconds(5),
                    errorNumbersToAdd: null);
            });

        Console.WriteLine($"[Factory] Creating ApplicationDbContext...");
        var context = new ApplicationDbContext(optionsBuilder.Options);
        Console.WriteLine($"[Factory] Context created successfully!");
        return context;
    }
}
