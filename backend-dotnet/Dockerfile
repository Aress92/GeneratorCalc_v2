# Stage 1: Build
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy solution and project files
COPY ["Fro.Api/Fro.Api.csproj", "Fro.Api/"]
COPY ["Fro.Application/Fro.Application.csproj", "Fro.Application/"]
COPY ["Fro.Infrastructure/Fro.Infrastructure.csproj", "Fro.Infrastructure/"]
COPY ["Fro.Domain/Fro.Domain.csproj", "Fro.Domain/"]

# Restore dependencies
RUN dotnet restore "Fro.Api/Fro.Api.csproj"

# Copy all source code
COPY . .

# Build the application
WORKDIR "/src/Fro.Api"
RUN dotnet build "Fro.Api.csproj" -c Release -o /app/build

# Stage 2: Publish
FROM build AS publish
RUN dotnet publish "Fro.Api.csproj" -c Release -o /app/publish /p:UseAppHost=false

# Stage 3: Runtime
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy published application
COPY --from=publish /app/publish .

# Expose ports
EXPOSE 5000
EXPOSE 5001

# Environment variables (can be overridden in docker-compose.yml)
ENV ASPNETCORE_URLS=http://+:5000
ENV ASPNETCORE_ENVIRONMENT=Development

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Run the application
ENTRYPOINT ["dotnet", "Fro.Api.dll"]
