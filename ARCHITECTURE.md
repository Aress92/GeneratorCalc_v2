# Forglass Regenerator Optimizer – Architecture

> This document describes the architecture of Forglass Regenerator Optimizer
> using a backend implemented in C#/.NET 8 (ASP.NET Core).

---

## 1. High-Level Overview

The system optimizes glass furnace regenerator operation based on process data and
engineer configuration. It consists of:

- **Frontend** – web UI for engineers and operators
- **Backend API** – business logic, optimization workflows, authentication, authorization
- **Background processing** – long-running and scheduled jobs
- **Database** – persistent storage of projects, configurations, optimization results
- **Cache & messaging** – Redis for caching and job coordination
- **Reverse proxy / HTTP entrypoint** – Nginx (optional in development)
- **Monitoring & logging** – metrics and logs for observability (optional)

---

## 2. Technology Stack

### 2.1. Frontend

- **Framework:** Next.js (React)
- **Language:** TypeScript
- **Package manager:** pnpm
- **Dev server:** `pnpm dev` (default port 3000)
- **Build:** `pnpm build`
- **Production run:** `pnpm start` (Next.js server) or static export behind Nginx

Frontend communicates only with the backend HTTP API (REST, JSON).

---

### 2.2. Backend – C# / .NET 8 (ASP.NET Core)

- **Platform:** .NET 8
- **Framework:** ASP.NET Core 8 (Minimal APIs or Controllers)
- **Language:** C#
- **Main responsibilities:**
  - Authentication & authorization
  - User and project management
  - Configuration of regenerators and optimization scenarios
  - Triggering optimization runs and exposing results
  - Validation and sanitization of input data
  - Exposing OpenAPI/Swagger spec for integration

#### Backend solution layout (proposed)

```text
/backend
  /Fro.Api            # ASP.NET Core Web API (HTTP endpoints)
  /Fro.Application    # Use cases, services, DTOs
  /Fro.Domain         # Domain model, entities, business rules
  /Fro.Infrastructure # EF Core, repositories, external services, Hangfire config
```

**Fro.Api**

- Defines HTTP endpoints (controllers or minimal APIs)
- Configures:
  - dependency injection container
  - middleware (logging, error handling, CORS, auth)
  - authentication & authorization
  - OpenAPI/Swagger
- References `Fro.Application` and `Fro.Infrastructure`

**Fro.Application**

- Application services (use cases)
- Commands, queries and DTOs
- Input validation (e.g. FluentValidation)
- Orchestrates domain operations and persistence
- Does **not** depend on ASP.NET Core primitives

**Fro.Domain**

- Domain entities and value objects
- Business rules and optimization logic
- Pure C# (no infrastructure concerns)
- Reusable between API and background workers

**Fro.Infrastructure**

- EF Core DbContext and entity mappings
- Repository implementations (database access)
- Redis integration (cache, distributed locks if needed)
- Hangfire configuration and background job handlers
- Integrations with external services (e.g. SMTP, file storage, external APIs)

---

### 2.3. Background Processing – Hangfire

Background tasks are handled by:

- **Library:** Hangfire
- **Storage:** Redis or SQL (depending on configuration)

Use cases:

- Long-running optimization tasks executed in the background
- Scheduling periodic tasks (e.g. cleanup, recurring calculations)
- Reliable retries and job history
- Dashboard for monitoring job status and performance

Job types:

- **Fire-and-forget** – started from HTTP API (e.g. “start optimization for project X”)
- **Delayed jobs** – deferred execution (e.g. re-run after cool-down)
- **Recurring jobs** – periodic tasks (e.g. nightly cleanup)

Implementation details:

- Job scheduling from application services in `Fro.Application`
- Job handlers (actual execution) implemented in `Fro.Infrastructure` or `Fro.Application`
- Hangfire server can run:
  - inside `Fro.Api` process, or
  - in a separate worker process (e.g. `Fro.Worker`)

---

### 2.4. Database

- **Engine:** MySQL
- **Access layer:** Entity Framework Core (EF Core)
- **Schema management:** EF Core migrations

Responsibilities:

- Store user accounts, roles and permissions
- Store projects, regenerator configuration, imported data
- Store optimization results and related metadata
- Store audit data (where applicable)

Schema strategy:

- The schema is initially based on the existing MySQL database used by the original backend.
- .NET model is created in:
  - **Database-first** mode (scaffold from existing DB), or
  - **Code-first** mode (recreate schema with EF Core migrations)
- Over time, schema changes are managed via EF Core migrations.

---

### 2.5. Cache & Messaging

- **Engine:** Redis

Use cases:

- Caching frequently used read-only data
- Hangfire storage (if configured to use Redis)
- Short-lived data (tokens, locks, temporary state)
- Optional: application-level distributed locking and coordination

Configuration:

- Connection string defined in backend configuration (`appsettings.json` / environment variables)
- Separate logical databases in Redis can be used for:
  - cache
  - jobs
  - other short-lived data

---

### 2.6. Reverse Proxy – Nginx

- **Engine:** Nginx

Responsibilities:

- Terminate HTTPS (TLS)
- Route requests to internal services
- Serve static assets (optional, if using static export from Next.js)
- Apply basic security headers

Routing example:

- `/` → Next.js frontend (port 3000) or static files
- `/api/` → `Fro.Api` backend (port 8000)

High-level path:

```text
Client (Browser)
    ↓
  Nginx
    ↓
+-----------+-----------------+
|           |                 |
Frontend (Next.js)      Backend (Fro.Api)
```

---

### 2.7. Monitoring & Logging

(Highly recommended, can be introduced gradually.)

Logging:

- ASP.NET Core built-in logging (console, files, external sinks)
- Structured logging (e.g. JSON) for easier aggregation

Metrics (optional):

- Prometheus + Grafana, or vendor-specific APM
- Typical metrics:
  - HTTP request count, duration, error rate
  - Background job counts (success/failure)
  - DB and Redis connectivity status
  - Resource usage (CPU, memory) from system or node exporter

---

## 3. Request & Data Flow

### 3.1. Typical user flow

1. **User** opens the frontend in a browser.
2. **Frontend** (Next.js) calls backend endpoints under `/api/...`:
   - authentication / authorization
   - project list and details
   - configuration read/write
   - start optimization
   - fetch optimization results
3. **Backend (Fro.Api)**:
   - authenticates the user
   - executes application services (`Fro.Application`)
   - uses `Fro.Domain` for business rules and calculations
   - persists data via EF Core in `Fro.Infrastructure`
   - optionally enqueues background jobs via Hangfire
4. **Background workers (Hangfire server)**:
   - pick up queued optimization jobs
   - run long-running optimization logic
   - store results back in MySQL
5. **Frontend**:
   - polls periodically or by user action to get updated results
   - displays results and allows further actions (e.g. export)

---

## 4. Environments

### 4.1. Development

Typical setup:

- **Frontend**
  - `pnpm dev` (Next.js dev server on port 3000)
- **Backend API**
  - `dotnet run` in `Fro.Api` (port 8000 by default)
  - Swagger UI available at `/swagger`
- **Background jobs**
  - Hangfire server started as part of `Fro.Api`
    or in a separate worker process
- **Dependencies**
  - MySQL and Redis installed locally
  - Configuration points to `localhost` services
- **Reverse proxy**
  - Optional; frontend can call `http://localhost:8000` directly

Configuration is typically handled via:

- `appsettings.Development.json`
- environment variables
- Next.js `.env.local`

---

### 4.2. Production (single server example)

Example deployment on a single Linux server:

- **Nginx**
  - Listens on ports 80/443
  - Proxies:
    - `/` → Next.js frontend (e.g. port 3000, or static files)
    - `/api/` → Fro.Api (port 8000)
  - Terminates HTTPS with TLS certificates

- **Frontend**
  - `pnpm build` + `pnpm start` (Next.js server) or static export
  - Runs as a system service (e.g. systemd unit)

- **Backend**
  - `Fro.Api` runs as a system service (systemd unit)
  - Hangfire server:
    - either part of `Fro.Api`
    - or in a separate worker service

- **Database & Cache**
  - MySQL and Redis as local system services or external managed services

- **Monitoring**
  - Logs forwarded to centralized storage
  - Optional Prometheus + Grafana or other APM solution

---

## 5. Migration Notes (from Python backend)

Historically, the system used:

- **Backend:** Python, FastAPI
- **Background tasks:** Celery + Redis
- **Database:** MySQL
- **Frontend:** Next.js (unchanged)

The migration strategy to .NET 8 is:

1. **Preserve external API contract**
   - Keep REST endpoints compatible where possible
   - Maintain stable request/response shapes
   - Keep MySQL schema compatible during transition

2. **Reimplement domain logic**
   - Move business rules and optimization algorithms into `Fro.Domain`
   - Recreate calculations and workflows in C#

3. **Replace Celery with Hangfire**
   - Map each Celery task to a Hangfire job
   - Use Redis (or SQL) as Hangfire storage
   - Ensure equivalent retry and scheduling behavior

4. **Incremental rollout**
   - Run the new .NET backend in parallel with the legacy backend
   - Gradually switch routes to the .NET backend (via configuration or Nginx)
   - After validation, fully decommission Python services

---

## 6. Configuration

Configuration is environment-specific and provided via:

- `appsettings.json` and `appsettings.{Environment}.json` for .NET
- Environment variables (connection strings, secrets)
- Next.js `.env` files for frontend API URLs and public settings

Key settings:

- **Database:**
  - MySQL connection string (host, database, user, password)
- **Redis:**
  - Redis connection string (host, database index, password if applicable)
- **Hangfire:**
  - Storage provider (Redis or SQL)
  - Dashboard endpoint and authorization
- **Authentication:**
  - JWT secret or identity provider configuration
- **Frontend:**
  - API base URLs (used by Next.js)

---

## 7. Security Considerations

- All external traffic should go through Nginx with HTTPS enabled.
- Sensitive data (DB passwords, JWT keys, Redis passwords, SMTP credentials) must never be stored in version control.
- Backend enforces:
  - authentication for protected endpoints
  - role/permission checks at application and/or controller level
  - input validation and output sanitization
- Database and Redis should not be accessible directly from the public internet.
- Regular security updates:
  - .NET runtime and NuGet dependencies
  - System packages (OS, MySQL, Redis, Nginx)
  - Frontend dependencies (pnpm packages)

---

