# Instrukcje Budowania - .NET Backend

## Problem: "MSBUILD : error MSB1011"

Jeśli otrzymujesz błąd:
```
MSBUILD : error MSB1011: określ plik projektu lub rozwiązania, który zostanie użyty,
ponieważ ten folder zawiera więcej niż jeden plik projektu lub rozwiązania.
```

**Przyczyna:** W folderze znajduje się więcej niż jeden plik `.sln` lub `.csproj` w głównym katalogu.

**Rozwiązanie:** Użyj konkretnego pliku rozwiązania:

```bash
dotnet build Forglass.RegeneratorOptimizer.sln
```

---

## Szybka Kompilacja

### Option 1: Użyj gotowego skryptu

**Windows:**
```cmd
build.bat
```

**Linux/Mac:**
```bash
./build.sh
```

### Option 2: Ręczna kompilacja

**1. Przywróć pakiety:**
```bash
dotnet restore Forglass.RegeneratorOptimizer.sln
```

**2. Zbuduj rozwiązanie:**
```bash
dotnet build Forglass.RegeneratorOptimizer.sln --configuration Release
```

**3. Uruchom API:**
```bash
cd Fro.Api
dotnet run
```

---

## Struktura Projektu

```
backend-dotnet/
├── Forglass.RegeneratorOptimizer.sln  ← Główny plik rozwiązania (użyj tego!)
├── Fro.Domain/                         ← Warstwa domenowa (encje, enumy)
├── Fro.Application/                    ← Warstwa aplikacji (serwisy, DTOs)
├── Fro.Infrastructure/                 ← Warstwa infrastruktury (EF Core, repos)
├── Fro.Api/                            ← Warstwa API (kontrolery, Program.cs)
├── build.sh                            ← Skrypt budowania (Linux/Mac)
└── build.bat                           ← Skrypt budowania (Windows)
```

**WAŻNE:**
- Zawsze używaj `Forglass.RegeneratorOptimizer.sln` do budowania
- NIE uruchamiaj `dotnet build` bez parametrów w głównym folderze
- Jeśli widzisz pliki testowe (np. `TestDbContext.csproj`), usuń je

---

## Migracje Entity Framework Core

### Wygeneruj nową migrację:

```bash
dotnet ef migrations add NazwaMigracji \
  --project Fro.Infrastructure \
  --startup-project Fro.Api \
  --output-dir Data/Migrations
```

**Przykład:**
```bash
dotnet ef migrations add InitialCreate \
  --project Fro.Infrastructure \
  --startup-project Fro.Api
```

### Zastosuj migrację do bazy danych:

```bash
dotnet ef database update \
  --project Fro.Infrastructure \
  --startup-project Fro.Api
```

### Zobacz wszystkie migracje:

```bash
dotnet ef migrations list \
  --project Fro.Infrastructure \
  --startup-project Fro.Api
```

### Cofnij ostatnią migrację:

```bash
dotnet ef migrations remove \
  --project Fro.Infrastructure \
  --startup-project Fro.Api
```

---

## Uruchomienie API

### Development Mode:

```bash
cd Fro.Api
dotnet run
```

API będzie dostępne pod:
- **Swagger:** http://localhost:5000/api/docs
- **Health Check:** http://localhost:5000/health
- **Hangfire Dashboard:** http://localhost:5000/hangfire (jeśli Redis działa)

### Watch Mode (auto-reload):

```bash
cd Fro.Api
dotnet watch run
```

### Production Mode:

```bash
cd Fro.Api
dotnet run --configuration Release
```

---

## Typowe Problemy

### Problem 1: "dotnet: command not found"

**Rozwiązanie:** Zainstaluj .NET SDK 8.0 lub wyższy:
- Windows: https://dotnet.microsoft.com/download
- Linux: `sudo apt install dotnet-sdk-8.0`
- Mac: `brew install dotnet`

### Problem 2: "Unable to create an object of type 'ApplicationDbContext'"

**Przyczyna:** Brak connection string lub nieprawidłowy connection string.

**Rozwiązanie:** Sprawdź `Fro.Api/appsettings.json`:
```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost;Port=3306;Database=fro_db;User=fro_user;Password=fro_password;"
  }
}
```

### Problem 3: Błędy kompilacji po aktualizacji encji

**Rozwiązanie:**
```bash
dotnet clean Forglass.RegeneratorOptimizer.sln
dotnet restore Forglass.RegeneratorOptimizer.sln
dotnet build Forglass.RegeneratorOptimizer.sln
```

### Problem 4: "Cannot connect to MySQL server"

**Sprawdź czy MySQL działa:**
```bash
# Linux/Mac
systemctl status mysql
# lub
mysql -h localhost -P 3306 -u fro_user -pfro_password

# Windows
net start mysql
```

**Rozwiązanie:** Upewnij się że:
- MySQL jest uruchomiony
- Port 3306 jest dostępny
- Użytkownik `fro_user` istnieje i ma uprawnienia

### Problem 5: Błędy NuGet

**Rozwiązanie:**
```bash
# Wyczyść cache NuGet
dotnet nuget locals all --clear

# Przywróć pakiety ponownie
dotnet restore Forglass.RegeneratorOptimizer.sln
```

---

## Polecenia Diagnostyczne

### Sprawdź wersję .NET:
```bash
dotnet --version
```

### Zobacz zainstalowane SDK:
```bash
dotnet --list-sdks
```

### Zobacz wszystkie projekty w rozwiązaniu:
```bash
dotnet sln Forglass.RegeneratorOptimizer.sln list
```

### Sprawdź zależności projektu:
```bash
dotnet list Fro.Api package
```

---

## Kompilacja dla Różnych Platform

### Windows x64:
```bash
dotnet publish Fro.Api -c Release -r win-x64 --self-contained
```

### Linux x64:
```bash
dotnet publish Fro.Api -c Release -r linux-x64 --self-contained
```

### macOS ARM64:
```bash
dotnet publish Fro.Api -c Release -r osx-arm64 --self-contained
```

Pliki wyjściowe będą w: `Fro.Api/bin/Release/net8.0/{runtime}/publish/`

---

## Debugowanie

### Visual Studio:
1. Otwórz `Forglass.RegeneratorOptimizer.sln`
2. Ustaw `Fro.Api` jako startup project
3. Naciśnij F5

### Visual Studio Code:
1. Zainstaluj rozszerzenie "C# Dev Kit"
2. Otwórz folder `backend-dotnet`
3. F5 → Wybierz ".NET Core Launch (web)"

### Rider:
1. Otwórz `Forglass.RegeneratorOptimizer.sln`
2. Run → Debug 'Fro.Api'

---

## Dalsze Kroki

Po pomyślnej kompilacji:

1. **Wygeneruj migracje EF Core:**
   ```bash
   dotnet ef migrations add InitialCreate --project Fro.Infrastructure --startup-project Fro.Api
   ```

2. **Zastosuj migracje:**
   ```bash
   dotnet ef database update --project Fro.Infrastructure --startup-project Fro.Api
   ```

3. **Uruchom API:**
   ```bash
   cd Fro.Api && dotnet run
   ```

4. **Testuj API:**
   - Otwórz Swagger: http://localhost:5000/api/docs
   - Przetestuj endpoint `/health`
   - Zaloguj się jako `admin/admin`

5. **Opcjonalnie - Uruchom Python optimizer service:**
   ```bash
   cd ../optimizer-service
   ./start.sh  # Linux/Mac
   start.bat   # Windows
   ```

---

## Dodatkowe Zasoby

- **Dokumentacja migracji:** [MIGRATIONS_GUIDE.md](./MIGRATIONS_GUIDE.md)
- **Analiza kompatybilności:** [SCHEMA_COMPATIBILITY_ANALYSIS.md](./SCHEMA_COMPATIBILITY_ANALYSIS.md)
- **Status implementacji:** [IMPLEMENTATION_STATUS_2025-11-14.md](./IMPLEMENTATION_STATUS_2025-11-14.md)
- **Testy API:** [DOTNET_API_TESTING_GUIDE.md](./DOTNET_API_TESTING_GUIDE.md)

---

**Ostatnia aktualizacja:** 2025-11-16
**Wersja:** 1.0
**Status:** Gotowe do użycia (100% kompatybilność z backendem Python)
