#!/bin/bash

# ============================================================================
# Forglass Regenerator Optimizer - .NET API Testing Examples
# ============================================================================
# This script contains curl commands for testing all API endpoints
# Usage: Copy individual commands or run sections
# Base URL: http://localhost:5000
# ============================================================================

BASE_URL="http://localhost:5000/api/v1"
CONTENT_TYPE="Content-Type: application/json"

# ============================================================================
# 1. HEALTH CHECK
# ============================================================================

echo "=== Health Check ==="
curl -X GET http://localhost:5000/health | jq

# ============================================================================
# 2. AUTHENTICATION FLOW
# ============================================================================

echo -e "\n=== Register New User ==="
curl -X POST "$BASE_URL/Auth/register" \
  -H "$CONTENT_TYPE" \
  -d '{
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "SecurePassword123!",
    "fullName": "Test User"
  }' | jq

echo -e "\n=== Login ==="
LOGIN_RESPONSE=$(curl -X POST "$BASE_URL/Auth/login" \
  -H "$CONTENT_TYPE" \
  -d '{
    "username": "testuser",
    "password": "SecurePassword123!"
  }')
echo $LOGIN_RESPONSE | jq

# Extract access token
ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.accessToken')
REFRESH_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.refreshToken')
echo "Access Token: $ACCESS_TOKEN"
echo "Refresh Token: $REFRESH_TOKEN"

echo -e "\n=== Get Current User ==="
curl -X GET "$BASE_URL/Auth/me" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

echo -e "\n=== Change Password ==="
curl -X POST "$BASE_URL/Auth/change-password" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "currentPassword": "SecurePassword123!",
    "newPassword": "NewSecurePassword456!"
  }' | jq

echo -e "\n=== Refresh Token ==="
curl -X POST "$BASE_URL/Auth/refresh" \
  -H "$CONTENT_TYPE" \
  -d "{
    \"refreshToken\": \"$REFRESH_TOKEN\"
  }" | jq

# ============================================================================
# 3. REGENERATOR CONFIGURATIONS
# ============================================================================

echo -e "\n=== Create Regenerator Configuration ==="
CREATE_CONFIG_RESPONSE=$(curl -X POST "$BASE_URL/Regenerators" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
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
  }')
echo $CREATE_CONFIG_RESPONSE | jq

# Extract configuration ID
CONFIG_ID=$(echo $CREATE_CONFIG_RESPONSE | jq -r '.id')
echo "Configuration ID: $CONFIG_ID"

echo -e "\n=== Get All Configurations (Paginated) ==="
curl -X GET "$BASE_URL/Regenerators?page=1&pageSize=10" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

echo -e "\n=== Get Configuration by ID ==="
curl -X GET "$BASE_URL/Regenerators/$CONFIG_ID" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

echo -e "\n=== Update Configuration ==="
curl -X PUT "$BASE_URL/Regenerators/$CONFIG_ID" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
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
  }' | jq

echo -e "\n=== Update Wizard Step ==="
curl -X PUT "$BASE_URL/Regenerators/$CONFIG_ID/wizard-step" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "wizardStep": 3
  }' | jq

echo -e "\n=== Validate Configuration ==="
curl -X POST "$BASE_URL/Regenerators/$CONFIG_ID/validate" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

echo -e "\n=== Complete Configuration ==="
curl -X POST "$BASE_URL/Regenerators/$CONFIG_ID/complete" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

echo -e "\n=== Duplicate Configuration ==="
curl -X POST "$BASE_URL/Regenerators/$CONFIG_ID/duplicate" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "newName": "Copy of Test Config"
  }' | jq

echo -e "\n=== Get Configuration Statistics ==="
curl -X GET "$BASE_URL/Regenerators/statistics" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

# ============================================================================
# 4. OPTIMIZATION SCENARIOS & JOBS
# ============================================================================

echo -e "\n=== Create Optimization Scenario ==="
CREATE_SCENARIO_RESPONSE=$(curl -X POST "$BASE_URL/Optimization/scenarios" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{
    \"configurationId\": \"$CONFIG_ID\",
    \"name\": \"Fuel Efficiency Optimization\",
    \"description\": \"Optimize for minimum fuel consumption\",
    \"objectiveType\": \"fuel_efficiency\",
    \"constraints\": {
      \"maxPressureDrop\": 500,
      \"minThermalEfficiency\": 0.85,
      \"maxMaterialCost\": 50000
    },
    \"bounds\": {
      \"checkerHeightMin\": 10.0,
      \"checkerHeightMax\": 15.0,
      \"numberOfLayersMin\": 20,
      \"numberOfLayersMax\": 40
    }
  }")
echo $CREATE_SCENARIO_RESPONSE | jq

# Extract scenario ID
SCENARIO_ID=$(echo $CREATE_SCENARIO_RESPONSE | jq -r '.id')
echo "Scenario ID: $SCENARIO_ID"

echo -e "\n=== Get All Scenarios (Paginated) ==="
curl -X GET "$BASE_URL/Optimization/scenarios?page=1&pageSize=10" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

echo -e "\n=== Get Scenario by ID ==="
curl -X GET "$BASE_URL/Optimization/scenarios/$SCENARIO_ID" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

echo -e "\n=== Start Optimization Job ==="
START_JOB_RESPONSE=$(curl -X POST "$BASE_URL/Optimization/jobs/start" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{
    \"scenarioId\": \"$SCENARIO_ID\",
    \"maxIterations\": 100,
    \"convergenceTolerance\": 0.001,
    \"priority\": \"normal\"
  }")
echo $START_JOB_RESPONSE | jq

# Extract job ID
JOB_ID=$(echo $START_JOB_RESPONSE | jq -r '.id')
echo "Job ID: $JOB_ID"

echo -e "\n=== Get Job Status ==="
curl -X GET "$BASE_URL/Optimization/jobs/$JOB_ID" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

echo -e "\n=== Get Job Progress ==="
curl -X GET "$BASE_URL/Optimization/jobs/$JOB_ID/progress" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

echo -e "\n=== Get All Jobs (Paginated) ==="
curl -X GET "$BASE_URL/Optimization/jobs?page=1&pageSize=10" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

echo -e "\n=== Get Job Result ==="
curl -X GET "$BASE_URL/Optimization/jobs/$JOB_ID/result" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

echo -e "\n=== Cancel Job ==="
curl -X POST "$BASE_URL/Optimization/jobs/$JOB_ID/cancel" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

# ============================================================================
# 5. USER MANAGEMENT (ADMIN ONLY)
# ============================================================================

echo -e "\n=== Login as Admin ==="
ADMIN_LOGIN_RESPONSE=$(curl -X POST "$BASE_URL/Auth/login" \
  -H "$CONTENT_TYPE" \
  -d '{
    "username": "admin",
    "password": "admin"
  }')
echo $ADMIN_LOGIN_RESPONSE | jq

# Extract admin access token
ADMIN_TOKEN=$(echo $ADMIN_LOGIN_RESPONSE | jq -r '.accessToken')
echo "Admin Token: $ADMIN_TOKEN"

echo -e "\n=== Get All Users (Admin) ==="
curl -X GET "$BASE_URL/Users?page=1&pageSize=20" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

echo -e "\n=== Get User by Username (Admin) ==="
curl -X GET "$BASE_URL/Users/username/testuser" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

echo -e "\n=== Create User (Admin) ==="
CREATE_USER_RESPONSE=$(curl -X POST "$BASE_URL/Users" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "username": "engineer1",
    "email": "engineer1@example.com",
    "password": "EngineerPass123!",
    "fullName": "Engineer One",
    "role": "ENGINEER"
  }')
echo $CREATE_USER_RESPONSE | jq

# Extract user ID
USER_ID=$(echo $CREATE_USER_RESPONSE | jq -r '.id')
echo "User ID: $USER_ID"

echo -e "\n=== Get User by ID (Admin) ==="
curl -X GET "$BASE_URL/Users/$USER_ID" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

echo -e "\n=== Update User (Admin) ==="
curl -X PUT "$BASE_URL/Users/$USER_ID" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "email": "engineer1.updated@example.com",
    "fullName": "Engineer One Updated",
    "isActive": true
  }' | jq

echo -e "\n=== Update User Role (Admin) ==="
curl -X PUT "$BASE_URL/Users/$USER_ID/role" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "role": "ADMIN"
  }' | jq

echo -e "\n=== Verify User Email (Admin) ==="
curl -X POST "$BASE_URL/Users/$USER_ID/verify" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

echo -e "\n=== Deactivate User (Admin) ==="
curl -X POST "$BASE_URL/Users/$USER_ID/deactivate" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

echo -e "\n=== Activate User (Admin) ==="
curl -X POST "$BASE_URL/Users/$USER_ID/activate" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

echo -e "\n=== Get User Statistics (Admin) ==="
curl -X GET "$BASE_URL/Users/statistics" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

echo -e "\n=== Delete User (Admin) ==="
curl -X DELETE "$BASE_URL/Users/$USER_ID" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

# ============================================================================
# 6. MATERIALS (READ-ONLY)
# ============================================================================

echo -e "\n=== Get All Materials (Paginated) ==="
curl -X GET "$BASE_URL/Materials?page=1&pageSize=20" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

echo -e "\n=== Search Materials ==="
curl -X POST "$BASE_URL/Materials/search" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "minTemperature": 1400,
    "maxTemperature": 1600,
    "materialType": "refractory",
    "maxDensity": 3000
  }' | jq

# ============================================================================
# 7. REPORTS
# ============================================================================

echo -e "\n=== Generate Report ==="
GENERATE_REPORT_RESPONSE=$(curl -X POST "$BASE_URL/Reports/generate" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{
    \"configurationId\": \"$CONFIG_ID\",
    \"reportType\": \"configuration_summary\",
    \"format\": \"pdf\",
    \"includeCharts\": true,
    \"includeTechnicalData\": true
  }")
echo $GENERATE_REPORT_RESPONSE | jq

# Extract report ID
REPORT_ID=$(echo $GENERATE_REPORT_RESPONSE | jq -r '.id')
echo "Report ID: $REPORT_ID"

echo -e "\n=== Get Report Status ==="
curl -X GET "$BASE_URL/Reports/$REPORT_ID" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

echo -e "\n=== Get All Reports (Paginated) ==="
curl -X GET "$BASE_URL/Reports?page=1&pageSize=10" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

echo -e "\n=== Download Report ==="
curl -X GET "$BASE_URL/Reports/$REPORT_ID/download" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  --output "report_$REPORT_ID.pdf"

echo -e "\n=== Delete Report ==="
curl -X DELETE "$BASE_URL/Reports/$REPORT_ID" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

# ============================================================================
# 8. ERROR HANDLING TESTS
# ============================================================================

echo -e "\n=== Test 400 Bad Request (Invalid Email) ==="
curl -X POST "$BASE_URL/Auth/register" \
  -H "$CONTENT_TYPE" \
  -d '{
    "username": "baduser",
    "email": "invalid-email",
    "password": "weak",
    "fullName": "Bad"
  }' | jq

echo -e "\n=== Test 401 Unauthorized (No Token) ==="
curl -X GET "$BASE_URL/Regenerators" \
  -H "$CONTENT_TYPE" | jq

echo -e "\n=== Test 401 Unauthorized (Invalid Token) ==="
curl -X GET "$BASE_URL/Regenerators" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer invalid-token-12345" | jq

echo -e "\n=== Test 403 Forbidden (Non-admin accessing admin endpoint) ==="
curl -X GET "$BASE_URL/Users" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

echo -e "\n=== Test 404 Not Found (Non-existent resource) ==="
curl -X GET "$BASE_URL/Regenerators/00000000-0000-0000-0000-000000000000" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

echo -e "\n=== Test 422 Unprocessable Entity (Business logic error) ==="
# Attempt to create scenario for draft configuration
curl -X POST "$BASE_URL/Optimization/scenarios" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "configurationId": "draft-config-id",
    "name": "Invalid Scenario",
    "objectiveType": "fuel_efficiency"
  }' | jq

# ============================================================================
# 9. CLEANUP (Optional)
# ============================================================================

echo -e "\n=== Delete Configuration (Cleanup) ==="
curl -X DELETE "$BASE_URL/Regenerators/$CONFIG_ID" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

echo -e "\n=== Delete Job (Cleanup) ==="
curl -X DELETE "$BASE_URL/Optimization/jobs/$JOB_ID" \
  -H "$CONTENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

echo -e "\n\n=== Testing Complete ==="
