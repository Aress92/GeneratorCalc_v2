using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi.Models;
using System.Text;
using Hangfire;
using Hangfire.Redis.StackExchange;
using StackExchange.Redis;
using Fro.Infrastructure.Data;
using Fro.Infrastructure;
using Fro.Application;
using Fro.Api.Middleware;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container
var configuration = builder.Configuration;

// Configure MySQL with Entity Framework Core
var connectionString = configuration.GetConnectionString("DefaultConnection");
builder.Services.AddDbContext<ApplicationDbContext>(options =>
{
    // Use explicit server version instead of AutoDetect to avoid connection during startup
    var serverVersion = new MySqlServerVersion(new Version(8, 0, 33));
    options.UseMySql(
        connectionString,
        serverVersion,
        mysqlOptions =>
        {
            mysqlOptions.EnableRetryOnFailure(
                maxRetryCount: 3,
                maxRetryDelay: TimeSpan.FromSeconds(5),
                errorNumbersToAdd: null);
        });
});

// Register Infrastructure services (Repositories)
builder.Services.AddInfrastructure();

// Register Application services (Business logic)
builder.Services.AddApplication();

// Configure Redis and Hangfire (optional - will be skipped if Redis is not available)
try
{
    var redisConnectionString = configuration.GetConnectionString("Redis");
    var redis = ConnectionMultiplexer.Connect(redisConnectionString!);
    builder.Services.AddSingleton<IConnectionMultiplexer>(redis);

    Console.WriteLine("✓ Connected to Redis");

    // Configure Hangfire with Redis storage
    builder.Services.AddHangfire(config =>
    {
        config.UseRedisStorage(redis, new Hangfire.Redis.StackExchange.RedisStorageOptions
        {
            Prefix = "hangfire:",
            InvisibilityTimeout = TimeSpan.FromMinutes(30)
        });
    });

    builder.Services.AddHangfireServer(options =>
    {
        options.WorkerCount = configuration.GetValue<int>("Hangfire:WorkerCount", 4);
        options.ServerName = $"FRO-Worker-{Environment.MachineName}";
    });

    Console.WriteLine("✓ Hangfire configured with Redis storage");
}
catch (Exception ex)
{
    Console.WriteLine($"⚠ Warning: Could not connect to Redis. Hangfire will not be available.");
    Console.WriteLine($"  Error: {ex.Message}");
    Console.WriteLine($"  API will start without background job support.");
}

// Configure JWT Authentication
var jwtSecret = configuration["JwtSettings:Secret"];
var jwtIssuer = configuration["JwtSettings:Issuer"];
var jwtAudience = configuration["JwtSettings:Audience"];

builder.Services.AddAuthentication(options =>
{
    options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
})
.AddJwtBearer(options =>
{
    options.TokenValidationParameters = new TokenValidationParameters
    {
        ValidateIssuer = true,
        ValidateAudience = true,
        ValidateLifetime = true,
        ValidateIssuerSigningKey = true,
        ValidIssuer = jwtIssuer,
        ValidAudience = jwtAudience,
        IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtSecret!)),
        ClockSkew = TimeSpan.Zero
    };
});

builder.Services.AddAuthorization();

// Configure CORS
var allowedOrigins = configuration.GetSection("Cors:AllowedOrigins").Get<string[]>() ?? Array.Empty<string>();
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.WithOrigins(allowedOrigins)
              .AllowAnyMethod()
              .AllowAnyHeader()
              .AllowCredentials();
    });
});

// Configure Swagger/OpenAPI
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "Forglass Regenerator Optimizer API",
        Version = "v1",
        Description = "API for optimizing glass furnace regenerators to reduce fuel consumption and CO2 emissions.",
        Contact = new OpenApiContact
        {
            Name = "Forglass",
            Url = new Uri("https://forglass.com")
        }
    });

    // Add JWT authentication to Swagger
    options.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Description = "JWT Authorization header using the Bearer scheme. Enter 'Bearer' [space] and then your token.",
        Name = "Authorization",
        In = ParameterLocation.Header,
        Type = SecuritySchemeType.ApiKey,
        Scheme = "Bearer"
    });

    options.AddSecurityRequirement(new OpenApiSecurityRequirement
    {
        {
            new OpenApiSecurityScheme
            {
                Reference = new OpenApiReference
                {
                    Type = ReferenceType.SecurityScheme,
                    Id = "Bearer"
                }
            },
            Array.Empty<string>()
        }
    });
});

// Add controllers
builder.Services.AddControllers();

var app = builder.Build();

// Configure the HTTP request pipeline

// Add global exception handler (must be first in pipeline)
app.UseGlobalExceptionHandler();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(options =>
    {
        options.SwaggerEndpoint("/swagger/v1/swagger.json", "FRO API v1");
        options.RoutePrefix = "api/docs";
    });
}

// Enable CORS
app.UseCors();

// Enable authentication and authorization
app.UseAuthentication();
app.UseAuthorization();

// Enable Hangfire Dashboard (only if Hangfire was configured)
if (app.Services.GetService<IConnectionMultiplexer>() != null)
{
    var dashboardPath = configuration["Hangfire:DashboardPath"] ?? "/hangfire";
    var enableAuth = configuration.GetValue<bool>("Hangfire:EnableDashboardAuthorization", true);

    if (enableAuth)
    {
        app.MapHangfireDashboard(dashboardPath);
    }
    else
    {
        // Development mode - no authorization
        app.MapHangfireDashboard(dashboardPath, new DashboardOptions
        {
            Authorization = Array.Empty<Hangfire.Dashboard.IDashboardAuthorizationFilter>()
        });
    }
    Console.WriteLine($"✓ Hangfire Dashboard available at {dashboardPath}");
}
else
{
    Console.WriteLine("⚠ Hangfire Dashboard is not available (Redis not connected)");
}

// Map controllers
app.MapControllers();

// Health check endpoint
app.MapGet("/health", () => Results.Ok(new
{
    status = "healthy",
    timestamp = DateTime.UtcNow,
    version = "1.0.0"
}))
.WithName("HealthCheck")
.WithOpenApi();

// Apply database migrations on startup (development only)
if (app.Environment.IsDevelopment())
{
    try
    {
        using var scope = app.Services.CreateScope();
        var dbContext = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();

        // Check if database connection is available
        if (dbContext.Database.CanConnect())
        {
            Console.WriteLine("✓ Connected to database");

            // Apply pending migrations if any exist
            var pendingMigrations = dbContext.Database.GetPendingMigrations();
            if (pendingMigrations.Any())
            {
                Console.WriteLine($"⚠ Applying {pendingMigrations.Count()} pending migration(s)...");
                dbContext.Database.Migrate();
                Console.WriteLine("✓ Migrations applied successfully");
            }
            else
            {
                Console.WriteLine("✓ Database is up to date (no pending migrations)");
            }
        }
        else
        {
            Console.WriteLine("⚠ Warning: Could not connect to database");
            Console.WriteLine("  API will start but database operations will fail until connection is restored");
        }
    }
    catch (Exception ex)
    {
        Console.WriteLine($"⚠ Warning: Database migration failed: {ex.Message}");
        Console.WriteLine("  API will start but may not function correctly");
    }
}

app.Run();
