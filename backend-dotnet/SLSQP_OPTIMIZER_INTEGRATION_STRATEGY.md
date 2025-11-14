# SLSQP Optimizer Integration Strategy for .NET Backend

**Date:** 2025-11-14
**Status:** Design Phase
**Priority:** HIGH (Critical for functionality)

---

## Executive Summary

The Python backend uses **SciPy's SLSQP (Sequential Least Squares Programming)** optimizer for regenerator thermal optimization. This is a gradient-based constrained optimization algorithm critical to the application's core functionality. This document evaluates three integration strategies for the .NET migration.

---

## Current Python Implementation Analysis

### Key Components

1. **Physics Model** (`RegeneratorPhysicsModel`)
   - Thermal performance calculations
   - Heat transfer coefficients (Reynolds, Nusselt numbers)
   - Pressure drop calculations
   - Wall heat loss modeling
   - ~250 lines of physics equations

2. **Optimization Service** (`OptimizationService`)
   - SLSQP algorithm integration via `scipy.optimize.minimize()`
   - Objective function: Maximize thermal efficiency
   - Nonlinear constraints: Pressure drop, efficiency thresholds
   - Bounds: Physical parameter ranges (height, spacing, materials)
   - Progress tracking via callbacks

3. **Celery Background Jobs** (`optimization_tasks.py`)
   - Async task execution
   - Progress updates to job status
   - Iteration logging to database

### SLSQP Usage Details

```python
from scipy.optimize import minimize, NonlinearConstraint, Bounds

result = minimize(
    objective_function,          # f(x) → thermal_efficiency (negated)
    initial_guess,               # Starting point (6D vector)
    method='SLSQP',              # Sequential Least Squares Programming
    bounds=bounds,               # Variable bounds (min/max)
    constraints=[nonlinear_constraint],  # g(x) >= 0 constraints
    options={
        'maxiter': 100,          # Max iterations
        'ftol': 1e-6,            # Tolerance
        'disp': True             # Display progress
    }
)
```

**Design Variables (6 parameters):**
- `checker_height`: 0.3 - 2.0 m
- `checker_spacing`: 0.05 - 0.3 m
- `wall_thickness`: 0.2 - 0.8 m
- `thermal_conductivity`: 1.0 - 5.0 W/(m·K)
- `specific_heat`: 700 - 1200 J/(kg·K)
- `density`: 1800 - 2800 kg/m³

**Constraints:**
- Pressure drop < 2000 Pa
- Thermal efficiency > 20%
- Heat transfer coefficient > 50 W/(m²·K)

---

## Integration Options Evaluation

### Option 1: Python Microservice (RECOMMENDED ⭐)

**Architecture:**
```
.NET API Controller
    ↓ HTTP POST
Python Microservice (Flask/FastAPI)
    ↓ SLSQP
SciPy optimizer
    ↓ Results
.NET API (process results)
```

#### Advantages ✅
- **Zero algorithm risk** - Identical behavior to current production system
- **Fast implementation** - Extract existing Python code (~2 days)
- **Easy testing** - Compare results directly with Python backend
- **Maintainability** - Use proven SciPy library (actively maintained)
- **Expertise** - Team already familiar with Python optimizer

#### Disadvantages ❌
- **Additional service** - One more container in Docker Compose
- **Network latency** - HTTP call overhead (~10-50ms per optimization)
- **Deployment complexity** - Must deploy Python service alongside .NET

#### Implementation Estimate: **2-3 days**

**Tasks:**
1. Extract physics model + optimizer to standalone Python service (1 day)
2. Create Flask/FastAPI wrapper with `/optimize` endpoint (4 hours)
3. Implement .NET HttpClient integration (4 hours)
4. Docker container + docker-compose configuration (2 hours)
5. Testing and validation (1 day)

**Docker Setup:**
```yaml
services:
  optimizer-service:
    build: ./optimizer-service
    ports:
      - "5001:5001"
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - ./optimizer-service:/app
```

---

### Option 2: Math.NET Numerics (Alternative)

**Library:** [Math.NET Numerics](https://numerics.mathdotnet.com/)
**Algorithm:** `NelderMeadSimplex` or `BfgsMinimizer`

#### Advantages ✅
- **Pure .NET** - No external service required
- **Single deployment** - Everything in one process
- **NuGet package** - Easy dependency management
- **Good performance** - Native C# implementation

#### Disadvantages ❌
- **Different algorithm** - BFGS ≠ SLSQP (may converge differently)
- **Constraint handling** - Limited nonlinear constraint support
- **Testing burden** - Must validate against Python results extensively
- **Risk of divergence** - Results may differ from production system

#### Implementation Estimate: **4-6 days**

**Tasks:**
1. Research Math.NET Numerics API (1 day)
2. Port physics model to C# (1-2 days)
3. Implement optimization logic (1 day)
4. Extensive validation testing (2 days)
5. Handle edge cases and differences (variable)

**Code Sample:**
```csharp
using MathNet.Numerics.Optimization;

var objective = ObjectiveFunction.Value(x => CalculateObjective(x));
var solver = new BfgsMinimizer(1e-6, 1e-6, 1e-6, maxIterations: 100);
var result = solver.FindMinimum(objective, initialGuess);
```

**Critical Issue:** Math.NET doesn't have a direct SLSQP equivalent. BFGS is unconstrained, penalty methods required for constraints.

---

### Option 3: Python.NET Interop (Not Recommended ⚠️)

**Library:** [Python.NET](https://pythonnet.github.io/)
**Approach:** Call Python SciPy directly from C#

#### Advantages ✅
- **Same algorithm** - Uses actual SciPy SLSQP
- **No microservice** - Embedded Python in .NET process

#### Disadvantages ❌
- **Complex setup** - Python runtime + packages in .NET process
- **Deployment nightmare** - Python environment in Docker + .NET
- **Memory issues** - GIL (Global Interpreter Lock) contention
- **Marshaling overhead** - Converting between C# and Python types
- **Debugging hell** - Cross-language debugging extremely difficult
- **Version conflicts** - Managing Python dependencies in .NET context

#### Implementation Estimate: **1-2 weeks** (high risk)

---

## Recommendation: Python Microservice

### Why Python Microservice Wins

1. **Production Parity** - Same algorithm = same results (critical for optimization)
2. **Fastest to Market** - 2-3 days vs 4-6 days (Math.NET) or 2 weeks (Python.NET)
3. **Lowest Risk** - No algorithm validation needed, proven code
4. **Scalability** - Can scale optimizer service independently
5. **Future-Proof** - Easy to replace with C# later if needed

### Implementation Plan

#### Phase 1: Python Optimizer Service (2 days)

**Service Structure:**
```
optimizer-service/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app
│   ├── physics_model.py         # Copied from backend
│   ├── optimizer.py             # SLSQP wrapper
│   └── schemas.py               # Pydantic models
├── Dockerfile
├── requirements.txt             # scipy, fastapi, uvicorn
└── README.md
```

**API Endpoint:**
```python
POST /api/v1/optimize
Content-Type: application/json

Request:
{
  "design_variables": ["checker_height", "checker_spacing", ...],
  "bounds": {"checker_height": {"min": 0.3, "max": 2.0}, ...},
  "constraints": {...},
  "initial_guess": [1.0, 0.15, 0.5, 2.5, 900, 2300],
  "config": {
    "geometry_config": {...},
    "thermal_config": {...},
    "flow_config": {...},
    "materials_config": {...}
  },
  "options": {
    "max_iterations": 100,
    "tolerance": 1e-6,
    "objective": "MAXIMIZE_EFFICIENCY"
  }
}

Response:
{
  "success": true,
  "converged": true,
  "iterations": 47,
  "optimal_values": {
    "checker_height": 1.45,
    "checker_spacing": 0.12,
    ...
  },
  "performance": {
    "thermal_efficiency": 0.87,
    "heat_transfer_rate": 125000,
    "pressure_drop": 1450,
    ...
  },
  "message": "Optimization terminated successfully",
  "execution_time_seconds": 2.3
}
```

#### Phase 2: .NET Integration (1 day)

**Service Class:**
```csharp
// Fro.Infrastructure/Services/PythonOptimizerService.cs
public class PythonOptimizerService : IOptimizerService
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<PythonOptimizerService> _logger;

    public async Task<OptimizationResult> RunOptimizationAsync(
        OptimizationRequest request,
        CancellationToken cancellationToken)
    {
        var response = await _httpClient.PostAsJsonAsync(
            "/api/v1/optimize",
            request,
            cancellationToken);

        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<OptimizationResult>();
    }
}
```

**Hangfire Job:**
```csharp
// Fro.Infrastructure/Jobs/OptimizationJob.cs
public async Task ExecuteAsync(Guid jobId)
{
    var job = await _jobRepository.GetByIdAsync(jobId);
    var scenario = await _scenarioRepository.GetByIdAsync(job.ScenarioId);

    // Build request from job + scenario
    var request = BuildOptimizationRequest(job, scenario);

    // Call Python optimizer service
    var result = await _optimizerService.RunOptimizationAsync(request);

    // Save results to database
    await SaveOptimizationResults(jobId, result);
}
```

#### Phase 3: Docker Configuration (2 hours)

**docker-compose.yml update:**
```yaml
services:
  backend-dotnet:
    depends_on:
      - optimizer-service
    environment:
      - OptimizerService__BaseUrl=http://optimizer-service:5001

  optimizer-service:
    build: ./optimizer-service
    ports:
      - "5001:5001"
    environment:
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=INFO
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/health"]
      interval: 10s
      timeout: 5s
      retries: 3
```

#### Phase 4: Testing (1 day)

1. **Unit Tests:** Mock HTTP responses
2. **Integration Tests:** Run actual optimizer service
3. **Validation Tests:** Compare with Python backend results
4. **Performance Tests:** Measure latency and throughput

---

## Alternative: Future C# Migration Path

If later we want to eliminate the Python dependency, we can:

1. **Port physics model to C#** - Straightforward (1-2 days)
2. **Use CenterSpace NMath** - Commercial library with SLSQP ($$$)
3. **Implement SLSQP ourselves** - 2-3 weeks, high risk
4. **Use Google OR-Tools** - Has C# bindings, SLSQP-like algorithms

**Cost-Benefit:** Python microservice is cheaper and faster NOW. Migrate to pure C# later if needed (e.g., licensing requirements, performance issues).

---

## Performance Considerations

### Python Microservice Overhead

**Expected Latency:**
- HTTP request/response: ~10-50ms
- SLSQP optimization: ~2-5 seconds (100 iterations)
- **Total overhead:** <2% of optimization time

**Optimization Profile (100 iterations):**
- Network: 30ms
- Physics calculations: 2000ms (40ms/iteration × 50 avg)
- SLSQP algorithm: 500ms
- **Total: ~2.5 seconds**

### Scalability

- **Concurrent jobs:** Limited by Python GIL (1 job/process)
- **Solution:** Run multiple optimizer service instances
- **Docker scaling:** `docker-compose up --scale optimizer-service=4`

---

## Migration Risk Matrix

| Option | Algorithm Risk | Implementation Risk | Testing Burden | Time to Production |
|--------|----------------|---------------------|----------------|-------------------|
| **Python Microservice** | ✅ None (same code) | 🟡 Low (Docker) | ✅ Low (compare results) | ⭐ 2-3 days |
| **Math.NET Numerics** | 🔴 High (different algorithm) | 🟡 Medium (port code) | 🔴 High (validate extensively) | 🟡 4-6 days |
| **Python.NET** | ✅ None (same code) | 🔴 Very High (interop) | 🟡 Medium | 🔴 1-2 weeks |

---

## Decision: Python Microservice

**Rationale:**
1. **Speed to market:** 2-3 days vs weeks
2. **Zero algorithm risk:** Production-proven code
3. **Easy rollback:** Keep Python backend running during migration
4. **Independent scaling:** Optimize service can scale separately
5. **Future flexibility:** Can replace later if needed

**Next Steps:**
1. Create `optimizer-service/` directory
2. Extract `RegeneratorPhysicsModel` and `_run_slsqp_optimization` from Python backend
3. Wrap in FastAPI with `/optimize` endpoint
4. Implement .NET HttpClient integration
5. Add to docker-compose.yml
6. Test and validate

---

## Appendix: SLSQP Algorithm Details

**SLSQP (Sequential Least Squares Programming):**
- **Type:** Gradient-based constrained optimization
- **Best for:** Smooth, continuous objective functions with nonlinear constraints
- **Convergence:** Quadratic near optimum (very fast)
- **Constraints:** Supports equality and inequality constraints
- **Implementation:** Fortran code (proven, battle-tested since 1980s)

**Why it's perfect for this application:**
- Thermal physics equations are smooth and differentiable
- 6 design variables (manageable dimensionality)
- Nonlinear constraints (pressure drop, efficiency)
- Fast convergence (~50-100 iterations)

**Alternatives (for reference):**
- **Nelder-Mead:** Derivative-free, slower, no constraints
- **BFGS:** Unconstrained, requires penalty methods
- **COBYLA:** Constraint-friendly but slower convergence
- **Genetic Algorithms:** Global search, very slow (~1000s of evaluations)

---

**Document Status:** ✅ Complete
**Approved for Implementation:** Pending team review
**Estimated Timeline:** 2-3 days (Python microservice)
**Risk Level:** LOW

