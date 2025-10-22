#!/bin/bash
# FRO Production Deployment Script
# Usage: ./deploy.sh [command]
# Commands: build, start, stop, restart, logs, status, init

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if docker compose is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi

    log_info "Docker and Docker Compose are available"
}

# Build images
build() {
    log_info "Building production images..."
    docker compose build --no-cache
    log_info "Build complete"
}

# Start services
start() {
    log_info "Starting production services..."
    docker compose --profile production up -d

    log_info "Waiting for services to start..."
    sleep 10

    status
}

# Stop services
stop() {
    log_info "Stopping all services..."
    docker compose down
    log_info "Services stopped"
}

# Restart services
restart() {
    stop
    start
}

# Show logs
logs() {
    SERVICE=${1:-}
    if [ -z "$SERVICE" ]; then
        docker compose logs -f
    else
        docker compose logs -f "$SERVICE"
    fi
}

# Show status
status() {
    log_info "Service status:"
    docker compose ps

    echo ""
    log_info "Health checks:"

    # Check backend
    if curl -s http://localhost:8000/health > /dev/null; then
        log_info "✅ Backend is healthy"
    else
        log_error "❌ Backend is not responding"
    fi

    # Check frontend via nginx
    if curl -s -I http://localhost/ | grep -q "200\|301\|302"; then
        log_info "✅ Frontend is accessible"
    else
        log_error "❌ Frontend is not accessible"
    fi

    # Check Redis
    if docker compose exec -T redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
        log_info "✅ Redis is running"
    else
        log_error "❌ Redis is not responding"
    fi

    # Check MySQL
    if docker compose exec -T mysql mysqladmin ping -h localhost -u root -pfro_password 2>/dev/null | grep -q "alive"; then
        log_info "✅ MySQL is running"
    else
        log_error "❌ MySQL is not responding"
    fi
}

# Initialize database and create admin user
init() {
    log_info "Initializing database..."

    log_info "Waiting for MySQL to be ready..."
    sleep 30

    log_info "Applying database migrations..."
    docker compose exec backend alembic upgrade head

    log_info "Initializing materials database..."
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

    log_info "Creating admin user..."
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
            password_hash=get_password_hash('admin'),
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        db.add(admin_user)
        await db.commit()
        print('Admin user created successfully (username: admin, password: admin)')

asyncio.run(create_admin())
"

    log_info "Initialization complete!"
    log_warn "⚠️  Default admin password is 'admin' - CHANGE IT IMMEDIATELY"
}

# Backup database
backup() {
    BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
    log_info "Creating database backup: $BACKUP_FILE"
    docker compose exec -T mysql mysqldump -u fro_user -pfro_password fro_db > "$BACKUP_FILE"
    log_info "Backup saved to $BACKUP_FILE"
}

# Full deployment
deploy() {
    log_info "Starting full deployment..."

    check_docker
    build
    start
    init

    echo ""
    log_info "========================================="
    log_info "Deployment complete! 🚀"
    log_info "========================================="
    log_info "Frontend: http://$(hostname -I | awk '{print $1}')/"
    log_info "API Docs: http://$(hostname -I | awk '{print $1}')/api/v1/docs"
    log_info "Login: admin / admin"
    log_warn "⚠️  CHANGE DEFAULT PASSWORD IMMEDIATELY"
    log_info "========================================="
}

# Show help
help() {
    echo "FRO Production Deployment Script"
    echo ""
    echo "Usage: ./deploy.sh [command]"
    echo ""
    echo "Commands:"
    echo "  deploy    - Full deployment (build + start + init)"
    echo "  build     - Build Docker images"
    echo "  start     - Start all services"
    echo "  stop      - Stop all services"
    echo "  restart   - Restart all services"
    echo "  status    - Show service status and health"
    echo "  logs      - Show logs (optional: specify service name)"
    echo "  init      - Initialize database and create admin user"
    echo "  backup    - Create database backup"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./deploy.sh deploy          # Full deployment"
    echo "  ./deploy.sh logs backend    # Show backend logs"
    echo "  ./deploy.sh backup          # Backup database"
}

# Main script
COMMAND=${1:-help}

case "$COMMAND" in
    deploy)
        deploy
        ;;
    build)
        check_docker
        build
        ;;
    start)
        check_docker
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs "$2"
        ;;
    init)
        init
        ;;
    backup)
        backup
        ;;
    help|--help|-h)
        help
        ;;
    *)
        log_error "Unknown command: $COMMAND"
        echo ""
        help
        exit 1
        ;;
esac
