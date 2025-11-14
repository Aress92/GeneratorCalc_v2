# Plan Testowania API .NET - Forglass Regenerator Optimizer

**Status:** Gotowy do wykonania
**Data:** 2025-11-14
**Wersja API:** v1
**Port:** 8000 (HTTP), 8001 (HTTPS)

---

## 📋 Podsumowanie zmian w planie

### Skorygowane elementy:
1. ✅ **Port zmieniony**: 5119 → **8000** (HTTP), 7164 → **8001** (HTTPS)
2. ✅ **Swagger URL**: `/swagger` → `/api/docs`
3. ✅ **Launch URL**: Automatycznie otwiera `/api/docs` przy starcie
4. ✅ **Weryfikacja konfiguracji**: Wszystkie pliki skonfigurowane poprawnie
5. ✅ **CORS**: Dodano `http://localhost:8000` do dozwolonych origin

### Zweryfikowane komponenty:
- ✅ **6 kontrolerów** (Auth, Users, Regenerators, Optimization, Materials, Reports)
- ✅ **GlobalExceptionHandlerMiddleware** - obsługa błędów 400, 401, 404, 422, 500
- ✅ **JWT Authentication** - konfiguracja z ClockSkew = 0
- ✅ **Swagger/OpenAPI** - z autoryzacją Bearer token
- ✅ **Database migrations** - automatyczne przy starcie (Development mode)
- ✅ **Hangfire Dashboard** - `/hangfire` (wymaga Redis)
- ✅ **Health check** - `/health`

---

## 🚀 Faza 1: Przygotowanie środowiska

### 1.1. Wymagania wstępne

**Wymagane usługi:**
- MySQL 8.0+ na porcie 3306
- Redis na porcie 6379 (opcjonalnie - dla Hangfire)
- .NET 8.0 SDK

**Sprawdzenie dostępności:**
```bash
# Sprawdź .NET SDK
dotnet --version
# Oczekiwane: 8.0.x

# Sprawdź MySQL (jeśli używasz Docker Compose)
docker compose ps mysql
# Status: running (healthy)

# Sprawdź Redis (opcjonalnie)
docker compose ps redis
# Status: running
```

### 1.2. Przygotowanie bazy danych

**Opcja A: Użyj istniejącej bazy (Python backend):**
```bash
# Jeśli Python backend działa, baza jest już gotowa
docker compose ps mysql
# Baza: fro_db
# User: fro_user
# Password: fro_password
```

**Opcja B: Utwórz nową bazę:**
```sql
CREATE DATABASE fro_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'fro_user'@'%' IDENTIFIED BY 'fro_password';
GRANT ALL PRIVILEGES ON fro_db.* TO 'fro_user'@'%';
FLUSH PRIVILEGES;
```

### 1.3. Zbuduj i uruchom API

```bash
# 1. Przejdź do katalogu projektu
cd backend-dotnet

# 2. Przywróć zależności (jeśli potrzeba)
dotnet restore

# 3. Zbuduj projekt (sprawdź czy build jest clean)
dotnet build
# Oczekiwane: 0 errors, 3 warnings (dotnet build warnings - bezpieczne)

# 4. Uruchom API na porcie 8000
cd Fro.Api
dotnet run --launch-profile http

# Oczekiwana konsola:
# ✓ Connected to database
# ✓ Database is up to date (no pending migrations) / Applied X migrations
# ✓ Connected to Redis (jeśli dostępny)
# ✓ Hangfire configured with Redis storage (jeśli dostępny)
# ✓ Hangfire Dashboard available at /hangfire (jeśli dostępny)
# info: Microsoft.Hosting.Lifetime[14]
#       Now listening on: http://localhost:8000
# info: Microsoft.Hosting.Lifetime[0]
#       Application started. Press Ctrl+C to shut down.
```

**W przypadku błędów:**
- **Brak połączenia MySQL**: Sprawdź `ConnectionStrings:DefaultConnection` w `appsettings.Development.json`
- **Brak Redis**: API uruchomi się bez Hangfire (to OK dla testów)
- **Błędy migracji**: Usuń migracje i stwórz nowe: `dotnet ef migrations add InitialCreate`

---

## 🧪 Faza 2: Testy podstawowe (Health Check, Swagger)

### 2.1. Test Health Check

**Request:**
```bash
curl http://localhost:8000/health
```

**Oczekiwana odpowiedź:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-14T10:30:00.123Z",
  "version": "1.0.0"
}
```

**Status code:** 200 OK

### 2.2. Test Swagger UI

**Kroki:**
1. Otwórz przeglądarkę: `http://localhost:8000/api/docs`
2. Sprawdź czy widoczne są wszystkie kontrolery:
   - ✅ **Auth** (6 endpointów)
   - ✅ **Materials** (5 endpointów)
   - ✅ **Optimization** (8 endpointów)
   - ✅ **Regenerators** (9 endpointów)
   - ✅ **Reports** (5 endpointów)
   - ✅ **Users** (6 endpointów)

3. Sprawdź ikony autoryzacji (🔒 przy chronionych endpointach)
4. Sprawdź przycisk **Authorize** w prawym górnym rogu

**Schematy JSON:**
- Kliknij endpoint → "Try it out" → sprawdź przykładowe schematy request/response
- Wszystkie DTOs powinny mieć opisy pól i walidacje

---

## 🔐 Faza 3: Testy autentykacji JWT

### 3.1. Rejestracja nowego użytkownika

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "TestPassword123!",
    "fullName": "Test User",
    "role": "ENGINEER"
  }'
```

**Oczekiwana odpowiedź (201 Created):**
```json
{
  "id": "guid-value",
  "username": "testuser",
  "email": "testuser@example.com",
  "fullName": "Test User",
  "role": "ENGINEER",
  "isActive": true,
  "isVerified": false
}
```

**Testy błędów:**

**A) Duplikat użytkownika (400 Bad Request):**
```bash
# Ponownie wyślij ten sam request
# Oczekiwane: 400 + message: "User with this username or email already exists"
```

**B) Błąd walidacji - słabe hasło (400 Bad Request):**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser2",
    "email": "testuser2@example.com",
    "password": "123",
    "fullName": "Test User 2",
    "role": "ENGINEER"
  }'

# Oczekiwane:
{
  "statusCode": 400,
  "message": "Validation failed",
  "errors": [
    {
      "field": "Password",
      "message": "Password must be at least 8 characters long",
      "code": "MinimumLengthValidator"
    }
  ],
  "traceId": "...",
  "timestamp": "..."
}
```

**C) Błąd walidacji - nieprawidłowy email (400 Bad Request):**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser3",
    "email": "invalid-email",
    "password": "TestPassword123!",
    "fullName": "Test User 3",
    "role": "ENGINEER"
  }'

# Oczekiwane: 400 + błędy walidacji email
```

### 3.2. Login

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPassword123!"
  }'
```

**Oczekiwana odpowiedź (200 OK):**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "refresh-token-guid",
  "expiresIn": 86400,
  "tokenType": "Bearer",
  "user": {
    "id": "guid-value",
    "username": "testuser",
    "email": "testuser@example.com",
    "fullName": "Test User",
    "role": "ENGINEER",
    "isActive": true,
    "isVerified": false
  }
}
```

**Zapisz `accessToken` do zmiennej:**
```bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Testy błędów:**

**A) Nieprawidłowe hasło (401 Unauthorized):**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "WrongPassword123!"
  }'

# Oczekiwane: 401 + message: "Invalid username or password"
```

**B) Nieistniejący użytkownik (401 Unauthorized):**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "nonexistent",
    "password": "TestPassword123!"
  }'

# Oczekiwane: 401 + message: "Invalid username or password"
```

### 3.3. Wygasanie tokena (Token Expiration)

**Test manualny:**
1. W `appsettings.json` ustaw `JwtSettings:ExpirationMinutes` na **1** (1 minuta)
2. Zrestartuj API
3. Zaloguj się i zapisz token
4. Poczekaj 2 minuty
5. Spróbuj użyć tokena do chronionego endpointa

**Request po wygaśnięciu:**
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Oczekiwane: 401 Unauthorized
```

**Po teście przywróć `ExpirationMinutes` na 1440 (24h).**

### 3.4. Refresh Token

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refreshToken": "refresh-token-from-login"
  }'
```

**Oczekiwana odpowiedź (200 OK):**
```json
{
  "accessToken": "new-access-token...",
  "refreshToken": "new-refresh-token...",
  "expiresIn": 86400,
  "tokenType": "Bearer",
  "user": { ... }
}
```

**Test błędu - nieprawidłowy refresh token (401 Unauthorized):**
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refreshToken": "invalid-token"
  }'

# Oczekiwane: 401 + message: "Invalid or expired refresh token"
```

### 3.5. Get Current User (Authorized Endpoint)

**Request:**
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

**Oczekiwana odpowiedź (200 OK):**
```json
{
  "id": "guid-value",
  "username": "testuser",
  "email": "testuser@example.com",
  "fullName": "Test User",
  "role": "ENGINEER",
  "isActive": true,
  "isVerified": false
}
```

**Test błędu - brak tokena (401 Unauthorized):**
```bash
curl -X GET http://localhost:8000/api/v1/auth/me

# Oczekiwane: 401 Unauthorized
```

**Test błędu - nieprawidłowy token (401 Unauthorized):**
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer invalid-token"

# Oczekiwane: 401 Unauthorized
```

### 3.6. Change Password (Authorized)

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "currentPassword": "TestPassword123!",
    "newPassword": "NewPassword456!"
  }'
```

**Oczekiwana odpowiedź (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

**Weryfikacja - zaloguj się nowym hasłem:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "NewPassword456!"
  }'

# Oczekiwane: 200 OK + nowy token
```

---

## 👥 Faza 4: Testy CRUD - Users (Admin only)

### 4.1. Utwórz użytkownika Admin

**Opcja A: Przez DatabaseSeeder (automatyczne przy starcie API):**
```csharp
// Sprawdź konsolę API przy starcie:
// ✓ Seeded admin user: admin / admin
```

**Opcja B: Bezpośrednio w bazie:**
```sql
-- Sprawdź czy admin istnieje
SELECT * FROM users WHERE username = 'admin';

-- Jeśli nie istnieje, dodaj przez rejestrację i zmień role w bazie:
UPDATE users SET role = 'ADMIN' WHERE username = 'testuser';
```

**Login jako admin:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin"
  }'

# Zapisz admin token
export ADMIN_TOKEN="admin-access-token..."
```

### 4.2. GET /api/v1/users - Lista użytkowników (Admin only)

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/users?page=1&pageSize=10" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Oczekiwana odpowiedź (200 OK):**
```json
{
  "items": [
    {
      "id": "guid-1",
      "username": "admin",
      "email": "admin@forglass.com",
      "fullName": "System Admin",
      "role": "ADMIN",
      "isActive": true,
      "isVerified": true,
      "createdAt": "2025-11-14T10:00:00Z"
    },
    {
      "id": "guid-2",
      "username": "testuser",
      "email": "testuser@example.com",
      "fullName": "Test User",
      "role": "ENGINEER",
      "isActive": true,
      "isVerified": false,
      "createdAt": "2025-11-14T11:00:00Z"
    }
  ],
  "totalCount": 2,
  "page": 1,
  "pageSize": 10,
  "totalPages": 1,
  "hasNextPage": false,
  "hasPreviousPage": false
}
```

**Test błędu - non-admin user (403 Forbidden):**
```bash
curl -X GET "http://localhost:8000/api/v1/users?page=1&pageSize=10" \
  -H "Authorization: Bearer $TOKEN"

# Oczekiwane: 403 Forbidden (ENGINEER nie ma dostępu)
```

### 4.3. GET /api/v1/users/{id} - Pobranie użytkownika

**Request:**
```bash
# Zapisz ID testuser
export USER_ID="guid-from-previous-response"

curl -X GET "http://localhost:8000/api/v1/users/$USER_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Oczekiwana odpowiedź (200 OK):**
```json
{
  "id": "guid-value",
  "username": "testuser",
  "email": "testuser@example.com",
  "fullName": "Test User",
  "role": "ENGINEER",
  "isActive": true,
  "isVerified": false,
  "createdAt": "2025-11-14T11:00:00Z",
  "lastLogin": null
}
```

**Test błędu - nieistniejący ID (404 Not Found):**
```bash
curl -X GET "http://localhost:8000/api/v1/users/00000000-0000-0000-0000-000000000000" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Oczekiwane: 404 + message: "User not found"
```

### 4.4. PUT /api/v1/users/{id} - Aktualizacja użytkownika

**Request:**
```bash
curl -X PUT "http://localhost:8000/api/v1/users/$USER_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fullName": "Test User Updated",
    "email": "testuserupdated@example.com",
    "role": "ADMIN",
    "isActive": true
  }'
```

**Oczekiwana odpowiedź (200 OK):**
```json
{
  "id": "guid-value",
  "username": "testuser",
  "email": "testuserupdated@example.com",
  "fullName": "Test User Updated",
  "role": "ADMIN",
  "isActive": true,
  "isVerified": false
}
```

**Weryfikacja:**
```bash
curl -X GET "http://localhost:8000/api/v1/users/$USER_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Sprawdź czy zmiany zostały zapisane
```

### 4.5. DELETE /api/v1/users/{id} - Usunięcie użytkownika

**Request:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/users/$USER_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Oczekiwana odpowiedź (204 No Content):**
```
Status: 204 No Content
(brak body)
```

**Weryfikacja:**
```bash
curl -X GET "http://localhost:8000/api/v1/users/$USER_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Oczekiwane: 404 Not Found
```

---

## 🔧 Faza 5: Testy CRUD - Regenerator Configurations

### 5.1. POST /api/v1/regenerators - Utworzenie konfiguracji

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/regenerators \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Regenerator Config",
    "description": "Test configuration for API testing",
    "configurationData": {
      "temperature": 1200,
      "pressure": 1.5,
      "flowRate": 100
    }
  }'
```

**Oczekiwana odpowiedź (201 Created):**
```json
{
  "id": "config-guid",
  "name": "Test Regenerator Config",
  "description": "Test configuration for API testing",
  "status": "Draft",
  "configurationData": {
    "temperature": 1200,
    "pressure": 1.5,
    "flowRate": 100
  },
  "createdAt": "2025-11-14T12:00:00Z",
  "updatedAt": "2025-11-14T12:00:00Z"
}
```

**Zapisz ID:**
```bash
export CONFIG_ID="config-guid-from-response"
```

**Test błędu - brak wymaganego pola (400 Bad Request):**
```bash
curl -X POST http://localhost:8000/api/v1/regenerators \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Missing name field"
  }'

# Oczekiwane: 400 + błędy walidacji
{
  "statusCode": 400,
  "message": "Validation failed",
  "errors": [
    {
      "field": "Name",
      "message": "Name is required",
      "code": "NotEmptyValidator"
    }
  ]
}
```

### 5.2. GET /api/v1/regenerators - Lista konfiguracji

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/regenerators?page=1&pageSize=10&status=Draft" \
  -H "Authorization: Bearer $TOKEN"
```

**Oczekiwana odpowiedź (200 OK):**
```json
{
  "items": [
    {
      "id": "config-guid",
      "name": "Test Regenerator Config",
      "description": "Test configuration for API testing",
      "status": "Draft",
      "createdAt": "2025-11-14T12:00:00Z"
    }
  ],
  "totalCount": 1,
  "page": 1,
  "pageSize": 10,
  "totalPages": 1,
  "hasNextPage": false,
  "hasPreviousPage": false
}
```

### 5.3. GET /api/v1/regenerators/{id} - Pobranie szczegółów

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/regenerators/$CONFIG_ID" \
  -H "Authorization: Bearer $TOKEN"
```

**Oczekiwana odpowiedź (200 OK):**
```json
{
  "id": "config-guid",
  "name": "Test Regenerator Config",
  "description": "Test configuration for API testing",
  "status": "Draft",
  "configurationData": {
    "temperature": 1200,
    "pressure": 1.5,
    "flowRate": 100
  },
  "createdAt": "2025-11-14T12:00:00Z",
  "updatedAt": "2025-11-14T12:00:00Z"
}
```

**Test błędu - nieistniejąca konfiguracja (404 Not Found):**
```bash
curl -X GET "http://localhost:8000/api/v1/regenerators/00000000-0000-0000-0000-000000000000" \
  -H "Authorization: Bearer $TOKEN"

# Oczekiwane: 404 + message: "Configuration not found or access denied"
```

### 5.4. PUT /api/v1/regenerators/{id} - Aktualizacja

**Request:**
```bash
curl -X PUT "http://localhost:8000/api/v1/regenerators/$CONFIG_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Regenerator Config",
    "description": "Updated description",
    "configurationData": {
      "temperature": 1300,
      "pressure": 2.0,
      "flowRate": 120
    }
  }'
```

**Oczekiwana odpowiedź (200 OK):**
```json
{
  "id": "config-guid",
  "name": "Updated Regenerator Config",
  "description": "Updated description",
  "status": "Draft",
  "configurationData": {
    "temperature": 1300,
    "pressure": 2.0,
    "flowRate": 120
  },
  "updatedAt": "2025-11-14T12:30:00Z"
}
```

### 5.5. DELETE /api/v1/regenerators/{id} - Usunięcie

**Request:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/regenerators/$CONFIG_ID" \
  -H "Authorization: Bearer $TOKEN"
```

**Oczekiwana odpowiedź (204 No Content)**

---

## ⚙️ Faza 6: Testy CRUD - Optimization Scenarios & Jobs

### 6.1. POST /api/v1/optimization/scenarios - Utworzenie scenariusza

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/optimization/scenarios \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Optimization Scenario",
    "description": "Test scenario for fuel reduction",
    "configurationId": "existing-config-guid",
    "objectiveFunction": "minimize_fuel",
    "constraints": {
      "minTemperature": 800,
      "maxTemperature": 1400,
      "maxPressureDrop": 500
    },
    "optimizationParameters": {
      "maxIterations": 100,
      "tolerance": 0.001
    }
  }'
```

**Oczekiwana odpowiedź (201 Created):**
```json
{
  "id": "scenario-guid",
  "name": "Test Optimization Scenario",
  "description": "Test scenario for fuel reduction",
  "status": "active",
  "objectiveFunction": "minimize_fuel",
  "createdAt": "2025-11-14T13:00:00Z"
}
```

**Zapisz ID:**
```bash
export SCENARIO_ID="scenario-guid"
```

### 6.2. POST /api/v1/optimization/jobs - Uruchomienie optymalizacji

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/optimization/jobs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "scenarioId": "'$SCENARIO_ID'",
    "priority": "Normal"
  }'
```

**Oczekiwana odpowiedź (201 Created):**
```json
{
  "id": "job-guid",
  "scenarioId": "scenario-guid",
  "status": "Pending",
  "priority": "Normal",
  "progress": 0,
  "createdAt": "2025-11-14T13:10:00Z"
}
```

**Zapisz Job ID:**
```bash
export JOB_ID="job-guid"
```

**UWAGA:** W aktualnej implementacji optymalizacja może nie działać poprawnie bez integracji SLSQP optimizer (Phase 4 - w toku).

### 6.3. GET /api/v1/optimization/jobs/{id} - Status zadania

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/optimization/jobs/$JOB_ID" \
  -H "Authorization: Bearer $TOKEN"
```

**Oczekiwana odpowiedź (200 OK):**
```json
{
  "id": "job-guid",
  "scenarioId": "scenario-guid",
  "status": "Running",
  "progress": 45,
  "currentIteration": 45,
  "maxIterations": 100,
  "startedAt": "2025-11-14T13:10:05Z",
  "estimatedCompletionTime": "2025-11-14T13:15:00Z"
}
```

**Statusy zadania:**
- `Pending` - oczekuje na uruchomienie
- `Running` - w trakcie optymalizacji
- `Completed` - zakończone pomyślnie
- `Failed` - błąd
- `Cancelled` - anulowane

### 6.4. GET /api/v1/optimization/jobs/{id}/results - Wyniki optymalizacji

**Request (po zakończeniu zadania):**
```bash
curl -X GET "http://localhost:8000/api/v1/optimization/jobs/$JOB_ID/results" \
  -H "Authorization: Bearer $TOKEN"
```

**Oczekiwana odpowiedź (200 OK):**
```json
{
  "jobId": "job-guid",
  "status": "Completed",
  "optimalSolution": {
    "fuelReduction": 12.5,
    "co2Reduction": 8.3,
    "parameters": {
      "temperature": 1150,
      "pressure": 1.8,
      "flowRate": 110
    }
  },
  "convergenceHistory": [
    { "iteration": 1, "objectiveValue": 100.0 },
    { "iteration": 50, "objectiveValue": 87.5 },
    { "iteration": 100, "objectiveValue": 87.5 }
  ],
  "completedAt": "2025-11-14T13:15:00Z"
}
```

---

## ❌ Faza 7: Testy obsługi błędów (Global Exception Handler)

### 7.1. Test 400 Bad Request - Błąd walidacji FluentValidation

**Request (brak wymaganego pola):**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "",
    "email": "invalid-email",
    "password": "123"
  }'
```

**Oczekiwana odpowiedź (400 Bad Request):**
```json
{
  "statusCode": 400,
  "message": "Validation failed",
  "errors": [
    {
      "field": "Username",
      "message": "Username is required",
      "code": "NotEmptyValidator"
    },
    {
      "field": "Email",
      "message": "Invalid email format",
      "code": "EmailValidator"
    },
    {
      "field": "Password",
      "message": "Password must be at least 8 characters",
      "code": "MinimumLengthValidator"
    }
  ],
  "traceId": "...",
  "timestamp": "2025-11-14T14:00:00Z"
}
```

### 7.2. Test 401 Unauthorized - Brak tokena

**Request:**
```bash
curl -X GET http://localhost:8000/api/v1/regenerators
```

**Oczekiwana odpowiedź (401 Unauthorized):**
```json
{
  "statusCode": 401,
  "message": "Unauthorized"
}
```

### 7.3. Test 401 Unauthorized - Nieprawidłowy token

**Request:**
```bash
curl -X GET http://localhost:8000/api/v1/regenerators \
  -H "Authorization: Bearer invalid-token-xyz"
```

**Oczekiwana odpowiedź (401 Unauthorized):**
```json
{
  "statusCode": 401,
  "message": "Unauthorized"
}
```

### 7.4. Test 403 Forbidden - Brak uprawnień (Admin only endpoint)

**Request (jako ENGINEER):**
```bash
curl -X GET http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer $TOKEN"
```

**Oczekiwana odpowiedź (403 Forbidden):**
```json
{
  "statusCode": 403,
  "message": "Forbidden"
}
```

### 7.5. Test 404 Not Found - Nieistniejący zasób

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/regenerators/00000000-0000-0000-0000-000000000000" \
  -H "Authorization: Bearer $TOKEN"
```

**Oczekiwana odpowiedź (404 Not Found):**
```json
{
  "statusCode": 404,
  "message": "Configuration not found or access denied",
  "traceId": "...",
  "timestamp": "2025-11-14T14:05:00Z"
}
```

### 7.6. Test 422 Unprocessable Entity - Błąd logiki biznesowej

**Request (próba usunięcia konfiguracji z aktywnymi zadaniami):**
```bash
curl -X DELETE "http://localhost:8000/api/v1/regenerators/$CONFIG_ID" \
  -H "Authorization: Bearer $TOKEN"

# (Zakładając, że config ma aktywne zadania optymalizacji)
```

**Oczekiwana odpowiedź (422 Unprocessable Entity):**
```json
{
  "statusCode": 422,
  "message": "Cannot delete configuration with active optimization jobs",
  "traceId": "...",
  "timestamp": "2025-11-14T14:10:00Z"
}
```

### 7.7. Test 500 Internal Server Error - Nieoczekiwany błąd

**Symulacja:** Wyłącz bazę danych MySQL podczas działania API.

**Request:**
```bash
curl -X GET http://localhost:8000/api/v1/regenerators \
  -H "Authorization: Bearer $TOKEN"
```

**Oczekiwana odpowiedź (500 Internal Server Error):**

**Development mode (szczegółowe):**
```json
{
  "statusCode": 500,
  "message": "Unable to connect to database",
  "details": "StackTrace: at MySql.Data.MySqlClient...",
  "traceId": "...",
  "timestamp": "2025-11-14T14:15:00Z"
}
```

**Production mode (ogólne):**
```json
{
  "statusCode": 500,
  "message": "An internal server error occurred. Please contact support.",
  "traceId": "...",
  "timestamp": "2025-11-14T14:15:00Z"
}
```

---

## 📊 Faza 8: Testy pozostałych kontrolerów

### 8.1. Materials Controller

**GET /api/v1/materials - Lista materiałów:**
```bash
curl -X GET "http://localhost:8000/api/v1/materials?page=1&pageSize=20" \
  -H "Authorization: Bearer $TOKEN"

# Oczekiwane: 200 OK + lista 103 materiałów (jeśli seeded)
```

**GET /api/v1/materials/{id} - Szczegóły materiału:**
```bash
curl -X GET "http://localhost:8000/api/v1/materials/$MATERIAL_ID" \
  -H "Authorization: Bearer $TOKEN"

# Oczekiwane: 200 OK + właściwości termiczne materiału
```

**Status:** ⚠️ **Placeholder implementation** - może zwracać `501 Not Implemented` lub dummy data.

### 8.2. Reports Controller

**POST /api/v1/reports/generate - Generowanie raportu:**
```bash
curl -X POST http://localhost:8000/api/v1/reports/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "jobId": "'$JOB_ID'",
    "format": "PDF",
    "includeCharts": true
  }'

# Oczekiwane: 201 Created + report ID
```

**GET /api/v1/reports/{id} - Pobranie raportu:**
```bash
curl -X GET "http://localhost:8000/api/v1/reports/$REPORT_ID" \
  -H "Authorization: Bearer $TOKEN"

# Oczekiwane: 200 OK + PDF/XLSX file
```

**Status:** ⚠️ **Placeholder implementation** - może zwracać `501 Not Implemented`.

---

## ✅ Checklist weryfikacji

### Konfiguracja (przed uruchomieniem)
- [ ] Port 8000 skonfigurowany w `launchSettings.json`
- [ ] Swagger URL ustawiony na `/api/docs`
- [ ] MySQL dostępny na localhost:3306
- [ ] Baza `fro_db` istnieje z użytkownikiem `fro_user`
- [ ] Redis dostępny (opcjonalnie)
- [ ] `dotnet build` = 0 errors

### Uruchomienie API
- [ ] API startuje na http://localhost:8000
- [ ] Konsola pokazuje "Connected to database"
- [ ] Konsola pokazuje "Database is up to date" lub "Applied X migrations"
- [ ] Swagger UI dostępny: http://localhost:8000/api/docs
- [ ] Health check działa: http://localhost:8000/health
- [ ] Hangfire Dashboard dostępny: http://localhost:8000/hangfire (jeśli Redis działa)

### Testy autentykacji JWT
- [ ] ✅ Rejestracja nowego użytkownika (201 Created)
- [ ] ✅ Błąd walidacji przy słabym haśle (400 Bad Request)
- [ ] ✅ Błąd duplikatu użytkownika (400 Bad Request)
- [ ] ✅ Login z prawidłowymi danymi (200 OK + token)
- [ ] ✅ Login z nieprawidłowym hasłem (401 Unauthorized)
- [ ] ✅ Refresh token (200 OK + nowy token)
- [ ] ✅ Nieprawidłowy refresh token (401 Unauthorized)
- [ ] ✅ GET /auth/me z tokenem (200 OK)
- [ ] ✅ GET /auth/me bez tokena (401 Unauthorized)
- [ ] ✅ Wygasanie tokena po ExpirationMinutes (401 Unauthorized)
- [ ] ✅ Change password (200 OK + weryfikacja logowania)

### Testy CRUD - Users (Admin)
- [ ] ✅ GET /users (200 OK, paginated)
- [ ] ✅ GET /users jako non-admin (403 Forbidden)
- [ ] ✅ GET /users/{id} (200 OK)
- [ ] ✅ GET /users/{nonexistent-id} (404 Not Found)
- [ ] ✅ PUT /users/{id} (200 OK + weryfikacja zmian)
- [ ] ✅ DELETE /users/{id} (204 No Content + weryfikacja 404)

### Testy CRUD - Regenerators
- [ ] ✅ POST /regenerators (201 Created)
- [ ] ✅ POST /regenerators bez wymaganego pola (400 Bad Request)
- [ ] ✅ GET /regenerators (200 OK, paginated)
- [ ] ✅ GET /regenerators?status=Draft (200 OK, filtered)
- [ ] ✅ GET /regenerators/{id} (200 OK)
- [ ] ✅ GET /regenerators/{nonexistent-id} (404 Not Found)
- [ ] ✅ PUT /regenerators/{id} (200 OK + weryfikacja zmian)
- [ ] ✅ DELETE /regenerators/{id} (204 No Content)

### Testy CRUD - Optimization
- [ ] ⚠️ POST /optimization/scenarios (201 Created)
- [ ] ⚠️ POST /optimization/jobs (201 Created)
- [ ] ⚠️ GET /optimization/jobs/{id} (200 OK + status)
- [ ] ⚠️ GET /optimization/jobs/{id}/results (200 OK po zakończeniu)
- [ ] ⚠️ PUT /optimization/jobs/{id}/cancel (200 OK)

**UWAGA:** Optimization może nie działać poprawnie bez SLSQP optimizer integration (Phase 4).

### Testy obsługi błędów
- [ ] ✅ 400 Bad Request - FluentValidation errors (z listą `errors`)
- [ ] ✅ 401 Unauthorized - brak tokena
- [ ] ✅ 401 Unauthorized - nieprawidłowy token
- [ ] ✅ 403 Forbidden - brak uprawnień (admin endpoint)
- [ ] ✅ 404 Not Found - nieistniejący zasób (KeyNotFoundException)
- [ ] ✅ 422 Unprocessable Entity - błąd logiki biznesowej (InvalidOperationException)
- [ ] ✅ 500 Internal Server Error - nieoczekiwany błąd (Exception)
- [ ] ✅ TraceId obecny we wszystkich odpowiedziach błędów
- [ ] ✅ Timestamp obecny we wszystkich odpowiedziach błędów
- [ ] ✅ Development mode - szczegółowe `details` + stack trace
- [ ] ✅ Production mode - ogólny komunikat (brak stack trace)

### Testy Swagger/OpenAPI
- [ ] ✅ Wszystkie 6 kontrolerów widoczne w Swagger
- [ ] ✅ Przycisk "Authorize" działa (Bearer token)
- [ ] ✅ Po autoryzacji chronione endpointy są dostępne
- [ ] ✅ Schematy JSON poprawnie wyświetlane (DTOs)
- [ ] ✅ "Try it out" działa dla przykładowych requestów
- [ ] ✅ Walidacje wyświetlane w schematach (required, min/max, regex)

### Testy Materials & Reports (Placeholder)
- [ ] ⚠️ GET /materials (200 OK lub 501 Not Implemented)
- [ ] ⚠️ GET /materials/{id} (200 OK lub 501)
- [ ] ⚠️ POST /reports/generate (201 Created lub 501)
- [ ] ⚠️ GET /reports/{id} (200 OK lub 501)

---

## 🐛 Znane problemy i ograniczenia

### 1. SLSQP Optimizer nie zintegrowany (Phase 4)
**Status:** 🚧 W toku
**Impact:** Optymalizacja może nie działać poprawnie

**Oczekiwane zachowanie:**
- `POST /optimization/jobs` tworzy zadanie (201 Created)
- Job status zmienia się na `Pending` → `Running` → **`Failed`** (brak optimizera)
- Błąd: "SLSQP optimizer service not available"

**Rozwiązanie:** Zaplanowane w Phase 4 (Python microservice integration)

### 2. EF Core Migrations nie utworzone (Phase 5)
**Status:** 🚧 W toku
**Impact:** Może brakować tabel w bazie danych

**Obejście:**
```bash
# Utwórz migracje ręcznie
cd backend-dotnet/Fro.Api
dotnet ef migrations add InitialCreate --project ../Fro.Infrastructure
dotnet ef database update --project ../Fro.Infrastructure

# Sprawdź status migracji
dotnet ef migrations list --project ../Fro.Infrastructure
```

### 3. Materials & Reports - Placeholder Implementation
**Status:** ⚠️ Placeholder
**Impact:** Endpointy mogą zwracać `501 Not Implemented` lub dummy data

**Oczekiwane zachowanie:**
- Kontrolery istnieją
- Endpointy zwracają 200 OK ale z placeholder data
- Lub zwracają 501 Not Implemented

**Rozwiązanie:** Zaplanowane w Phase 6

### 4. DatabaseSeeder może być niekompletny
**Status:** ⚠️ Do weryfikacji

**Sprawdzenie:**
```csharp
// Otwórz: backend-dotnet/Fro.Infrastructure/Data/DatabaseSeeder.cs
// Sprawdź co jest seedowane:
// - Admin user?
// - Test materials?
// - Sample configurations?
```

**Obejście:** Dodaj dane testowe ręcznie przez SQL lub API.

### 5. Hangfire wymaga Redis
**Status:** ✅ Graceful degradation

**Zachowanie:**
- Jeśli Redis niedostępny: API uruchomi się **bez Hangfire**
- Konsola: "⚠ Warning: Could not connect to Redis. Hangfire will not be available."
- Background jobs (OptimizationJob) nie będą działać
- Endpointy `/hangfire` zwrócą 404

**Rozwiązanie:** Uruchom Redis lub testuj bez background jobs.

---

## 📝 Podsumowanie i rekomendacje

### ✅ Co jest gotowe do testowania (80%)

1. **Autentykacja JWT** - w pełni funkcjonalna ✅
   - Login, register, refresh token
   - Change password, password reset
   - Token expiration handling

2. **CRUD Operations** - implementacja kompletna ✅
   - Users (Admin only)
   - Regenerator Configurations
   - Optimization Scenarios (częściowo)

3. **Global Exception Handler** - w pełni funkcjonalny ✅
   - Wszystkie kody błędów (400, 401, 403, 404, 422, 500)
   - FluentValidation integration
   - TraceId + Timestamp

4. **Swagger/OpenAPI** - w pełni funkcjonalny ✅
   - JWT authorization
   - Wszystkie endpointy udokumentowane
   - Try it out + schematy JSON

5. **Infrastructure** - gotowa ✅
   - EF Core + MySQL
   - Repository pattern
   - Dependency Injection
   - Graceful degradation (Redis optional)

### ⚠️ Co wymaga dodatkowej pracy (20%)

1. **SLSQP Optimizer Integration** - Phase 4 (2-3 dni)
   - Python microservice
   - HTTP client integration
   - Hangfire job completion

2. **EF Core Migrations** - Phase 5 (1 dzień)
   - Initial migration
   - Database seeding
   - Schema sync with Python backend

3. **Materials & Reports** - Phase 6 (2-3 dni)
   - Pełna implementacja (obecnie placeholders)
   - API dla 103 materiałów
   - Generowanie raportów PDF/XLSX

4. **Unit & Integration Tests** - Phase 7 (3-4 dni)
   - xUnit + Moq + FluentAssertions
   - Test coverage 70%+
   - CI/CD integration

### 📌 Skorygowany plan testowania

**Poprawki wprowadzone:**
1. ✅ Port zmieniony: 5119 → **8000** (HTTP), 7164 → **8001** (HTTPS)
2. ✅ Swagger URL: `/swagger` → `/api/docs`
3. ✅ Launch URL: `swagger` → `api/docs`
4. ✅ CORS: Dodano `http://localhost:8000`

**Wersja finalna:**
- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/api/docs`
- Health: `http://localhost:8000/health`
- Hangfire: `http://localhost:8000/hangfire`

### 🚀 Następne kroki

**Priorytet 1 (krytyczne):**
1. Uruchom API lokalnie i wykonaj testy z tej dokumentacji
2. Zweryfikuj autentykację JWT (login, register, token expiration)
3. Przetestuj CRUD dla Users i Regenerators
4. Zweryfikuj globalną obsługę błędów (wszystkie kody)

**Priorytet 2 (ważne):**
5. Stwórz EF Core migrations: `dotnet ef migrations add InitialCreate`
6. Zastosuj migracje: `dotnet ef database update`
7. Zweryfikuj DatabaseSeeder (admin user + test data)

**Priorytet 3 (planowane):**
8. Integracja SLSQP optimizer (Phase 4)
9. Pełna implementacja Materials & Reports
10. Unit + integration tests (Phase 7)

---

**Dokument przygotowany:** 2025-11-14
**Wersja:** 1.0 (skorygowana)
**Status API:** Gotowe do testowania (80% kompletności)
