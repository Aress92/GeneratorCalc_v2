# 🚀 Przewodnik Wdrożenia Produkcyjnego - FRO System

**System**: Forglass Regenerator Optimizer v1.0
**Data**: 2025-10-05
**Status**: Production Ready

---

## ⚡ Quick Start (5 minut)

```bash
# 1. Clone repository
git clone <repository-url>
cd RegeneratorCalc_v2

# 2. Configure environment
cp .env.example .env
# Edit .env with production values

# 3. Start all services
docker compose up -d

# 4. Wait for MySQL (30 seconds)
sleep 30

# 5. Run database migrations
docker compose exec backend alembic upgrade head

# 6. Initialize materials database
docker compose exec backend python -c "
from app.services.materials_service import MaterialsService
from app.core.database import AsyncSessionLocal
import asyncio
async def init():
    async with AsyncSessionLocal() as db:
        service = MaterialsService(db)
        await service.initialize_default_materials()
asyncio.run(init())
"

# 7. Create admin user
docker compose exec backend python -c "
from app.core.security import get_password_hash
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
import asyncio
async def create_admin():
    async with AsyncSessionLocal() as db:
        user = User(
            username='admin',
            email='admin@company.com',
            full_name='System Administrator',
            password_hash=get_password_hash('ChangeMeInProduction!'),
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        db.add(user)
        await db.commit()
        print('Admin user created: admin / ChangeMeInProduction!')
asyncio.run(create_admin())
"

# 8. Verify deployment
curl http://localhost:8000/health
# Expected: {"status":"healthy","timestamp":"..."}

# 9. Access applications
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api/v1/docs
# Login: admin / ChangeMeInProduction!
```

---

## 📋 Pre-Deployment Checklist

### Infrastructure Requirements

- [ ] **Docker**: Version 24.0+ installed
- [ ] **Docker Compose**: Version 2.20+ installed
- [ ] **RAM**: Minimum 8GB, recommended 16GB
- [ ] **CPU**: Minimum 4 cores
- [ ] **Disk**: Minimum 50GB free space
- [ ] **Network**: Ports 3000, 8000, 3306, 6379 available

### Configuration

- [ ] Copy `.env.example` to `.env`
- [ ] Update `DATABASE_URL` with production credentials
- [ ] Set strong `SECRET_KEY` (min 32 characters)
- [ ] Configure `REDIS_URL` if external Redis
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure `ALLOWED_ORIGINS` for CORS
- [ ] Set secure `ADMIN_EMAIL` and password

### Security

- [ ] Change default admin password
- [ ] Generate new JWT secret key
- [ ] Configure HTTPS/TLS certificates
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Configure backup strategy

---

## 🔧 Environment Variables

### Required Variables

```bash
# Application
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<generate-strong-32-char-key>

# Database
DATABASE_URL=mysql+aiomysql://user:password@mysql:3306/fro_db
MYSQL_ROOT_PASSWORD=<strong-password>
MYSQL_DATABASE=fro_db
MYSQL_USER=fro_user
MYSQL_PASSWORD=<strong-password>

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@company.com
SMTP_PASSWORD=<app-password>
```

### Optional Variables

```bash
# Logging
LOG_LEVEL=INFO
SENTRY_DSN=<your-sentry-dsn>

# Performance
WORKERS_PER_CORE=2
MAX_WORKERS=8

# File Upload
MAX_UPLOAD_SIZE=10485760  # 10MB
UPLOAD_DIR=/app/uploads

# Monitoring
PROMETHEUS_ENABLED=true
METRICS_PORT=9090
```

---

## 🐳 Docker Compose Services

### Services Overview

| Service | Port | Purpose |
|---------|------|---------|
| `frontend` | 3000 | Next.js web application |
| `backend` | 8000 | FastAPI REST API |
| `celery` | - | Background task workers |
| `celery-beat` | - | Task scheduler |
| `mysql` | 3306 | Main database |
| `redis` | 6379 | Cache + message broker |

### Health Checks

```bash
# Check all services
docker compose ps

# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000

# Check database
docker compose exec mysql mysql -u fro_user -p<password> -e "SELECT 1"

# Check redis
docker compose exec redis redis-cli ping
```

---

## 📊 Database Setup

### Initial Migration

```bash
# Run migrations
docker compose exec backend alembic upgrade head

# Check current version
docker compose exec backend alembic current

# View migration history
docker compose exec backend alembic history
```

### Seed Data

```bash
# Initialize 111 standard materials
docker compose exec backend python scripts/seed_materials.py

# Create sample scenarios (optional)
docker compose exec backend python scripts/seed_scenarios.py

# Import sample data (optional)
docker compose exec backend python scripts/import_sample_data.py
```

---

## 👥 User Management

### Create Admin User

```bash
docker compose exec backend python -c "
from app.core.security import get_password_hash
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
import asyncio

async def create_admin():
    async with AsyncSessionLocal() as db:
        user = User(
            username='admin',
            email='admin@company.com',
            full_name='Administrator',
            password_hash=get_password_hash('SecurePassword123!'),
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        db.add(user)
        await db.commit()
        print(f'Admin created: {user.username}')

asyncio.run(create_admin())
"
```

### Create Regular Users

```bash
# Via API (requires admin token)
curl -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "engineer1",
    "email": "engineer@company.com",
    "full_name": "John Engineer",
    "password": "Password123!",
    "role": "engineer"
  }'
```

---

## 🔍 Monitoring & Logging

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f celery

# Last 100 lines
docker compose logs --tail=100 backend

# With timestamps
docker compose logs -f -t backend
```

### Celery Monitoring

```bash
# Active tasks
docker compose exec celery celery -A app.celery inspect active

# Scheduled tasks
docker compose exec celery celery -A app.celery inspect scheduled

# Worker stats
docker compose exec celery celery -A app.celery inspect stats
```

### Database Monitoring

```bash
# Connection count
docker compose exec mysql mysql -u root -p<password> \
  -e "SHOW STATUS LIKE 'Threads_connected'"

# Table sizes
docker compose exec mysql mysql -u fro_user -p<password> fro_db \
  -e "SELECT table_name, ROUND((data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)' FROM information_schema.tables WHERE table_schema='fro_db'"
```

---

## 🔄 Backup & Restore

### Database Backup

```bash
# Create backup
docker compose exec mysql mysqldump -u root -p<password> fro_db > backup_$(date +%Y%m%d).sql

# Automated daily backup (add to cron)
0 2 * * * cd /path/to/project && docker compose exec mysql mysqldump -u root -p<password> fro_db | gzip > backups/fro_db_$(date +\%Y\%m\%d).sql.gz
```

### Restore Database

```bash
# From backup file
docker compose exec -T mysql mysql -u root -p<password> fro_db < backup_20251005.sql

# From gzipped backup
gunzip < backups/fro_db_20251005.sql.gz | docker compose exec -T mysql mysql -u root -p<password> fro_db
```

### File Backup

```bash
# Backup uploads directory
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz backend/uploads/

# Backup reports
tar -czf reports_backup_$(date +%Y%m%d).tar.gz backend/reports/
```

---

## 🚨 Troubleshooting

### Common Issues

#### 1. Services Won't Start

```bash
# Check logs
docker compose logs

# Restart services
docker compose restart

# Full rebuild
docker compose down
docker compose up -d --build
```

#### 2. Database Connection Errors

```bash
# Wait for MySQL to be ready
docker compose exec backend python -c "
from app.core.database import engine
import asyncio
async def test():
    async with engine.begin() as conn:
        result = await conn.execute('SELECT 1')
        print('Database OK')
asyncio.run(test())
"

# Restart backend
docker compose restart backend
```

#### 3. Celery Tasks Stuck

```bash
# Purge all tasks
docker compose exec celery celery -A app.celery purge

# Restart workers
docker compose restart celery celery-beat
```

#### 4. Frontend Not Compiling

```bash
# Clear Next.js cache
docker compose exec frontend rm -rf .next

# Restart frontend
docker compose restart frontend
```

---

## 🔐 Security Hardening

### Production Checklist

- [ ] Change all default passwords
- [ ] Generate new SECRET_KEY (32+ characters)
- [ ] Enable HTTPS (use Nginx with SSL)
- [ ] Configure rate limiting
- [ ] Set up firewall (UFW/iptables)
- [ ] Enable audit logging
- [ ] Configure backup encryption
- [ ] Set up intrusion detection
- [ ] Regular security updates

### SSL/TLS Setup (Nginx)

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📈 Performance Tuning

### Database Optimization

```sql
-- Add indexes for frequent queries
CREATE INDEX idx_materials_type ON materials(material_type);
CREATE INDEX idx_materials_category ON materials(category);
CREATE INDEX idx_jobs_status ON optimization_jobs(status);
CREATE INDEX idx_jobs_user ON optimization_jobs(user_id);
```

### Redis Configuration

```bash
# redis.conf adjustments
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
```

### Celery Workers

```bash
# Scale workers based on load
docker compose up -d --scale celery=8
```

---

## ✅ Post-Deployment Verification

### Functional Tests

```bash
# 1. Health check
curl http://localhost:8000/health

# 2. Login test
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"YourPassword"}'

# 3. Get materials
curl http://localhost:8000/api/v1/materials \
  -H "Authorization: Bearer <token>"

# 4. Create test optimization
# (Use Swagger UI at /api/v1/docs)
```

### Performance Tests

```bash
# API response time
ab -n 100 -c 10 http://localhost:8000/health

# Database query time
docker compose exec mysql mysql -u fro_user -p<password> fro_db \
  -e "SELECT SQL_NO_CACHE COUNT(*) FROM materials" \
  --verbose
```

---

## 📞 Support & Maintenance

### Regular Maintenance Tasks

**Daily**:
- Check service health
- Monitor error logs
- Verify backup completion

**Weekly**:
- Database optimization (ANALYZE tables)
- Clear old logs
- Review security alerts

**Monthly**:
- Update dependencies
- Security patches
- Performance review
- Backup testing

### Getting Help

1. **Documentation**: See `/docs` folder
2. **API Docs**: http://localhost:8000/api/v1/docs
3. **GitHub Issues**: For bug reports
4. **Email**: support@company.com

---

## 🎉 Deployment Complete!

**Your FRO system is now running in production.**

**Access Points**:
- 🌐 Frontend: http://localhost:3000
- 🔌 Backend API: http://localhost:8000/api/v1/docs
- 👤 Login: admin / (your password)

**Next Steps**:
1. Configure SSL/HTTPS
2. Set up monitoring (Prometheus/Grafana)
3. Create user accounts
4. Import production data
5. Train users

**Good luck with your deployment!** 🚀
