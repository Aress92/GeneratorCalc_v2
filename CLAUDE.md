# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚀 Quick Reference

### Most Common Commands
```bash
# Start all services
docker compose up -d

# View logs (follow mode)
docker compose logs -f backend celery

# Run basic tests
docker compose exec backend python -m pytest tests/test_simple.py tests/test_models.py -v

# Restart services after code changes
docker compose restart backend celery celery-beat

# Health check
curl http://localhost:8000/health

# Stop all services
docker compose down
```

### Access Points
- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/api/v1/docs (Swagger UI)
- **Backend Health**: http://localhost:8000/health
- **Default Admin**: username: `admin` / password: `admin`

### Critical Files & Directories
```
CLAUDE.md                              # This file - development guide
backend/TEST_COVERAGE_ANALYSIS.md      # Detailed test coverage report
USER_GUIDE.md                          # End-user documentation
ARCHITECTURE.md                        # Technical architecture
backend/app/tasks/                     # Celery background tasks
backend/app/services/                  # Business logic layer
frontend/src/app/                      # Next.js pages
frontend/src/components/               # React components
```

### Quick Troubleshooting
```bash
# Services won't start?
docker compose ps                      # Check service status
docker compose logs mysql redis        # Check database/cache logs

# Backend can't connect to MySQL?
docker compose restart backend         # MySQL needs ~5s to be ready after restart

# Tests failing?
docker compose exec backend python -m pytest --collect-only  # See what tests exist
docker compose exec backend python -m pytest -vv --tb=long   # Verbose output

# Optimization jobs stuck?
docker compose exec celery celery -A app.celery inspect active  # Check active tasks
docker compose restart celery celery-beat                       # Restart workers

# Frontend compilation errors?
docker compose restart frontend        # Clear Next.js build cache
```

---

## ⚠️ Common Pitfalls (Read This First!)

### ❌ DON'T: Use Poetry commands in Docker containers
```bash
# WRONG - Poetry is not available in containers
docker compose exec backend poetry run pytest
docker compose exec backend poetry install
```
✅ **DO**: Use direct Python commands
```bash
# CORRECT
docker compose exec backend python -m pytest
docker compose exec backend pip install package-name
```

### ❌ DON'T: Use deprecated `datetime.utcnow()`
```python
# WRONG - Deprecated in Python 3.12+
expire = datetime.utcnow() + timedelta(hours=1)
```
✅ **DO**: Use timezone-aware `datetime.now(UTC)`
```python
# CORRECT
from datetime import datetime, UTC
expire = datetime.now(UTC) + timedelta(hours=1)
```

### ❌ DON'T: Import sonner in frontend (temporarily disabled)
```typescript
// WRONG - Package not in pnpm-lock.yaml
import { toast } from 'sonner';
```
✅ **DO**: Use temporary console.log fallback
```typescript
// CORRECT (until pnpm-lock.yaml is generated)
const toast = {
  success: (msg: string) => console.log('✅', msg),
  error: (msg: string) => console.error('❌', msg),
  warning: (msg: string) => console.warn('⚠️', msg),
};
```

### ❌ DON'T: Put viewport in metadata export (Next.js 14)
```typescript
// WRONG - Deprecated in Next.js 14
export const metadata: Metadata = {
  viewport: 'width=device-width, initial-scale=1',
};
```
✅ **DO**: Use separate viewport export
```typescript
// CORRECT
import type { Metadata, Viewport } from 'next';
export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
};
```

### ❌ DON'T: Compare UUID objects directly with database CHAR(36) fields
```python
# WRONG - UUID format mismatch
stmt = select(Model).where(Model.user_id == current_user.id)  # UUID object
```
✅ **DO**: Convert UUID to string first
```python
# CORRECT
user_id_str = str(current_user.id)
stmt = select(Model).where(Model.user_id == user_id_str)
```

### ❌ DON'T: Update database in Celery progress callbacks
```python
# WRONG - Creates event loop conflicts
def progress_callback(iteration, max_iter):
    job.current_iteration = iteration
    await db.commit()  # ❌ Event loop crash!
```
✅ **DO**: Only update Celery task state, save DB for task completion
```python
# CORRECT
def progress_callback(iteration, max_iter):
    self.update_state(state='PROGRESS', meta={'iteration': iteration})
    # DB update happens after task completes
```

### ❌ DON'T: Use `asyncio.get_event_loop()` in Celery tasks
```python
# WRONG - Returns closed loop
def celery_task():
    loop = asyncio.get_event_loop()  # ❌ RuntimeError: Event loop is closed
```
✅ **DO**: Create new event loop with `nest_asyncio`
```python
# CORRECT
import nest_asyncio
def celery_task():
    nest_asyncio.apply()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(async_function())
    finally:
        loop.close()
```

---

## Project Overview

Forglass Regenerator Optimizer (FRO) is an on-premise enterprise system for optimizing glass furnace regenerators to reduce fuel consumption by 5-15% and CO₂ emissions. Uses SLSQP optimization algorithm with advanced thermodynamic calculations.

**Current Status**: Production-ready MVP with all core modules complete (Import, Optimization Engine, Reporting, 3D Visualization, Materials Database, Interactive Dashboard).

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js       │    │   FastAPI       │    │   Celery        │
│   Frontend      │───▶│   Backend       │───▶│   Workers       │
│   (Port 3000)   │    │   (Port 8000)   │    │   (Background)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
          │                       │                       │
          └─────────────────┐     │           ┌───────────┘
                            │     │           │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx         │    │   MySQL 8.0     │    │   Redis 7       │
│   Reverse Proxy │    │   Database      │    │   Cache/Queue   │
│   (Port 80/443) │    │   (Port 3306)   │    │   (Port 6379)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**Data Flow**:
1. User interacts with Next.js frontend (React components, TypeScript)
2. Frontend calls FastAPI backend REST endpoints
3. Backend performs CRUD operations on MySQL database
4. Long-running tasks (optimization, reports) dispatched to Celery workers
5. Celery workers process jobs asynchronously, update job status in database
6. Redis serves as Celery broker (queue) and result backend
7. Frontend polls for job status updates via SSE or REST endpoints

**Technology Stack**:
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, React Three Fiber (3D viz)
- **Backend**: FastAPI, SQLAlchemy 2.0 (async), Pydantic V2, Alembic migrations
- **Workers**: Celery, Redis broker, SciPy (SLSQP optimizer), NumPy
- **Database**: MySQL 8.0 with utf8mb4 encoding
- **Cache/Queue**: Redis 7 (separate DBs for cache and Celery)
- **Deployment**: Docker Compose with health checks

---

## Essential Commands

### Quick Start
```bash
# Start all services
docker compose up -d

# Wait 30-60 seconds for MySQL to be ready, then apply migrations
docker compose exec backend alembic upgrade head

# Initialize materials database (103 standard materials)
docker compose exec backend python -c "
from app.services.materials_service import MaterialsService
from app.core.database import AsyncSessionLocal
import asyncio
async def init():
    async with AsyncSessionLocal() as db:
        service = MaterialsService(db)
        await service.initialize_default_materials()
asyncio.run(init())
"

# Create admin user (username: admin, password: admin)
docker compose exec backend python -c "
from app.core.security import get_password_hash
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
import asyncio
async def create_admin():
    async with AsyncSessionLocal() as db:
        user = User(
            username='admin',
            email='admin@forglass.com',
            full_name='Administrator',
            password_hash=get_password_hash('admin'),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(user)
        await db.commit()
asyncio.run(create_admin())
"

# Access points
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api/v1/docs
# Health check: curl http://localhost:8000/health
```

### Backend Development (Docker-based - RECOMMENDED)

```bash
# IMPORTANT: Poetry is NOT available in Docker containers
# Use direct python/alembic commands, not "poetry run ..."

# Run all stable tests
docker compose exec backend python -m pytest tests/test_simple.py tests/test_models.py -v --tb=short

# Run comprehensive service tests
docker compose exec backend python -m pytest tests/test_materials_service.py -v --tb=short
docker compose exec backend python -m pytest tests/test_optimization_service.py -v --tb=short
docker compose exec backend python -m pytest tests/test_regenerator_service.py -v --tb=short
docker compose exec backend python -m pytest tests/test_import_service.py -v --tb=short
docker compose exec backend python -m pytest tests/test_reporting_service.py -v --tb=short

# Run single test with coverage
docker compose exec backend python -m pytest tests/test_specific.py::test_function -v --cov=app

# TypeScript type checking (frontend)
cd frontend && npm run type-check
```

### Frontend Development

```bash
# Frontend logs (watch compilation)
docker compose logs frontend -f

# Restart frontend (clears Next.js cache)
docker compose restart frontend

# Access frontend shell
docker compose exec frontend sh
```

### Database Operations

```bash
# Create new migration
docker compose exec backend alembic revision --autogenerate -m "Description"

# Apply migrations
docker compose exec backend alembic upgrade head

# Rollback last migration
docker compose exec backend alembic downgrade -1

# View migration history
docker compose exec backend alembic history

# Direct MySQL access
docker compose exec mysql mysql -u fro_user -pfro_password fro_db
```

---

## Celery Background Tasks

**Architecture:** Redis-based message broker with separate worker processes

**Services:**
- `celery` - 4 concurrent workers for task execution
- `celery-beat` - Scheduler for periodic tasks
- `redis` - Broker (DB 1) and result backend (DB 2)

**Task Locations:**
```
backend/app/tasks/
├── optimization_tasks.py    # SLSQP optimization with progress tracking
├── import_export.py          # XLSX import/export jobs
├── reports.py                # PDF/Excel report generation
├── reporting_tasks.py        # Report generation tasks
└── maintenance.py            # Cleanup tasks (periodic)
```

**Monitoring:**
```bash
# View worker logs
docker compose logs celery --tail=50 -f

# Check task status in Redis
docker compose exec redis redis-cli
> SELECT 1  # Broker DB
> KEYS celery-task-*

# Inspect running tasks
docker compose exec celery celery -A app.celery inspect active

# Inspect scheduled tasks
docker compose exec celery celery -A app.celery inspect scheduled
```

**Progress Tracking:**
- Celery task updates state to 'PROGRESS' with meta dict
- OptimizationService calls `progress_callback(iteration, max_iter, obj_value)`
- Database updated with: current_iteration, progress_%, estimated_completion_at
- Frontend polls every 3s for real-time updates

---

## Known Issues

### Active Issues (2025-10-05)
- **Sonner toast notifications**: Temporarily disabled due to missing pnpm-lock.yaml
  - Current workaround: Console.log fallback in 6 files
  - TODO: Generate pnpm-lock.yaml and re-enable real toast notifications
- **Test coverage**: 42% current vs 80% target (-38% gap) - see `backend/TEST_COVERAGE_ANALYSIS.md`
  - ✅ Models/Schemas: 93-100% coverage (excellent)
  - ⚠️ Core utilities: 71-89% coverage (good)
  - ❌ Services layer: 9-25% coverage (critical gap - business logic)
  - ❌ Celery tasks: 0% coverage (need mocking strategy)
- **TypeScript errors**: 9 non-blocking type-checking warnings in frontend components
- **Three.js peer dependencies**: Some @react-three/drei sub-deps require newer Three.js (0.170+) but system works with 0.167.1 using `--legacy-peer-deps`

### Recently Fixed (2025-10-05) ✅
- ✅ **DateTime deprecation** - Fixed 32 instances across 10 production files + 1 migration
- ✅ **Sonner module errors** - Commented out imports, added console.log fallback
- ✅ **Next.js viewport warning** - Moved to separate `viewport` export
- ✅ **Backend MySQL connection** - Added restart after MySQL initialization
- ✅ **Frontend compilation** - All pages now compile without errors
- ✅ **All Docker services** - 6/6 containers healthy and operational

### Previously Resolved ✅
- ~~**Celery maintenance tasks crash**~~ → **FIXED**: Event loop handling with nest_asyncio (Oct 3, 2025)
- ~~**DateTime offset-naive/aware mismatch**~~ → **FIXED**: All datetime operations use `datetime.now(UTC)` (Oct 2, 2025)
- ~~**Physics model heat transfer**~~ → **FIXED**: Correct efficiency formula (Oct 2, 2025)
- ~~**SLSQP optimizer**~~ → **FIXED**: Removed restrictive 10% efficiency lower bound (Oct 2, 2025)
- ~~**UUID/String mapping**~~ → **FIXED**: Convert UUID to string before DB comparisons (Oct 1, 2025)
- ~~**Celery Task ID race condition**~~ → **FIXED**: Set ID only in task (Oct 1, 2025)

---

## System Status (Last Verified: 2025-10-05)

```bash
Docker Services: 6/6 healthy ✅
Backend API:     /health responding ✅
Frontend:        Compiling without errors ✅
MySQL:           Connected ✅
Redis:           Connected ✅
Celery:          4 workers active ✅
Tests:           11/11 passing ✅
Coverage:        42% (stable)
```

---

## Documentation

- **ARCHITECTURE.md**: Technical architecture, NFRs, system design
- **README.md**: Project overview, quick start guide
- **USER_GUIDE.md**: End-user documentation
- **VALIDATION_ERRORS.md**: 422 error handling implementation
- **backend/TEST_COVERAGE_ANALYSIS.md**: Detailed test coverage analysis and strategy
- **API Docs**: http://localhost:8000/api/v1/docs (Swagger UI)
