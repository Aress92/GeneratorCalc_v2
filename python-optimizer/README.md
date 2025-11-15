# FRO SLSQP Optimizer Microservice

Standalone Python microservice for regenerator optimization using the SLSQP (Sequential Least Squares Programming) algorithm.

## Overview

This microservice provides a REST API for optimizing regenerator configurations. It extracts the physics model and SLSQP optimization logic from the main backend, allowing it to run independently without Docker.

## Architecture

```
python-optimizer/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── physics_model.py     # Regenerator physics calculations
│   ├── optimizer.py         # SLSQP optimization algorithm
│   └── schemas.py           # Pydantic models for validation
├── requirements.txt
├── fro-optimizer.service    # systemd service configuration
└── README.md
```

## Installation

### 1. Create Virtual Environment

```bash
cd python-optimizer
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the Service

### Development Mode

```bash
# From python-optimizer directory
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 7000 --reload
```

### Production Mode (Direct)

```bash
# From python-optimizer directory
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 7000 --workers 4
```

### Production Mode (systemd service)

See **Systemd Service Setup** section below.

## API Endpoints

### Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "scipy_available": true
}
```

### Optimize

```bash
POST /optimize
```

Request body:
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
  "design_variables": {
    "checker_height": {},
    "checker_spacing": {},
    "wall_thickness": {}
  },
  "bounds": {
    "checker_height": {"min": 0.3, "max": 2.0},
    "checker_spacing": {"min": 0.05, "max": 0.3},
    "wall_thickness": {"min": 0.2, "max": 0.8}
  },
  "initial_values": {
    "checker_height": 0.5,
    "checker_spacing": 0.1,
    "wall_thickness": 0.3
  },
  "objective": "maximize_efficiency",
  "algorithm": "SLSQP",
  "max_iterations": 100,
  "tolerance": 1e-6
}
```

Response:
```json
{
  "success": true,
  "message": "Optimization terminated successfully",
  "iterations": 42,
  "final_objective_value": -0.8234,
  "optimized_design_variables": {
    "checker_height": 1.23,
    "checker_spacing": 0.12,
    "wall_thickness": 0.45
  },
  "performance_metrics": {
    "thermal_efficiency": 0.8234,
    "heat_transfer_rate": 45678.9,
    "pressure_drop": 1234.5,
    "ntu_value": 4.56,
    "effectiveness": 0.82,
    "heat_transfer_coefficient": 123.4,
    "surface_area": 5678.9,
    "wall_heat_loss": 12345.6,
    "reynolds_number": 1234.5,
    "nusselt_number": 23.4
  },
  "convergence_info": {
    "converged": true,
    "status": 0,
    "nfev": 42,
    "njev": 12,
    "nit": 42
  },
  "constraints_satisfied": true,
  "constraint_violations": null
}
```

### API Documentation

Interactive Swagger UI:
```
http://localhost:7000/docs
```

ReDoc:
```
http://localhost:7000/redoc
```

## Systemd Service Setup

### 1. Create Service File

Edit the service file to match your system paths:

```bash
sudo nano /etc/systemd/system/fro-optimizer.service
```

Content (adjust paths as needed):
```ini
[Unit]
Description=FRO SLSQP Optimizer Microservice
After=network.target

[Service]
Type=simple
User=fro
Group=fro
WorkingDirectory=/opt/fro/python-optimizer
Environment="PATH=/opt/fro/python-optimizer/venv/bin"
ExecStart=/opt/fro/python-optimizer/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 7000 --workers 4
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=fro-optimizer

[Install]
WantedBy=multi-user.target
```

### 2. Create User and Set Permissions

```bash
# Create system user
sudo useradd -r -s /bin/false fro

# Copy optimizer to /opt
sudo mkdir -p /opt/fro
sudo cp -r python-optimizer /opt/fro/

# Set permissions
sudo chown -R fro:fro /opt/fro/python-optimizer
```

### 3. Install and Enable Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable fro-optimizer

# Start service
sudo systemctl start fro-optimizer

# Check status
sudo systemctl status fro-optimizer
```

### 4. Service Management Commands

```bash
# Start
sudo systemctl start fro-optimizer

# Stop
sudo systemctl stop fro-optimizer

# Restart
sudo systemctl restart fro-optimizer

# Status
sudo systemctl status fro-optimizer

# Logs
sudo journalctl -u fro-optimizer -f
```

## Testing

### Test Health Endpoint

```bash
curl http://localhost:7000/health
```

### Test Optimization

```bash
curl -X POST http://localhost:7000/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "configuration": {
      "geometry_config": {"length": 10.0, "width": 8.0},
      "thermal_config": {"gas_temp_inlet": 1600, "gas_temp_outlet": 600},
      "flow_config": {"mass_flow_rate": 50, "cycle_time": 1200}
    },
    "design_variables": {
      "checker_height": {},
      "checker_spacing": {},
      "wall_thickness": {}
    },
    "bounds": {
      "checker_height": {"min": 0.3, "max": 2.0},
      "checker_spacing": {"min": 0.05, "max": 0.3},
      "wall_thickness": {"min": 0.2, "max": 0.8}
    },
    "initial_values": {
      "checker_height": 0.5,
      "checker_spacing": 0.1,
      "wall_thickness": 0.3
    },
    "objective": "maximize_efficiency",
    "algorithm": "SLSQP",
    "max_iterations": 100,
    "tolerance": 1e-6
  }'
```

## Integration with .NET Backend

The .NET backend (Fro.Api) calls this microservice via HTTP:

```csharp
// In OptimizationService.cs
var httpClient = new HttpClient();
var response = await httpClient.PostAsync(
    "http://localhost:7000/optimize",
    new StringContent(jsonRequest, Encoding.UTF8, "application/json")
);
```

## Logging

Logs are sent to systemd journal and can be viewed with:

```bash
# Follow logs in real-time
sudo journalctl -u fro-optimizer -f

# View last 100 lines
sudo journalctl -u fro-optimizer -n 100

# Filter by priority
sudo journalctl -u fro-optimizer -p err
```

## Troubleshooting

### Service won't start

Check logs:
```bash
sudo journalctl -u fro-optimizer -n 50
```

Common issues:
- Virtual environment path incorrect
- Port 7000 already in use
- Missing dependencies
- Permission issues

### Port already in use

Change port in service file or find conflicting process:
```bash
sudo lsof -i :7000
```

### Missing dependencies

Reinstall in virtual environment:
```bash
cd /opt/fro/python-optimizer
source venv/bin/activate
pip install -r requirements.txt
```

## Performance

- **Workers**: Configured for 4 workers (adjust based on CPU cores)
- **Expected response time**: 2-10 seconds for typical optimization (100 iterations)
- **Memory**: ~200-500 MB per worker
- **CPU**: High CPU usage during optimization (expected)

## Security Notes

- **No authentication**: Currently no auth. Add API keys or JWT if exposing to network.
- **CORS**: Currently allows all origins. Restrict in production.
- **Input validation**: Pydantic validates all inputs.
- **Error handling**: Detailed errors in development, sanitized in production.

## Future Improvements

- [ ] Add authentication (API keys or JWT)
- [ ] Add request rate limiting
- [ ] Add metrics and monitoring (Prometheus)
- [ ] Add caching for repeated optimizations
- [ ] Add async optimization with websockets for progress updates
- [ ] Add support for multiple algorithms (not just SLSQP)

## License

Proprietary - Forglass Regenerator Optimizer
