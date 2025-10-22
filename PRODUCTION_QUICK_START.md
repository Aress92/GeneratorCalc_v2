# Production Quick Start Guide

## Problem Solved ✅

**Error Fixed**: `ModuleParseError: Unexpected character '@'` in Tailwind CSS

**Root Cause**: Development Dockerfile was being used in production, which runs `pnpm dev` instead of building Next.js application.

**Solution**: Created multi-stage production Dockerfile with proper Tailwind CSS compilation.

---

## Prerequisites

✅ VPS with Ubuntu/Debian
✅ Docker & Docker Compose installed
✅ 4GB+ RAM, 20GB+ disk space
✅ Port 80 open in firewall

---

## One-Command Deployment

```bash
# Upload project to VPS
scp -r RegeneratorCalc_v2/ user@51.195.40.228:/opt/fro/

# SSH into VPS
ssh user@51.195.40.228

# Navigate to project
cd /opt/fro/RegeneratorCalc_v2

# Make deploy script executable
chmod +x deploy.sh

# Run full deployment
./deploy.sh deploy
```

This will:
1. Build all Docker images
2. Start all services (frontend, backend, nginx, MySQL, Redis, Celery)
3. Apply database migrations
4. Initialize 103 materials
5. Create admin user (admin/admin)

**⏱ Estimated time: 10-15 minutes**

---

## Manual Deployment Steps

### 1. Update Configuration

Edit `docker-compose.yml`:
```bash
nano docker-compose.yml
```

Update these lines:
- Line 13: `NEXT_PUBLIC_API_URL=http://YOUR_VPS_IP/`
- Line 35: `SECRET_KEY=YOUR_GENERATED_SECRET`
- Line 39: `BACKEND_CORS_ORIGINS=http://YOUR_VPS_IP`
- Line 117: `MYSQL_ROOT_PASSWORD=STRONG_PASSWORD`
- Line 120: `MYSQL_PASSWORD=STRONG_PASSWORD`

Generate strong secret:
```bash
openssl rand -base64 32
```

### 2. Build Images

```bash
docker compose build --no-cache
```

**Expected time**: 5-7 minutes

### 3. Start Services

```bash
docker compose --profile production up -d
```

### 4. Verify Services Running

```bash
docker compose ps
```

Expected output:
```
NAME                          STATUS    PORTS
regcalc-nginx                 Up        0.0.0.0:80->80/tcp
regeneratorcalc_v2-frontend   Up        3000/tcp
regeneratorcalc_v2-backend    Up        8000/tcp
regeneratorcalc_v2-celery     Up
regeneratorcalc_v2-mysql      Up        3306/tcp
regeneratorcalc_v2-redis      Up        6379/tcp
```

### 5. Initialize Database

Wait for MySQL to start (60 seconds):
```bash
sleep 60
```

Apply migrations:
```bash
docker compose exec backend alembic upgrade head
```

### 6. Initialize Materials Database

```bash
docker compose exec backend python -c "
from app.services.materials_service import MaterialsService
from app.core.database import AsyncSessionLocal
import asyncio

async def init():
    async with AsyncSessionLocal() as db:
        service = MaterialsService(db)
        count = await service.initialize_standard_materials()
        print(f'✅ Initialized {count} materials')

asyncio.run(init())
"
```

### 7. Create Admin User

```bash
docker compose exec backend python -c "
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from sqlalchemy import select
import asyncio

async def create_admin():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.username == 'admin'))
        if result.scalar():
            print('ℹ️  Admin user already exists')
            return
        admin_user = User(
            username='admin',
            email='admin@forglass.com',
            full_name='System Administrator',
            password_hash=get_password_hash('admin'),
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        db.add(admin_user)
        await db.commit()
        print('✅ Admin user created')

asyncio.run(create_admin())
"
```

---

## Verification

### Check Backend Health
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","service":"fro-api"}
```

### Check Frontend via Nginx
```bash
curl -I http://localhost/
# Expected: HTTP/1.1 200 OK
```

### Check API via Nginx
```bash
curl http://localhost/api/v1/health
# Expected: {"status":"healthy","service":"fro-api"}
```

### Access from Browser
- Frontend: `http://YOUR_VPS_IP/`
- API Docs: `http://YOUR_VPS_IP/api/v1/docs`
- Login: `admin` / `admin`

---

## Common Issues & Solutions

### Issue: Tailwind CSS not loading (white page)

**Cause**: Frontend not built properly

**Solution**:
```bash
docker compose stop frontend
docker compose build --no-cache frontend
docker compose up -d frontend
```

### Issue: 502 Bad Gateway

**Cause**: Backend not running or not ready

**Solution**:
```bash
# Check logs
docker compose logs backend --tail 50

# Restart backend
docker compose restart backend

# Wait 30 seconds
sleep 30
```

### Issue: Cannot connect to database

**Cause**: MySQL not fully initialized

**Solution**:
```bash
# Wait for MySQL
sleep 60

# Test connection
docker compose exec mysql mysqladmin ping -h localhost -u root -p

# Check logs
docker compose logs mysql --tail 50
```

### Issue: Frontend shows "Connection Refused"

**Cause**: Wrong API URL configuration

**Solution**:
```bash
# Check environment variable
docker compose exec frontend env | grep NEXT_PUBLIC_API_URL

# Should output: NEXT_PUBLIC_API_URL=http://YOUR_VPS_IP/

# If wrong, update docker-compose.yml and rebuild:
docker compose up -d --force-recreate frontend
```

---

## Useful Commands

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f nginx

# Last 100 lines
docker compose logs --tail 100 backend
```

### Restart Services
```bash
# All services
docker compose restart

# Specific service
docker compose restart backend
docker compose restart frontend
```

### Backup Database
```bash
docker compose exec mysql mysqldump -u fro_user -pSTRONG_PASSWORD fro_db > backup_$(date +%Y%m%d).sql
```

### Stop Services
```bash
docker compose down
```

### Update Application
```bash
# Pull latest code (if using git)
git pull

# Rebuild and restart
docker compose down
docker compose build
docker compose --profile production up -d

# Apply new migrations
docker compose exec backend alembic upgrade head
```

---

## Security Checklist

⚠️ **CRITICAL - Complete These After Deployment:**

- [ ] Change admin password from default `admin`
- [ ] Update `SECRET_KEY` in `docker-compose.yml`
- [ ] Update MySQL passwords in `docker-compose.yml`
- [ ] Configure firewall (allow only ports 22, 80, 443)
- [ ] Setup SSL certificate (certbot)
- [ ] Setup automatic backups
- [ ] Configure log rotation
- [ ] Enable automatic security updates

---

## Next Steps

1. **Change Default Passwords**: Login to http://YOUR_VPS_IP/ and change admin password
2. **Setup SSL**: Follow steps in `DEPLOYMENT.md` section "Setup SSL Certificate"
3. **Configure Firewall**: See `DEPLOYMENT.md` section "Configure Firewall"
4. **Enable Monitoring**: Start Prometheus/Grafana with `docker compose --profile monitoring up -d`
5. **Setup Backups**: Create cron job for daily database backups

---

## File Reference

- `DEPLOYMENT.md` - Complete deployment guide with troubleshooting
- `CLAUDE.md` - Development guide and project documentation
- `docker-compose.yml` - Production configuration
- `docker-compose.dev.yml` - Development configuration override
- `deploy.sh` - Automated deployment script
- `frontend/Dockerfile` - Production frontend build
- `frontend/Dockerfile.dev` - Development frontend build

---

## Support

For detailed troubleshooting, see `DEPLOYMENT.md`

For development setup, see `CLAUDE.md`

For architecture details, see `ARCHITECTURE.md`
