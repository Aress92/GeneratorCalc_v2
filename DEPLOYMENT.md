# FRO Production Deployment Guide

## Problem Fixed: Tailwind CSS Build Error

### Root Cause
The error `ModuleParseError: Unexpected character '@' (1:0)` occurred because:
1. **Wrong Dockerfile**: Used `Dockerfile.dev` which runs `pnpm dev` (development server)
2. **No Build Step**: Tailwind CSS requires `next build` to process directives like `@tailwind`
3. **NODE_ENV Conflict**: Mixed development/production environment variables

### Solution Applied
✅ Created production `Dockerfile` with multi-stage build
✅ Added `output: 'standalone'` to `next.config.js`
✅ Removed source code volume mounts from production `docker-compose.yml`
✅ Created separate `docker-compose.dev.yml` for local development

---

## Pre-Deployment Checklist

### 1. Update Environment Variables

**Backend** (`docker-compose.yml` lines 35-40):
```yaml
- SECRET_KEY=ZMIEN_TO_NA_MOCNY_SEKRET  # ⚠️ Generate strong secret (min 32 chars)
- BACKEND_CORS_ORIGINS=http://51.195.40.228  # Update to your VPS IP/domain
- ALLOWED_HOSTS=51.195.40.228,backend,nginx,localhost,127.0.0.1
```

**Frontend** (`docker-compose.yml` line 13):
```yaml
- NEXT_PUBLIC_API_URL=http://51.195.40.228/  # Update to your VPS IP/domain
```

**Database** (`docker-compose.yml` lines 117-120):
```yaml
- MYSQL_ROOT_PASSWORD=root_password  # ⚠️ Change to strong password
- MYSQL_PASSWORD=fro_password        # ⚠️ Change to strong password
```

### 2. Generate Strong Secrets

```bash
# Generate SECRET_KEY (Python)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or using OpenSSL
openssl rand -base64 32
```

### 3. Verify File Structure

```
RegeneratorCalc_v2/
├── docker-compose.yml           # ✅ Production configuration
├── docker-compose.dev.yml       # ✅ Development override
├── frontend/
│   ├── Dockerfile               # ✅ NEW: Production multi-stage build
│   ├── Dockerfile.dev           # ✅ Development hot-reload
│   └── next.config.js           # ✅ UPDATED: standalone output
├── backend/
│   └── Dockerfile.simple
└── infrastructure/
    └── nginx/
        └── nginx.conf           # ✅ Reverse proxy configuration
```

---

## Deployment Steps

### On VPS Server

#### 1. Upload Project to VPS
```bash
# From local machine (Windows)
scp -r K:\Projekty_ClaudeCode\RegeneratorCalc_v2 user@51.195.40.228:/opt/fro/

# Or use Git
ssh user@51.195.40.228
cd /opt/fro
git clone <repository_url> RegeneratorCalc_v2
cd RegeneratorCalc_v2
```

#### 2. Update Environment Variables
```bash
# Edit docker-compose.yml with production values
nano docker-compose.yml

# Update SECRET_KEY (line 35)
# Update MYSQL passwords (lines 117, 120)
# Verify NEXT_PUBLIC_API_URL matches your domain/IP
```

#### 3. Build and Start Services
```bash
# Stop any running containers
docker compose down

# Build fresh images (this may take 5-10 minutes)
docker compose build --no-cache

# Start with nginx profile for reverse proxy
docker compose --profile production up -d

# Check service status
docker compose ps
```

#### 4. Apply Database Migrations
```bash
# Wait 30-60 seconds for MySQL to initialize
sleep 60

# Apply Alembic migrations
docker compose exec backend alembic upgrade head
```

#### 5. Initialize Materials Database
```bash
docker compose exec backend python -c "
from app.services.materials_service import MaterialsService
from app.core.database import AsyncSessionLocal
import asyncio

async def init_materials():
    async with AsyncSessionLocal() as db:
        service = MaterialsService(db)
        count = await service.initialize_standard_materials()
        print(f'Initialized {count} materials')

asyncio.run(init_materials())
"
```

#### 6. Create Admin User
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
            print('Admin user already exists')
            return
        admin_user = User(
            username='admin',
            email='admin@forglass.com',
            full_name='System Administrator',
            password_hash=get_password_hash('admin'),  # ⚠️ Change default password after first login
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        db.add(admin_user)
        await db.commit()
        print('Admin user created successfully')

asyncio.run(create_admin())
"
```

#### 7. Verify Deployment
```bash
# Check all services are running
docker compose ps

# Expected output:
# NAME                          STATUS    PORTS
# regcalc-nginx                 Up        0.0.0.0:80->80/tcp
# regeneratorcalc_v2-frontend   Up        3000/tcp
# regeneratorcalc_v2-backend    Up        8000/tcp
# regeneratorcalc_v2-celery     Up
# regeneratorcalc_v2-mysql      Up        3306/tcp
# regeneratorcalc_v2-redis      Up        6379/tcp

# Test backend health
curl http://localhost:8000/health
# Expected: {"status":"healthy","service":"fro-api"}

# Test nginx routing
curl http://localhost/api/v1/health
# Expected: {"status":"healthy","service":"fro-api"}

# Check frontend (from browser or curl)
curl -I http://51.195.40.228/
# Expected: HTTP/1.1 200 OK
```

#### 8. Access Application
```
Frontend: http://51.195.40.228/
API Docs: http://51.195.40.228/api/v1/docs
Login: admin / admin (⚠️ change after first login)
```

---

## Post-Deployment Tasks

### 1. Change Default Passwords
```bash
# Access admin panel at http://51.195.40.228/
# Login with admin/admin
# Go to Settings → Change Password
```

### 2. Configure Firewall
```bash
# Allow only HTTP/HTTPS and SSH
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS (for future SSL)
sudo ufw enable

# Verify rules
sudo ufw status
```

### 3. Setup SSL Certificate (Recommended)
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate (requires domain name)
sudo certbot --nginx -d yourdomain.com

# Auto-renewal test
sudo certbot renew --dry-run
```

### 4. Configure Log Rotation
```bash
# Create logrotate config
sudo nano /etc/logrotate.d/fro

# Add configuration:
/opt/fro/RegeneratorCalc_v2/infrastructure/nginx/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}

/opt/fro/RegeneratorCalc_v2/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 root root
}
```

### 5. Setup Monitoring (Optional)
```bash
# Start Prometheus and Grafana
docker compose --profile monitoring up -d

# Access Grafana: http://51.195.40.228:3001 (add to nginx config)
# Default login: admin / admin_password (from docker-compose.yml)
```

---

## Troubleshooting

### Issue: Tailwind CSS Not Loading (White/Unstyled Page)
```bash
# Check if build completed successfully
docker compose logs frontend | grep "Compiled successfully"

# Rebuild frontend with no cache
docker compose stop frontend
docker compose build --no-cache frontend
docker compose up -d frontend
```

### Issue: 502 Bad Gateway
```bash
# Check if backend is running
docker compose ps backend

# Check backend logs
docker compose logs backend --tail 100

# Restart backend
docker compose restart backend
```

### Issue: Database Connection Failed
```bash
# Check MySQL status
docker compose ps mysql

# Verify credentials in docker-compose.yml match DATABASE_URL
# Wait for MySQL to fully initialize (60 seconds)
docker compose exec mysql mysqladmin ping -h localhost -u root -p
```

### Issue: Celery Tasks Not Running
```bash
# Check Celery worker status
docker compose logs celery --tail 50

# Check Redis connection
docker compose exec redis redis-cli ping
# Expected: PONG

# Restart Celery workers
docker compose restart celery celery-beat
```

### Issue: Frontend Shows "Connection Refused"
```bash
# Verify NEXT_PUBLIC_API_URL is correct
docker compose exec frontend env | grep NEXT_PUBLIC_API_URL

# Should match your VPS IP/domain: http://51.195.40.228/

# Rebuild if env var was changed
docker compose up -d --force-recreate frontend
```

---

## Maintenance Commands

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

### Backup Database
```bash
# Create backup
docker compose exec mysql mysqldump -u fro_user -pfro_password fro_db > backup_$(date +%Y%m%d).sql

# Restore from backup
docker compose exec -T mysql mysql -u fro_user -pfro_password fro_db < backup_20250122.sql
```

### Update Application
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker compose down
docker compose build
docker compose --profile production up -d

# Apply new migrations
docker compose exec backend alembic upgrade head
```

### Clean Up Docker Resources
```bash
# Remove old images
docker image prune -a

# Remove unused volumes
docker volume prune

# Full cleanup (⚠️ removes all unused resources)
docker system prune -a --volumes
```

---

## Performance Optimization

### 1. Enable HTTP/2 and Gzip in Nginx
Edit `infrastructure/nginx/nginx.conf`:
```nginx
http {
  gzip on;
  gzip_vary on;
  gzip_proxied any;
  gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

  # ... existing config
}
```

### 2. Configure Redis Persistence
Edit `infrastructure/redis/redis.conf`:
```
save 900 1
save 300 10
save 60 10000
appendonly yes
```

### 3. MySQL Performance Tuning
Edit `infrastructure/mysql/conf.d/custom.cnf`:
```ini
[mysqld]
innodb_buffer_pool_size = 1G
max_connections = 200
query_cache_size = 0
query_cache_type = 0
```

### 4. Resource Limits
Add to `docker-compose.yml` for each service:
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '0.5'
      memory: 512M
```

---

## Security Best Practices

✅ **Completed:**
- HttpOnly cookies for JWT tokens
- CORS configuration
- Input validation with Pydantic/Zod
- Non-root Docker containers
- Security headers in nginx

⚠️ **TODO:**
- [ ] Change all default passwords
- [ ] Setup SSL/TLS certificate
- [ ] Configure fail2ban for SSH
- [ ] Enable automatic security updates
- [ ] Regular backup schedule
- [ ] Implement rate limiting in nginx

---

## Support and Documentation

- **Project README**: `README.md`
- **Architecture**: `ARCHITECTURE.md`
- **Development Guide**: `CLAUDE.md`
- **API Documentation**: http://51.195.40.228/api/v1/docs (after deployment)

---

## Quick Reference

### Development Mode (Local)
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### Production Mode (VPS)
```bash
docker compose --profile production up -d
```

### Health Check URLs
- Frontend: http://51.195.40.228/
- Backend: http://51.195.40.228/api/v1/health
- API Docs: http://51.195.40.228/api/v1/docs
- Grafana: http://51.195.40.228:3001 (if monitoring enabled)
