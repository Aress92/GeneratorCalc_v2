# .NET Backend - Quick Start Guide

## 🚀 Opcja 1: Uruchomienie z Docker (ZALECANE)

### Wymagania
- Docker Desktop zainstalowany i uruchomiony
- MySQL i Redis działają (przez docker-compose)

### Krok 1: Uruchom infrastrukturę (MySQL + Redis)

```bash
# Z głównego katalogu projektu
docker compose up -d mysql redis
```

Sprawdź czy usługi działają:
```bash
docker compose ps
```

### Krok 2: Uruchom backend .NET

```bash
# Uruchom tylko backend .NET (z profilem dotnet)
docker compose --profile dotnet up -d backend-dotnet

# Lub zbuduj i uruchom z logami
docker compose --profile dotnet up --build backend-dotnet
```

### Krok 3: Sprawdź czy działa

Otwórz w przeglądarce:
- **Swagger UI**: http://localhost:5000/api/docs
- **Health Check**: http://localhost:5000/health
- **Hangfire Dashboard**: http://localhost:5000/hangfire (jeśli Redis działa)

### Sprawdź logi

```bash
# Logi w czasie rzeczywistym
docker compose logs backend-dotnet -f

# Ostatnie 100 linii
docker compose logs backend-dotnet --tail=100
```

### Zatrzymaj serwis

```bash
# Zatrzymaj backend .NET
docker compose stop backend-dotnet

# Zatrzymaj wszystko
docker compose down
```

---

## 🔧 Opcja 2: Uruchomienie lokalnie (bez Docker)

### Wymagania
- **.NET 8 SDK** zainstalowany: https://dotnet.microsoft.com/download/dotnet/8.0
- MySQL działa lokalnie lub w Docker
- Redis działa lokalnie lub w Docker (opcjonalnie)

### Krok 1: Sprawdź instalację .NET

```bash
dotnet --version
# Powinno pokazać: 8.0.x
```

Jeśli nie masz .NET 8:
- **Windows**: Pobierz installer z https://dotnet.microsoft.com/download/dotnet/8.0
- **macOS**: `brew install dotnet@8`
- **Linux**: Sprawdź instrukcje dla swojej dystrybucji

### Krok 2: Uruchom MySQL i Redis (opcjonalnie przez Docker)

```bash
# Z głównego katalogu projektu
docker compose up -d mysql redis

# Sprawdź czy działają
docker compose ps
```

Lub użyj lokalnych instalacji MySQL/Redis.

### Krok 3: Skonfiguruj connection string

Edytuj `backend-dotnet/Fro.Api/appsettings.json`:

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost;Port=3306;Database=fro_db;User=fro_user;Password=fro_password;",
    "Redis": "localhost:6379,abortConnect=false"
  }
}
```

### Krok 4: Uruchom aplikację

```bash
cd backend-dotnet/Fro.Api
dotnet run
```

Lub dla auto-reload podczas developmentu:
```bash
dotnet watch run
```

### Krok 5: Sprawdź czy działa

Otwórz w przeglądarce:
- **Swagger UI**: http://localhost:5000/api/docs
- **Health Check**: http://localhost:5000/health
- **Hangfire Dashboard**: http://localhost:5000/hangfire

---

## 📝 Testowanie API

### 1. Zarejestruj użytkownika (Swagger)

Otwórz http://localhost:5000/api/docs i użyj endpointu:

**POST** `/api/v1/auth/register`

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "Test123!@#",
  "fullName": "Test User"
}
```

### 2. Zaloguj się

**POST** `/api/v1/auth/login`

```json
{
  "username": "testuser",
  "password": "Test123!@#"
}
```

Skopiuj **access_token** z odpowiedzi.

### 3. Autoryzuj w Swagger

Kliknij przycisk **Authorize** (🔒) w prawym górnym rogu Swagger UI:
```
Bearer <WKLEJ_TOKEN_TUTAJ>
```

### 4. Testuj inne endpointy

Teraz możesz testować wszystkie endpointy:
- **GET** `/api/v1/users/me` - Twój profil
- **GET** `/api/v1/regenerator-configurations` - Lista konfiguracji
- **POST** `/api/v1/regenerator-configurations` - Utwórz nową konfigurację

---

## 🛠️ Rozwiązywanie problemów

### Problem: "Unable to connect to database"

**Rozwiązanie 1**: Sprawdź czy MySQL działa
```bash
docker compose ps mysql
# lub
docker compose logs mysql --tail=50
```

**Rozwiązanie 2**: Sprawdź connection string w `appsettings.json`
- Server: `localhost` (lokalnie) lub `mysql` (w Docker)
- Port: `3306`
- Database: `fro_db`
- User: `fro_user`
- Password: `fro_password`

**Rozwiązanie 3**: Test połączenia MySQL
```bash
# Z Docker
docker compose exec mysql mysql -u fro_user -pfro_password fro_db -e "SHOW TABLES;"

# Lokalnie
mysql -h localhost -P 3306 -u fro_user -pfro_password fro_db -e "SHOW TABLES;"
```

### Problem: "Could not connect to Redis"

To jest **normalne** - Hangfire jest opcjonalny. Aplikacja uruchomi się bez Hangfire.

Jeśli chcesz użyć Hangfire:
```bash
docker compose up -d redis
```

### Problem: "Port 5000 is already in use"

**Rozwiązanie 1**: Zatrzymaj proces używający portu 5000
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :5000
kill -9 <PID>
```

**Rozwiązanie 2**: Zmień port w `appsettings.json`:
```json
{
  "Kestrel": {
    "Endpoints": {
      "Http": {
        "Url": "http://localhost:5001"
      }
    }
  }
}
```

### Problem: Build errors

```bash
# Wyczyść i zbuduj ponownie
cd backend-dotnet
dotnet clean
dotnet restore
dotnet build
```

---

## 📊 Dostępne endpointy

Po uruchomieniu aplikacji masz dostęp do:

### API Documentation
- **Swagger UI**: http://localhost:5000/api/docs
- **OpenAPI JSON**: http://localhost:5000/swagger/v1/swagger.json

### Monitoring
- **Health Check**: http://localhost:5000/health
- **Hangfire Dashboard**: http://localhost:5000/hangfire (wymaga Redis)

### API Routes (57 endpoints)
- **Authentication** (6): `/api/v1/auth/*`
- **Users** (10): `/api/v1/users/*`
- **Regenerator Configurations** (13): `/api/v1/regenerator-configurations/*`
- **Optimization** (18): `/api/v1/optimization/*`
- **Materials** (6): `/api/v1/materials/*` ⚠️ *placeholder*
- **Reports** (4): `/api/v1/reports/*` ⚠️ *placeholder*

---

## 🐛 Debugging

### Visual Studio (Windows)

1. Otwórz `backend-dotnet/Fro.sln` w Visual Studio
2. Ustaw `Fro.Api` jako Startup Project (prawy klik → Set as Startup Project)
3. Naciśnij **F5** lub kliknij **▶ Start Debugging**

### Visual Studio Code (wszystkie platformy)

1. Otwórz folder `backend-dotnet` w VS Code
2. Zainstaluj rozszerzenie: **C# Dev Kit**
3. Naciśnij **F5** lub:
   - **Run and Debug** panel (Ctrl+Shift+D)
   - Wybierz **".NET Core Launch (web)"**
   - Kliknij **▶ Start Debugging**

### JetBrains Rider (wszystkie platformy)

1. Otwórz `backend-dotnet/Fro.sln` w Rider
2. Wybierz konfigurację **Fro.Api**
3. Naciśnij **Shift+F10** (Run) lub **Shift+F9** (Debug)

---

## 📚 Więcej informacji

- **Architektura**: Zobacz `CLAUDE.md` w głównym katalogu
- **Status migracji**: Zobacz `IMPLEMENTATION_STATUS_2025-11-14.md`
- **API Testing**: Zobacz `API_TESTING_PLAN.md`

---

## 🎯 Następne kroki

Po uruchomieniu aplikacji:

1. ✅ Przetestuj wszystkie endpointy w Swagger
2. ✅ Zweryfikuj JWT authentication
3. ✅ Sprawdź walidację danych (FluentValidation)
4. ⏳ Integracja SLSQP optimizer (Python microservice)
5. ⏳ Unit & integration tests
6. ⏳ Production deployment
