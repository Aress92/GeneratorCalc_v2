using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Design;

namespace Fro.Infrastructure.Data;

/// <summary>
/// Factory for creating ApplicationDbContext instances at design time (for migrations).
/// Uses SQLite for simplicity - no server required!
/// </summary>
public class ApplicationDbContextFactory : IDesignTimeDbContextFactory<ApplicationDbContext>
{
    public ApplicationDbContext CreateDbContext(string[] args)
    {
        var optionsBuilder = new DbContextOptionsBuilder<ApplicationDbContext>();

        // Use SQLite for development/migrations - simple file-based database
        // File will be created in the API project directory
        var dbPath = Path.Combine("..", "Fro.Api", "fro_dev.db");
        optionsBuilder.UseSqlite($"Data Source={dbPath}");

        return new ApplicationDbContext(optionsBuilder.Options);
    }
}
