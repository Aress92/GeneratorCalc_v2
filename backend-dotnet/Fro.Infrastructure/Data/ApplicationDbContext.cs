using Microsoft.EntityFrameworkCore;
using Fro.Domain.Entities;
using Fro.Domain.Enums;
using System.Text.Json;

namespace Fro.Infrastructure.Data;

/// <summary>
/// Main application database context using Entity Framework Core.
/// </summary>
public class ApplicationDbContext : DbContext
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
        : base(options)
    {
    }

    // DbSets
    public DbSet<User> Users => Set<User>();
    public DbSet<RegeneratorConfiguration> RegeneratorConfigurations => Set<RegeneratorConfiguration>();
    public DbSet<ConfigurationTemplate> ConfigurationTemplates => Set<ConfigurationTemplate>();
    public DbSet<OptimizationScenario> OptimizationScenarios => Set<OptimizationScenario>();
    public DbSet<OptimizationJob> OptimizationJobs => Set<OptimizationJob>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Configure User entity
        modelBuilder.Entity<User>(entity =>
        {
            entity.ToTable("users");

            entity.HasKey(e => e.Id);

            entity.Property(e => e.Id)
                .HasColumnType("CHAR(36)")
                .HasConversion(
                    v => v.ToString(),
                    v => Guid.Parse(v));

            entity.Property(e => e.Username)
                .IsRequired()
                .HasMaxLength(50)
                .HasColumnName("username");

            entity.Property(e => e.Email)
                .IsRequired()
                .HasMaxLength(255)
                .HasColumnName("email");

            entity.Property(e => e.FullName)
                .HasMaxLength(200)
                .HasColumnName("full_name");

            entity.Property(e => e.PasswordHash)
                .IsRequired()
                .HasColumnType("TEXT")
                .HasColumnName("password_hash");

            entity.Property(e => e.Role)
                .IsRequired()
                .HasMaxLength(20)
                .HasConversion<string>()
                .HasColumnName("role");

            entity.Property(e => e.IsActive)
                .HasColumnName("is_active");

            entity.Property(e => e.IsVerified)
                .HasColumnName("is_verified");

            entity.Property(e => e.CreatedAt)
                .HasColumnType("DATETIME")
                .HasColumnName("created_at");

            entity.Property(e => e.UpdatedAt)
                .HasColumnType("DATETIME")
                .HasColumnName("updated_at");

            entity.Property(e => e.LastLogin)
                .HasColumnType("DATETIME")
                .HasColumnName("last_login");

            entity.Property(e => e.ResetToken)
                .HasMaxLength(255)
                .HasColumnName("reset_token");

            entity.Property(e => e.ResetTokenExpires)
                .HasColumnType("DATETIME")
                .HasColumnName("reset_token_expires");

            // Indexes
            entity.HasIndex(e => e.Username).IsUnique();
            entity.HasIndex(e => e.Email).IsUnique();
            entity.HasIndex(e => e.Role);

            // Ignore computed properties
            entity.Ignore(e => e.IsAdmin);
            entity.Ignore(e => e.IsEngineer);
            entity.Ignore(e => e.CanCreateScenarios);
            entity.Ignore(e => e.CanManageUsers);
            entity.Ignore(e => e.CanViewAllScenarios);
        });

        // Configure RegeneratorConfiguration entity
        modelBuilder.Entity<RegeneratorConfiguration>(entity =>
        {
            entity.ToTable("regenerator_configurations");

            entity.HasKey(e => e.Id);

            entity.Property(e => e.Id)
                .HasColumnType("CHAR(36)")
                .HasConversion(
                    v => v.ToString(),
                    v => Guid.Parse(v));

            entity.Property(e => e.UserId)
                .HasColumnType("CHAR(36)")
                .HasConversion(
                    v => v.ToString(),
                    v => Guid.Parse(v))
                .HasColumnName("user_id");

            entity.Property(e => e.Name)
                .IsRequired()
                .HasMaxLength(255)
                .HasColumnName("name");

            entity.Property(e => e.Description)
                .HasColumnType("TEXT")
                .HasColumnName("description");

            entity.Property(e => e.RegeneratorType)
                .IsRequired()
                .HasMaxLength(50)
                .HasConversion<string>()
                .HasColumnName("regenerator_type");

            entity.Property(e => e.ConfigurationVersion)
                .HasMaxLength(20)
                .HasColumnName("configuration_version");

            entity.Property(e => e.Status)
                .IsRequired()
                .HasMaxLength(20)
                .HasColumnName("status");

            entity.Property(e => e.CurrentStep)
                .HasColumnName("current_step");

            entity.Property(e => e.TotalSteps)
                .HasColumnName("total_steps");

            entity.Property(e => e.CompletedSteps)
                .HasColumnType("JSON")
                .HasConversion(
                    v => JsonSerializer.Serialize(v, (JsonSerializerOptions)null!),
                    v => JsonSerializer.Deserialize<List<int>>(v, (JsonSerializerOptions)null!) ?? new List<int>())
                .HasColumnName("completed_steps");

            // JSON configuration columns
            entity.Property(e => e.GeometryConfig)
                .HasColumnType("JSON")
                .HasColumnName("geometry_config");

            entity.Property(e => e.MaterialsConfig)
                .HasColumnType("JSON")
                .HasColumnName("materials_config");

            entity.Property(e => e.ThermalConfig)
                .HasColumnType("JSON")
                .HasColumnName("thermal_config");

            entity.Property(e => e.FlowConfig)
                .HasColumnType("JSON")
                .HasColumnName("flow_config");

            entity.Property(e => e.ConstraintsConfig)
                .HasColumnType("JSON")
                .HasColumnName("constraints_config");

            entity.Property(e => e.VisualizationConfig)
                .HasColumnType("JSON")
                .HasColumnName("visualization_config");

            entity.Property(e => e.ModelGeometry)
                .HasColumnType("JSON")
                .HasColumnName("model_geometry");

            entity.Property(e => e.ModelMaterials)
                .HasColumnType("JSON")
                .HasColumnName("model_materials");

            entity.Property(e => e.IsValidated)
                .HasColumnName("is_validated");

            entity.Property(e => e.ValidationScore)
                .HasColumnName("validation_score");

            entity.Property(e => e.ValidationErrors)
                .HasColumnType("JSON")
                .HasConversion(
                    v => JsonSerializer.Serialize(v, (JsonSerializerOptions)null!),
                    v => JsonSerializer.Deserialize<List<string>>(v, (JsonSerializerOptions)null!) ?? new List<string>())
                .HasColumnName("validation_errors");

            entity.Property(e => e.ValidationWarnings)
                .HasColumnType("JSON")
                .HasConversion(
                    v => JsonSerializer.Serialize(v, (JsonSerializerOptions)null!),
                    v => JsonSerializer.Deserialize<List<string>>(v, (JsonSerializerOptions)null!) ?? new List<string>())
                .HasColumnName("validation_warnings");

            entity.Property(e => e.BasedOnTemplateId)
                .HasColumnType("CHAR(36)")
                .HasConversion(
                    v => v.HasValue ? v.Value.ToString() : null,
                    v => v != null ? Guid.Parse(v) : (Guid?)null)
                .HasColumnName("based_on_template_id");

            entity.Property(e => e.IsTemplate)
                .HasColumnName("is_template");

            entity.Property(e => e.CreatedAt)
                .HasColumnType("DATETIME")
                .HasColumnName("created_at");

            entity.Property(e => e.UpdatedAt)
                .HasColumnType("DATETIME")
                .HasColumnName("updated_at");

            entity.Property(e => e.CompletedAt)
                .HasColumnType("DATETIME")
                .HasColumnName("completed_at");

            // Relationships
            entity.HasOne(e => e.User)
                .WithMany(u => u.Configurations)
                .HasForeignKey(e => e.UserId)
                .OnDelete(DeleteBehavior.Cascade);

            entity.HasOne(e => e.Template)
                .WithMany(t => t.Configurations)
                .HasForeignKey(e => e.BasedOnTemplateId)
                .OnDelete(DeleteBehavior.SetNull);
        });

        // Configure OptimizationScenario entity
        modelBuilder.Entity<OptimizationScenario>(entity =>
        {
            entity.ToTable("optimization_scenarios");

            entity.HasKey(e => e.Id);

            entity.Property(e => e.Id)
                .HasColumnType("CHAR(36)")
                .HasConversion(
                    v => v.ToString(),
                    v => Guid.Parse(v));

            entity.Property(e => e.UserId)
                .HasColumnType("CHAR(36)")
                .HasConversion(
                    v => v.ToString(),
                    v => Guid.Parse(v))
                .HasColumnName("user_id");

            entity.Property(e => e.BaseConfigurationId)
                .HasColumnType("CHAR(36)")
                .HasConversion(
                    v => v.ToString(),
                    v => Guid.Parse(v))
                .HasColumnName("base_configuration_id");

            entity.Property(e => e.Name)
                .IsRequired()
                .HasMaxLength(255)
                .HasColumnName("name");

            entity.Property(e => e.Algorithm)
                .IsRequired()
                .HasMaxLength(50)
                .HasConversion<string>()
                .HasColumnName("algorithm");

            entity.Property(e => e.OptimizationConfig)
                .IsRequired()
                .HasColumnType("JSON")
                .HasColumnName("optimization_config");

            entity.Property(e => e.DesignVariables)
                .IsRequired()
                .HasColumnType("JSON")
                .HasColumnName("design_variables");

            entity.Property(e => e.MaxIterations)
                .HasColumnName("max_iterations");

            entity.Property(e => e.Tolerance)
                .HasColumnName("tolerance");

            entity.Property(e => e.CreatedAt)
                .HasColumnType("DATETIME")
                .HasColumnName("created_at");

            entity.Property(e => e.UpdatedAt)
                .HasColumnType("DATETIME")
                .HasColumnName("updated_at");

            // Relationships
            entity.HasOne(e => e.User)
                .WithMany(u => u.OptimizationScenarios)
                .HasForeignKey(e => e.UserId)
                .OnDelete(DeleteBehavior.Cascade);

            entity.HasOne(e => e.BaseConfiguration)
                .WithMany(c => c.OptimizationScenarios)
                .HasForeignKey(e => e.BaseConfigurationId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // Configure OptimizationJob entity
        modelBuilder.Entity<OptimizationJob>(entity =>
        {
            entity.ToTable("optimization_jobs");

            entity.HasKey(e => e.Id);

            entity.Property(e => e.Id)
                .HasColumnType("CHAR(36)")
                .HasConversion(
                    v => v.ToString(),
                    v => Guid.Parse(v));

            entity.Property(e => e.ScenarioId)
                .HasColumnType("CHAR(36)")
                .HasConversion(
                    v => v.ToString(),
                    v => Guid.Parse(v))
                .HasColumnName("scenario_id");

            entity.Property(e => e.CeleryTaskId)
                .HasMaxLength(255)
                .HasColumnName("celery_task_id");

            entity.Property(e => e.Status)
                .IsRequired()
                .HasMaxLength(20)
                .HasConversion<string>()
                .HasColumnName("status");

            entity.Property(e => e.Progress)
                .HasColumnName("progress");

            entity.Property(e => e.CurrentIteration)
                .HasColumnName("current_iteration");

            entity.Property(e => e.BestSolution)
                .HasColumnType("JSON")
                .HasColumnName("best_solution");

            entity.Property(e => e.Results)
                .HasColumnType("JSON")
                .HasColumnName("results");

            entity.Property(e => e.ErrorMessage)
                .HasColumnType("TEXT")
                .HasColumnName("error_message");

            entity.Property(e => e.CreatedAt)
                .HasColumnType("DATETIME")
                .HasColumnName("created_at");

            entity.Property(e => e.StartedAt)
                .HasColumnType("DATETIME")
                .HasColumnName("started_at");

            entity.Property(e => e.CompletedAt)
                .HasColumnType("DATETIME")
                .HasColumnName("completed_at");

            // Relationships
            entity.HasOne(e => e.Scenario)
                .WithMany(s => s.OptimizationJobs)
                .HasForeignKey(e => e.ScenarioId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // Configure ConfigurationTemplate entity
        modelBuilder.Entity<ConfigurationTemplate>(entity =>
        {
            entity.ToTable("configuration_templates");

            entity.HasKey(e => e.Id);

            entity.Property(e => e.Id)
                .HasColumnType("CHAR(36)")
                .HasConversion(
                    v => v.ToString(),
                    v => Guid.Parse(v));

            entity.Property(e => e.Name)
                .IsRequired()
                .HasMaxLength(255)
                .HasColumnName("name");

            entity.Property(e => e.RegeneratorType)
                .IsRequired()
                .HasMaxLength(50)
                .HasConversion<string>()
                .HasColumnName("regenerator_type");

            entity.Property(e => e.IsActive)
                .HasColumnName("is_active");

            entity.Property(e => e.CreatedAt)
                .HasColumnType("DATETIME")
                .HasColumnName("created_at");
        });
    }
}
