using System;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Infrastructure;
using Microsoft.EntityFrameworkCore.Metadata;
using Fro.Infrastructure.Data;
using Fro.Domain.Entities;

class TestDbContext
{
    static void Main()
    {
        Console.WriteLine("=== Testing DbContext Creation ===\n");

        try
        {
            Console.WriteLine("Step 1: Creating DbContextOptionsBuilder...");
            var optionsBuilder = new DbContextOptionsBuilder<ApplicationDbContext>();
            var serverVersion = new MySqlServerVersion(new Version(8, 0, 33));

            optionsBuilder.UseMySql(
                "Server=localhost;Port=3306;Database=fro_db;User=fro_user;Password=fro_password;",
                serverVersion);

            Console.WriteLine("✓ Options configured\n");

            Console.WriteLine("Step 2: Creating ApplicationDbContext...");
            using var context = new ApplicationDbContext(optionsBuilder.Options);
            Console.WriteLine("✓ Context created\n");

            Console.WriteLine("Step 3: Getting model (this triggers OnModelCreating)...");
            var model = context.Model;
            Console.WriteLine("✓ Model retrieved\n");

            Console.WriteLine("Step 4: Iterating through entities...");
            foreach (var entityType in model.GetEntityTypes())
            {
                Console.WriteLine($"\nEntity: {entityType.Name}");

                foreach (var property in entityType.GetProperties())
                {
                    try
                    {
                        Console.Write($"  - {property.Name} ({property.ClrType.Name})");

                        // Try to get the type mapping - this is where the error occurs
                        var mapping = property.FindTypeMapping();

                        if (mapping != null)
                        {
                            Console.WriteLine($" -> {mapping.StoreType} ✓");
                        }
                        else
                        {
                            Console.WriteLine(" -> NO MAPPING ✗");
                        }
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($" -> ERROR: {ex.GetType().Name}: {ex.Message}");
                        Console.WriteLine($"\n>>> FOUND THE PROBLEM! Property: {property.Name}");
                        Console.WriteLine($"    Type: {property.ClrType.FullName}");
                        Console.WriteLine($"    Column Type: {property.GetColumnType()}");
                        Console.WriteLine($"\nFull error:");
                        Console.WriteLine(ex.ToString());
                        return;
                    }
                }
            }

            Console.WriteLine("\n✅ All properties mapped successfully!");

        }
        catch (Exception ex)
        {
            Console.WriteLine($"\n❌ Error: {ex.GetType().Name}");
            Console.WriteLine($"Message: {ex.Message}");
            Console.WriteLine($"\nStack trace:");
            Console.WriteLine(ex.ToString());
        }
    }
}
