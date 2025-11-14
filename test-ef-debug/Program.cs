using Microsoft.EntityFrameworkCore;
using Fro.Infrastructure.Data;
using System;

Console.WriteLine("=== EF Core Property Mapping Diagnostic Tool ===\n");

try
{
    Console.WriteLine("[1] Creating DbContextOptionsBuilder...");
    var optionsBuilder = new DbContextOptionsBuilder<ApplicationDbContext>();
    var serverVersion = new MySqlServerVersion(new Version(8, 0, 33));

    optionsBuilder.UseMySql(
        "Server=localhost;Port=3306;Database=fro_db;User=fro_user;Password=fro_password;",
        serverVersion,
        mysqlOptions =>
        {
            mysqlOptions.EnableRetryOnFailure(
                maxRetryCount: 3,
                maxRetryDelay: TimeSpan.FromSeconds(5),
                errorNumbersToAdd: null);
        });

    Console.WriteLine("[2] Creating ApplicationDbContext...");
    using var context = new ApplicationDbContext(optionsBuilder.Options);

    Console.WriteLine("[3] Getting model from context...");
    var model = context.Model;

    Console.WriteLine("[4] Iterating through entities and properties...\n");

    foreach (var entityType in model.GetEntityTypes())
    {
        Console.WriteLine($"\n╔══════════════════════════════════════════════════════════════");
        Console.WriteLine($"║ Entity: {entityType.Name}");
        Console.WriteLine($"╚══════════════════════════════════════════════════════════════");

        foreach (var property in entityType.GetProperties())
        {
            try
            {
                Console.Write($"  → {property.Name,-30} ({property.ClrType.Name,-20})");

                // This is where the NullReferenceException should occur
                var mapping = property.FindTypeMapping();

                if (mapping != null)
                {
                    Console.WriteLine($" ✓ {mapping.StoreType}");
                }
                else
                {
                    Console.WriteLine($" ⚠ NO MAPPING FOUND!");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($" ✗ ERROR!");
                Console.WriteLine($"\n╔══════════════════════════════════════════════════════════════");
                Console.WriteLine($"║ 🔴 FOUND THE PROBLEM!");
                Console.WriteLine($"╠══════════════════════════════════════════════════════════════");
                Console.WriteLine($"║ Entity:   {entityType.Name}");
                Console.WriteLine($"║ Property: {property.Name}");
                Console.WriteLine($"║ CLR Type: {property.ClrType.FullName}");
                Console.WriteLine($"╠══════════════════════════════════════════════════════════════");
                Console.WriteLine($"║ Exception: {ex.GetType().FullName}");
                Console.WriteLine($"║ Message:   {ex.Message}");
                Console.WriteLine($"╠══════════════════════════════════════════════════════════════");
                Console.WriteLine($"║ Stack Trace:");
                Console.WriteLine($"╚══════════════════════════════════════════════════════════════");
                Console.WriteLine(ex.StackTrace);
                Console.WriteLine();

                // Stop after finding the first error
                return;
            }
        }
    }

    Console.WriteLine("\n✓ All properties checked successfully - no errors found!");
}
catch (Exception ex)
{
    Console.WriteLine($"\n✗ Fatal error during diagnostic:");
    Console.WriteLine($"   Type: {ex.GetType().FullName}");
    Console.WriteLine($"   Message: {ex.Message}");
    Console.WriteLine($"\n   Stack trace:");
    Console.WriteLine(ex.StackTrace);
}
