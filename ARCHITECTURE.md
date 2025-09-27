Spis treści
Metadane dokumentu

Streszczenie wykonawcze

Kontekst i cele biznesowe

Widoki architektury

Decyzje technologiczne i uzasadnienia

Model danych

Kontrakty interfejsów

Wymagania niefunkcjonalne

Operacje i uruchomienie

Roadmapa rozszerzeń

Słownik pojęć

Checklist akceptacji

Changelog

Metadane dokumentu
Pole	Wartość
Tytuł	Architektura systemu Forglass Regenerator Optimizer
Wersja	1.0.0
Data	2025-09-23
Status	Draft
Właściciel	Tech Lead / Senior Full-Stack Architect
Zakres	Architektura logiczna i fizyczna systemu optymalizacji regeneratorów
Streszczenie wykonawcze
Forglass Regenerator Optimizer to system klasy enterprise do modelowania i optymalizacji regeneratorów pieców szklarskich, działający w pełni on-premise. System pozwala na redukcję zużycia paliwa i emisji CO₂ poprzez precyzyjne obliczenia fizyczne i optymalizację parametrów termodynamicznych. Architektura oparta na mikroserwisach zapewnia skalowalność, niezawodność i bezpieczeństwo danych w środowisku przemysłowym.

Kontekst i cele biznesowe
Problem biznesowy
Wysokie koszty energii i emisje CO₂ w procesach szklarskich

Brak narzędzi do precyzyjnej optymalizacji regeneratorów

Potrzeba audytowalności decyzji technicznych

Konieczność zachowania danych w infrastrukturze lokalnej

Kluczowe wskaźniki wydajności (KPI)
Czas optymalizacji: < 2 min dla scenariusza referencyjnego (algorytm SLSQP)

Dostępność: 99.5% (8760h - 43.8h downtime/rok)

Pokrycie testami backend: ≥ 80%

Skuteczność walidacji importu: ≥ 95%

Średni czas odpowiedzi API: < 200ms P95

Throughput optymalizacji: 50+ scenariuszy/godzinę

Widoki architektury
Context Diagram
text
graph TB
    subgraph "Użytkownicy"
        ENG[Inżynier Procesu]
        UTR[UTR/Automatyk]
        MGR[Kierownik Produkcji]
        ADM[Administrator]
    end
    
    subgraph "Forglass Regenerator Optimizer"
        SYS[System FRO]
    end
    
    subgraph "Systemy zewnętrzne"
        NAS[NAS/QNAP Storage]
        MON[System Monitorowania]
        MAIL[SMTP Server]
    end
    
    ENG -->|Import XLSX, Konfiguracja| SYS
    UTR -->|Monitoring, Raporty| SYS
    MGR -->|Raporty PDF, Analiza| SYS
    ADM -->|Zarządzanie, Audit| SYS
    
    SYS -->|Backup, Logi| NAS
    SYS -->|Metryki, Alerty| MON
    SYS -->|Powiadomienia| MAIL
Container Diagram
text
graph TB
    subgraph "Infrastructure Layer"
        NGX[Nginx Reverse Proxy<br/>Port 80/443]
        PROM[Prometheus<br/>Port 9090]
        GRAF[Grafana<br/>Port 3001]
    end
    
    subgraph "Application Layer"
        WEB[Next.js Frontend<br/>Port 3000]
        API[FastAPI Backend<br/>Port 8000]
        CELERY[Celery Workers<br/>Background Tasks]
    end
    
    subgraph "Data Layer"
        MYSQL[(MySQL Database<br/>Port 3306)]
        REDIS[(Redis Cache/Queue<br/>Port 6379)]
    end
    
    subgraph "Storage"
        VOLUMES[Docker Volumes<br/>logs, uploads, backups]
        NAS[NAS/QNAP<br/>Long-term Storage]
    end
    
    NGX --> WEB
    NGX --> API
    WEB --> API
    API --> MYSQL
    API --> REDIS
    CELERY --> REDIS
    CELERY --> MYSQL
    
    PROM --> API
    PROM --> MYSQL
    GRAF --> PROM
    
    API --> VOLUMES
    VOLUMES --> NAS
Component Diagram - Backend
text
graph LR
    subgraph "FastAPI Backend"
        AUTH[Auth Module<br/>JWT + RBAC]
        API_LAYER[API Layer<br/>REST Endpoints]
        
        subgraph "Business Logic"
            IMP[Importer Module<br/>XLSX Processing]
            EXP[Exporter Module<br/>PDF/XLSX Reports]
            PHY[Physics Engine<br/>Calculations]
            OPT[Optimizer Module<br/>SLSQP Algorithm]
        end
        
        subgraph "Data Access"
            ORM[SQLAlchemy ORM]
            CACHE[Redis Client]
        end
        
        subgraph "Infrastructure"
            LOG[Logging Module]
            AUDIT[Audit Service]
            HEALTH[Health Checks]
        end
    end
    
    API_LAYER --> AUTH
    API_LAYER --> IMP
    API_LAYER --> EXP
    API_LAYER --> PHY
    API_LAYER --> OPT
    
    IMP --> ORM
    EXP --> ORM
    PHY --> CACHE
    OPT --> ORM
    
    AUTH --> AUDIT
    OPT --> LOG
Deployment Diagram
text
graph TB
    subgraph "Production VLAN (10.1.100.0/24)"
        subgraph "Docker Host (10.1.100.10)"
            subgraph "Docker Network: fro_network"
                NGINX[nginx:1.24<br/>:80,:443]
                WEB[fro-frontend:1.0<br/>:3000]
                API[fro-backend:1.0<br/>:8000]
                CELERY[fro-celery:1.0]
                MYSQL[mysql:8.0<br/>:3306]
                REDIS[redis:7-alpine<br/>:6379]
                PROM[prometheus:v2.45<br/>:9090]
                GRAF[grafana:10.0<br/>:3001]
            end
        end
        
        subgraph "Storage (10.1.100.20)"
            NAS[QNAP NAS<br/>Backups & Logs]
        end
        
        subgraph "Monitoring (10.1.100.30)"
            SMTP[SMTP Relay<br/>Notifications]
        end
    end
    
    subgraph "Management VLAN"
        ADMIN[Admin Workstation<br/>10.1.101.100]
    end
    
    ADMIN -->|HTTPS:443| NGINX
    NGINX --> WEB
    NGINX --> API
    NGINX --> GRAF
    
    API --> MYSQL
    API --> REDIS
    CELERY --> REDIS
    
    PROM --> API
    GRAF --> PROM
    
    API -->|Backup/Logs| NAS
    GRAF -->|Alerts| SMTP
Decyzje technologiczne i uzasadnienia
Architecture Decision Records (ADR)
Decyzja	Technologia	Uzasadnienie	Alternatywy
Backend Framework	FastAPI	Async/await, automatyczna dokumentacja OpenAPI, wysoka wydajność	Django REST, Flask
ORM	SQLAlchemy 2.0	Mature ORM, async support, migrations z Alembic	Django ORM, Tortoise
Queue System	Celery + Redis	Proven solution, monitoring, retry logic	RQ, Dramatiq
Frontend	Next.js 14 (App Router)	SSR, TypeScript, React Server Components	Nuxt.js, SvelteKit
UI Framework	Tailwind + shadcn/ui	Design system, accessibility, customizable	Material-UI, Chakra
Database	MySQL 8.0	Enterprise grade, ACID, JSON support	PostgreSQL, MariaDB
Authentication	JWT HttpOnly	Stateless, secure, RBAC ready	Session-based, OAuth2
Monitoring	Prometheus + Grafana	Industry standard, rich ecosystem	DataDog, New Relic
Containerization	Docker Compose	Simple deployment, reproducible environments	Kubernetes, Podman
Biblioteki obliczeniowe
python
# Feature flag dla różnych solverów
PHYSICS_SOLVER = {
    "default": "scipy",  # SLSQP
    "experimental": "pyomo"  # MINLP support
}

# Przykład modułu physics_engine/core.py
from scipy.optimize import minimize
import numpy as np

def optimize_regenerator(params: RegeneratorParams) -> OptimizationResult:
    """SLSQP optimization for regenerator efficiency"""
    def objective(x):
        return calculate_fuel_consumption(x, params)
    
    result = minimize(
        objective, 
        x0=params.initial_guess,
        method='SLSQP',
        bounds=params.bounds,
        constraints=params.constraints
    )
    return OptimizationResult.from_scipy(result)
Model danych
Entity Relationship Diagram
text
erDiagram
    USERS {
        uuid id PK
        string username UK
        string email UK
        string password_hash
        string role "ADMIN|ENGINEER|VIEWER"
        timestamp created_at
        timestamp last_login
        boolean is_active
    }
    
    MATERIALS {
        uuid id PK
        string name UK
        string category
        json properties "thermal, physical"
        string version
        uuid created_by FK
        timestamp created_at
        boolean is_active
    }
    
    REGENERATORS {
        uuid id PK
        string name UK
        json configuration
        uuid created_by FK
        timestamp created_at
        timestamp updated_at
    }
    
    WALLS {
        uuid id PK
        uuid regenerator_id FK
        string wall_type "HOT|COLD|FLUE"
        uuid material_id FK
        decimal thickness_mm
        decimal area_m2
        json thermal_properties
    }
    
    CHECKERPACKS {
        uuid id PK
        uuid regenerator_id FK
        string pattern_type
        uuid material_id FK
        json geometry
        decimal porosity
        decimal surface_area_m2
    }
    
    SCENARIOS {
        uuid id PK
        string name
        uuid regenerator_id FK
        json input_parameters
        string status "DRAFT|RUNNING|COMPLETED|FAILED"
        uuid created_by FK
        timestamp created_at
        timestamp started_at
        timestamp completed_at
    }
    
    SCENARIO_ITERATIONS {
        uuid id PK
        uuid scenario_id FK
        int iteration_number
        json parameters
        json results
        decimal objective_value
        timestamp created_at
    }
    
    OPTIMIZATION_JOBS {
        uuid id PK
        uuid scenario_id FK
        string status "QUEUED|RUNNING|COMPLETED|FAILED|PAUSED"
        json progress_data
        text error_message
        timestamp created_at
        timestamp updated_at
    }
    
    REPORTS {
        uuid id PK
        uuid scenario_id FK
        string report_type "PDF|XLSX"
        string file_path
        string hash_sha256
        uuid generated_by FK
        timestamp generated_at
        json metadata
    }
    
    AUDIT_LOGS {
        uuid id PK
        uuid user_id FK
        string action
        string resource_type
        uuid resource_id
        json old_values
        json new_values
        string ip_address
        string user_agent
        timestamp created_at
    }
    
    USERS ||--o{ MATERIALS : creates
    USERS ||--o{ REGENERATORS : creates
    USERS ||--o{ SCENARIOS : creates
    USERS ||--o{ REPORTS : generates
    USERS ||--o{ AUDIT_LOGS : performs
    
    REGENERATORS ||--o{ WALLS : contains
    REGENERATORS ||--o{ CHECKERPACKS : contains
    REGENERATORS ||--o{ SCENARIOS : analyzed_in
    
    MATERIALS ||--o{ WALLS : used_in
    MATERIALS ||--o{ CHECKERPACKS : made_of
    
    SCENARIOS ||--o{ SCENARIO_ITERATIONS : has
    SCENARIOS ||--o{ OPTIMIZATION_JOBS : tracked_by
    SCENARIOS ||--o{ REPORTS : generates
Indeksy i wydajność
sql
-- Kluczowe indeksy dla wydajności
CREATE INDEX idx_scenarios_status ON scenarios(status);
CREATE INDEX idx_scenarios_created_by_date ON scenarios(created_by, created_at DESC);
CREATE INDEX idx_audit_logs_user_date ON audit_logs(user_id, created_at DESC);
CREATE INDEX idx_optimization_jobs_status ON optimization_jobs(status);
CREATE FULLTEXT INDEX idx_materials_search ON materials(name, category);

-- Retencja danych
-- Audit logs: 2 lata
-- Scenario iterations: 1 rok (archiwizacja po 6 miesiącach)
-- Job logs: 90 dni
Kontrakty interfejsów
REST API Endpoints
text
# Fragment OpenAPI 3.0
paths:
  /api/v1/optimize:
    post:
      summary: "Uruchom optymalizację scenariusza"
      operationId: "startOptimization"
      requestBody:
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/OptimizationRequest"
      responses:
        202:
          description: "Zadanie uruchomione"
          content:
            application/json:
              schema:
                properties:
                  job_id:
                    type: string
                    format: uuid
                  status:
                    type: string
                    enum: [QUEUED]
  
  /api/v1/jobs/{job_id}/events:
    get:
      summary: "Server-Sent Events dla zadania"
      parameters:
        - name: job_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        200:
          description: "Stream eventów"
          content:
            text/event-stream:
              schema:
                type: string

  /api/v1/physics/wall-loss/solve:
    post:
      summary: "Oblicz straty ciepła przez ściany"
      requestBody:
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/WallLossRequest"
      responses:
        200:
          description: "Wynik obliczeń"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/WallLossResult"

components:
  schemas:
    OptimizationRequest:
      type: object
      required: [scenario_id, algorithm, parameters]
      properties:
        scenario_id:
          type: string
          format: uuid
        algorithm:
          type: string
          enum: [SLSQP, COBYLA]
        parameters:
          type: object
          properties:
            max_iterations:
              type: integer
              default: 1000
            tolerance:
              type: number
              default: 1e-6
Server-Sent Events Schema
json
// Przykładowe eventy SSE
{
  "type": "optimization.started",
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2025-09-23T17:48:00Z",
  "data": {
    "scenario_name": "Test Scenario 1",
    "algorithm": "SLSQP",
    "estimated_duration": 120
  }
}

{
  "type": "optimization.progress",
  "job_id": "123e4567-e89b-12d3-a456-426614174000", 
  "timestamp": "2025-09-23T17:48:30Z",
  "data": {
    "iteration": 45,
    "objective_value": 1234.56,
    "convergence": 0.001,
    "progress_percent": 35
  }
}

{
  "type": "optimization.completed",
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2025-09-23T17:50:00Z",
  "data": {
    "final_objective": 1189.23,
    "iterations_count": 127,
    "execution_time": 118.5,
    "convergence_status": "SUCCESS"
  }
}
Wymagania niefunkcjonalne
Wydajność
Czas odpowiedzi API: P95 < 200ms dla operacji CRUD

Throughput: 100 req/s przy 80% wykorzystaniu CPU

Optymalizacja: < 2 min dla scenariusza referencyjnego

Import XLSX: < 30s dla pliku 10MB (10k rekordów)

Bezpieczeństwo
Autoryzacja: JWT HttpOnly cookies + RBAC

Szyfrowanie: TLS 1.3 dla komunikacji zewnętrznej

Dane: AES-256 dla backup'ów

Audit: Pełne logowanie działań użytkowników

OWASP: Zabezpieczenia Top 10 (XSS, CSRF, SQL Injection)

Obserwowalność
Metryki: Prometheus (custom metrics + business KPI)

Logi: Strukturalne JSON z trace_id

Tracing: OpenTelemetry dla distributed tracing

Dashboardy: Grafana (infrastruktura + biznes)

Alerty: Email + webhook dla krytycznych błędów

Niezawodność
Dostępność: 99.5% (planned maintenance: 4h/miesiąc)

Backup: Automatyczny daily backup (3-2-1 strategy)

Recovery: RTO < 4h, RPO < 1h

Graceful degradation: System działa bez modułu optymalizacji

Zgodność i compliance
RODO: Prawo do usunięcia danych, pseudonimizacja

ISO 27001: Zarządzanie bezpieczeństwem informacji

21 CFR Part 11: Elektroniczne podpisy i rekordy (jeśli wymagane)

Retencja: Automatyczne archiwizowanie starych danych

Operacje i uruchomienie
Docker Compose Configuration
text
version: '3.8'

services:
  nginx:
    image: nginx:1.24-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/certs:/etc/nginx/certs:ro
      - ./nginx/logs:/var/log/nginx
    depends_on:
      - frontend
      - backend
    networks:
      - fro_network
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    image: fro-frontend:${VERSION:-latest}
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=http://backend:8000
    volumes:
      - frontend_cache:/app/.next/cache
    networks:
      - fro_network
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    image: fro-backend:${VERSION:-latest}
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - SMTP_HOST=${SMTP_HOST}
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
      - backend_cache:/app/cache
    depends_on:
      - mysql
      - redis
    networks:
      - fro_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  celery:
    image: fro-backend:${VERSION:-latest}
    command: celery -A app.celery worker --loglevel=info
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
      - backend_cache:/app/cache
    depends_on:
      - mysql
      - redis
    networks:
      - fro_network
    restart: unless-stopped

  mysql:
    image: mysql:8.0
    ports:
      - "3306:3306"
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
      - MYSQL_DATABASE=${MYSQL_DATABASE}
      - MYSQL_USER=${MYSQL_USER}
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
      - ./mysql/conf.d:/etc/mysql/conf.d:ro
      - ./mysql/init:/docker-entrypoint-initdb.d:ro
    networks:
      - fro_network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
      - ./redis/redis.conf:/etc/redis/redis.conf:ro
    command: redis-server /etc/redis/redis.conf
    networks:
      - fro_network
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:v2.45.0
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=90d'
    networks:
      - fro_network
    restart: unless-stopped

  grafana:
    image: grafana/grafana:10.0.0
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./grafana/datasources:/etc/grafana/provisioning/datasources:ro
    networks:
      - fro_network
    restart: unless-stopped

volumes:
  mysql_data:
  redis_data:
  prometheus_data:
  grafana_data:
  frontend_cache:
  backend_cache:

networks:
  fro_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
Zmienne środowiskowe (.env)
bash
# Application
VERSION=1.0.0
SECRET_KEY=your-secret-key-here
DEBUG=false

# Database
DATABASE_URL=mysql+aiomysql://fro_user:password@mysql:3306/fro_db
MYSQL_ROOT_PASSWORD=root-password
MYSQL_DATABASE=fro_db
MYSQL_USER=fro_user
MYSQL_PASSWORD=user-password

# Redis
REDIS_URL=redis://redis:6379/0

# SMTP
SMTP_HOST=smtp.company.com
SMTP_PORT=587
SMTP_USER=notifications@company.com
SMTP_PASSWORD=smtp-password

# Monitoring
GRAFANA_ADMIN_PASSWORD=grafana-admin-password

# Storage
BACKUP_PATH=/mnt/nas/backups/fro
LOG_RETENTION_DAYS=90
Monitoring i metryki
python
# Przykład custom metrics w FastAPI
from prometheus_client import Counter, Histogram, Gauge

# Business metrics
optimization_jobs_total = Counter(
    'fro_optimization_jobs_total',
    'Total number of optimization jobs',
    ['status', 'algorithm']
)

optimization_duration = Histogram(
    'fro_optimization_duration_seconds',
    'Time spent on optimization',
    ['algorithm'],
    buckets=[10, 30, 60, 120, 300, 600, 1800]
)

active_optimization_jobs = Gauge(
    'fro_active_optimization_jobs',
    'Number of currently running optimizations'
)

# Technical metrics
api_requests_total = Counter(
    'fro_api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

database_connections = Gauge(
    'fro_database_connections',
    'Active database connections'
)
Backup i restore
bash
#!/bin/bash
# backup.sh - Daily backup script

set -e

BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/mnt/nas/backups/fro"
DATABASE_BACKUP="${BACKUP_DIR}/mysql_${BACKUP_DATE}.sql.gz"
UPLOADS_BACKUP="${BACKUP_DIR}/uploads_${BACKUP_DATE}.tar.gz"

# MySQL backup
docker exec fro_mysql_1 mysqldump \
    --single-transaction \
    --routines \
    --triggers \
    fro_db | gzip > "$DATABASE_BACKUP"

# Uploads backup
tar -czf "$UPLOADS_BACKUP" -C ./uploads .

# Retention (keep 30 days)
find "$BACKUP_DIR" -name "*.gz" -mtime +30 -delete

# Verify backup integrity
gzip -t "$DATABASE_BACKUP"
tar -tzf "$UPLOADS_BACKUP" > /dev/null

echo "Backup completed: $BACKUP_DATE"
Roadmapa rozszerzeń
Faza 1 (Q1 2026): Rozszerzone algorytmy
Integracja z Pyomo dla MINLP optimization

Algorytmy genetyczne dla złożonych scenariuszy

Wielokryterialna optymalizacja (Pareto front)

Faza 2 (Q2 2026): Machine Learning
Predykcja optymalnych parametrów startowych

Anomaly detection w danych wejściowych

Automated parameter tuning

Faza 3 (Q3 2026): Rozszerzona integracja
REST API dla systemów SCADA/DCS

Webhook notifications

Advanced reporting (Power BI connector)

Faza 4 (Q4 2026): Enterprise features
Multi-tenant architecture

Advanced RBAC z grupami

Workflow approval system

Data lineage tracking

Słownik pojęć
Termin	Definicja
Regenerator	Urządzenie wymiany ciepła w piecu szklarskim, składające się z murki ogniotrwałej
Checkerpack	Ułożenie cegieł w regeneratorze tworzące kanały przepływu gazów
U-value	Współczynnik przenikania ciepła [W/m²K]
Q_wall	Strumień ciepła przez ścianę [W]
NTU	Number of Transfer Units - bezwymiarowa wielkość charakteryzująca wymiennik
LMTD	Logarithmic Mean Temperature Difference
Fouling	Zanieczyszczenie powierzchni wymiany ciepła
Δp	Spadek ciśnienia w kanałach regeneratora [Pa]
SLSQP	Sequential Least Squares Programming - algorytm optymalizacji
RBAC	Role-Based Access Control - kontrola dostępu oparta na rolach
SSE	Server-Sent Events - jednokierunkowy stream danych z serwera
On-premise	Uruchomienie w lokalnej infrastrukturze klienta
Checklist akceptacji
Architecture Readiness Checklist
 Context Diagram: Zdefiniowani wszyscy aktorzy i granice systemu

 Container Diagram: Wszystkie komponenty z portami i protokołami

 Component Diagram: Moduły backendu i frontendu z zależnościami

 Deployment Diagram: Sieć, hosty, porty, ścieżki storage

 Technology Stack: Uzasadnione wybory z alternatywami

 Data Model: ERD z kluczami, indeksami, retencją

 API Contracts: OpenAPI spec z przykładami

 NFRs: Wydajność, bezpieczeństwo, obserwowalność

 Docker Compose: Kompletna konfiguracja środowiska

 Monitoring: Metryki, dashboardy, alerty

 Backup/Restore: Procedury i testowanie

 Security: Authentication, authorization, encryption

 Observability: Logging, tracing, metrics

Security Review Checklist
 Authentication: JWT HttpOnly implementation

 Authorization: RBAC model z rolami USER/ADMIN/ENGINEER

 Input Validation: Sanitization XLSX imports

 OWASP Top 10: XSS, CSRF, SQL Injection protection

 TLS: Enforced HTTPS, cert management

 Secrets: Environment variables, no hardcoded passwords

 Audit Logging: User actions tracking

 Data Encryption: Backup encryption, PII handling

 Network Security: Firewall rules, network segmentation

 Vulnerability Scanning: Dependencies, container images

Operational Readiness Checklist
 Deployment: Docker Compose tested

 Environment Variables: Complete .env template

 Health Checks: All services health endpoints

 Monitoring: Prometheus + Grafana configured

 Logging: Structured JSON logs with rotation

 Backup: Automated daily backup tested

 Disaster Recovery: RTO/RPO procedures documented

 Performance: Load testing completed

 Documentation: README, runbooks, troubleshooting

 Support: On-call procedures, escalation matrix

Changelog
[1.0.0] - 2025-09-23
Added
Kompletna architektura systemu Forglass Regenerator Optimizer

4 diagramy Mermaid (Context, Container, Component, Deployment)

Model danych z 9 tabelami głównymi i audytem

Kontrakty API z OpenAPI i SSE events

Docker Compose configuration dla wszystkich usług

NFR requirements z konkretnymi metrykami

Roadmapa rozwoju na 4 kwartały

Security i operational checklists

Monitoring stack (Prometheus + Grafana)

Backup/restore procedures

Technical Decisions
FastAPI + SQLAlchemy 2.0 + Alembic

Next.js 14 App Router + Tailwind + shadcn/ui

MySQL 8.0 + Redis 7

Celery dla background jobs

JWT HttpOnly + RBAC authorization

Docker Compose deployment

Prometheus/Grafana monitoring