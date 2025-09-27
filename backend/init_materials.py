#!/usr/bin/env python3
"""
Initialize materials database script.
"""

import asyncio
from app.services.materials_service import MaterialsService
from app.core.database import AsyncSessionLocal

async def init_materials():
    """Initialize standard materials."""
    async with AsyncSessionLocal() as db:
        service = MaterialsService(db)
        count = await service.initialize_standard_materials()
        stats = await service.get_material_statistics()
        print(f'Initialized {count} new materials')
        print(f'Total materials: {stats["total_materials"]} (Target: 100+)')
        print(f'By type: {stats["by_type"]}')

if __name__ == "__main__":
    asyncio.run(init_materials())