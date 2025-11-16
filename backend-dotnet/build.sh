#!/bin/bash
# Build script for Forglass Regenerator Optimizer .NET Backend

set -e  # Exit on error

echo "=== Budowanie Forglass Regenerator Optimizer ==="
echo ""

# Navigate to backend-dotnet directory
cd "$(dirname "$0")"

# Clean previous builds
echo "1. Czyszczenie poprzednich kompilacji..."
dotnet clean Forglass.RegeneratorOptimizer.sln

# Restore NuGet packages
echo ""
echo "2. Przywracanie pakietów NuGet..."
dotnet restore Forglass.RegeneratorOptimizer.sln

# Build solution
echo ""
echo "3. Kompilacja rozwiązania..."
dotnet build Forglass.RegeneratorOptimizer.sln --configuration Release --no-restore

# Check build result
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Kompilacja zakończona sukcesem!"
    echo ""
    echo "Aby uruchomić API:"
    echo "  cd Fro.Api"
    echo "  dotnet run"
    echo ""
    echo "Aby wygenerować migrację EF Core:"
    echo "  dotnet ef migrations add NazwaMigracji --project Fro.Infrastructure --startup-project Fro.Api"
    echo ""
    echo "Aby zastosować migrację do bazy danych:"
    echo "  dotnet ef database update --project Fro.Infrastructure --startup-project Fro.Api"
else
    echo ""
    echo "❌ Kompilacja nie powiodła się. Sprawdź błędy powyżej."
    exit 1
fi
