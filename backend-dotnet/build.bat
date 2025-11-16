@echo off
REM Build script for Forglass Regenerator Optimizer .NET Backend

echo === Budowanie Forglass Regenerator Optimizer ===
echo.

REM Navigate to backend-dotnet directory
cd /d "%~dp0"

REM Clean previous builds
echo 1. Czyszczenie poprzednich kompilacji...
dotnet clean Forglass.RegeneratorOptimizer.sln
if %ERRORLEVEL% NEQ 0 goto :error

REM Restore NuGet packages
echo.
echo 2. Przywracanie pakietow NuGet...
dotnet restore Forglass.RegeneratorOptimizer.sln
if %ERRORLEVEL% NEQ 0 goto :error

REM Build solution
echo.
echo 3. Kompilacja rozwiazania...
dotnet build Forglass.RegeneratorOptimizer.sln --configuration Release --no-restore
if %ERRORLEVEL% NEQ 0 goto :error

echo.
echo ✓ Kompilacja zakonczona sukcesem!
echo.
echo Aby uruchomic API:
echo   cd Fro.Api
echo   dotnet run
echo.
echo Aby wygenerowac migracje EF Core:
echo   dotnet ef migrations add NazwaMigracji --project Fro.Infrastructure --startup-project Fro.Api
echo.
echo Aby zastosowac migracje do bazy danych:
echo   dotnet ef database update --project Fro.Infrastructure --startup-project Fro.Api
echo.

goto :end

:error
echo.
echo X Kompilacja nie powiodla sie. Sprawdz bledy powyzej.
exit /b 1

:end
exit /b 0
