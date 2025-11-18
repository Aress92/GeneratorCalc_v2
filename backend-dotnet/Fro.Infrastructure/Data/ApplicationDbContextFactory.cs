using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Design;

namespace Fro.Infrastructure.Data;

/// <summary>
/// Factory for creating ApplicationDbContext instances at design time (for migrations).
/// </summary>
public class ApplicationDbContextFactory : IDesignTimeDbContextFactory<ApplicationDbContext>
{
    public ApplicationDbContext CreateDbContext(string[] args)
    {
        // Set environment variable to indicate we're in design-time mode
        Environment.SetEnvironmentVariable("EF_DESIGN_TIME", "true");

        // Use hardcoded connection string for migrations (simplest approach)
        var connectionString = "Server=localhost;Port=3306;Database=fro_db;User=fro_user;Password=fro_password;";

        var optionsBuilder = new DbContextOptionsBuilder<ApplicationDbContext>();
        var serverVersion = new MySqlServerVersion(new Version(8, 0, 33));

        optionsBuilder.UseMySql(
            connectionString,
            serverVersion,
            mysqlOptions =>
            {
                // Specify the assembly containing the migrations
                mysqlOptions.MigrationsAssembly("Fro.Infrastructure");
            });

        return new ApplicationDbContext(optionsBuilder.Options);
    }
}
