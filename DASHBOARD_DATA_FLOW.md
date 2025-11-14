# Analiza Przepływu Danych Dashboard

## 🔍 Problem: Dashboard używa symulowanych danych

### **Stan obecny:**

Dashboard (`MetricsDashboard.tsx`) **NIE POBIERA** danych z API - używa zahardkodowanych wartości.

---

## 📊 Źródła Danych Dashboard

### **1. Backend Endpoint (DOSTĘPNY)**

**Endpoint:** `GET /api/v1/reports/dashboard/metrics`

**Lokalizacja:** `backend/app/api/v1/endpoints/reports.py:31-40`

```python
@router.get("/dashboard/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard metrics for current user."""
    reporting_service = ReportingService(db)
    metrics = await reporting_service.get_dashboard_metrics(current_user.id)
    return metrics
```

### **2. Serwis Raportów** (`reporting_service.py:532-569`)

**Metoda:** `get_dashboard_metrics(user_id: str)`

**Rzeczywiste dane z bazy:**

| Metryka | Źródło | Zapytanie SQL |
|---------|--------|---------------|
| **total_optimizations** | `OptimizationJob` | `COUNT(*) WHERE user_id = ?` |
| **active_users** | `OptimizationJob` | `COUNT(DISTINCT user_id) WHERE created_at >= NOW() - 30 days` |
| **fuel_savings_total** | `OptimizationResult` + JOIN | `AVG(fuel_savings_percentage) WHERE user_id = ?` |
| **success_rate** | `OptimizationJob` | `COUNT(status='completed') / COUNT(*) * 100` |
| **co2_reduction_total** | ❌ Placeholder | `0` (TODO) |
| **system_uptime** | ❌ Placeholder | `99.5` (hardcoded) |
| **api_response_time_avg** | ❌ Placeholder | `150` (hardcoded) |
| **optimizations_this_month** | ❌ Placeholder | `0` (TODO) |

---

### **3. Frontend - MetricsDashboard.tsx** (`lines 77-106`)

**Problem:** Zakomentowano prawdziwe API call i używa symulacji

```typescript
// ❌ PROBLEM - linie 82-93:
const fetchMetrics = async () => {
    try {
        setLoading(true);
        setError(null);

        // In production, this would be:
        // const data = await ReportsAPI.getDashboard(); // ⚠️ ZAKOMENTOWANE!

        // For now, simulating with realistic data
        const simulatedMetrics: DashboardMetrics = {
            total_optimizations: 156,      // ❌ Fake
            active_users: 12,               // ❌ Fake
            fuel_savings_total: 11.8,       // ❌ Fake
            co2_reduction_total: 1250,      // ❌ Fake
            system_uptime: 99.5,            // ❌ Fake
            api_response_time_avg: 145,     // ❌ Fake
            optimizations_this_month: 28,   // ❌ Fake
            success_rate: 89.7              // ❌ Fake
        };

        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));

        setMetrics(simulatedMetrics);
        setLastRefresh(new Date());
    } catch (err) {
        console.error('Failed to fetch dashboard metrics:', err);
        setError('Failed to load dashboard metrics. Please try again.');
    } finally {
        setLoading(false);
    }
};
```

---

### **4. Dane Wykresów** (`lines 45-75`)

**Wszystkie wykresy używają fake data:**

```typescript
// ❌ Fake - trend optymalizacji
const optimizationTrends: ChartDataPoint[] = [
    { name: 'Jan', value: 12, success: 10 },
    { name: 'Feb', value: 19, success: 16 },
    // ...
];

// ❌ Fake - oszczędności paliwa
const fuelSavingsData: ChartDataPoint[] = [
    { name: 'Regenerator A', value: 12.5 },
    { name: 'Regenerator B', value: 8.3 },
    // ...
];

// ❌ Fake - zdrowie systemu
const systemHealthData: ChartDataPoint[] = [
    { name: 'API Response', value: 95 },
    { name: 'Database', value: 98 },
    // ...
];

// ❌ Fake - typy optymalizacji
const optimizationTypesData: ChartDataPoint[] = [
    { name: 'Fuel Efficiency', value: 45 },
    { name: 'Heat Transfer', value: 30 },
    // ...
];
```

---

## 🔄 Jak Dane Powinny Być Aktualizowane?

### **Mechanizm Auto-Refresh** (lines 120-129)

```typescript
// ✅ Mechanizm istnieje - odświeża co 30 sekund
useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
        fetchMetrics();  // Wywołuje funkcję z fake data!
    }, 30000);

    return () => clearInterval(interval);
}, [autoRefresh]);
```

**Problem:** Auto-refresh działa, ale pobiera **fake data** zamiast prawdziwych z API.

---

## 📈 Rzeczywiste Dane w Bazie (Przykład dla użytkownika admin)

```sql
-- Total optimizations
SELECT COUNT(*) FROM optimization_jobs
WHERE user_id = '64c41315-9eb5-4878-bcdb-3e943847e76f';
-- Wynik: 37 (15 completed, 15 cancelled, 7 failed)

-- Success rate
SELECT
    COUNT(CASE WHEN status = 'completed' THEN 1 END) * 100.0 / COUNT(*)
FROM optimization_jobs
WHERE user_id = '64c41315-9eb5-4878-bcdb-3e943847e76f';
-- Wynik: ~40.5% (15/37)

-- Fuel savings average
SELECT AVG(fuel_savings_percentage)
FROM optimization_results r
JOIN optimization_jobs j ON j.id = r.job_id
WHERE j.user_id = '64c41315-9eb5-4878-bcdb-3e943847e76f';
-- Wynik: zależy od wyników optymalizacji

-- Active users (last 30 days)
SELECT COUNT(DISTINCT user_id)
FROM optimization_jobs
WHERE created_at >= NOW() - INTERVAL 30 DAY;
-- Wynik: 1 (tylko admin)
```

---

## ⚠️ Braki w Implementacji Backend

### **Metryki z placeholder wartościami:**

1. **co2_reduction_total** - zawsze `0`
   - Powinno: `SUM(co2_reduction_percentage)` z `optimization_results`

2. **system_uptime** - zawsze `99.5` (hardcoded)
   - Powinno: Monitoring czasu działania serwera

3. **api_response_time_avg** - zawsze `150` (hardcoded)
   - Powinno: Middleware z logowaniem czasu odpowiedzi

4. **optimizations_this_month** - zawsze `0`
   - Powinno: `COUNT(*) WHERE created_at >= first_day_of_month`

### **Brakujące endpointy dla wykresów:**

1. **Trend optymalizacji** (line chart)
   - Brak: `GET /api/v1/analytics/optimization-trends?months=6`

2. **Oszczędności paliwa** (bar chart)
   - Brak: `GET /api/v1/analytics/fuel-savings-by-regenerator`

3. **Zdrowie systemu** (area chart)
   - Brak: `GET /api/v1/system/health`

4. **Typy optymalizacji** (pie chart)
   - Brak: `GET /api/v1/analytics/optimization-types-distribution`

---

## ✅ Rozwiązanie

### **Krok 1: Napraw frontend** (`MetricsDashboard.tsx`)

Zamień fake data na prawdziwy API call:

```typescript
const fetchMetrics = async () => {
    try {
        setLoading(true);
        setError(null);

        // ✅ Użyj prawdziwego API
        const data = await ReportsAPI.getDashboardMetrics();

        setMetrics(data);
        setLastRefresh(new Date());
    } catch (err) {
        console.error('Failed to fetch dashboard metrics:', err);
        setError('Failed to load dashboard metrics. Please try again.');
    } finally {
        setLoading(false);
    }
};
```

### **Krok 2: Dodaj metodę do API client** (`api-client.ts`)

```typescript
static async getDashboardMetrics() {
    return ApiClient.get('/reports/dashboard/metrics');
}
```

### **Krok 3: Uzupełnij backend - brakujące metryki**

```python
# reporting_service.py - get_dashboard_metrics()

# CO2 reduction total
co2_stmt = select(func.sum(OptimizationResult.co2_reduction_percentage)).join(
    OptimizationJob
).where(OptimizationJob.user_id == user_id)
co2_reduction_total = (await self.db.execute(co2_stmt)).scalar() or 0

# Optimizations this month
from datetime import date
first_day_of_month = date.today().replace(day=1)
month_count_stmt = select(func.count(OptimizationJob.id)).where(
    and_(
        OptimizationJob.user_id == user_id,
        OptimizationJob.created_at >= first_day_of_month
    )
)
optimizations_this_month = (await self.db.execute(month_count_stmt)).scalar()
```

### **Krok 4: (Opcjonalnie) Dodaj endpointy dla wykresów**

Przykład:
```python
@router.get("/analytics/optimization-trends")
async def get_optimization_trends(
    months: int = 6,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get optimization trends for last N months."""
    # Implementacja zapytania SQL z GROUP BY month
    pass
```

---

## 🎯 Podsumowanie

| Komponent | Status | Dane |
|-----------|--------|------|
| **Backend endpoint** | ✅ Działa | `/api/v1/reports/dashboard/metrics` |
| **Backend service** | ⚠️ Częściowo | 4/8 metryk z prawdziwymi danymi |
| **Frontend API call** | ❌ Nie używany | Zakomentowany, używa fake data |
| **Auto-refresh** | ✅ Działa | Co 30s (ale fake data) |
| **Wykresy** | ❌ Fake data | Brak endpointów backend |

**Wniosek:** Dashboard **NIE** pobiera danych z bazy - wszystko jest symulowane w kodzie frontendu.
