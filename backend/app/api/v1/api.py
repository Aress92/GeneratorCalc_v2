"""
API v1 router configuration.

Główny router dla API v1 łączący wszystkie endpointy.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, scenarios, materials, optimization, import_data, units, reports, regenerators

api_router = APIRouter()

# Authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# User management routes
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Core business logic routes
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["scenarios"])
api_router.include_router(materials.router, prefix="/materials", tags=["materials"])
api_router.include_router(regenerators.router, prefix="/regenerators", tags=["regenerators"])
api_router.include_router(optimization.router, prefix="/optimize", tags=["optimization"])

# Data import routes
api_router.include_router(import_data.router, prefix="/import", tags=["import"])

# Unit conversion routes
api_router.include_router(units.router, prefix="/units", tags=["units"])

# Reporting routes
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])