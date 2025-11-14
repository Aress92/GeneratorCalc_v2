# Quick Start - .NET API Testing

**5-Minute Guide to Testing the .NET Backend**

---

## Prerequisites Checklist

- [ ] .NET SDK 8.0 installed - Run: `dotnet --version` (should show 8.0.x)
- [ ] MySQL 8.0 running on `localhost:3306`
- [ ] (Optional) Redis running on `localhost:6379`

---

## Step 1: Start MySQL (If Not Running)

**Docker:**
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

**Or native MySQL:**
```bash
# Check status
systemctl status mysql    # Linux
brew services list         # Mac
net start MySQL80          # Windows

# Create database
mysql -u root -p
> CREATE DATABASE fro_db;
> CREATE USER 'fro_user'@'localhost' IDENTIFIED BY 'fro_password';
> GRANT ALL PRIVILEGES ON fro_db.* TO 'fro_user'@'localhost';
> FLUSH PRIVILEGES;
> exit;
```

---

## Step 2: Start the API

```bash
cd backend-dotnet/Fro.Api
dotnet run
```

**Expected output:**
```
info: Microsoft.Hosting.Lifetime[14]
      Now listening on: http://localhost:5000
✓ Connected to database
✓ Database is up to date (no pending migrations)
```

**Open Swagger:** http://localhost:5000/api/docs

---

## Step 3: Test Authentication (Swagger UI)

### 3.1 Register User

1. Expand `POST /api/v1/Auth/register`
2. Click **"Try it out"**
3. Enter:
```json
{
  "username": "testuser",
  "email": "testuser@example.com",
  "password": "SecurePassword123!",
  "fullName": "Test User"
}
```
4. Click **"Execute"**
5. Verify **201 Created** response

### 3.2 Login

1. Expand `POST /api/v1/Auth/login`
2. Click **"Try it out"**
3. Enter:
```json
{
  "username": "testuser",
  "password": "SecurePassword123!"
}
```
4. Click **"Execute"**
5. **Copy the `accessToken`** from response

### 3.3 Authorize

1. Click **green "Authorize" button** at top-right
2. Paste: `Bearer <your-access-token>`
3. Click **"Authorize"** then **"Close"**

✅ **You're now authenticated!** All requests will include the JWT token.

---

## Step 4: Test CRUD Operations

### 4.1 Create Regenerator Configuration

1. Expand `POST /api/v1/Regenerators`
2. Click **"Try it out"**
3. Enter:
```json
{
  "name": "My First Config",
  "description": "Testing the API",
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
4. Click **"Execute"**
5. **Copy the `id`** from response (e.g., `a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6`)

### 4.2 Get All Configurations

1. Expand `GET /api/v1/Regenerators`
2. Click **"Try it out"** → **"Execute"**
3. Verify your config appears in `items` array

### 4.3 Update Configuration

1. Expand `PUT /api/v1/Regenerators/{id}`
2. Click **"Try it out"**
3. Paste the config ID from step 4.1
4. Modify the name or description
5. Click **"Execute"**
6. Verify **200 OK** response

---

## Step 5: Test Error Handling

### 5.1 Test 401 Unauthorized

1. Click **green "Authorize" button**
2. Click **"Logout"** (removes token)
3. Try `GET /api/v1/Regenerators`
4. Verify **401 Unauthorized**

### 5.2 Test 404 Not Found

1. Re-authorize with token
2. Try `GET /api/v1/Regenerators/00000000-0000-0000-0000-000000000000`
3. Verify **404 Not Found** with message "Configuration not found"

### 5.3 Test 400 Bad Request (Validation)

1. Try `POST /api/v1/Auth/register` with invalid email:
```json
{
  "username": "bad",
  "email": "not-an-email",
  "password": "weak",
  "fullName": "Bad"
}
```
2. Verify **400 Bad Request** with validation errors

---

## Alternative Testing Methods

### Using curl (Terminal)

```bash
# Health check
curl http://localhost:5000/health

# Register
curl -X POST http://localhost:5000/api/v1/Auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"Secure123!","fullName":"Test"}'

# Login (save token)
TOKEN=$(curl -X POST http://localhost:5000/api/v1/Auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"Secure123!"}' | jq -r '.accessToken')

# Get configs
curl http://localhost:5000/api/v1/Regenerators \
  -H "Authorization: Bearer $TOKEN"
```

### Using Postman

1. Import `FRO_API_Postman_Collection.json` from `backend-dotnet/`
2. Set variable `base_url` to `http://localhost:5000/api/v1`
3. Run **"Register"** → **"Login"** (auto-sets `access_token`)
4. Test other endpoints

---

## Common Issues & Solutions

### Issue: "dotnet: command not found"

**Solution:** Install .NET SDK 8.0
- **Windows:** https://dotnet.microsoft.com/download/dotnet/8.0
- **Mac:** `brew install dotnet@8`
- **Linux:** Follow [Microsoft docs](https://learn.microsoft.com/en-us/dotnet/core/install/linux)

### Issue: "Could not connect to database"

**Solution:** Check MySQL connection
```bash
# Test connection
mysql -h localhost -P 3306 -u fro_user -pfro_password fro_db

# If fails, check MySQL is running
systemctl status mysql         # Linux
brew services list              # Mac
docker ps | grep mysql          # Docker
```

### Issue: "Table 'fro_db.users' doesn't exist"

**Solution:** Apply EF Core migrations
```bash
cd backend-dotnet
dotnet ef database update --project Fro.Infrastructure --startup-project Fro.Api
```

### Issue: Swagger shows "Failed to fetch"

**Solution:** Check CORS settings in `appsettings.json`
```json
"Cors": {
  "AllowedOrigins": [
    "http://localhost:3000",
    "http://localhost:5000"
  ]
}
```

### Issue: All requests return 401 after login

**Solution:** Check JWT token format
- Must be: `Bearer <token>`
- Not: `<token>` (missing "Bearer" prefix)

---

## Testing Checklist

After following this guide, you should have tested:

- [x] Health check endpoint
- [x] User registration
- [x] User login (JWT token)
- [x] Authorization in Swagger
- [x] Create regenerator configuration
- [x] Get all configurations (paginated)
- [x] Update configuration
- [x] 401 Unauthorized error
- [x] 404 Not Found error
- [x] 400 Bad Request (validation)

---

## Next Steps

1. **Test Admin Endpoints** - Login as admin, test user management
2. **Test Optimization Flow** - Create scenario, start job, check progress
3. **Read Full Guide** - See `DOTNET_API_TESTING_GUIDE.md` for all 57 endpoints
4. **Run Shell Script** - Execute `API_TESTING_EXAMPLES.sh` for automated tests
5. **Write Unit Tests** - Create xUnit tests for services and controllers

---

## Resources

- **Full Testing Guide:** `DOTNET_API_TESTING_GUIDE.md` (95 pages)
- **curl Examples:** `API_TESTING_EXAMPLES.sh` (Shell script)
- **Postman Collection:** `FRO_API_Postman_Collection.json`
- **API Documentation:** http://localhost:5000/api/docs (when running)
- **Hangfire Dashboard:** http://localhost:5000/hangfire (if Redis connected)

---

**Status:** Phase 3 Complete (80%) - API Ready for Testing
**Last Updated:** 2025-11-14
**Build Status:** ✅ Clean (0 errors, 3 warnings)

🚀 **Happy Testing!**
