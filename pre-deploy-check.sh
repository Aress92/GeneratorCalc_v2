#!/bin/bash
# Pre-Deployment Configuration Check
# Run this before deploying to catch configuration issues

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

echo -e "${BLUE}=== FRO Pre-Deployment Configuration Check ===${NC}\n"

# Function to report issues
check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    WARNINGS=$((WARNINGS + 1))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ERRORS=$((ERRORS + 1))
}

# Check 1: Docker and Docker Compose
echo -e "${BLUE}[1] Checking Docker Installation${NC}"
if command -v docker &> /dev/null; then
    check_pass "Docker is installed: $(docker --version | cut -d' ' -f3)"
else
    check_fail "Docker is not installed"
fi

if docker compose version &> /dev/null; then
    check_pass "Docker Compose is installed: $(docker compose version --short)"
else
    check_fail "Docker Compose is not installed"
fi
echo ""

# Check 2: Required files exist
echo -e "${BLUE}[2] Checking Required Files${NC}"
REQUIRED_FILES=(
    "docker-compose.yml"
    "frontend/Dockerfile"
    "frontend/Dockerfile.dev"
    "backend/Dockerfile.simple"
    "infrastructure/nginx/nginx.conf"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        check_pass "Found: $file"
    else
        check_fail "Missing: $file"
    fi
done
echo ""

# Check 3: Configuration values in docker-compose.yml
echo -e "${BLUE}[3] Checking Configuration Values${NC}"

# Check SECRET_KEY
if grep -q "SECRET_KEY=ZMIEN_TO_NA_MOCNY_SEKRET" docker-compose.yml; then
    check_warn "SECRET_KEY is still default - MUST change for production"
else
    check_pass "SECRET_KEY has been changed"
fi

# Check MySQL passwords
if grep -q "MYSQL_ROOT_PASSWORD=root_password" docker-compose.yml; then
    check_warn "MySQL root password is default - SHOULD change for production"
else
    check_pass "MySQL root password has been changed"
fi

if grep -q "MYSQL_PASSWORD=fro_password" docker-compose.yml; then
    check_warn "MySQL user password is default - SHOULD change for production"
else
    check_pass "MySQL user password has been changed"
fi

# Check API URL
if grep -q "NEXT_PUBLIC_API_URL" docker-compose.yml; then
    API_URL=$(grep "NEXT_PUBLIC_API_URL" docker-compose.yml | head -n1 | cut -d'=' -f2)
    if [[ "$API_URL" == *"localhost"* ]]; then
        check_warn "API URL contains 'localhost' - update to production IP/domain"
    elif [[ "$API_URL" == *"51.195.40.228"* ]]; then
        check_warn "API URL is set to example IP (51.195.40.228) - update if needed"
    else
        check_pass "API URL is configured: $API_URL"
    fi
else
    check_fail "NEXT_PUBLIC_API_URL not found in docker-compose.yml"
fi

# Check CORS origins
if grep -q "BACKEND_CORS_ORIGINS" docker-compose.yml; then
    CORS=$(grep "BACKEND_CORS_ORIGINS" docker-compose.yml | head -n1 | cut -d'=' -f2)
    if [[ "$CORS" == *"localhost"* ]]; then
        check_warn "CORS contains 'localhost' - update to production IP/domain"
    else
        check_pass "CORS origins configured: $CORS"
    fi
fi
echo ""

# Check 4: Next.js configuration
echo -e "${BLUE}[4] Checking Next.js Configuration${NC}"
if grep -q "output: 'standalone'" frontend/next.config.js; then
    check_pass "Next.js standalone output is configured"
else
    check_fail "Next.js standalone output NOT configured - build will fail"
fi

if [ -f "frontend/postcss.config.js" ]; then
    check_pass "PostCSS config exists"
else
    check_warn "PostCSS config not found"
fi

if [ -f "frontend/tailwind.config.js" ] || [ -f "frontend/tailwind.config.ts" ]; then
    check_pass "Tailwind config exists"
else
    check_fail "Tailwind config not found"
fi
echo ""

# Check 5: Dockerfile configuration
echo -e "${BLUE}[5] Checking Dockerfile Configuration${NC}"
if grep -q "dockerfile: Dockerfile" docker-compose.yml; then
    check_pass "Production Dockerfile is configured in docker-compose.yml"
elif grep -q "dockerfile: Dockerfile.dev" docker-compose.yml; then
    check_fail "Development Dockerfile in docker-compose.yml - WILL CAUSE TAILWIND ERROR"
else
    check_warn "No dockerfile specified - will use default 'Dockerfile'"
fi

if grep -q "pnpm build" frontend/Dockerfile; then
    check_pass "Frontend Dockerfile includes build step"
else
    check_warn "Frontend Dockerfile may not include build step"
fi
echo ""

# Check 6: Port configuration
echo -e "${BLUE}[6] Checking Port Configuration${NC}"

# Check if ports 80, 3000, 8000 are in use
for port in 80 3000 8000; do
    if command -v netstat &> /dev/null; then
        if netstat -tuln 2>/dev/null | grep -q ":$port "; then
            check_warn "Port $port is already in use - may cause conflicts"
        else
            check_pass "Port $port is available"
        fi
    elif command -v lsof &> /dev/null; then
        if lsof -i ":$port" &> /dev/null; then
            check_warn "Port $port is already in use - may cause conflicts"
        else
            check_pass "Port $port is available"
        fi
    else
        check_warn "Cannot check port $port (netstat/lsof not available)"
    fi
done
echo ""

# Check 7: Volume mounts
echo -e "${BLUE}[7] Checking Volume Configuration${NC}"
if grep -A 10 "frontend:" docker-compose.yml | grep -q "volumes:" && \
   grep -A 10 "frontend:" docker-compose.yml | grep -q "./frontend:/app"; then
    check_warn "Frontend has source code volume mounts - recommended only for development"
else
    check_pass "Frontend uses standalone build (no source volume mounts)"
fi
echo ""

# Check 8: Security
echo -e "${BLUE}[8] Security Checklist${NC}"
if [ -f ".env" ]; then
    check_warn ".env file found - ensure it's in .gitignore"
else
    check_pass "No .env file in repository (good for security)"
fi

if [ -f ".env.production.example" ]; then
    check_pass "Production .env template exists"
else
    check_warn "No .env.production.example template"
fi

if grep -q "admin:admin" docker-compose.yml 2>/dev/null; then
    check_warn "Default admin:admin credentials found - change after first login"
fi
echo ""

# Check 9: Nginx configuration
echo -e "${BLUE}[9] Checking Nginx Configuration${NC}"
if grep -q "proxy_pass http://frontend:3000" infrastructure/nginx/nginx.conf; then
    check_pass "Nginx configured to proxy frontend"
else
    check_fail "Nginx frontend proxy not configured"
fi

if grep -q "proxy_pass http://backend:8000" infrastructure/nginx/nginx.conf; then
    check_pass "Nginx configured to proxy backend"
else
    check_fail "Nginx backend proxy not configured"
fi

if grep -q "client_max_body_size" infrastructure/nginx/nginx.conf; then
    check_pass "Nginx max body size configured"
fi
echo ""

# Summary
echo -e "${BLUE}=== Summary ===${NC}"
echo -e "Errors:   ${RED}$ERRORS${NC}"
echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"
echo ""

if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}✗ Pre-deployment check FAILED${NC}"
    echo -e "${RED}Fix errors before deploying to production${NC}"
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠ Pre-deployment check passed with warnings${NC}"
    echo -e "${YELLOW}Review warnings before deploying to production${NC}"
    exit 0
else
    echo -e "${GREEN}✓ Pre-deployment check PASSED${NC}"
    echo -e "${GREEN}Configuration looks good for production deployment${NC}"
    exit 0
fi
