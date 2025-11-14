# Microservices Architecture - Setup Guide

**Running .NET API + Python Optimizer without Docker**

---

## Overview

The system now uses a **microservices architecture** with two standalone processes:

1. **.NET API** (port 5000) - Main backend API
2. **Python Optimizer Service** (port 8001) - SLSQP optimization microservice

Both run as **local processes** without Docker, communicating via HTTP.

---

## Architecture Diagram

```
┌─────────────────┐      HTTP          ┌──────────────────────┐
│                 │   (localhost:8001)  │                      │
│   .NET API      ├────────────────────►│  Python Optimizer    │
│  (port 5000)    │   OptimizeAsync()   │  Service (port 8001) │
│                 │◄────────────────────┤                      │
│  OptimizationService                  │  - RegeneratorPhysicsModel │
│  + OptimizerHttpClient               │  - SLSQPOptimizer    │
└─────────────────┘                     └──────────────────────┘
        │                                          │
        │                                          │
        ▼                                          ▼
  ┌──────────┐                               ┌──────────┐
  │  MySQL   │                               │  FastAPI │
  │ (3306)   │                               │  + scipy │
  └──────────┘                               └──────────┘
```

---

## Prerequisites

### For .NET API

- **.NET SDK 8.0** - [Download](https://dotnet.microsoft.com/download/dotnet/8.0)
- **MySQL 8.0** - Running on localhost:3306
- **(Optional) Redis** - For Hangfire background jobs

### For Python Optimizer

- **Python 3.11+** (Python 3.10 also works)
- **pip** package manager

---

## Quick Start (Step by Step)

### Step 1: Start MySQL

```bash
# If using Docker
docker run -d --name mysql-fro \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=fro_db \
  -e MYSQL_USER=fro_user \
  -e MYSQL_PASSWORD=fro_password \
  -p 3306:3306 \
  mysql:8.0

# Or start native MySQL service
systemctl start mysql    # Linux
brew services start mysql  # Mac
net start MySQL80          # Windows
```

---

### Step 2: Start Python Optimizer Service

Open **Terminal 1**:

```bash
cd optimizer-service

# Linux/Mac
./start.sh

# Windows
start.bat
```

**Expected output:**
```
╔═══════════════════════════════════════════════════════════╗
║  SLSQP Optimizer Microservice Startup                     ║
╚═══════════════════════════════════════════════════════════╝

[1/5] Checking Python version...
✓ Python 3.11.5 found

[2/5] Checking virtual environment...
✓ Virtual environment found

[3/5] Activating virtual environment...
✓ Virtual environment activated

[4/5] Installing dependencies...
✓ Dependencies installed

[5/5] Starting optimizer service...

╔═══════════════════════════════════════════════════════════╗
║  Service Starting...                                      ║
║  API Docs: http://127.0.0.1:8001/docs                     ║
║  Health: http://127.0.0.1:8001/health                     ║
║  Press Ctrl+C to stop                                     ║
╚═══════════════════════════════════════════════════════════╝

INFO:     Started server process
INFO:     Uvicorn running on http://127.0.0.1:8001
```

**Verify:**
```bash
curl http://localhost:8001/health
# Expected: {"status":"healthy","version":"1.0.0",...}
```

---

### Step 3: Start .NET API

Open **Terminal 2**:

```bash
cd backend-dotnet/Fro.Api
dotnet restore
dotnet build
dotnet run
```

**Expected output:**
```
info: Microsoft.Hosting.Lifetime[14]
      Now listening on: http://localhost:5000
✓ Connected to database
✓ Database is up to date
✓ Hangfire configured with Redis storage
Application started. Press Ctrl+C to shut down.
```

**Verify:**
```bash
curl http://localhost:5000/health
# Expected: {"status":"healthy","timestamp":"...","version":"1.0.0"}
```

---

### Step 4: Test Integration

Open **Terminal 3** or Browser:

**1. Access Swagger UIs:**
- .NET API: http://localhost:5000/api/docs
- Python Optimizer: http://localhost:8001/docs

**2. Test Python optimizer directly:**
```bash
curl -X POST http://localhost:8001/api/v1/performance \
  -H "Content-Type: application/json" \
  -d '{
    "configuration": {
      "geometry_config": {"length": 10.0, "width": 8.0},
      "thermal_config": {"gas_temp_inlet": 1600, "gas_temp_outlet": 600},
      "flow_config": {"mass_flow_rate": 50, "cycle_time": 1200}
    },
    "design_variables": {
      "checker_height": 0.5,
      "checker_spacing": 0.1,
      "wall_thickness": 0.3
    }
  }'
```

**Expected:** Performance metrics JSON response

**3. Test full optimization flow via .NET API:**
- Register/Login via .NET API
- Create regenerator configuration
- Create optimization scenario
- Start optimization job
- .NET API will call Python service internally

---

## Configuration

### .NET API Configuration

**File:** `backend-dotnet/Fro.Api/appsettings.json`

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost;Port=3306;Database=fro_db;User=fro_user;Password=fro_password;",
    "Redis": "localhost:6379,abortConnect=false"
  },
  "OptimizerService": {
    "BaseUrl": "http://localhost:8001",
    "TimeoutSeconds": 300,
    "RetryCount": 3,
    "RetryDelaySeconds": 2
  }
}
```

### Python Optimizer Configuration

**File:** `optimizer-service/app/config.py`

```python
class Settings:
    HOST: str = os.getenv("OPTIMIZER_HOST", "127.0.0.1")
    PORT: int = int(os.getenv("OPTIMIZER_PORT", "8001"))
    CORS_ORIGINS: list = [
        "http://localhost:5000",   # .NET API
        "http://localhost:8000",   # Python API (legacy)
        "http://localhost:3000",   # Frontend
    ]
```

---

## Ports Used

| Service | Port | Protocol | Access |
|---------|------|----------|--------|
| .NET API | 5000 | HTTP | http://localhost:5000 |
| Python Optimizer | 8001 | HTTP | http://localhost:8001 |
| MySQL | 3306 | TCP | localhost only |
| Redis (optional) | 6379 | TCP | localhost only |
| Frontend | 3000 | HTTP | http://localhost:3000 |

---

## Troubleshooting

### Issue 1: "Connection refused" from .NET to Python service

**Symptoms:** .NET API logs show `Failed to communicate with optimizer service`

**Solutions:**

1. **Check Python service is running:**
   ```bash
   curl http://localhost:8001/health
   ```

2. **Check port 8001 is not blocked:**
   ```bash
   # Linux
   sudo ufw allow 8001

   # Check if port is listening
   netstat -an | grep 8001
   lsof -i :8001
   ```

3. **Verify configuration:**
   - .NET `appsettings.json` → `OptimizerService:BaseUrl` = `http://localhost:8001`
   - Python `app/config.py` → `PORT` = `8001`

---

### Issue 2: Python service won't start - "Address already in use"

**Solution:** Port 8001 is occupied

```bash
# Find process using port 8001
lsof -i :8001  # Linux/Mac
netstat -ano | findstr :8001  # Windows

# Kill the process or use different port
python run.py --port 8002
```

Update .NET config to match:
```json
"OptimizerService": {
  "BaseUrl": "http://localhost:8002"
}
```

---

### Issue 3: Optimization times out

**Symptoms:** .NET logs show `Optimization request timed out`

**Solutions:**

1. **Increase timeout in .NET config:**
   ```json
   "OptimizerService": {
     "TimeoutSeconds": 600
   }
   ```

2. **Reduce max iterations in optimization request:**
   ```json
   {
     "max_iterations": 50,
     "tolerance": 0.00001
   }
   ```

---

### Issue 4: scipy/numpy installation fails (Python)

**Linux:**
```bash
sudo apt-get update
sudo apt-get install python3-dev build-essential
cd optimizer-service
pip install -r requirements.txt
```

**Mac:**
```bash
brew install gcc
cd optimizer-service
pip install -r requirements.txt
```

**Windows:**
- Install Visual Studio Build Tools
- Or use pre-built wheels: `pip install --only-binary :all: scipy numpy`

---

### Issue 5: .NET API can't find OptimizerHttpClient

**Symptoms:** Build error or DI resolution error

**Solution:** Verify registration in `Fro.Application/DependencyInjection.cs`:

```csharp
services.AddHttpClient<OptimizerHttpClient>()
    .ConfigureHttpClient(client => { ... });

services.AddScoped<OptimizerHttpClient>(...);
```

---

## Development Workflow

### Python Development (with auto-reload)

```bash
cd optimizer-service
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

Changes to Python code will auto-reload the service.

### .NET Development (with auto-reload)

```bash
cd backend-dotnet/Fro.Api
dotnet watch run
```

Changes to C# code will trigger automatic rebuild and restart.

---

## Stopping Services

### Stop Python Optimizer

In Terminal 1 (where optimizer is running):
- Press `Ctrl+C`

### Stop .NET API

In Terminal 2 (where .NET API is running):
- Press `Ctrl+C`

### Stop MySQL

```bash
# Docker
docker stop mysql-fro

# Native
systemctl stop mysql    # Linux
brew services stop mysql  # Mac
net stop MySQL80          # Windows
```

---

## Performance Notes

### Python Optimizer

- **Typical optimization time:** 2-10 seconds
- **Memory usage:** ~200 MB per optimization
- **Concurrent requests:** Supported (FastAPI async)
- **CPU usage:** High during optimization (scipy uses native code)

### .NET API

- **HTTP overhead:** ~10-50 ms per request to Python service
- **Total optimization time:** Python time + HTTP overhead
- **Timeout default:** 300 seconds (5 minutes)

---

## Production Deployment

### Recommended Setup

1. **Process managers:**
   - **Python:** systemd service or supervisor
   - **.NET:** systemd service or IIS

2. **Reverse proxy:**
   - Nginx in front of both services
   - Terminate SSL at nginx level

3. **Monitoring:**
   - Health check endpoints
   - Prometheus + Grafana for metrics
   - Centralized logging (syslog, ELK stack)

4. **High availability:**
   - Multiple Python optimizer instances (load balanced)
   - Single .NET API instance (or multiple with shared MySQL)

---

## Example systemd Services

### Python Optimizer Service

**File:** `/etc/systemd/system/optimizer-service.service`

```ini
[Unit]
Description=SLSQP Optimizer Microservice
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/optimizer-service
ExecStart=/opt/optimizer-service/venv/bin/python run.py
Restart=always
RestartSec=10
Environment="OPTIMIZER_HOST=0.0.0.0"
Environment="OPTIMIZER_PORT=8001"

[Install]
WantedBy=multi-user.target
```

### .NET API Service

**File:** `/etc/systemd/system/fro-api.service`

```ini
[Unit]
Description=Forglass Regenerator Optimizer API
After=network.target mysql.service

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/fro-api
ExecStart=/usr/bin/dotnet Fro.Api.dll
Restart=always
RestartSec=10
Environment="ASPNETCORE_ENVIRONMENT=Production"
Environment="ASPNETCORE_URLS=http://localhost:5000"

[Install]
WantedBy=multi-user.target
```

---

## Security Considerations

1. **Firewall:** Only expose Nginx (80/443) to public, keep 5000/8001 internal
2. **Authentication:** Python service should only accept requests from .NET API
3. **Network:** Use private network or VPN between services in production
4. **Secrets:** Never commit connection strings or API keys to git
5. **HTTPS:** Always use HTTPS in production (terminate at nginx)

---

## Next Steps

1. **Test full optimization workflow** via .NET API Swagger
2. **Monitor logs** for any communication errors
3. **Measure performance** (optimization times, memory usage)
4. **Write integration tests** for .NET ↔ Python communication
5. **Set up systemd services** for production deployment

---

## Resources

- **Python Optimizer README:** `optimizer-service/README.md`
- **.NET API Testing Guide:** `backend-dotnet/QUICK_START_TESTING.md`
- **Architecture Documentation:** `ARCHITECTURE.md`
- **Project Overview:** `CLAUDE.md`

---

**Status:** ✅ Ready for Testing
**Version:** 1.0.0
**Last Updated:** 2025-11-14
