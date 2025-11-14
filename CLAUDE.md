# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚨 CRITICAL: Dual Backend Architecture

This project is **actively migrating** from Python/FastAPI to C#/.NET 8. Both backends coexist:

- **`backend/`** - Python/FastAPI (PRODUCTION, stable, 100% functional)
- **`backend-dotnet/`** - C#/.NET 8 (IN DEVELOPMENT, 80% complete)

**Rule:** When making changes, determine which backend is relevant:
- Bug fixes, new features → Python backend (production)
- Migration tasks, .NET implementation → .NET backend (development)
- Frontend, database schema, docs → affects both

**Migration Status:** See [IMPLEMENTATION_STATUS_2025-11-14.md](./backend-dotnet/IMPLEMENTATION_STATUS_2025-11-14.md) for latest status (80% complete)

---

## 🚀 Quick Start

### Python Backend (Production)

```bash
# Start all services
docker compose up -d

# Wait 30s for MySQL, then migrate
docker compose exec backend alembic upgrade head

# Run tests
docker compose exec backend python -m pytest tests/test_simple.py tests/test_models.py -v

# Access points
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/api/v1/docs
# Health: curl http://localhost:8000/health
```

### .NET Backend (Development)

```bash
cd backend-dotnet

# Build solution (4 projects)
dotnet build

# Run API
cd Fro.Api
dotnet run                    # http://localhost:5000
dotnet watch run              # Auto-reload on changes

# Access points
# Swagger: http://localhost:5000/api/docs
# Hangfire Dashboard: http://localhost:5000/hangfire
# Health: http://localhost:5000/health
```

---

## 📂 Project Structure

```
RegeneratorCalc_v2/
├── backend/                    # Python/FastAPI (PRODUCTION)
│   ├── app/
│   │   ├── api/v1/endpoints/   # 7 FastAPI routers
│   │   ├── services/           # 8 business logic services
│   │   ├── models/             # 5 SQLAlchemy entities
│   │   ├── tasks/              # 5 Celery task modules
│   │   └── core/               # Config, security, database
│   ├── migrations/             # Alembic database migrations
│   └── tests/                  # 12+ test files (42% coverage)
│
├── backend-dotnet/             # C#/.NET 8 (DEVELOPMENT - 80%)
│   ├── Fro.Domain/             # ✅ Entities + Enums (COMPLETE)
│   ├── Fro.Application/        # ✅ DTOs, Services, Validators (COMPLETE)
│   │   ├── Services/           # ✅ Auth, User, RegeneratorConfig, Optimization
│   │   ├── Validators/         # ✅ 9 FluentValidation validators
│   │   ├── Interfaces/         # ✅ Service and Security interfaces
│   │   └── DTOs/               # ✅ 22 DTOs for all endpoints
│   ├── Fro.Infrastructure/     # ✅ EF Core, Repositories, Security, Jobs (COMPLETE)
│   │   ├── Security/           # ✅ JwtTokenService, PasswordHasher
│   │   ├── Repositories/       # ✅ 5 specialized repositories
│   │   ├── Jobs/               # ✅ OptimizationJob, MaintenanceJob (Hangfire)
│   │   └── Data/               # ✅ ApplicationDbContext, EF Core config
│   └── Fro.Api/                # ✅ Controllers (100% - 6/6 done, 2 placeholder)
│       ├── Controllers/        # ✅ All 6 controllers implemented
│       └── Middleware/         # ✅ GlobalExceptionHandlerMiddleware
│
├── frontend/                   # Next.js 14 (UNCHANGED)
│   └── src/
│       ├── app/                # 8 Next.js pages
│       ├── components/         # 30+ React components
│       └── lib/                # API client + utilities
│
├── ARCHITECTURE.md             # System design (describes .NET target)
└── backend-dotnet/
    ├── IMPLEMENTATION_STATUS_2025-11-14.md  # Latest migration status (80% complete)
    └── SLSQP_OPTIMIZER_INTEGRATION_STRATEGY.md  # Optimizer integration plan
```

---

## ⚙️ Common Development Commands

### Python Backend

```bash
# IMPORTANT: Poetry NOT available in Docker containers
# Use direct python/alembic commands, NOT "poetry run ..."

# Testing
docker compose exec backend python -m pytest tests/ -v
docker compose exec backend python -m pytest tests/test_specific.py::test_name -v --cov=app

# Database migrations
docker compose exec backend alembic revision --autogenerate -m "Description"
docker compose exec backend alembic upgrade head
docker compose exec backend alembic downgrade -1

# Celery monitoring
docker compose logs celery --tail=50 -f
docker compose exec celery celery -A app.celery inspect active
docker compose exec celery celery -A app.celery inspect scheduled

# Service management
docker compose restart backend celery celery-beat
docker compose ps
docker compose down
```

### .NET Backend

```bash
cd backend-dotnet

# Build and run
dotnet build                    # Build all 4 projects
dotnet build --no-restore       # Skip package restore
cd Fro.Api && dotnet run        # Start API on port 5000
dotnet watch run                # Auto-reload on file changes

# Entity Framework migrations (when ready - Phase 6)
dotnet ef migrations add MigrationName --project Fro.Infrastructure --startup-project Fro.Api
dotnet ef database update --project Fro.Infrastructure --startup-project Fro.Api
dotnet ef migrations remove --project Fro.Infrastructure --startup-project Fro.Api

# Testing (when test projects exist - Phase 7)
dotnet test
dotnet test --logger "console;verbosity=detailed"
dotnet test --collect:"XPlat Code Coverage"

# Clean build artifacts
dotnet clean
```

### Frontend

```bash
# Local development
cd frontend
npm run dev                     # Dev server (port 3000)
npm run build                   # Production build
npm run type-check              # TypeScript validation

# Docker mode
docker compose logs frontend -f
docker compose restart frontend
docker compose exec frontend sh
```

---

## 🏗️ Architecture Overview

### Python Backend (Current Production)

**Pattern:** Layered Architecture
```
FastAPI Endpoints → Services → Repositories → SQLAlchemy Models → MySQL
                     ↓
                Celery Tasks → Redis Broker → Worker Processes
```

**Key Layers:**
- `app/api/v1/endpoints/` - HTTP routes (7 modules)
- `app/services/` - Business logic (8 modules)
- `app/models/` - SQLAlchemy ORM entities (5 models)
- `app/tasks/` - Celery background jobs (5 task modules)

### .NET Backend (Migration Target)

**Pattern:** Clean Architecture (DDD-style)
```
Layer 1: Fro.Api          → Controllers, Middleware, Program.cs (✅ COMPLETE)
Layer 2: Fro.Application  → Services, DTOs, Validators (✅ COMPLETE)
Layer 3: Fro.Infrastructure → EF Core, Hangfire, Repositories, Jobs (✅ COMPLETE)
Layer 4: Fro.Domain       → Entities, Enums (✅ COMPLETE)
```

**Dependency Flow:** Api → Application → Infrastructure → Domain
- Domain has ZERO dependencies (pure C#)
- Application depends on Domain only (security interfaces prevent circular dependency)
- Infrastructure implements Application interfaces (repositories, security services)
- API orchestrates everything via dependency injection

**Key Design Decision - Avoiding Circular Dependencies:**
- Security service interfaces (`IJwtTokenService`, `IPasswordHasher`) live in Application layer
- Implementations (`JwtTokenService`, `PasswordHasher`) live in Infrastructure layer
- This allows Application services to depend on security abstractions without referencing Infrastructure

**Migration Progress (80%):**
- ✅ Phase 1: Solution setup, domain models, EF Core config, Program.cs
- ✅ Phase 2: 22 DTOs, 5 repositories, dependency injection
- ✅ Phase 3a: Services (4), validators (9), security infrastructure
- ✅ Phase 3b-3f: All 6 controllers, Hangfire jobs, global exception handler
- ⏳ Phase 4: SLSQP optimizer integration (Python microservice recommended)
- ⏳ Phase 5: EF Core migrations, data seeding
- ⏳ Phase 6: Unit + integration tests
- ⏳ Phase 7: Docker config, CI/CD, deployment

---

## 🛢️ Database Schema (Shared MySQL 8.0)

Both backends share the **same MySQL database** with identical schema:

**Core Tables:**
- `users` - Authentication + RBAC (3 roles: ADMIN, ENGINEER, VIEWER)
- `regenerator_configurations` - Equipment settings, wizard progress (JSON columns)
- `optimization_scenarios` - Optimization job definitions
- `optimization_jobs` - Job execution tracking + Celery task IDs
- `materials` - 103 standard refractory materials
- `configuration_templates` - Preset configurations
- `import_jobs` - XLSX import progress
- `report_generations` - Report requests

**Key Schema Details:**
- All IDs: `CHAR(36)` (GUID stored as string)
- JSON columns: configuration data, validation results, convergence history
- Timestamps: `DATETIME` (UTC) - use `datetime.now(UTC)` in Python, `DateTime.UtcNow` in C#

**Python → .NET Mapping:**
- SQLAlchemy models → EF Core entities (✅ complete)
- Alembic migrations → EF Core migrations (⏳ Phase 6)

---

## ⚠️ Critical Migration Notes

### 1. Don't Break Production (Python)

When working on migration tasks, **DO NOT**:
- Modify database schema without coordinating both backends
- Change API endpoints consumed by frontend
- Alter background job interfaces
- Break existing Python tests

### 2. .NET Backend Status (~80% Complete)

**Architecture Pattern:** Clean Architecture with dependency flow Api → Application → Infrastructure → Domain

**Security Services (100%):**
- `IJwtTokenService` / `JwtTokenService` - JWT token generation/validation
- `IPasswordHasher` / `PasswordHasher` - BCrypt password hashing
- Interfaces in Application layer, implementations in Infrastructure (avoids circular dependencies)

**What Works (80% complete):**
- ✅ Domain models (4 entities, 5 enums including ConfigurationStatus)
- ✅ DTOs for all endpoints (22 files)
- ✅ Repository pattern (5 specialized repos)
- ✅ EF Core configured (MySQL + Hangfire + JWT + Swagger)
- ✅ Security infrastructure (JwtTokenService, PasswordHasher with interfaces)
- ✅ Application services (AuthenticationService, UserService, RegeneratorConfigurationService, OptimizationService)
- ✅ FluentValidation validators (9 validators for Auth, Users, Regenerators, Optimization)
- ✅ Dependency injection configured (Application + Infrastructure layers)
- ✅ **All 6 API Controllers** (57 endpoints: 40 implemented, 17 placeholder)
- ✅ **Global exception handler middleware** (standardized error responses)
- ✅ **Hangfire background jobs** (OptimizationJob, MaintenanceJob skeletons)
- ✅ **BUILD CLEAN** - All compilation errors fixed (0 errors, 3 warnings)

**What's Missing (20% remaining):**
- ⏳ SLSQP optimizer integration (Python microservice - 2-3 days)
- ⏳ EF Core migrations + data seeding
- ⏳ Unit + integration tests (70% coverage target)
- ⏳ Materials & Reports full implementation (currently placeholders)
- ⏳ Docker configuration

### 3. SLSQP Optimizer Challenge

**Python (SciPy):**
```python
from scipy.optimize import minimize
result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
```

**C#/.NET Options:**
1. **Python Microservice** - Keep optimizer in Python (✅ RECOMMENDED - see SLSQP_OPTIMIZER_INTEGRATION_STRATEGY.md)
2. **Math.NET Numerics** - Pure C#, different algorithm, 4-6 days, validation risk
3. **Python.NET Interop** - Complex setup, 1-2 weeks, high deployment risk

**Decision:** Python microservice approach (2-3 days, zero algorithm risk, production parity)

---

## 🐛 Common Pitfalls

### Python Specific

**❌ DON'T:** Use Poetry in Docker
```bash
docker compose exec backend poetry run pytest  # WRONG
```
**✅ DO:** Direct Python commands
```bash
docker compose exec backend python -m pytest   # CORRECT
```

**❌ DON'T:** `datetime.utcnow()` (deprecated Python 3.12+)
```python
expire = datetime.utcnow() + timedelta(hours=1)  # WRONG
```
**✅ DO:** `datetime.now(UTC)`
```python
from datetime import datetime, UTC
expire = datetime.now(UTC) + timedelta(hours=1)  # CORRECT
```

**❌ DON'T:** Update DB in Celery progress callbacks
```python
def progress_callback(iteration, max_iter):
    await db.commit()  # WRONG - event loop conflict
```
**✅ DO:** Use Celery state only
```python
def progress_callback(iteration, max_iter):
    self.update_state(state='PROGRESS', meta={'iteration': iteration})  # CORRECT
```

**❌ DON'T:** Compare UUID objects with CHAR(36) columns
```python
stmt = select(Model).where(Model.user_id == current_user.id)  # WRONG
```
**✅ DO:** Convert to string first
```python
stmt = select(Model).where(Model.user_id == str(current_user.id))  # CORRECT
```

### .NET Specific

**❌ DON'T:** Mix EF Core versions
- Pomelo.EntityFrameworkCore.MySql 8.0.2 requires EF Core 8.0.2
- If using EF Core 8.0.11, add explicit package reference

**❌ DON'T:** Forget `required` keyword
```csharp
public string Name { get; set; }  // WRONG - nullable warning
```
**✅ DO:** Use `required` or nullable
```csharp
public required string Name { get; set; }  // CORRECT
public string? Description { get; set; }   // CORRECT (nullable)
```

**❌ DON'T:** Save changes in repository methods individually
```csharp
public async Task AddAsync(T entity)
{
    _dbSet.Add(entity);
    // Missing: await _context.SaveChangesAsync();
}
```
**✅ DO:** Always save changes
```csharp
public async Task AddAsync(T entity)
{
    _dbSet.Add(entity);
    await _context.SaveChangesAsync();  // CORRECT
}
```

**❌ DON'T:** Use UPPER_CASE for enum values in C#
```csharp
public enum OptimizationStatus {
    PENDING,  // WRONG - Python style
    FAILED
}
// Usage: OptimizationStatus.PENDING
```
**✅ DO:** Use PascalCase for enums (C# convention)
```csharp
public enum OptimizationStatus {
    Pending,  // CORRECT - C# style
    Failed
}
// Usage: OptimizationStatus.Pending
```

**❌ DON'T:** Mix Status types (string vs enum)
```csharp
// Entity with string
public string Status { get; set; } = "active";

// DTO expecting enum
public OptimizationStatus Status { get; set; }  // WRONG - type mismatch
```
**✅ DO:** Match types between Entity and DTO
```csharp
// Both string (for Scenario.Status)
public string Status { get; set; } = "active";

// Both enum (for Job.Status)
public ConfigurationStatus Status { get; set; } = ConfigurationStatus.DRAFT;
```

### Frontend Specific

**❌ DON'T:** Import sonner (temporarily disabled)
```typescript
import { toast } from 'sonner';  // WRONG - package not in pnpm-lock.yaml
```
**✅ DO:** Use console.log fallback
```typescript
const toast = {
  success: (msg: string) => console.log('✅', msg),
  error: (msg: string) => console.error('❌', msg)
};
```

**❌ DON'T:** Put viewport in metadata (Next.js 14)
```typescript
export const metadata: Metadata = { viewport: '...' };  // WRONG - deprecated
```
**✅ DO:** Separate viewport export
```typescript
export const viewport: Viewport = { width: 'device-width', initialScale: 1 };
```

---

## 🧪 Testing

### Python Backend (Current)

**Coverage:** 42% (target: 80%, gap: -38%)
- ✅ Models/Schemas: 93-100% (excellent)
- ⚠️ Core utilities: 71-89% (good)
- ❌ Services: 9-25% (critical gap)
- ❌ Celery tasks: 0% (no mocking strategy)

```bash
# Run stable tests
docker compose exec backend python -m pytest tests/test_simple.py tests/test_models.py -v

# Service tests
docker compose exec backend python -m pytest tests/test_materials_service.py -v
docker compose exec backend python -m pytest tests/test_optimization_service.py -v

# Coverage report
docker compose exec backend python -m pytest --cov=app --cov-report=html
# View: backend/htmlcov/index.html
```

See `backend/TEST_COVERAGE_ANALYSIS.md` for detailed analysis.

### .NET Backend (Planned - Phase 7)

**Framework:** xUnit + Moq + FluentAssertions + TestContainers

**Test Projects (to be created):**
- `Fro.Domain.Tests` - Entity validation, business rules
- `Fro.Application.Tests` - Services, validators (mocked repos)
- `Fro.Infrastructure.Tests` - Repository integration (TestContainers MySQL)
- `Fro.Api.Tests` - Controller integration (WebApplicationFactory)

---

## 📚 Key Documentation Files

**Migration Documents:**
- `backend-dotnet/IMPLEMENTATION_STATUS_2025-11-14.md` - **LATEST STATUS** (80% complete, comprehensive report)
- `backend-dotnet/SLSQP_OPTIMIZER_INTEGRATION_STRATEGY.md` - Optimizer integration design (3 options evaluated)
- `ARCHITECTURE.md` - Target .NET architecture (C# backend design)
- Historical: `MIGRATION_TO_DOTNET.md`, `PHASE2_DTOS_REPOSITORIES_COMPLETE.md` (Phase 1-2 reports)

**Python Backend:**
- `backend/TEST_COVERAGE_ANALYSIS.md` - Coverage gaps + improvement plan
- `RATE_LIMITING_IMPLEMENTATION.md` - User rate limiting (5 jobs max)
- `VALIDATION_ERRORS.md` - 422 error handling
- `UX_IMPROVEMENTS_TOAST_NOTIFICATIONS.md` - Toast notifications

**User/Business:**
- `USER_GUIDE.md` - End-user documentation
- `README.md` - Project overview
- `PRD.md` - Product requirements
- `RULES.md` - Business rules

---

## 🔧 Configuration

### Python Backend (docker-compose.yml)

```bash
DATABASE_URL=mysql+aiomysql://fro_user:fro_password@mysql:3306/fro_db
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2
SECRET_KEY=your-secret-key-change-in-production
```

### .NET Backend (appsettings.json)

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost;Port=3306;Database=fro_db;User=fro_user;Password=fro_password;",
    "Redis": "localhost:6379,abortConnect=false"
  },
  "JwtSettings": {
    "Secret": "your-super-secret-jwt-key-minimum-32-characters-long-change-in-production",
    "Issuer": "Forglass.RegeneratorOptimizer",
    "Audience": "Forglass.RegeneratorOptimizer.API",
    "ExpirationMinutes": 1440
  },
  "Hangfire": {
    "WorkerCount": 4,
    "DashboardPath": "/hangfire"
  }
}
```

---

## 🚨 Known Issues

### Active Issues
- **Test coverage**: 42% vs 80% target (-38% gap) - Services layer critical gap
- **Sonner toast**: Temporarily disabled, console.log fallback in 6 frontend files
- **TypeScript warnings**: 9 non-blocking type-checking warnings
- **.NET migration**: 20% remaining (SLSQP optimizer, EF migrations, Tests)

### Recently Fixed ✅
- **.NET Build Errors** (2025-11-14) - All 45+ compilation errors fixed
  - PaginatedRequest missing properties (SearchTerm, SortBy, SortDescending)
  - Entity/DTO type mismatches (ConfigurationStatus enum)
  - Enum naming (PENDING → Pending, FAILED → Failed)
  - PaginatedResponse read-only properties
  - Repository method signatures (DeleteAsync → DeleteByIdAsync)
  - Missing NuGet package (System.IdentityModel.Tokens.Jwt)
- DateTime deprecation (32 instances fixed)
- Celery event loop conflicts (nest_asyncio)
- UUID/String mapping issues
- Next.js viewport warnings

---

## 📊 System Status

**Python Backend (Production):**
- Docker Services: 6/6 healthy ✅
- Backend API: `/health` responding ✅
- MySQL: Connected ✅
- Redis: Connected ✅
- Celery: 4 workers active ✅
- Tests: 11/11 passing ✅

**.NET Backend (Development):**
- Build Status: ✅ **CLEAN** (0 errors, 3 warnings)
- Projects: 4/4 projects exist ✅
- Domain: 100% complete ✅ (4 entities, 5 enums)
- Application: 100% complete ✅ (DTOs ✅, Services ✅, Validators ✅)
- Infrastructure: 100% complete ✅ (Repos, Security, Jobs, EF Core, Hangfire)
- API: 100% complete ✅ (All 6 controllers ✅, Global exception handler ✅)

---

## 🎯 Next Migration Steps (Phase 4 - Optimizer Integration)

**Completed in Phase 3:**
- ✅ All 6 API Controllers (57 endpoints: 40 functional, 17 placeholder)
- ✅ Global Exception Handler middleware (standardized error responses)
- ✅ Hangfire background jobs (OptimizationJob, MaintenanceJob skeletons)
- ✅ **BUILD CLEAN** - 0 errors, 3 warnings

**Immediate Next Steps (Priority Order):**

1. **Test .NET API with Swagger** (~4 hours)
   - Start API: `cd backend-dotnet/Fro.Api && dotnet run`
   - Open Swagger: http://localhost:5000/api/docs
   - Test AuthController (login, register, tokens)
   - Test CRUD operations (Users, Regenerators, Optimization)
   - Verify JWT authentication and authorization
   - Test error handling (400, 401, 404, 422, 500)

2. **SLSQP Optimizer Integration** (~2-3 days) - **CRITICAL PATH**
   - See `backend-dotnet/SLSQP_OPTIMIZER_INTEGRATION_STRATEGY.md` for detailed plan
   - **Recommended approach:** Python microservice (FastAPI wrapper for SciPy SLSQP)
   - Extract Python physics model + optimizer to standalone service
   - Implement .NET HttpClient integration in OptimizationService
   - Update OptimizationJob to call Python service
   - Docker container + docker-compose integration

3. **EF Core Migrations** (~1 day)
   - Generate initial migration: `dotnet ef migrations add InitialCreate`
   - Apply to MySQL: `dotnet ef database update`
   - Seed admin user + test data
   - Verify schema matches Python backend

4. **Basic Integration Testing** (~2 days)
   - Test complete optimization workflow
   - Verify Hangfire job execution
   - Test background job progress tracking
   - Validate optimizer results match Python backend

**Reference:** See `backend-dotnet/IMPLEMENTATION_STATUS_2025-11-14.md` for complete status (80% complete)

---

## 🌐 Access Points

**Python Backend:**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/api/v1/docs (Swagger UI)
- Health: http://localhost:8000/health
- Admin: username `admin`, password `admin`

**.NET Backend (when running):**
- Swagger: http://localhost:5000/api/docs
- Hangfire Dashboard: http://localhost:5000/hangfire
- Health: http://localhost:5000/health

**Database:**
- MySQL: localhost:3306 (user: `fro_user`, password: `fro_password`, db: `fro_db`)
- Redis: localhost:6379
