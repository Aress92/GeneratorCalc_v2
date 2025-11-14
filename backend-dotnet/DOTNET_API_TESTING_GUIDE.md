# .NET API Testing Guide

Complete guide for testing the Forglass Regenerator Optimizer .NET API through Swagger UI and HTTP clients.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Starting the API](#starting-the-api)
3. [Accessing Swagger UI](#accessing-swagger-ui)
4. [Authentication Flow](#authentication-flow)
5. [Testing Scenarios](#testing-scenarios)
6. [Endpoint Reference](#endpoint-reference)
7. [Error Handling Tests](#error-handling-tests)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **.NET SDK 8.0** - [Download](https://dotnet.microsoft.com/download/dotnet/8.0)
- **MySQL 8.0** - Running on localhost:3306
- **Redis** (optional) - Running on localhost:6379 (for Hangfire background jobs)

### Database Setup

Ensure MySQL is running with the following configuration:

```bash
# Connection details (from appsettings.json)
Server: localhost
Port: 3306
Database: fro_db
User: fro_user
Password: fro_password
```

If using Docker for MySQL:

```bash
docker run -d \
  --name mysql-fro \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=fro_db \
  -e MYSQL_USER=fro_user \
  -e MYSQL_PASSWORD=fro_password \
  -p 3306:3306 \
  mysql:8.0
```

### Redis Setup (Optional)

For background job support (Hangfire):

```bash
docker run -d \
  --name redis-fro \
  -p 6379:6379 \
  redis:alpine
```

**Note:** The API will start without Redis, but Hangfire features won't be available.

---

## Starting the API

### Step 1: Navigate to API Project

```bash
cd backend-dotnet/Fro.Api
```

### Step 2: Restore Dependencies

```bash
dotnet restore
```

### Step 3: Build the Project

```bash
dotnet build
```

### Step 4: Run the API

**Standard mode:**
```bash
dotnet run
```

**Watch mode (auto-reload on file changes):**
```bash
dotnet watch run
```

### Step 5: Verify Startup

You should see output similar to:

```
info: Microsoft.Hosting.Lifetime[14]
      Now listening on: http://localhost:5000
info: Microsoft.Hosting.Lifetime[0]
      Application started. Press Ctrl+C to shut down.
✓ Connected to database
✓ Database is up to date (no pending migrations)
✓ Connected to Redis
✓ Hangfire configured with Redis storage
✓ Hangfire Dashboard available at /hangfire
```

**If Redis is not available:**
```
⚠ Warning: Could not connect to Redis. Hangfire will not be available.
  API will start without background job support.
```

---

## Accessing Swagger UI

### Swagger URL

Once the API is running, open your browser to:

**http://localhost:5000/api/docs**

### Other Access Points

- **Health Check:** http://localhost:5000/health
- **Hangfire Dashboard:** http://localhost:5000/hangfire (if Redis connected)

### Swagger Interface Overview

The Swagger UI provides:

1. **Interactive API documentation** - All endpoints grouped by controller
2. **"Try it out" feature** - Execute requests directly from the browser
3. **JWT Authentication** - Green "Authorize" button at top-right
4. **Request/Response schemas** - Auto-generated from C# DTOs
5. **Error codes** - All possible HTTP status codes documented

---

## Authentication Flow

### Step 1: Register a New User

**Endpoint:** `POST /api/v1/Auth/register`

**Request Body:**
```json
{
  "username": "testuser",
  "email": "testuser@example.com",
  "password": "SecurePassword123!",
  "fullName": "Test User"
}
```

**Expected Response (201 Created):**
```json
{
  "id": "64c41315-9eb5-4878-bcdb-3e943847e76f",
  "username": "testuser",
  "email": "testuser@example.com",
  "fullName": "Test User",
  "role": "ENGINEER",
  "isActive": true,
  "isVerified": false
}
```

**Notes:**
- Default role is `ENGINEER`
- `isVerified` starts as `false` (admin can verify later)
- Password must meet complexity requirements (8+ chars, uppercase, lowercase, number, special char)

---

### Step 2: Login

**Endpoint:** `POST /api/v1/Auth/login`

**Request Body:**
```json
{
  "username": "testuser",
  "password": "SecurePassword123!"
}
```

**Expected Response (200 OK):**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "d4e5f6g7-h8i9-j0k1-l2m3-n4o5p6q7r8s9",
  "expiresIn": 86400,
  "tokenType": "Bearer",
  "user": {
    "id": "64c41315-9eb5-4878-bcdb-3e943847e76f",
    "username": "testuser",
    "email": "testuser@example.com",
    "fullName": "Test User",
    "role": "ENGINEER",
    "isActive": true,
    "isVerified": false
  }
}
```

**Token Details:**
- `accessToken` - JWT token valid for 24 hours (1440 minutes)
- `refreshToken` - Valid for 7 days
- `expiresIn` - Seconds until token expiration

---

### Step 3: Authorize in Swagger

1. Click the **green "Authorize" button** at top-right of Swagger UI
2. In the "Value" field, enter: `Bearer <your-access-token>`
   - Example: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
3. Click **"Authorize"**
4. Click **"Close"**

**All subsequent requests will include the Authorization header automatically.**

---

### Step 4: Get Current User

**Endpoint:** `GET /api/v1/Auth/me`

**No request body needed (uses JWT token)**

**Expected Response (200 OK):**
```json
{
  "id": "64c41315-9eb5-4878-bcdb-3e943847e76f",
  "username": "testuser",
  "email": "testuser@example.com",
  "fullName": "Test User",
  "role": "ENGINEER",
  "isActive": true,
  "isVerified": false
}
```

---

### Step 5: Refresh Token (Before Expiration)

**Endpoint:** `POST /api/v1/Auth/refresh`

**Request Body:**
```json
{
  "refreshToken": "d4e5f6g7-h8i9-j0k1-l2m3-n4o5p6q7r8s9"
}
```

**Expected Response (200 OK):**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "expiresIn": 86400,
  "tokenType": "Bearer",
  "user": { ... }
}
```

**Notes:**
- Old refresh token is invalidated
- New tokens are issued

---

## Testing Scenarios

### Scenario 1: User Registration & Authentication ✅

**Objective:** Verify complete user lifecycle from registration to authenticated requests.

**Steps:**

1. **Register new user** - `POST /api/v1/Auth/register`
2. **Login with credentials** - `POST /api/v1/Auth/login`
3. **Get current user info** - `GET /api/v1/Auth/me`
4. **Change password** - `POST /api/v1/Auth/change-password`
5. **Login with new password** - `POST /api/v1/Auth/login`

**Password Change Request:**
```json
{
  "currentPassword": "SecurePassword123!",
  "newPassword": "NewSecurePassword456!"
}
```

**Expected:** All operations succeed (200/201 status codes).

---

### Scenario 2: Regenerator Configuration CRUD ✅

**Objective:** Test complete lifecycle of regenerator configurations.

**Steps:**

1. **Create new configuration** - `POST /api/v1/Regenerators`

```json
{
  "name": "Test Regenerator Config",
  "description": "Test configuration for API testing",
  "configurationData": {
    "regeneratorType": "checker",
    "height": 12.5,
    "width": 8.0,
    "depth": 10.0,
    "numberOfChambers": 2,
    "operatingTemperature": 1450,
    "flueGasTemperature": 1350
  }
}
```

**Expected Response (201 Created):**
```json
{
  "id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "userId": "64c41315-9eb5-4878-bcdb-3e943847e76f",
  "name": "Test Regenerator Config",
  "description": "Test configuration for API testing",
  "status": "DRAFT",
  "wizardStep": 1,
  "configurationData": { ... },
  "createdAt": "2025-11-14T12:00:00Z",
  "updatedAt": "2025-11-14T12:00:00Z"
}
```

2. **Get all configurations** - `GET /api/v1/Regenerators?page=1&pageSize=10`

**Expected Response (200 OK):**
```json
{
  "items": [
    {
      "id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
      "name": "Test Regenerator Config",
      "status": "DRAFT",
      ...
    }
  ],
  "totalCount": 1,
  "page": 1,
  "pageSize": 10,
  "totalPages": 1,
  "hasPreviousPage": false,
  "hasNextPage": false
}
```

3. **Get configuration by ID** - `GET /api/v1/Regenerators/{id}`

4. **Update configuration** - `PUT /api/v1/Regenerators/{id}`

```json
{
  "name": "Updated Regenerator Config",
  "description": "Updated description",
  "wizardStep": 2,
  "configurationData": {
    "regeneratorType": "checker",
    "height": 13.0,
    "width": 8.5,
    "depth": 10.5,
    "numberOfChambers": 2,
    "operatingTemperature": 1500,
    "flueGasTemperature": 1400
  }
}
```

5. **Delete configuration** - `DELETE /api/v1/Regenerators/{id}`

**Expected Response (200 OK):**
```json
{
  "message": "Configuration deleted successfully"
}
```

---

### Scenario 3: Optimization Workflow ✅

**Objective:** Test complete optimization job lifecycle.

**Prerequisites:**
- Existing regenerator configuration (from Scenario 2)
- Configuration must have `status: "VALIDATED"` or `"COMPLETED"`

**Steps:**

1. **Create optimization scenario** - `POST /api/v1/Optimization/scenarios`

```json
{
  "configurationId": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "name": "Fuel Efficiency Optimization",
  "description": "Optimize for minimum fuel consumption",
  "objectiveType": "fuel_efficiency",
  "constraints": {
    "maxPressureDrop": 500,
    "minThermalEfficiency": 0.85,
    "maxMaterialCost": 50000
  },
  "bounds": {
    "checkerHeightMin": 10.0,
    "checkerHeightMax": 15.0,
    "numberOfLayersMin": 20,
    "numberOfLayersMax": 40
  }
}
```

**Expected Response (201 Created):**
```json
{
  "id": "b2c3d4e5-f6g7-h8i9-j0k1-l2m3n4o5p6q7",
  "configurationId": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "userId": "64c41315-9eb5-4878-bcdb-3e943847e76f",
  "name": "Fuel Efficiency Optimization",
  "description": "Optimize for minimum fuel consumption",
  "status": "active",
  "objectiveType": "fuel_efficiency",
  "constraints": { ... },
  "bounds": { ... },
  "createdAt": "2025-11-14T12:05:00Z",
  "updatedAt": "2025-11-14T12:05:00Z"
}
```

2. **Start optimization job** - `POST /api/v1/Optimization/jobs/start`

```json
{
  "scenarioId": "b2c3d4e5-f6g7-h8i9-j0k1-l2m3n4o5p6q7",
  "maxIterations": 100,
  "convergenceTolerance": 0.001,
  "priority": "normal"
}
```

**Expected Response (201 Created):**
```json
{
  "id": "c3d4e5f6-g7h8-i9j0-k1l2-m3n4o5p6q7r8",
  "scenarioId": "b2c3d4e5-f6g7-h8i9-j0k1-l2m3n4o5p6q7",
  "userId": "64c41315-9eb5-4878-bcdb-3e943847e76f",
  "status": "Pending",
  "priority": "normal",
  "maxIterations": 100,
  "convergenceTolerance": 0.001,
  "currentIteration": 0,
  "progress": 0,
  "hangfireJobId": "hangfire-job-123456",
  "startedAt": "2025-11-14T12:10:00Z",
  "createdAt": "2025-11-14T12:10:00Z",
  "updatedAt": "2025-11-14T12:10:00Z"
}
```

3. **Get job status** - `GET /api/v1/Optimization/jobs/{id}`

**Expected Response (200 OK) - Running:**
```json
{
  "id": "c3d4e5f6-g7h8-i9j0-k1l2-m3n4o5p6q7r8",
  "status": "Running",
  "currentIteration": 45,
  "progress": 45,
  "estimatedTimeRemaining": "00:02:30",
  ...
}
```

**Expected Response (200 OK) - Completed:**
```json
{
  "id": "c3d4e5f6-g7h8-i9j0-k1l2-m3n4o5p6q7r8",
  "status": "Completed",
  "currentIteration": 100,
  "progress": 100,
  "result": {
    "objectiveValue": 0.92,
    "convergenceReached": true,
    "optimalParameters": {
      "checkerHeight": 12.8,
      "numberOfLayers": 32,
      "materialId": "refractory-123"
    },
    "metrics": {
      "fuelConsumptionReduction": 15.3,
      "co2EmissionReduction": 18.2,
      "thermalEfficiency": 0.88
    }
  },
  "completedAt": "2025-11-14T12:15:00Z",
  ...
}
```

4. **Cancel running job** - `POST /api/v1/Optimization/jobs/{id}/cancel`

**Expected Response (200 OK):**
```json
{
  "message": "Optimization job cancelled successfully"
}
```

---

### Scenario 4: User Management (Admin Only) ✅

**Objective:** Test admin user management capabilities.

**Prerequisites:**
- Admin account with role `ADMIN`
- Login as admin to get JWT token

**Steps:**

1. **Create admin user (first time)** - Use register endpoint, then manually update role in database:

```sql
UPDATE users SET role = 'ADMIN' WHERE username = 'admin';
```

Or use existing admin account:
```json
{
  "username": "admin",
  "password": "admin"
}
```

2. **Get all users (paginated)** - `GET /api/v1/Users?page=1&pageSize=20`

**Expected Response (200 OK):**
```json
{
  "items": [
    {
      "id": "64c41315-9eb5-4878-bcdb-3e943847e76f",
      "username": "testuser",
      "email": "testuser@example.com",
      "fullName": "Test User",
      "role": "ENGINEER",
      "isActive": true,
      "isVerified": false,
      "createdAt": "2025-11-14T10:00:00Z"
    },
    ...
  ],
  "totalCount": 5,
  "page": 1,
  "pageSize": 20,
  "totalPages": 1,
  "hasPreviousPage": false,
  "hasNextPage": false
}
```

3. **Get user by ID** - `GET /api/v1/Users/{id}`

4. **Create new user (admin)** - `POST /api/v1/Users`

```json
{
  "username": "engineer1",
  "email": "engineer1@example.com",
  "password": "EngineerPass123!",
  "fullName": "Engineer One",
  "role": "ENGINEER"
}
```

5. **Update user role** - `PUT /api/v1/Users/{id}/role`

```json
{
  "role": "ADMIN"
}
```

**Expected Response (200 OK):**
```json
{
  "message": "User role updated successfully"
}
```

6. **Verify user email** - `POST /api/v1/Users/{id}/verify`

**Expected Response (200 OK):**
```json
{
  "message": "Email verified successfully"
}
```

7. **Deactivate user** - `POST /api/v1/Users/{id}/deactivate`

8. **Activate user** - `POST /api/v1/Users/{id}/activate`

9. **Get user statistics** - `GET /api/v1/Users/statistics`

**Expected Response (200 OK):**
```json
{
  "totalUsers": 10,
  "activeUsers": 8,
  "verifiedUsers": 6,
  "usersByRole": {
    "ADMIN": 2,
    "ENGINEER": 6,
    "VIEWER": 2
  },
  "recentRegistrations": 3
}
```

---

## Endpoint Reference

### AuthController (`/api/v1/Auth`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/register` | No | Register new user |
| POST | `/login` | No | User login |
| POST | `/refresh` | No | Refresh access token |
| POST | `/change-password` | Yes | Change current user password |
| POST | `/request-password-reset` | No | Request password reset email |
| POST | `/reset-password` | No | Reset password with token |
| GET | `/me` | Yes | Get current user info |

### UsersController (`/api/v1/Users`)

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| GET | `/` | Yes | ADMIN | Get paginated users |
| GET | `/{id}` | Yes | ADMIN | Get user by ID |
| GET | `/username/{username}` | Yes | ADMIN | Get user by username |
| POST | `/` | Yes | ADMIN | Create new user |
| PUT | `/{id}` | Yes | ADMIN | Update user |
| DELETE | `/{id}` | Yes | ADMIN | Delete user (soft) |
| POST | `/{id}/activate` | Yes | ADMIN | Activate user |
| POST | `/{id}/deactivate` | Yes | ADMIN | Deactivate user |
| POST | `/{id}/verify` | Yes | ADMIN | Verify user email |
| PUT | `/{id}/role` | Yes | ADMIN | Update user role |
| GET | `/statistics` | Yes | ADMIN | Get user statistics |

### RegeneratorsController (`/api/v1/Regenerators`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | Yes | Get user's configurations (paginated) |
| GET | `/{id}` | Yes | Get configuration by ID |
| POST | `/` | Yes | Create new configuration |
| PUT | `/{id}` | Yes | Update configuration |
| DELETE | `/{id}` | Yes | Delete configuration |
| PUT | `/{id}/wizard-step` | Yes | Update wizard step |
| POST | `/{id}/validate` | Yes | Validate configuration |
| POST | `/{id}/complete` | Yes | Mark configuration as complete |
| POST | `/{id}/duplicate` | Yes | Duplicate configuration |
| GET | `/statistics` | Yes | Get user's config statistics |

### OptimizationController (`/api/v1/Optimization`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/scenarios` | Yes | Get user's scenarios (paginated) |
| GET | `/scenarios/{id}` | Yes | Get scenario by ID |
| POST | `/scenarios` | Yes | Create new scenario |
| POST | `/jobs/start` | Yes | Start optimization job |
| GET | `/jobs/{id}` | Yes | Get job by ID |
| GET | `/jobs` | Yes | Get user's jobs (paginated) |
| POST | `/jobs/{id}/cancel` | Yes | Cancel running job |
| GET | `/jobs/{id}/progress` | Yes | Get job progress |
| DELETE | `/jobs/{id}` | Yes | Delete job |
| GET | `/jobs/{id}/result` | Yes | Get job result |

### MaterialsController (`/api/v1/Materials`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | Yes | Get all materials (paginated) |
| GET | `/{id}` | Yes | Get material by ID |
| POST | `/search` | Yes | Search materials by criteria |

### ReportsController (`/api/v1/Reports`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/generate` | Yes | Generate report |
| GET | `/{id}` | Yes | Get report by ID |
| GET | `/{id}/download` | Yes | Download report file |
| GET | `/` | Yes | Get user's reports (paginated) |
| DELETE | `/{id}` | Yes | Delete report |

---

## Error Handling Tests

### Test 1: 400 Bad Request (Validation Error)

**Scenario:** Register user with invalid email format

**Request:** `POST /api/v1/Auth/register`
```json
{
  "username": "testuser",
  "email": "invalid-email",
  "password": "weak",
  "fullName": "Test"
}
```

**Expected Response (400):**
```json
{
  "type": "https://tools.ietf.org/html/rfc7231#section-6.5.1",
  "title": "One or more validation errors occurred.",
  "status": 400,
  "errors": {
    "Email": ["Email must be a valid email address"],
    "Password": ["Password must be at least 8 characters long"]
  }
}
```

---

### Test 2: 401 Unauthorized

**Scenario:** Access protected endpoint without token

**Request:** `GET /api/v1/Users` (No Authorization header)

**Expected Response (401):**
```json
{
  "message": "Unauthorized"
}
```

---

### Test 3: 403 Forbidden (Insufficient Permissions)

**Scenario:** Non-admin user tries to access admin endpoint

**Request:** `GET /api/v1/Users` (Authenticated as ENGINEER)

**Expected Response (403):**
```json
{
  "message": "Forbidden"
}
```

---

### Test 4: 404 Not Found

**Scenario:** Get non-existent configuration

**Request:** `GET /api/v1/Regenerators/00000000-0000-0000-0000-000000000000`

**Expected Response (404):**
```json
{
  "message": "Configuration not found or access denied"
}
```

---

### Test 5: 422 Unprocessable Entity (Business Logic Error)

**Scenario:** Start optimization for configuration in DRAFT status

**Request:** `POST /api/v1/Optimization/scenarios`
```json
{
  "configurationId": "draft-config-id",
  "name": "Test Optimization",
  "objectiveType": "fuel_efficiency"
}
```

**Expected Response (422):**
```json
{
  "message": "Configuration must be validated before creating optimization scenario",
  "errorCode": "INVALID_CONFIGURATION_STATUS"
}
```

---

### Test 6: 500 Internal Server Error

**Scenario:** Database connection failure

**Setup:** Stop MySQL server

**Request:** `GET /api/v1/Regenerators`

**Expected Response (500):**
```json
{
  "type": "https://tools.ietf.org/html/rfc7231#section-6.6.1",
  "title": "An error occurred while processing your request.",
  "status": 500,
  "detail": "An error occurred while retrieving configurations"
}
```

**Note:** Error details are sanitized in production (no stack traces exposed).

---

## Troubleshooting

### Issue 1: API Won't Start - Database Connection Failed

**Symptom:**
```
⚠ Warning: Could not connect to database
  API will start but database operations will fail
```

**Solutions:**

1. **Check MySQL is running:**
```bash
# Linux/Mac
systemctl status mysql
# or
docker ps | grep mysql

# Windows
net start MySQL80
```

2. **Verify connection string in `appsettings.json`:**
```json
"ConnectionStrings": {
  "DefaultConnection": "Server=localhost;Port=3306;Database=fro_db;User=fro_user;Password=fro_password;"
}
```

3. **Test connection manually:**
```bash
mysql -h localhost -P 3306 -u fro_user -pfro_password fro_db
```

4. **Create database if missing:**
```sql
CREATE DATABASE fro_db;
CREATE USER 'fro_user'@'localhost' IDENTIFIED BY 'fro_password';
GRANT ALL PRIVILEGES ON fro_db.* TO 'fro_user'@'localhost';
FLUSH PRIVILEGES;
```

---

### Issue 2: 401 Unauthorized After Login

**Symptom:** Login succeeds, but all subsequent requests return 401.

**Solutions:**

1. **Check JWT token format in Authorization header:**
   - Must be: `Bearer <token>`
   - Not: `<token>` (missing "Bearer" prefix)

2. **Verify token hasn't expired:**
   - Default expiration: 24 hours (1440 minutes)
   - Check `expiresIn` field in login response

3. **Check JWT secret in `appsettings.json`:**
```json
"JwtSettings": {
  "Secret": "your-super-secret-jwt-key-minimum-32-characters-long-change-in-production"
}
```
   - Must be at least 32 characters
   - Must match between token generation and validation

4. **Refresh token if expired:**
```bash
POST /api/v1/Auth/refresh
{
  "refreshToken": "<your-refresh-token>"
}
```

---

### Issue 3: Swagger Shows "Failed to fetch"

**Symptom:** Swagger UI loads but shows "Failed to fetch" for all operations.

**Solutions:**

1. **Check CORS configuration:**
```json
"Cors": {
  "AllowedOrigins": [
    "http://localhost:3000",
    "http://localhost:5000"
  ]
}
```

2. **Verify API is running on correct port:**
```bash
netstat -an | grep 5000
# or
lsof -i :5000
```

3. **Clear browser cache and reload:**
```
Ctrl+Shift+R (Windows/Linux)
Cmd+Shift+R (Mac)
```

---

### Issue 4: Hangfire Dashboard Not Available

**Symptom:** `/hangfire` returns 404.

**Solutions:**

1. **Check Redis connection:**
```bash
redis-cli ping
# Expected: PONG
```

2. **Check startup logs:**
```
✓ Hangfire Dashboard available at /hangfire
```
   - If missing, Redis is not connected

3. **Start Redis if not running:**
```bash
# Docker
docker run -d --name redis-fro -p 6379:6379 redis:alpine

# Linux
systemctl start redis

# Mac
brew services start redis
```

4. **Verify Redis connection string:**
```json
"ConnectionStrings": {
  "Redis": "localhost:6379,abortConnect=false"
}
```

---

### Issue 5: EF Core Migrations Not Applied

**Symptom:** Tables don't exist in database.

**Solutions:**

1. **Check if migrations exist:**
```bash
cd backend-dotnet/Fro.Infrastructure
ls Migrations/
```

2. **If no migrations exist, create initial migration:**
```bash
cd backend-dotnet
dotnet ef migrations add InitialCreate --project Fro.Infrastructure --startup-project Fro.Api
```

3. **Apply migrations:**
```bash
dotnet ef database update --project Fro.Infrastructure --startup-project Fro.Api
```

4. **Auto-apply on startup (Development only):**
   - Program.cs already includes auto-migration code
   - Check startup logs:
```
✓ Applying 1 pending migration(s)...
✓ Migrations applied successfully
```

---

### Issue 6: FluentValidation Errors Not Showing

**Symptom:** Invalid requests return 400 but no detailed error messages.

**Solutions:**

1. **Check FluentValidation registration in Application layer:**
```csharp
// Fro.Application/ApplicationServiceExtensions.cs
services.AddValidatorsFromAssembly(Assembly.GetExecutingAssembly());
```

2. **Verify validator is implemented for DTO:**
```bash
cd backend-dotnet/Fro.Application/Validators
ls -la
```

3. **Check service calls validator:**
```csharp
await _validator.ValidateAndThrowAsync(request);
```

---

## Summary Checklist

Before testing, ensure:

- [ ] .NET SDK 8.0 installed (`dotnet --version`)
- [ ] MySQL 8.0 running on localhost:3306
- [ ] Redis running on localhost:6379 (optional)
- [ ] Database `fro_db` created with user `fro_user`
- [ ] Dependencies restored (`dotnet restore`)
- [ ] Project builds successfully (`dotnet build`)
- [ ] API starts without errors (`dotnet run`)
- [ ] Swagger accessible at http://localhost:5000/api/docs
- [ ] Health check responds at http://localhost:5000/health

**Happy Testing!** 🚀

---

## Next Steps

After completing manual testing:

1. **Document any bugs found** - Create GitHub issues
2. **Test SLSQP optimizer integration** - Once Python microservice is ready
3. **Write automated tests** - xUnit, Moq, FluentAssertions
4. **Performance testing** - Load test with Apache Bench or k6
5. **Security testing** - JWT token validation, RBAC, SQL injection prevention
6. **Deploy to staging** - Docker Compose configuration
7. **Frontend integration** - Update Next.js API client for .NET endpoints

---

**Document Version:** 1.0
**Last Updated:** 2025-11-14
**Status:** Phase 3 Complete - Ready for Manual Testing
