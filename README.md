# Forglass Regenerator Optimizer

System optymalizacji regeneratorów pieców szklarskich - kompleksowe narzędzie inżynierskie do analizy i optymalizacji parametrów termodynamicznych regeneratorów.

## 🎯 Cel projektu

Forglass Regenerator Optimizer (FRO) umożliwia inżynierom:
- **Redukcję zużycia paliwa o 5-15%** poprzez optymalizację parametrów regeneratorów
- **Obniżenie emisji CO₂** w procesach szklarskich
- **Standaryzację procesów** analizy termodynamicznej
- **Audytowalność decyzji** technicznych z pełną dokumentacją

## 🏗️ Architektura systemu

### Stack technologiczny
- **Backend**: FastAPI + SQLAlchemy + Celery
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **Baza danych**: MySQL 8.0
- **Cache/Queue**: Redis 7
- **Monitoring**: Prometheus + Grafana
- **Deployment**: Docker Compose

### Komponenty systemu
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

## 🚀 Szybki start

### Wymagania
- Docker + Docker Compose
- Git
- (Opcjonalnie) Node.js 18+ i Python 3.12+ dla rozwoju

### Uruchomienie środowiska deweloperskiego

1. **Klonowanie repozytorium**
```bash
git clone <repository-url>
cd RegeneratorCalc_v2
```

2. **Konfiguracja środowiska**
```bash
cp .env.example .env
# Edytuj .env zgodnie z potrzebami
```

3. **Uruchomienie aplikacji**
```bash
# Podstawowe usługi (frontend + backend + baza danych)
docker-compose up -d

# Z monitoringiem (Prometheus + Grafana)
docker-compose --profile monitoring up -d

# Tylko dla deweloperów (z Mailhog)
docker-compose --profile development up -d
```

4. **Migracje bazy danych**
```bash
# Uruchom migracje
docker-compose exec backend poetry run alembic upgrade head

# Utwórz użytkownika admin
docker-compose exec backend poetry run python -m app.scripts.create_admin
```

### Dostęp do aplikacji
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3001 (admin/admin_password)
- **Prometheus**: http://localhost:9090
- **Mailhog**: http://localhost:8025 (tylko development)

## 🔧 Rozwój aplikacji

### Backend (FastAPI)

```bash
cd backend

# Instalacja zależności
poetry install

# Uruchomienie serwera deweloperskiego
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Testy
poetry run pytest
poetry run pytest --cov=app --cov-report=html

# Linting i formatowanie
poetry run ruff check .
poetry run black .
poetry run mypy .
```

### Frontend (Next.js)

```bash
cd frontend

# Instalacja zależności
pnpm install

# Uruchomienie serwera deweloperskiego
pnpm dev

# Testy
pnpm test
pnpm test:e2e

# Linting i formatowanie
pnpm lint
pnpm format
```

### Baza danych

```bash
# Tworzenie nowej migracji
docker-compose exec backend poetry run alembic revision --autogenerate -m "Add new table"

# Aplikowanie migracji
docker-compose exec backend poetry run alembic upgrade head

# Rollback
docker-compose exec backend poetry run alembic downgrade -1
```

## 📊 Funkcjonalności MVP

### 1. Import i walidacja danych
- Import plików XLSX z szablonami regeneratorów
- Walidacja danych fizycznych i geometrycznych
- Mapowanie kolumn i konwersje jednostek
- Podgląd 3D geometrii

### 2. Konfiguracja scenariuszy
- Wizard krok-po-kroku
- Biblioteka materiałów ogniotrwałych
- Walidacja ograniczeń fizycznych
- Szablony typowych konfiguracji

### 3. Silnik optymalizacji
- Algorytm SLSQP z fallback COBYLA
- Real-time progress tracking (SSE)
- Pause/Resume/Cancel funkcjonalność
- Parallel processing scenariuszy

### 4. Raporty i eksporty
- Executive Summary (PDF)
- Technical Data (XLSX)
- Porównanie scenariuszy
- Digital signature i metadane

### 5. Zarządzanie użytkownikami
- Role-Based Access Control (Admin/Engineer/Viewer)
- JWT authentication
- Audit log wszystkich działań
- Session management

## 🔒 Bezpieczeństwo

- **Authentication**: JWT z HttpOnly cookies
- **Authorization**: RBAC z trzema rolami
- **Data encryption**: TLS 1.3 + AES-256 dla backupów
- **Input validation**: Kompleksowa walidacja wszystkich wejść
- **Audit logging**: Pełne logowanie działań użytkowników
- **OWASP compliance**: Zabezpieczenia Top 10

## 📈 Monitoring i metryki

### Metryki biznesowe
- Fuel savings achieved (%)
- CO₂ reduction (tonnes/year)
- User adoption rate
- Time to insight

### Metryki techniczne
- API response times (P95 < 200ms)
- Optimization completion rate (≥95%)
- System availability (99.5%)
- Database connection pool

### Dashboardy Grafana
- Infrastructure monitoring
- Business KPIs
- User activity
- Error tracking

## 🧪 Testowanie

### Poziomy testów
- **Unit tests**: ≥80% backend, ≥70% frontend
- **Integration tests**: API endpoints + database
- **E2E tests**: Krytyczne ścieżki użytkownika
- **Performance tests**: Load testing kluczowych endpointów

```bash
# Uruchomienie wszystkich testów
docker-compose exec backend poetry run pytest
docker-compose exec frontend pnpm test

# E2E tests
docker-compose exec frontend pnpm test:e2e

# Load testing
docker-compose exec backend poetry run locust -f tests/load/locustfile.py
```

## 📁 Struktura projektu

```
RegeneratorCalc_v2/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   ├── core/              # Core functionality
│   │   ├── models/            # SQLAlchemy models
│   │   ├── repositories/      # Data access layer
│   │   ├── services/          # Business logic
│   │   └── schemas/           # Pydantic schemas
│   ├── migrations/            # Alembic migrations
│   └── tests/                 # Backend tests
├── frontend/                   # Next.js frontend
│   ├── src/
│   │   ├── app/               # App Router pages
│   │   ├── components/        # React components
│   │   ├── hooks/             # Custom hooks
│   │   ├── lib/               # Utilities
│   │   └── stores/            # Zustand stores
│   └── tests/                 # Frontend tests
├── infrastructure/            # Docker configs
│   ├── nginx/                 # Reverse proxy
│   ├── prometheus/            # Monitoring
│   └── grafana/              # Dashboards
├── docs/                      # Documentation
├── docker-compose.yml         # Development environment
└── .env.example              # Environment template
```

## 🤝 Wkład w rozwój

### Git workflow
```bash
# Feature branch
git checkout -b feature/FRO-123-new-feature

# Conventional commits
git commit -m "feat(api): add XLSX import validation

Add comprehensive validation for XLSX imports including:
- Schema validation against predefined templates
- Data type checking and conversion
- Constraint validation for physical properties

Closes: FRO-123"
```

### Code standards
- **Python**: Ruff + Black + MyPy
- **TypeScript**: ESLint + Prettier
- **Conventional Commits**: Mandatory
- **PR size**: ≤400 LOC
- **Test coverage**: Backend ≥80%, Frontend ≥70%

## 📚 Dokumentacja

- [Architektura systemu](./ARCHITECTURE.md)
- [Product Requirements](./PRD.md)
- [Engineering Rules](./RULES.md)
- [API Documentation](http://localhost:8000/docs)
- [User Manual](./docs/user-manual.md)

## 🔧 Troubleshooting

### Typowe problemy

**1. Błędy połączenia z bazą danych**
```bash
# Sprawdź status kontenerów
docker-compose ps

# Logi MySQL
docker-compose logs mysql

# Restart bazy danych
docker-compose restart mysql
```

**2. Problemy z migracjami**
```bash
# Reset bazy danych (UWAGA: usuwa dane!)
docker-compose down -v
docker-compose up -d mysql
docker-compose exec backend poetry run alembic upgrade head
```

**3. Frontend nie łączy się z backend**
```bash
# Sprawdź konfigurację CORS w .env
BACKEND_CORS_ORIGINS=http://localhost:3000

# Restart backend
docker-compose restart backend
```

## 📞 Wsparcie

- **Issues**: GitHub Issues dla bugów i feature requestów
- **Dokumentacja**: Confluence wiki
- **Chat**: Teams channel #fro-development
- **Email**: engineering@forglass.com

## 📄 Licencja

Copyright © 2025 Forglass Sp. z o.o. All rights reserved.

---

**Wersja**: 1.0.0
**Ostatnia aktualizacja**: 2025-09-23
**Maintainer**: Forglass Engineering Team