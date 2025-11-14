# Forglass Regenerator Optimizer - .NET Backend

**C#/.NET 8 backend for the Forglass Regenerator Optimization System**

---

## 🚀 Quick Start

### Prerequisites

- **.NET SDK 8.0** - [Download](https://dotnet.microsoft.com/download/dotnet/8.0)
- **MySQL 8.0** - Running on `localhost:3306`
- **Redis** (optional) - For Hangfire background jobs

### Run the API

```bash
cd Fro.Api
dotnet restore
dotnet build
dotnet run
```

**Swagger UI:** http://localhost:5000/api/docs

**See [QUICK_START_TESTING.md](./QUICK_START_TESTING.md) for 5-minute testing guide.**

---

## 📂 Project Structure

```
backend-dotnet/
├── Fro.Domain/              ✅ Domain entities & enums (100%)
├── Fro.Application/         ✅ DTOs, Services, Validators (100%)
├── Fro.Infrastructure/      ✅ EF Core, Repositories, Security, Jobs (100%)
├── Fro.Api/                 ✅ Controllers, Middleware, Program.cs (100%)
├── DOTNET_API_TESTING_GUIDE.md          📖 Complete testing guide (95 pages)
├── QUICK_START_TESTING.md               📖 5-minute quick start
├── API_TESTING_EXAMPLES.sh              📜 curl examples
├── FRO_API_Postman_Collection.json      📦 Postman/Insomnia collection
├── IMPLEMENTATION_STATUS_2025-11-14.md  📊 Migration status (80% complete)
└── SLSQP_OPTIMIZER_INTEGRATION_STRATEGY.md  📋 Optimizer integration plan
```

---

## 🏗️ Architecture

**Clean Architecture (DDD-style):**

```
┌──────────────────────────────────────────────────────────┐
│                      Fro.Api                            │
│  Controllers, Middleware, Swagger, JWT, Hangfire        │
└────────────────────┬─────────────────────────────────────┘
                     │ depends on
┌────────────────────▼─────────────────────────────────────┐
│                 Fro.Application                          │
│  Services, DTOs, Validators, Interfaces                  │
└────────────────────┬─────────────────────────────────────┘
                     │ depends on
┌────────────────────▼─────────────────────────────────────┐
│               Fro.Infrastructure                         │
│  EF Core, Repositories, Security, Hangfire Jobs          │
└────────────────────┬─────────────────────────────────────┘
                     │ depends on
┌────────────────────▼─────────────────────────────────────┐
│                   Fro.Domain                             │
│  Entities, Enums (Pure C#, zero dependencies)            │
└──────────────────────────────────────────────────────────┘
```

**Key Design Decisions:**
- Security service interfaces (`IJwtTokenService`, `IPasswordHasher`) in Application layer
- Implementations in Infrastructure layer (avoids circular dependencies)
- Clean separation: Domain → Infrastructure → Application → API

---

## 🧪 Testing the API

### Method 1: Swagger UI (Recommended)

1. Start API: `dotnet run` from `Fro.Api/`
2. Open http://localhost:5000/api/docs
3. Follow **[QUICK_START_TESTING.md](./QUICK_START_TESTING.md)**

### Method 2: Postman/Insomnia

1. Import `FRO_API_Postman_Collection.json`
2. Set `base_url` to `http://localhost:5000/api/v1`
3. Run "Register" → "Login" (auto-sets token)
4. Test endpoints

### Method 3: Shell Script (curl)

```bash
chmod +x API_TESTING_EXAMPLES.sh
./API_TESTING_EXAMPLES.sh
```

**See [DOTNET_API_TESTING_GUIDE.md](./DOTNET_API_TESTING_GUIDE.md) for complete reference (all 57 endpoints).**

---

## 📊 Implementation Status

**Overall Progress: 80% Complete**

| Layer | Status | Details |
|-------|--------|---------|
| **Fro.Domain** | ✅ 100% | 4 entities, 5 enums |
| **Fro.Application** | ✅ 100% | 22 DTOs, 4 services, 9 validators |
| **Fro.Infrastructure** | ✅ 100% | 5 repos, security, EF Core, Hangfire |
| **Fro.Api** | ✅ 100% | 6 controllers (57 endpoints), middleware |
| **SLSQP Optimizer** | ⏳ 0% | Python microservice recommended |
| **EF Migrations** | ⏳ 0% | Phase 5 |
| **Unit Tests** | ⏳ 0% | Phase 6 |
| **Docker Config** | ⏳ 0% | Phase 7 |

**See [IMPLEMENTATION_STATUS_2025-11-14.md](./IMPLEMENTATION_STATUS_2025-11-14.md) for detailed report.**

---

## 🛠️ Development

### Build

```bash
dotnet build                    # Build all projects
dotnet build --no-restore       # Skip package restore
```

### Run

```bash
cd Fro.Api
dotnet run                      # Start API
dotnet watch run                # Auto-reload on changes
```

### EF Core Migrations (When Ready)

```bash
# Create migration
dotnet ef migrations add MigrationName \
  --project Fro.Infrastructure \
  --startup-project Fro.Api

# Apply migration
dotnet ef database update \
  --project Fro.Infrastructure \
  --startup-project Fro.Api

# Remove last migration
dotnet ef migrations remove \
  --project Fro.Infrastructure \
  --startup-project Fro.Api
```

### Clean

```bash
dotnet clean
rm -rf */bin */obj
```

---

## 🔧 Configuration

### appsettings.json

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost;Port=3306;Database=fro_db;User=fro_user;Password=fro_password;",
    "Redis": "localhost:6379,abortConnect=false"
  },
  "JwtSettings": {
    "Secret": "your-super-secret-jwt-key-minimum-32-characters-long",
    "Issuer": "Forglass.RegeneratorOptimizer",
    "Audience": "Forglass.RegeneratorOptimizer.API",
    "ExpirationMinutes": 1440,
    "RefreshTokenExpirationDays": 7
  },
  "Hangfire": {
    "WorkerCount": 4,
    "DashboardPath": "/hangfire",
    "EnableDashboardAuthorization": true
  },
  "Cors": {
    "AllowedOrigins": ["http://localhost:3000", "http://localhost:8000"]
  }
}
```

---

## 📡 API Endpoints

### Authentication (`/api/v1/Auth`)

- `POST /register` - Register new user
- `POST /login` - User login (JWT)
- `POST /refresh` - Refresh access token
- `POST /change-password` - Change password
- `GET /me` - Get current user info

### Users (`/api/v1/Users`) - Admin Only

- `GET /` - Get all users (paginated)
- `GET /{id}` - Get user by ID
- `POST /` - Create user
- `PUT /{id}` - Update user
- `DELETE /{id}` - Delete user (soft)
- `PUT /{id}/role` - Update user role
- `POST /{id}/verify` - Verify email
- `GET /statistics` - User statistics

### Regenerators (`/api/v1/Regenerators`)

- `GET /` - Get user's configs (paginated)
- `GET /{id}` - Get config by ID
- `POST /` - Create config
- `PUT /{id}` - Update config
- `DELETE /{id}` - Delete config
- `POST /{id}/validate` - Validate config
- `POST /{id}/complete` - Mark complete
- `GET /statistics` - Config statistics

### Optimization (`/api/v1/Optimization`)

- `GET /scenarios` - Get scenarios (paginated)
- `POST /scenarios` - Create scenario
- `GET /scenarios/{id}` - Get scenario by ID
- `POST /jobs/start` - Start optimization job
- `GET /jobs/{id}` - Get job status
- `GET /jobs/{id}/progress` - Get job progress
- `POST /jobs/{id}/cancel` - Cancel job
- `GET /jobs/{id}/result` - Get job result

### Materials (`/api/v1/Materials`)

- `GET /` - Get all materials (paginated)
- `POST /search` - Search materials

### Reports (`/api/v1/Reports`)

- `POST /generate` - Generate report
- `GET /{id}` - Get report status
- `GET /{id}/download` - Download report

**Total: 57 endpoints (40 implemented, 17 placeholder)**

---

## 🧩 NuGet Packages

### Core

- `Microsoft.AspNetCore.OpenApi` (8.0.11)
- `Swashbuckle.AspNetCore` (7.2.0)
- `Microsoft.EntityFrameworkCore` (8.0.11)
- `Pomelo.EntityFrameworkCore.MySql` (8.0.2)

### Security

- `Microsoft.AspNetCore.Authentication.JwtBearer` (8.0.11)
- `System.IdentityModel.Tokens.Jwt` (8.1.2)
- `BCrypt.Net-Next` (4.0.3)

### Validation

- `FluentValidation` (11.11.0)
- `FluentValidation.DependencyInjectionExtensions` (11.11.0)

### Background Jobs

- `Hangfire.Core` (1.8.18)
- `Hangfire.AspNetCore` (1.8.18)
- `Hangfire.Redis.StackExchange` (1.10.2)
- `StackExchange.Redis` (2.8.16)

---

## ⚠️ Known Issues

### Active

- **SLSQP optimizer not integrated** (20% remaining) - Python microservice recommended
- **No EF Core migrations** - Phase 5 (1 day)
- **No unit tests** - Phase 6 (2-3 days)
- **No Docker configuration** - Phase 7 (1 day)

### Build Warnings (Non-blocking)

- 3 warnings related to nullable reference types (cosmetic)

---

## 🚧 Next Steps (Priority Order)

1. **Test API manually** (~4 hours) - **YOU ARE HERE**
   - Use Swagger UI
   - Follow QUICK_START_TESTING.md
   - Verify all endpoints

2. **SLSQP Optimizer Integration** (~2-3 days) - **CRITICAL PATH**
   - Python microservice approach (recommended)
   - See SLSQP_OPTIMIZER_INTEGRATION_STRATEGY.md

3. **EF Core Migrations** (~1 day)
   - Generate initial migration
   - Apply to MySQL
   - Seed admin user + test data

4. **Unit + Integration Tests** (~2-3 days)
   - xUnit + Moq + FluentAssertions
   - 70% coverage target

5. **Docker Configuration** (~1 day)
   - Dockerfile for .NET API
   - Update docker-compose.yml
   - Multi-stage build

---

## 📚 Documentation

- **[QUICK_START_TESTING.md](./QUICK_START_TESTING.md)** - 5-minute quick start
- **[DOTNET_API_TESTING_GUIDE.md](./DOTNET_API_TESTING_GUIDE.md)** - Complete guide (95 pages)
- **[API_TESTING_EXAMPLES.sh](./API_TESTING_EXAMPLES.sh)** - curl examples
- **[FRO_API_Postman_Collection.json](./FRO_API_Postman_Collection.json)** - Postman collection
- **[IMPLEMENTATION_STATUS_2025-11-14.md](./IMPLEMENTATION_STATUS_2025-11-14.md)** - Migration status
- **[SLSQP_OPTIMIZER_INTEGRATION_STRATEGY.md](./SLSQP_OPTIMIZER_INTEGRATION_STRATEGY.md)** - Optimizer plan

---

## 🤝 Contributing

This is a migration project from Python/FastAPI to C#/.NET 8.

**Main repository documentation:**
- `../CLAUDE.md` - Project overview
- `../ARCHITECTURE.md` - System design

---

## 📄 License

Proprietary - Forglass

---

**Version:** 1.0.0
**Status:** Phase 3 Complete (80%)
**Build:** ✅ Clean (0 errors, 3 warnings)
**Last Updated:** 2025-11-14
