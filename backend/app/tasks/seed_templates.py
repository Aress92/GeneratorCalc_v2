"""
Seed default regenerator configuration templates.

Wypełnienie bazy danych domyślnymi szablonami konfiguracji regeneratorów.
"""

import asyncio
from datetime import datetime, UTC
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.regenerator import RegeneratorConfiguration
from app.models.user import User
import structlog

logger = structlog.get_logger(__name__)


DEFAULT_TEMPLATES = [
    {
        "name": "Szablon: Regenerator koronowy - mały",
        "description": "Typowy regenerator koronowy dla małych pieców szklarskich (50-100 ton/dzień)",
        "regenerator_type": "crown",
        "geometry_config": {
            "length": 8.0,
            "width": 6.0,
            "height": 10.0,
            "checker_height": 8.5,
            "wall_thickness": 0.4,
        },
        "thermal_config": {
            "gas_temp_inlet": 1450,
            "gas_temp_outlet": 600,
            "air_temp_inlet": 200,
            "air_temp_outlet": 1200,
            "max_operating_temp": 1600,
            "target_efficiency": 85.0,
        },
        "flow_config": {
            "mass_flow_rate": 40,
            "air_flow_rate": 20000,
            "gas_flow_rate": 25000,
            "cycle_time": 1200,
            "design_pressure": 2500,
            "pressure_drop_limit": 4000,
        },
        "materials_config": {
            "checker_material": "Silica brick (96% SiO2)",
            "wall_material": "Alumina-silica brick",
            "thermal_conductivity": 2.5,
            "specific_heat": 950,
            "density": 2200,
        },
    },
    {
        "name": "Szablon: Regenerator koronowy - średni",
        "description": "Regenerator koronowy dla średnich pieców szklarskich (100-250 ton/dzień)",
        "regenerator_type": "crown",
        "geometry_config": {
            "length": 12.0,
            "width": 9.0,
            "height": 14.0,
            "checker_height": 12.0,
            "wall_thickness": 0.5,
        },
        "thermal_config": {
            "gas_temp_inlet": 1500,
            "gas_temp_outlet": 550,
            "air_temp_inlet": 200,
            "air_temp_outlet": 1250,
            "max_operating_temp": 1650,
            "target_efficiency": 87.0,
        },
        "flow_config": {
            "mass_flow_rate": 65,
            "air_flow_rate": 35000,
            "gas_flow_rate": 40000,
            "cycle_time": 1200,
            "design_pressure": 3000,
            "pressure_drop_limit": 5000,
        },
        "materials_config": {
            "checker_material": "High-alumina brick (65% Al2O3)",
            "wall_material": "Alumina brick",
            "thermal_conductivity": 3.0,
            "specific_heat": 980,
            "density": 2400,
        },
    },
    {
        "name": "Szablon: Regenerator koronowy - duży",
        "description": "Duży regenerator koronowy dla dużych pieców szklarskich (250-500 ton/dzień)",
        "regenerator_type": "crown",
        "geometry_config": {
            "length": 16.0,
            "width": 12.0,
            "height": 18.0,
            "checker_height": 15.5,
            "wall_thickness": 0.6,
        },
        "thermal_config": {
            "gas_temp_inlet": 1550,
            "gas_temp_outlet": 500,
            "air_temp_inlet": 180,
            "air_temp_outlet": 1300,
            "max_operating_temp": 1700,
            "target_efficiency": 90.0,
        },
        "flow_config": {
            "mass_flow_rate": 100,
            "air_flow_rate": 60000,
            "gas_flow_rate": 70000,
            "cycle_time": 1500,
            "design_pressure": 3500,
            "pressure_drop_limit": 6000,
        },
        "materials_config": {
            "checker_material": "Magnesia-alumina brick",
            "wall_material": "High-alumina brick",
            "thermal_conductivity": 3.5,
            "specific_heat": 1000,
            "density": 2600,
        },
    },
    {
        "name": "Szablon: Regenerator czołowy (end-port)",
        "description": "Typowy regenerator czołowy dla pieców szklarskich",
        "regenerator_type": "end_port",
        "geometry_config": {
            "length": 10.0,
            "width": 8.0,
            "height": 12.0,
            "checker_height": 10.0,
            "wall_thickness": 0.5,
        },
        "thermal_config": {
            "gas_temp_inlet": 1480,
            "gas_temp_outlet": 580,
            "air_temp_inlet": 220,
            "air_temp_outlet": 1220,
            "max_operating_temp": 1620,
            "target_efficiency": 86.0,
        },
        "flow_config": {
            "mass_flow_rate": 55,
            "air_flow_rate": 28000,
            "gas_flow_rate": 33000,
            "cycle_time": 1200,
            "design_pressure": 2800,
            "pressure_drop_limit": 4500,
        },
        "materials_config": {
            "checker_material": "Silica brick (96% SiO2)",
            "wall_material": "Alumina-silica brick",
            "thermal_conductivity": 2.8,
            "specific_heat": 960,
            "density": 2250,
        },
    },
    {
        "name": "Szablon: Regenerator poprzeczny (cross-fired)",
        "description": "Regenerator poprzeczny dla specjalistycznych zastosowań",
        "regenerator_type": "cross_fired",
        "geometry_config": {
            "length": 11.0,
            "width": 9.0,
            "height": 13.0,
            "checker_height": 11.0,
            "wall_thickness": 0.5,
        },
        "thermal_config": {
            "gas_temp_inlet": 1470,
            "gas_temp_outlet": 570,
            "air_temp_inlet": 210,
            "air_temp_outlet": 1210,
            "max_operating_temp": 1610,
            "target_efficiency": 85.5,
        },
        "flow_config": {
            "mass_flow_rate": 58,
            "air_flow_rate": 30000,
            "gas_flow_rate": 35000,
            "cycle_time": 1200,
            "design_pressure": 2900,
            "pressure_drop_limit": 4700,
        },
        "materials_config": {
            "checker_material": "Alumina brick (50% Al2O3)",
            "wall_material": "Alumina-silica brick",
            "thermal_conductivity": 2.7,
            "specific_heat": 970,
            "density": 2280,
        },
    },
]


async def seed_default_templates():
    """
    Seed default regenerator configuration templates.

    Creates 5 template configurations (small/medium/large crown, end-port, cross-fired)
    and assigns them to the admin user.
    """
    async with AsyncSessionLocal() as db:
        try:
            # Get admin user
            stmt = select(User).where(User.username == "admin")
            result = await db.execute(stmt)
            admin = result.scalar_one_or_none()

            if not admin:
                logger.error("Admin user not found - cannot seed templates")
                return

            admin_id = str(admin.id)
            logger.info("Found admin user", user_id=admin_id)

            # Check if templates already exist
            stmt = select(RegeneratorConfiguration).where(
                RegeneratorConfiguration.is_template == True
            )
            result = await db.execute(stmt)
            existing_templates = result.scalars().all()

            if existing_templates:
                logger.info(
                    "Templates already exist - skipping seed",
                    count=len(existing_templates)
                )
                return

            # Create template configurations
            created_count = 0
            for template_data in DEFAULT_TEMPLATES:
                config = RegeneratorConfiguration(
                    user_id=admin_id,
                    name=template_data["name"],
                    description=template_data["description"],
                    regenerator_type=template_data["regenerator_type"],
                    configuration_version="1.0",
                    status="completed",
                    current_step=5,
                    total_steps=5,
                    completed_steps=5,
                    geometry_config=template_data["geometry_config"],
                    materials_config=template_data["materials_config"],
                    thermal_config=template_data["thermal_config"],
                    flow_config=template_data["flow_config"],
                    constraints_config={},
                    visualization_config={},
                    is_validated=True,
                    validation_score=1.0,
                    validation_errors=[],
                    validation_warnings=[],
                    is_template=True,
                    completed_at=datetime.now(UTC),
                )

                db.add(config)
                created_count += 1
                logger.info("Created template", name=template_data["name"])

            await db.commit()
            logger.info("Successfully seeded default templates", count=created_count)

        except Exception as e:
            logger.error("Failed to seed default templates", error=str(e))
            await db.rollback()
            raise


async def main():
    """Main entry point for seeding templates."""
    print("Starting default template seeding...")
    await seed_default_templates()
    print("Template seeding completed!")


if __name__ == "__main__":
    asyncio.run(main())
