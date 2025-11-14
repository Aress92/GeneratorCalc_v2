# SLSQP Optimizer Microservice

**Standalone Python microservice for glass furnace regenerator thermal optimization using SciPy SLSQP algorithm.**

---

## Overview

This microservice provides HTTP API endpoints for running thermal optimization on glass furnace regenerators. It's designed to work with the .NET backend without requiring Docker.

### Features

- ✅ **SLSQP Optimization** - Sequential Least Squares Programming algorithm
- ✅ **Physics Model** - Complete thermal performance calculations
- ✅ **FastAPI** - Modern async Python web framework
- ✅ **No Docker Required** - Runs as standalone Python process
- ✅ **Production-Ready** - Logging, error handling, CORS support

---

## Prerequisites

- **Python 3.11+** (Python 3.10 also works)
- **pip** or **pip3** package manager

---

## Installation

### Step 1: Create Virtual Environment (Recommended)

```bash
cd optimizer-service
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `numpy` - Numerical computing
- `scipy` - Scientific computing (SLSQP algorithm)

---

## Running the Service

### Method 1: Using run.py (Recommended)

```bash
python run.py
```

**Custom host/port:**
```bash
python run.py --host 0.0.0.0 --port 8001
```

**Debug mode:**
```bash
python run.py --log-level DEBUG
```

### Method 2: Direct uvicorn

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8001
```

### Method 3: With auto-reload (Development)

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

---

## Verifying Installation

### Check Health Endpoint

```bash
curl http://localhost:8001/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "message": "SLSQP Optimizer Microservice is running"
}
```

### Access API Documentation

Open in browser: **http://localhost:8001/docs**

This opens interactive Swagger UI with all available endpoints.

---

## API Endpoints

### 1. Health Check

**GET /health**

Returns service health status.

```bash
curl http://localhost:8001/health
```

---

### 2. Run Optimization

**POST /api/v1/optimize**

Run SLSQP optimization for regenerator configuration.

**Request Body:**
```json
{
  "configuration": {
    "geometry_config": {
      "length": 10.0,
      "width": 8.0
    },
    "thermal_config": {
      "gas_temp_inlet": 1600,
      "gas_temp_outlet": 600
    },
    "flow_config": {
      "mass_flow_rate": 50,
      "cycle_time": 1200
    }
  },
  "initial_guess": {
    "checker_height": 0.5,
    "checker_spacing": 0.1,
    "wall_thickness": 0.3
  },
  "objective_type": "minimize_fuel_consumption",
  "max_iterations": 100,
  "tolerance": 0.000001
}
```

**Example with curl:**
```bash
curl -X POST http://localhost:8001/api/v1/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "configuration": {
      "geometry_config": {"length": 10.0, "width": 8.0},
      "thermal_config": {"gas_temp_inlet": 1600, "gas_temp_outlet": 600},
      "flow_config": {"mass_flow_rate": 50, "cycle_time": 1200}
    },
    "initial_guess": {
      "checker_height": 0.5,
      "checker_spacing": 0.1,
      "wall_thickness": 0.3
    },
    "objective_type": "minimize_fuel_consumption",
    "max_iterations": 100,
    "tolerance": 0.000001
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Optimization terminated successfully",
  "final_design_variables": {
    "checker_height": 0.85,
    "checker_spacing": 0.12,
    "wall_thickness": 0.35,
    "thermal_conductivity": 2.8,
    "specific_heat": 950,
    "density": 2350
  },
  "final_performance": {
    "thermal_efficiency": 0.89,
    "heat_transfer_rate": 55000000,
    "pressure_drop": 1850,
    "ntu_value": 8.5,
    "effectiveness": 0.895,
    "heat_transfer_coefficient": 125.5,
    "surface_area": 4200,
    "wall_heat_loss": 80000,
    "reynolds_number": 2500,
    "nusselt_number": 45.3
  },
  "objective_value": -0.89,
  "iterations": 45,
  "convergence_reached": true,
  "computation_time_seconds": 3.25
}
```

---

### 3. Calculate Performance

**POST /api/v1/performance**

Calculate thermal performance for given design variables (no optimization).

**Request Body:**
```json
{
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
}
```

**Response:**
```json
{
  "thermal_efficiency": 0.85,
  "heat_transfer_rate": 52000000,
  "pressure_drop": 1650,
  "ntu_value": 7.8,
  "effectiveness": 0.886,
  "heat_transfer_coefficient": 118.2,
  "surface_area": 3800,
  "wall_heat_loss": 95000,
  "reynolds_number": 2300,
  "nusselt_number": 42.5
}
```

---

## Integration with .NET API

The .NET `OptimizationService` communicates with this microservice via HTTP.

### .NET Configuration (appsettings.json)

```json
{
  "OptimizerService": {
    "BaseUrl": "http://localhost:8001",
    "TimeoutSeconds": 300
  }
}
```

### .NET HttpClient Call

```csharp
var optimizerUrl = "http://localhost:8001/api/v1/optimize";
var response = await _httpClient.PostAsJsonAsync(optimizerUrl, request);
var result = await response.Content.ReadFromJsonAsync<OptimizationResult>();
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPTIMIZER_HOST` | `127.0.0.1` | Host to bind to |
| `OPTIMIZER_PORT` | `8001` | Port to bind to |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

### CORS Origins

Edit `app/config.py` to add allowed origins:

```python
CORS_ORIGINS: list = [
    "http://localhost:5000",   # .NET API
    "http://localhost:8000",   # Python API
    "http://localhost:3000",   # Frontend
]
```

---

## Project Structure

```
optimizer-service/
├── app/
│   ├── __init__.py       # Package initialization
│   ├── main.py           # FastAPI app & endpoints
│   ├── models.py         # Pydantic request/response models
│   ├── optimizer.py      # Physics model + SLSQP optimizer
│   └── config.py         # Configuration
├── requirements.txt      # Python dependencies
├── run.py                # Startup script
└── README.md             # This file
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'app'"

**Solution:** Run from `optimizer-service/` directory:
```bash
cd optimizer-service
python run.py
```

### Issue: "Address already in use"

**Solution:** Port 8001 is occupied, use different port:
```bash
python run.py --port 8002
```

### Issue: scipy/numpy installation fails

**Solution:** Install system dependencies (Linux):
```bash
sudo apt-get update
sudo apt-get install python3-dev build-essential
pip install -r requirements.txt
```

**Solution (Mac):**
```bash
brew install gcc
pip install -r requirements.txt
```

### Issue: Connection refused from .NET API

**Solution:** Check firewall allows port 8001:
```bash
# Linux
sudo ufw allow 8001

# Test connection
curl http://localhost:8001/health
```

---

## Development

### Running Tests (to be added)

```bash
pytest tests/
```

### Linting

```bash
pip install ruff
ruff check app/
```

### Type Checking

```bash
pip install mypy
mypy app/
```

---

## Performance

- **Typical optimization time:** 2-10 seconds (depends on convergence)
- **Max iterations:** Configurable (default 100)
- **Memory usage:** ~200 MB per optimization job
- **Concurrent requests:** Supports multiple simultaneous optimizations

---

## Deployment

### Production Recommendations

1. **Use a process manager:**
   ```bash
   pip install supervisor
   # or
   systemctl (systemd service)
   ```

2. **Enable HTTPS** (if exposed externally):
   - Use nginx as reverse proxy
   - Terminate SSL at nginx level

3. **Resource limits:**
   - Set CPU/memory limits in systemd unit
   - Monitor with Prometheus/Grafana

4. **Logging:**
   - Redirect logs to file or syslog
   - Use structured logging for production

---

## API Documentation

- **Swagger UI:** http://localhost:8001/docs (interactive)
- **ReDoc:** http://localhost:8001/redoc (read-only)
- **OpenAPI JSON:** http://localhost:8001/openapi.json

---

## License

Proprietary - Forglass

---

## Support

For issues or questions:
- Check logs: `tail -f optimizer.log`
- Verify health: `curl http://localhost:8001/health`
- Review .NET API logs for connection errors

---

**Status:** Ready for Testing
**Version:** 1.0.0
**Last Updated:** 2025-11-14
