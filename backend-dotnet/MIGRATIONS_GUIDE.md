# EF Core Migrations Guide

Complete guide for generating and applying Entity Framework Core migrations to MySQL database.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Step-by-Step Migration Process](#step-by-step-migration-process)
4. [Database Seeding](#database-seeding)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)
7. [Schema Compatibility](#schema-compatibility)

---

## Prerequisites

### 1. Install EF Core Tools

```bash
# Global tool (recommended)
dotnet tool install --global dotnet-ef

# Or update if already installed
dotnet tool update --global dotnet-ef

# Verify installation
dotnet ef --version
# Expected: Entity Framework Core .NET Command-line Tools 8.0.x
```

### 2. Verify MySQL Connection

Ensure MySQL is running and accessible:

```bash
# Test connection
mysql -h localhost -P 3306 -u fro_user -pfro_password -e "SHOW DATABASES;"

# Should show fro_db database (or create it)
mysql -h localhost -P 3306 -u fro_user -pfro_password -e "CREATE DATABASE IF NOT EXISTS fro_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### 3. Verify Project Structure

```bash
cd backend-dotnet

# Check all 4 projects exist
ls -la Fro.Domain/Fro.Domain.csproj
ls -la Fro.Application/Fro.Application.csproj
ls -la Fro.Infrastructure/Fro.Infrastructure.csproj
ls -la Fro.Api/Fro.Api.csproj

# Build solution to verify no errors
dotnet build
# Expected: Build succeeded. 0 Error(s)
```

---

## Quick Start

**5-Minute Migration Setup:**

```bash
cd backend-dotnet

# 1. Generate migration
dotnet ef migrations add InitialCreate \
  --project Fro.Infrastructure \
  --startup-project Fro.Api \
  --output-dir Data/Migrations

# 2. Review generated migration
cat Fro.Infrastructure/Data/Migrations/*_InitialCreate.cs

# 3. Apply migration to MySQL
dotnet ef database update \
  --project Fro.Infrastructure \
  --startup-project Fro.Api

# 4. Verify tables created
mysql -h localhost -P 3306 -u fro_user -pfro_password fro_db -e "SHOW TABLES;"

# 5. Seed database (Option A: SQL script)
mysql -h localhost -P 3306 -u fro_user -pfro_password fro_db < database-seed.sql

# Or 5. Seed database (Option B: Programmatic - requires code change)
# See "Database Seeding" section below
```

**Expected Result:**
```
Build succeeded. 0 Error(s)
Migration '20251114_InitialCreate' applied to database 'fro_db'.
Tables: users, regenerator_configurations, optimization_scenarios, optimization_jobs, materials, configuration_templates, import_jobs, report_generations
```

---

## Step-by-Step Migration Process

### Step 1: Navigate to Solution Directory

```bash
cd /path/to/GeneratorCalc_v2/backend-dotnet
```

### Step 2: Generate Initial Migration

This creates C# code that defines the database schema:

```bash
dotnet ef migrations add InitialCreate \
  --project Fro.Infrastructure \
  --startup-project Fro.Api \
  --output-dir Data/Migrations \
  --context ApplicationDbContext
```

**What This Does:**
- Analyzes all entities in `Fro.Domain/Entities/`
- Generates migration file: `Fro.Infrastructure/Data/Migrations/YYYYMMDDHHMMSS_InitialCreate.cs`
- Creates snapshot: `ApplicationDbContextModelSnapshot.cs`

**Generated Files:**
```
Fro.Infrastructure/Data/Migrations/
├── 20251114120000_InitialCreate.cs          # Migration Up/Down methods
└── ApplicationDbContextModelSnapshot.cs      # Current model state
```

### Step 3: Review Generated Migration

**Open migration file:**
```bash
cat Fro.Infrastructure/Data/Migrations/*_InitialCreate.cs
```

**Expected Structure:**
```csharp
public partial class InitialCreate : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        // Create users table
        migrationBuilder.CreateTable(
            name: "users",
            columns: table => new
            {
                id = table.Column<Guid>(type: "char(36)", nullable: false),
                username = table.Column<string>(type: "varchar(100)", maxLength: 100, nullable: false),
                email = table.Column<string>(type: "varchar(255)", maxLength: 255, nullable: false),
                // ... more columns
            },
            constraints: table =>
            {
                table.PrimaryKey("PK_users", x => x.id);
            });

        // Create indexes
        migrationBuilder.CreateIndex(
            name: "IX_users_username",
            table: "users",
            column: "username",
            unique: true);

        // ... more tables: regenerator_configurations, optimization_scenarios, etc.
    }

    protected override void Down(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.DropTable(name: "users");
        // ... drop other tables
    }
}
```

**Key Points to Verify:**
- ✅ Table names match Python schema (snake_case: `users`, `regenerator_configurations`)
- ✅ Column names match (snake_case: `user_id`, `created_at`)
- ✅ GUIDs stored as `CHAR(36)` (MySQL compatible)
- ✅ Indexes created for foreign keys and unique constraints
- ✅ JSON columns defined as `TEXT` or `JSON` type

### Step 4: Apply Migration to Database

This executes the generated SQL against MySQL:

```bash
dotnet ef database update \
  --project Fro.Infrastructure \
  --startup-project Fro.Api \
  --verbose
```

**What This Does:**
1. Connects to MySQL using connection string from `appsettings.json`
2. Creates `__EFMigrationsHistory` table (if not exists)
3. Checks which migrations have been applied
4. Executes `Up()` method from pending migrations
5. Records migration in history table

**Expected Output:**
```
Build succeeded. 0 Error(s)
Build completed in 3.2 seconds.

Applying migration '20251114120000_InitialCreate'.
Creating table 'users'.
Creating table 'regenerator_configurations'.
Creating table 'optimization_scenarios'.
Creating table 'optimization_jobs'.
Creating table 'materials'.
Creating table 'configuration_templates'.
Creating table 'import_jobs'.
Creating table 'report_generations'.
Creating index 'IX_users_username' on table 'users'.
Creating index 'IX_users_email' on table 'users'.
... (more indexes)

Done. Migration '20251114120000_InitialCreate' applied to database 'fro_db'.
```

### Step 5: Verify Database Schema

**Check tables created:**
```bash
mysql -h localhost -P 3306 -u fro_user -pfro_password fro_db -e "SHOW TABLES;"
```

**Expected Tables:**
```
+----------------------------------+
| Tables_in_fro_db                 |
+----------------------------------+
| __EFMigrationsHistory            |
| configuration_templates          |
| import_jobs                      |
| materials                        |
| optimization_jobs                |
| optimization_scenarios           |
| regenerator_configurations       |
| report_generations               |
| users                            |
+----------------------------------+
```

**Check users table structure:**
```bash
mysql -h localhost -P 3306 -u fro_user -pfro_password fro_db -e "DESCRIBE users;"
```

**Expected Structure:**
```
+----------------+--------------+------+-----+---------+-------+
| Field          | Type         | Null | Key | Default | Extra |
+----------------+--------------+------+-----+---------+-------+
| id             | char(36)     | NO   | PRI | NULL    |       |
| username       | varchar(100) | NO   | UNI | NULL    |       |
| email          | varchar(255) | NO   | UNI | NULL    |       |
| full_name      | varchar(200) | YES  |     | NULL    |       |
| password_hash  | varchar(255) | NO   |     | NULL    |       |
| role           | varchar(20)  | NO   |     | NULL    |       |
| is_active      | tinyint(1)   | NO   |     | 1       |       |
| is_verified    | tinyint(1)   | NO   |     | 0       |       |
| created_at     | datetime(6)  | NO   |     | NULL    |       |
| updated_at     | datetime(6)  | NO   |     | NULL    |       |
+----------------+--------------+------+-----+---------+-------+
```

---

## Database Seeding

Two options for populating initial data:

### Option A: SQL Script (Recommended for First Setup)

**Advantages:**
- No code changes required
- Easy to review and modify
- Can be run multiple times safely

**Execute SQL script:**
```bash
cd backend-dotnet

# Run seeding script
mysql -h localhost -P 3306 -u fro_user -pfro_password fro_db < database-seed.sql

# Expected output shows verification queries
```

**Script Contents:**
- 3 users: admin/admin, engineer/engineer123, viewer/viewer123
- 3 materials: Silica brick, Mullite checker, Ceramic fiber
- 2 templates: Standard End-Port, High-Temperature Crown

**Verify seeding:**
```bash
mysql -h localhost -P 3306 -u fro_user -pfro_password fro_db -e "SELECT username, email, role FROM users;"
```

**Expected Result:**
```
+----------+-----------------------+----------+
| username | email                 | role     |
+----------+-----------------------+----------+
| admin    | admin@forglass.com    | ADMIN    |
| engineer | engineer@forglass.com | ENGINEER |
| viewer   | viewer@forglass.com   | VIEWER   |
+----------+-----------------------+----------+
```

### Option B: Programmatic Seeding (For Development)

**Advantages:**
- Type-safe C# code
- Can use dependency injection
- Automatic BCrypt password hashing

**1. Register DatabaseSeeder in DI:**

Edit `Fro.Infrastructure/DependencyInjection.cs`:

```csharp
public static IServiceCollection AddInfrastructure(this IServiceCollection services, IConfiguration configuration)
{
    // ... existing registrations ...

    // Register DatabaseSeeder
    services.AddScoped<DatabaseSeeder>();

    return services;
}
```

**2. Run seeder on application startup:**

Edit `Fro.Api/Program.cs` (add after `app` is built, before `app.Run()`):

```csharp
// Seed database in development
if (app.Environment.IsDevelopment())
{
    using var scope = app.Services.CreateScope();
    var services = scope.ServiceProvider;

    try
    {
        var seeder = services.GetRequiredService<DatabaseSeeder>();
        await seeder.SeedAsync();
        Console.WriteLine("✅ Database seeding completed successfully.");
    }
    catch (Exception ex)
    {
        var logger = services.GetRequiredService<ILogger<Program>>();
        logger.LogError(ex, "❌ An error occurred while seeding the database.");
    }
}

app.Run();
```

**3. Run application to trigger seeding:**

```bash
cd Fro.Api
dotnet run
```

**Expected Console Output:**
```
✅ Database seeding completed successfully.
[INFO] Seeded 3 users: admin, engineer, viewer
[INFO] Seeded 3 materials
[INFO] Seeded 2 configuration templates
Now listening on: http://localhost:5000
Application started. Press Ctrl+C to shut down.
```

**Seeder Features:**
- Checks if data exists before inserting (idempotent)
- Uses BCrypt for password hashing (compatible with Python backend)
- Creates relationships between users and templates

---

## Verification

### 1. Verify Migration History

```bash
mysql -h localhost -P 3306 -u fro_user -pfro_password fro_db -e "SELECT * FROM __EFMigrationsHistory;"
```

**Expected:**
```
+----------------------------+-----------------+
| MigrationId                | ProductVersion  |
+----------------------------+-----------------+
| 20251114120000_InitialCreate | 8.0.2          |
+----------------------------+-----------------+
```

### 2. Verify Schema Matches Python Backend

**Check Python schema:**
```bash
cd backend
cat migrations/versions/001_initial_migration.py
```

**Compare table structures:**
```bash
# Python: Check Alembic migration
grep -A 20 "op.create_table('users'" backend/migrations/versions/*.py

# .NET: Check EF Core migration
grep -A 20 "CreateTable" backend-dotnet/Fro.Infrastructure/Data/Migrations/*_InitialCreate.cs
```

**Key Compatibility Points:**
- ✅ Both use `CHAR(36)` for UUID/GUID columns
- ✅ Both use `VARCHAR` with same max lengths
- ✅ Both use `DATETIME` (MySQL) for timestamps
- ✅ Both use `TINYINT(1)` for booleans
- ✅ Both use `TEXT` or `JSON` for configuration columns
- ✅ Both create same indexes (username, email unique)

### 3. Test EF Core Queries

Create a test endpoint or run in Program.cs:

```csharp
// Test query in Program.cs (development only)
if (app.Environment.IsDevelopment())
{
    using var scope = app.Services.CreateScope();
    var context = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();

    var userCount = await context.Users.CountAsync();
    Console.WriteLine($"✅ Users in database: {userCount}");

    var adminUser = await context.Users.FirstOrDefaultAsync(u => u.Username == "admin");
    Console.WriteLine($"✅ Admin user found: {adminUser?.Email}");
}
```

### 4. Test Python Backend Compatibility

Start Python backend and verify it can read .NET seeded data:

```bash
cd backend
docker compose up -d backend

# Test login with admin user
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# Expected: JWT token returned
```

---

## Troubleshooting

### Error: "dotnet ef command not found"

**Problem:** EF Core tools not installed globally.

**Solution:**
```bash
dotnet tool install --global dotnet-ef
dotnet tool update --global dotnet-ef

# Add to PATH if needed (Linux/Mac)
export PATH="$PATH:$HOME/.dotnet/tools"
```

### Error: "Unable to create an object of type 'ApplicationDbContext'"

**Problem:** No connection string or invalid connection string.

**Solution:**
```bash
# Check appsettings.json has correct connection string
cat Fro.Api/appsettings.json | grep DefaultConnection

# Test MySQL connection manually
mysql -h localhost -P 3306 -u fro_user -pfro_password -e "SELECT 1;"
```

**Fix appsettings.json:**
```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost;Port=3306;Database=fro_db;User=fro_user;Password=fro_password;"
  }
}
```

### Error: "Authentication to host 'localhost' for user 'fro_user' failed"

**Problem:** MySQL user doesn't exist or has wrong password.

**Solution:**
```bash
# Create MySQL user
mysql -u root -p <<EOF
CREATE USER IF NOT EXISTS 'fro_user'@'localhost' IDENTIFIED BY 'fro_password';
GRANT ALL PRIVILEGES ON fro_db.* TO 'fro_user'@'localhost';
FLUSH PRIVILEGES;
EOF
```

### Error: "Table 'users' already exists"

**Problem:** Migration tries to create tables that already exist (from Python backend).

**Solution A - Start fresh (safe for development):**
```bash
# Drop and recreate database
mysql -u root -p -e "DROP DATABASE IF EXISTS fro_db; CREATE DATABASE fro_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Re-run migration
dotnet ef database update --project Fro.Infrastructure --startup-project Fro.Api
```

**Solution B - Mark migration as applied (if schema matches):**
```bash
# Manually insert migration record
mysql -h localhost -P 3306 -u fro_user -pfro_password fro_db -e "
CREATE TABLE IF NOT EXISTS __EFMigrationsHistory (
    MigrationId varchar(150) NOT NULL PRIMARY KEY,
    ProductVersion varchar(32) NOT NULL
);
INSERT INTO __EFMigrationsHistory (MigrationId, ProductVersion)
VALUES ('20251114120000_InitialCreate', '8.0.2');
"
```

### Error: "Build failed" when running migrations

**Problem:** Compilation errors in code.

**Solution:**
```bash
# Build solution first to see errors
cd backend-dotnet
dotnet build

# Fix any compilation errors
# Then retry migration
dotnet ef migrations add InitialCreate --project Fro.Infrastructure --startup-project Fro.Api
```

### Error: "Cannot insert duplicate key in object 'users'"

**Problem:** Trying to seed data that already exists.

**Solution:**
- SQL script uses `ON DUPLICATE KEY UPDATE` to handle duplicates
- DatabaseSeeder checks `if (await _context.Users.AnyAsync())` before inserting
- Verify seeding code has these safeguards

### Warning: "Pomelo.EntityFrameworkCore.MySql version mismatch"

**Problem:** EF Core version doesn't match Pomelo version.

**Solution:**
```bash
# Check current versions
grep "Microsoft.EntityFrameworkCore" Fro.Infrastructure/Fro.Infrastructure.csproj
grep "Pomelo.EntityFrameworkCore.MySql" Fro.Infrastructure/Fro.Infrastructure.csproj

# Update to matching versions
cd Fro.Infrastructure
dotnet add package Microsoft.EntityFrameworkCore --version 8.0.2
dotnet add package Pomelo.EntityFrameworkCore.MySql --version 8.0.2
```

---

## Schema Compatibility

### Python (SQLAlchemy) vs .NET (EF Core) Mapping

| Python Type | .NET Type | MySQL Type | Notes |
|-------------|-----------|------------|-------|
| `String(36)` for UUID | `Guid` | `CHAR(36)` | ✅ Compatible |
| `String(100)` | `string` (MaxLength: 100) | `VARCHAR(100)` | ✅ Compatible |
| `Text` | `string` | `TEXT` | ✅ Compatible |
| `JSON` | `string` (manual serialize) | `JSON` or `TEXT` | ✅ Compatible |
| `Boolean` | `bool` | `TINYINT(1)` | ✅ Compatible |
| `DateTime` | `DateTime` | `DATETIME(6)` | ✅ Compatible (UTC) |
| `Enum` (String) | `enum` | `VARCHAR(20)` | ✅ Compatible |
| `Integer` | `int` | `INT` | ✅ Compatible |
| `Float` | `double` | `DOUBLE` | ✅ Compatible |

### Key Differences

**1. UUID Storage:**
- Python: `String(36)` stored as string
- .NET: `Guid` type, but mapped to `CHAR(36)` for MySQL
- **Result:** ✅ Compatible - both store as 36-character string

**2. Enum Handling:**
- Python: Stores enum values as strings (e.g., "ADMIN", "ENGINEER")
- .NET: Uses C# enums, but configured to store as strings
- **Result:** ✅ Compatible - both store string values

**3. JSON Columns:**
- Python: Uses `JSON` column type (MySQL 5.7.8+)
- .NET: Uses `string` with manual JSON serialization
- **Result:** ✅ Compatible - can read/write same data

**4. Timestamps:**
- Python: `DateTime(timezone=True)` with `server_default=func.now()`
- .NET: `DateTime` with `.HasDefaultValueSql("CURRENT_TIMESTAMP(6)")`
- **Result:** ✅ Compatible - both use UTC, MySQL stores as DATETIME

**5. Password Hashing:**
- Python: Uses `bcrypt` library (salt rounds: 12)
- .NET: Uses `BCrypt.Net-Next` (salt rounds: 11)
- **Result:** ✅ Compatible - both can verify each other's hashes

### Migration Checklist

Before running migrations, verify:

- [ ] Connection string points to same MySQL database as Python backend
- [ ] MySQL version 8.0+ (for JSON support)
- [ ] Character set: `utf8mb4`, Collation: `utf8mb4_unicode_ci`
- [ ] All entity classes have `[Table("snake_case_name")]` attributes
- [ ] All properties have `[Column("snake_case_name")]` attributes
- [ ] GUIDs mapped to `CHAR(36)` in Fluent API
- [ ] Enums configured to store as strings
- [ ] DateTime properties use UTC timezone
- [ ] BCrypt password hashing configured

---

## Common Commands Reference

### Migration Management

```bash
# List all migrations
dotnet ef migrations list --project Fro.Infrastructure --startup-project Fro.Api

# Generate new migration
dotnet ef migrations add MigrationName --project Fro.Infrastructure --startup-project Fro.Api

# Apply all pending migrations
dotnet ef database update --project Fro.Infrastructure --startup-project Fro.Api

# Apply specific migration
dotnet ef database update MigrationName --project Fro.Infrastructure --startup-project Fro.Api

# Rollback to previous migration
dotnet ef database update PreviousMigrationName --project Fro.Infrastructure --startup-project Fro.Api

# Rollback all migrations
dotnet ef database update 0 --project Fro.Infrastructure --startup-project Fro.Api

# Remove last migration (if not applied)
dotnet ef migrations remove --project Fro.Infrastructure --startup-project Fro.Api

# Generate SQL script (don't apply)
dotnet ef migrations script --project Fro.Infrastructure --startup-project Fro.Api --output migration.sql
```

### Database Management

```bash
# Drop database (destructive!)
dotnet ef database drop --project Fro.Infrastructure --startup-project Fro.Api

# Show DbContext info
dotnet ef dbcontext info --project Fro.Infrastructure --startup-project Fro.Api

# Scaffold DbContext from existing database (reverse engineering)
dotnet ef dbcontext scaffold "Server=localhost;Database=fro_db;User=fro_user;Password=fro_password;" Pomelo.EntityFrameworkCore.MySql --project Fro.Infrastructure --startup-project Fro.Api --output-dir ScaffoldedModels
```

---

## Next Steps

After successful migration:

1. **Test API with Swagger**
   - Start API: `cd Fro.Api && dotnet run`
   - Open: http://localhost:5000/api/docs
   - Test authentication with admin user

2. **Run Integration Tests** (when test project exists)
   ```bash
   dotnet test Fro.Infrastructure.Tests
   ```

3. **Verify Python Backend Compatibility**
   ```bash
   cd backend
   docker compose up -d backend
   # Test endpoints with same database
   ```

4. **Set Up SLSQP Optimizer Microservice**
   - See `MICROSERVICES_SETUP.md` for instructions
   - Start Python optimizer service on port 8001

5. **Configure Production Connection String**
   - Use environment variables
   - Never commit production credentials

---

## Production Considerations

### Security

**DO NOT** use default credentials in production:
```json
// ❌ WRONG - Development only
"DefaultConnection": "Server=localhost;Database=fro_db;User=fro_user;Password=fro_password;"

// ✅ CORRECT - Use environment variables
"DefaultConnection": "${CONNECTION_STRING}"
```

**Set environment variable:**
```bash
export ConnectionStrings__DefaultConnection="Server=prod-mysql;Database=fro_db;User=secure_user;Password=STRONG_RANDOM_PASSWORD;"
```

### Migration Deployment

**Option 1: Run migrations on startup (simpler, but risky)**
```csharp
// Program.cs
if (args.Contains("--migrate"))
{
    using var scope = app.Services.CreateScope();
    var context = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
    await context.Database.MigrateAsync();
}
```

**Option 2: Separate migration step (recommended)**
```bash
# Deploy new code
# Then run migrations separately
dotnet ef database update --project Fro.Infrastructure --startup-project Fro.Api --connection "$PROD_CONNECTION_STRING"
```

**Option 3: Generate SQL scripts (most control)**
```bash
# Generate SQL for review
dotnet ef migrations script --project Fro.Infrastructure --startup-project Fro.Api --idempotent --output migration.sql

# DBA reviews and executes
mysql -h prod-mysql -u admin -p fro_db < migration.sql
```

### Backup Before Migration

```bash
# Always backup before production migrations
mysqldump -h prod-mysql -u backup_user -p fro_db > fro_db_backup_$(date +%Y%m%d_%H%M%S).sql
```

---

## Summary

✅ **Prerequisites Checklist:**
- [ ] dotnet-ef tools installed globally
- [ ] MySQL 8.0+ running and accessible
- [ ] fro_db database created
- [ ] fro_user MySQL user with permissions
- [ ] All 4 .NET projects build successfully

✅ **Migration Steps:**
1. Generate migration: `dotnet ef migrations add InitialCreate`
2. Review generated migration code
3. Apply to MySQL: `dotnet ef database update`
4. Verify tables created
5. Seed database (SQL script or programmatic)

✅ **Verification:**
- [ ] 9 tables created (including __EFMigrationsHistory)
- [ ] 3 users seeded (admin, engineer, viewer)
- [ ] Schema matches Python backend
- [ ] Python backend can read .NET seeded data
- [ ] .NET API can read Python seeded data

🎯 **Next:** Test API endpoints through Swagger at http://localhost:5000/api/docs

---

**For questions or issues:**
- See [TROUBLESHOOTING](#troubleshooting) section above
- Review [IMPLEMENTATION_STATUS_2025-11-14.md](./IMPLEMENTATION_STATUS_2025-11-14.md) for migration progress
- Check [ARCHITECTURE.md](../ARCHITECTURE.md) for system design

---

**Last Updated:** 2025-11-14
**Migration Status:** Phase 5 - EF Core Migrations (Ready for Execution)
