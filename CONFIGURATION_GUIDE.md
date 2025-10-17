# Przewodnik Konfiguracji Regeneratorów

## Dostępne Konfiguracje Bazowe

System zawiera **8 konfiguracji bazowych** (3 oryginalne + 5 szablonów):

### Szablony Domyślne (Dostępne od razu)

1. **Szablon: Regenerator koronowy - mały**
   - Dla pieców: 50-100 ton/dzień
   - Geometria: 8.0m × 6.0m × 10.0m
   - Wysokość checkerów: 8.5m
   - Przepływ: 40 kg/s
   - Sprawność: 85%
   - Materiał: Silica brick (96% SiO₂)

2. **Szablon: Regenerator koronowy - średni**
   - Dla pieców: 100-250 ton/dzień
   - Geometria: 12.0m × 9.0m × 14.0m
   - Wysokość checkerów: 12.0m
   - Przepływ: 65 kg/s
   - Sprawność: 87%
   - Materiał: High-alumina brick (65% Al₂O₃)

3. **Szablon: Regenerator koronowy - duży**
   - Dla pieców: 250-500 ton/dzień
   - Geometria: 16.0m × 12.0m × 18.0m
   - Wysokość checkerów: 15.5m
   - Przepływ: 100 kg/s
   - Sprawność: 90%
   - Materiał: Magnesia-alumina brick

4. **Szablon: Regenerator czołowy (end-port)**
   - Dla pieców szklarskich
   - Geometria: 10.0m × 8.0m × 12.0m
   - Wysokość checkerów: 10.0m
   - Przepływ: 55 kg/s
   - Sprawność: 86%
   - Materiał: Silica brick (96% SiO₂)

5. **Szablon: Regenerator poprzeczny (cross-fired)**
   - Dla specjalistycznych zastosowań
   - Geometria: 11.0m × 9.0m × 13.0m
   - Wysokość checkerów: 11.0m
   - Przepływ: 58 kg/s
   - Sprawność: 85.5%
   - Materiał: Alumina brick (50% Al₂O₃)

---

## Jak Utworzyć Własną Konfigurację Bazową?

### Krok 1: Przejdź do Kreatora Konfiguracji

**Menu:** Dashboard → **Konfigurator** (lub `/configurator`)

**Wymagane uprawnienia:** ENGINEER lub ADMIN

### Krok 2: Wypełnij 7-etapowy formularz

#### **Etap 1: Podstawowe informacje**
- **Nazwa**: Unikalna nazwa konfiguracji (np. "Piec 3 - Regenerator prawy")
- **Opis**: Szczegółowy opis zastosowania

#### **Etap 2: Typ regeneratora**
Wybierz typ:
- `crown` - Regenerator koronowy (Crown regenerator)
- `end_port` - Regenerator czołowy (End-port regenerator)
- `cross_fired` - Regenerator poprzeczny (Cross-fired regenerator)

#### **Etap 3: Geometria**
- **Długość** (length): 8-20 m
- **Szerokość** (width): 6-15 m
- **Wysokość całkowita** (height): 10-20 m
- **Wysokość checkerów** (checker_height): 8-18 m

#### **Etap 4: Materiały**
Wybierz materiały z bazy danych (103 materiały):
- **Materiał checkerów**: Cegła ogniotrwała dla wypełnienia
- **Materiał ścian**: Cegła ogniotrwała dla izolacji

**Popularne materiały:**
- Silica brick (96% SiO₂) - dla T < 1650°C
- High-alumina brick (65% Al₂O₃) - dla T < 1700°C
- Magnesia brick - dla T > 1700°C

#### **Etap 5: Warunki pracy**
- **Przepływ powietrza** (air_flow_rate): 15,000-80,000 Nm³/h
- **Przepływ gazu** (gas_flow_rate): 20,000-90,000 Nm³/h
- **Temp. powietrza wlot** (air_inlet_temp): 150-300°C
- **Temp. gazu wlot** (gas_inlet_temp): 1400-1600°C
- **Ciśnienie projektowe** (design_pressure): 2000-4000 Pa

#### **Etap 6: Właściwości termiczne**
- **Docelowa sprawność** (target_efficiency): 80-95%
- **Max temp. operacyjna** (max_operating_temp): 1500-1750°C
- **Limit spadku ciśnienia** (pressure_drop_limit): 3000-7000 Pa

#### **Etap 7: Podsumowanie**
Przegląd wszystkich danych przed zapisem.

### Krok 3: Zapisz konfigurację

**Przycisk:** "Zapisz konfigurację"

**Wynik:**
- Konfiguracja zapisana w bazie danych
- Status: `completed`
- Dostępna natychmiast w module optymalizacji

---

## Jak Użyć Konfiguracji w Optymalizacji?

### 1. Przejdź do modułu optymalizacji
`/optimize` → Zakładka "Scenariusze"

### 2. Utwórz nowy scenariusz
Kliknij **"Nowy scenariusz"**

### 3. Wybierz konfigurację bazową
W polu **"Base Configuration"** wybierz swoją konfigurację z listy rozwijanej:
- Szablony (5 domyślnych)
- Twoje własne konfiguracje

### 4. Zdefiniuj zmienne optymalizacji
Przykład:
```json
{
  "checker_height": {
    "min_value": 0.3,
    "max_value": 2.0,
    "baseline_value": 0.5
  },
  "checker_spacing": {
    "min_value": 0.05,
    "max_value": 0.3,
    "baseline_value": 0.1
  }
}
```

### 5. Uruchom optymalizację
Kliknij **"Uruchom optymalizację"** → system zoptymalizuje parametry

---

## Sprawdzanie Dostępnych Konfiguracji

### Przez API (Backend)
```bash
docker compose exec backend python -c "
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.regenerator import RegeneratorConfiguration
from sqlalchemy import select

async def list_configs():
    async with AsyncSessionLocal() as db:
        stmt = select(RegeneratorConfiguration).order_by(
            RegeneratorConfiguration.created_at.desc()
        )
        result = await db.execute(stmt)
        configs = result.scalars().all()

        print(f'\nTotal configurations: {len(configs)}\n')
        for config in configs:
            template_flag = '[SZABLON]' if config.is_template else ''
            print(f'{template_flag} {config.name}')
            print(f'  ID: {config.id}')
            print(f'  Type: {config.regenerator_type}')
            print(f'  Status: {config.status}')
            print('-' * 60)

asyncio.run(list_configs())
"
```

### Przez Dashboard (Frontend)
1. Przejdź do `/optimize`
2. Kliknij "Nowy scenariusz"
3. Pole "Base Configuration" pokaże wszystkie dostępne konfiguracje

---

## Typowe Problemy i Rozwiązania

### Problem: "Brak konfiguracji bazowych w liście"

**Przyczyna:** Szablony nie zostały załadowane do bazy

**Rozwiązanie:**
```bash
docker compose exec backend python -m app.tasks.seed_templates
```

### Problem: "Scenario not found" przy tworzeniu zadania optymalizacji

**Przyczyna:** Nie wybrano konfiguracji bazowej

**Rozwiązanie:**
1. Edytuj scenariusz
2. Wybierz konfigurację w polu "Base Configuration"
3. Zapisz scenariusz
4. Spróbuj ponownie uruchomić optymalizację

### Problem: "BASE_CONFIG_NOT_FOUND" podczas uruchamiania optymalizacji

**Przyczyna:** Konfiguracja bazowa została usunięta z bazy

**Rozwiązanie:**
1. Utwórz nową konfigurację w Kreatorze
2. Lub użyj jednego z 5 szablonów domyślnych
3. Edytuj scenariusz i wybierz nową konfigurację bazową

---

## Przykładowe Wartości Referencyjne

### Mały piec szklarski (50-100 ton/dzień)
```
Geometria: 8×6×10m (checker: 8.5m)
Przepływ: 40 kg/s (20k/25k Nm³/h)
Temperatura: 1450°C → 600°C
Sprawność: 85%
Ciśnienie: 2500 Pa
```

### Średni piec szklarski (100-250 ton/dzień)
```
Geometria: 12×9×14m (checker: 12m)
Przepływ: 65 kg/s (35k/40k Nm³/h)
Temperatura: 1500°C → 550°C
Sprawność: 87%
Ciśnienie: 3000 Pa
```

### Duży piec szklarski (250-500 ton/dzień)
```
Geometria: 16×12×18m (checker: 15.5m)
Przepływ: 100 kg/s (60k/70k Nm³/h)
Temperatura: 1550°C → 500°C
Sprawność: 90%
Ciśnienie: 3500 Pa
```

---

## Kontakt i Wsparcie

Problemy z konfiguracją? Sprawdź:
- `CLAUDE.md` - Przewodnik developerski
- `USER_GUIDE.md` - Instrukcja użytkownika
- Logi backend: `docker compose logs backend -f`
