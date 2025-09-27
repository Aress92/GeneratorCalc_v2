#!/usr/bin/env python3
"""
Create database tables script.
"""

import asyncio
from app.core.database import engine, Base

# Import all models to register them with Base.metadata
from app.models.user import User
from app.models.regenerator import Material, RegeneratorConfiguration
from app.models.import_job import ImportJob, ImportedRegenerator
from app.models.optimization import OptimizationScenario, OptimizationJob, OptimizationResult
from app.models.reporting import Report, ReportData, SystemMetrics

async def create_tables():
    """Create all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully")

if __name__ == "__main__":
    asyncio.run(create_tables())