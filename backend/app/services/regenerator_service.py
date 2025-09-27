"""
Regenerator service for managing regenerator configurations.

Serwis regeneratora do zarządzania konfiguracjami regeneratorów.
"""

import structlog
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.orm import joinedload

from app.models.regenerator import RegeneratorConfiguration, RegeneratorType, ConfigurationStatus
from app.schemas.regenerator_schemas import RegeneratorConfigurationCreate, RegeneratorConfigurationResponse
from app.services.validation_service import RegeneratorPhysicsValidator

logger = structlog.get_logger(__name__)


class RegeneratorService:
    """Service for managing regenerator configurations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.validator = RegeneratorPhysicsValidator()

    async def create_regenerator(
        self,
        regenerator_data: RegeneratorConfigurationCreate,
        user_id: str
    ) -> RegeneratorConfiguration:
        """
        Create a new regenerator configuration.

        Args:
            regenerator_data: Regenerator configuration data
            user_id: ID of the user creating the regenerator

        Returns:
            Created regenerator configuration

        Raises:
            ValueError: If validation fails
        """
        try:
            # Validate the configuration data
            validation_result = await self.validator.validate_regenerator_physics(
                regenerator_data.model_dump()
            )

            if not validation_result.is_valid:
                error_messages = [error.message for error in validation_result.errors]
                raise ValueError(f"Validation failed: {'; '.join(error_messages)}")

            # Create regenerator configuration
            regenerator = RegeneratorConfiguration(
                id=str(uuid4()),
                name=regenerator_data.name,
                description=regenerator_data.description,
                regenerator_type=regenerator_data.regenerator_type,
                geometry_config=regenerator_data.geometry_config,
                materials_config=regenerator_data.materials_config,
                thermal_config=regenerator_data.thermal_config,
                flow_config=regenerator_data.flow_config,
                operating_config=regenerator_data.operating_config,
                status=ConfigurationStatus.DRAFT,
                user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            self.db.add(regenerator)
            await self.db.commit()
            await self.db.refresh(regenerator)

            logger.info(
                "Regenerator configuration created",
                regenerator_id=regenerator.id,
                name=regenerator.name,
                user_id=user_id
            )

            return regenerator

        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to create regenerator", error=str(e), user_id=user_id)
            raise

    async def get_regenerator(
        self,
        regenerator_id: str,
        user_id: str
    ) -> Optional[RegeneratorConfiguration]:
        """
        Get a regenerator configuration by ID.

        Args:
            regenerator_id: ID of the regenerator
            user_id: ID of the requesting user

        Returns:
            Regenerator configuration or None if not found
        """
        try:
            query = select(RegeneratorConfiguration).where(
                and_(
                    RegeneratorConfiguration.id == regenerator_id,
                    RegeneratorConfiguration.user_id == user_id
                )
            )

            result = await self.db.execute(query)
            regenerator = result.scalar_one_or_none()

            if regenerator:
                logger.info(
                    "Regenerator retrieved",
                    regenerator_id=regenerator_id,
                    user_id=user_id
                )

            return regenerator

        except Exception as e:
            logger.error(
                "Failed to get regenerator",
                regenerator_id=regenerator_id,
                user_id=user_id,
                error=str(e)
            )
            raise

    async def list_user_regenerators(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ConfigurationStatus] = None,
        regenerator_type: Optional[RegeneratorType] = None
    ) -> List[RegeneratorConfiguration]:
        """
        List regenerator configurations for a user.

        Args:
            user_id: ID of the user
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Optional status filter
            regenerator_type: Optional type filter

        Returns:
            List of regenerator configurations
        """
        try:
            query = select(RegeneratorConfiguration).where(
                RegeneratorConfiguration.user_id == user_id
            )

            # Apply filters
            if status:
                query = query.where(RegeneratorConfiguration.status == status)

            if regenerator_type:
                query = query.where(RegeneratorConfiguration.regenerator_type == regenerator_type)

            # Apply ordering, skip, and limit
            query = query.order_by(desc(RegeneratorConfiguration.updated_at)).offset(skip).limit(limit)

            result = await self.db.execute(query)
            regenerators = result.scalars().all()

            logger.info(
                "Listed user regenerators",
                user_id=user_id,
                count=len(regenerators),
                skip=skip,
                limit=limit
            )

            return list(regenerators)

        except Exception as e:
            logger.error(
                "Failed to list regenerators",
                user_id=user_id,
                error=str(e)
            )
            raise

    async def update_regenerator(
        self,
        regenerator_id: str,
        regenerator_data: RegeneratorConfigurationCreate,
        user_id: str
    ) -> Optional[RegeneratorConfiguration]:
        """
        Update a regenerator configuration.

        Args:
            regenerator_id: ID of the regenerator to update
            regenerator_data: Updated configuration data
            user_id: ID of the requesting user

        Returns:
            Updated regenerator configuration or None if not found

        Raises:
            ValueError: If validation fails
        """
        try:
            # Get existing regenerator
            regenerator = await self.get_regenerator(regenerator_id, user_id)
            if not regenerator:
                return None

            # Validate the updated configuration data
            validation_result = await self.validator.validate_regenerator_physics(
                regenerator_data.model_dump()
            )

            if not validation_result.is_valid:
                error_messages = [error.message for error in validation_result.errors]
                raise ValueError(f"Validation failed: {'; '.join(error_messages)}")

            # Update regenerator fields
            regenerator.name = regenerator_data.name
            regenerator.description = regenerator_data.description
            regenerator.regenerator_type = regenerator_data.regenerator_type
            regenerator.geometry_config = regenerator_data.geometry_config
            regenerator.materials_config = regenerator_data.materials_config
            regenerator.thermal_config = regenerator_data.thermal_config
            regenerator.flow_config = regenerator_data.flow_config
            regenerator.operating_config = regenerator_data.operating_config
            regenerator.updated_at = datetime.utcnow()

            await self.db.commit()
            await self.db.refresh(regenerator)

            logger.info(
                "Regenerator configuration updated",
                regenerator_id=regenerator_id,
                name=regenerator.name,
                user_id=user_id
            )

            return regenerator

        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Failed to update regenerator",
                regenerator_id=regenerator_id,
                user_id=user_id,
                error=str(e)
            )
            raise

    async def delete_regenerator(
        self,
        regenerator_id: str,
        user_id: str
    ) -> bool:
        """
        Delete a regenerator configuration.

        Args:
            regenerator_id: ID of the regenerator to delete
            user_id: ID of the requesting user

        Returns:
            True if deleted, False if not found
        """
        try:
            regenerator = await self.get_regenerator(regenerator_id, user_id)
            if not regenerator:
                return False

            await self.db.delete(regenerator)
            await self.db.commit()

            logger.info(
                "Regenerator configuration deleted",
                regenerator_id=regenerator_id,
                user_id=user_id
            )

            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Failed to delete regenerator",
                regenerator_id=regenerator_id,
                user_id=user_id,
                error=str(e)
            )
            raise

    async def validate_configuration(
        self,
        regenerator_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate regenerator configuration without saving.

        Args:
            regenerator_data: Configuration data to validate

        Returns:
            Validation result with errors and recommendations
        """
        try:
            validation_result = await self.validator.validate_regenerator_physics(
                regenerator_data
            )

            return {
                "is_valid": validation_result.is_valid,
                "errors": [
                    {
                        "field": error.field,
                        "message": error.message,
                        "current_value": error.current_value,
                        "suggestion": error.suggestion
                    }
                    for error in validation_result.errors
                ],
                "warnings": [
                    {
                        "field": warning.field,
                        "message": warning.message,
                        "current_value": warning.current_value,
                        "suggestion": warning.suggestion
                    }
                    for warning in validation_result.warnings
                ]
            }

        except Exception as e:
            logger.error("Failed to validate configuration", error=str(e))
            raise

    async def get_configuration_templates(
        self,
        regenerator_type: Optional[RegeneratorType] = None
    ) -> List[Dict[str, Any]]:
        """
        Get configuration templates for different regenerator types.

        Args:
            regenerator_type: Optional filter by regenerator type

        Returns:
            List of configuration templates
        """
        templates = []

        # Glass furnace regenerator template
        if not regenerator_type or regenerator_type == RegeneratorType.GLASS_FURNACE:
            templates.append({
                "name": "Glass Furnace Regenerator",
                "description": "Standard configuration for glass furnace regenerator",
                "regenerator_type": RegeneratorType.GLASS_FURNACE,
                "geometry_config": {
                    "length": 12.0,  # meters
                    "width": 8.0,    # meters
                    "height": 6.0,   # meters
                    "checker_height": 0.25,  # meters
                    "checker_spacing": 0.05,  # meters
                    "wall_thickness": 0.5     # meters
                },
                "materials_config": {
                    "checker_material": "silica_brick",
                    "wall_material": "refractory_concrete",
                    "insulation_material": "ceramic_fiber"
                },
                "thermal_config": {
                    "hot_gas_temp": 1500.0,  # Celsius
                    "cold_gas_temp": 200.0,  # Celsius
                    "cycle_time": 1800,      # seconds
                    "target_efficiency": 0.85
                },
                "flow_config": {
                    "gas_flow_rate": 10.0,   # m³/s
                    "pressure_drop_limit": 2000.0  # Pa
                }
            })

        # Industrial furnace template
        if not regenerator_type or regenerator_type == RegeneratorType.INDUSTRIAL_FURNACE:
            templates.append({
                "name": "Industrial Furnace Regenerator",
                "description": "Standard configuration for industrial furnace regenerator",
                "regenerator_type": RegeneratorType.INDUSTRIAL_FURNACE,
                "geometry_config": {
                    "length": 10.0,
                    "width": 6.0,
                    "height": 5.0,
                    "checker_height": 0.20,
                    "checker_spacing": 0.04,
                    "wall_thickness": 0.4
                },
                "materials_config": {
                    "checker_material": "alumina_brick",
                    "wall_material": "high_alumina_concrete",
                    "insulation_material": "mineral_wool"
                },
                "thermal_config": {
                    "hot_gas_temp": 1200.0,
                    "cold_gas_temp": 150.0,
                    "cycle_time": 1200,
                    "target_efficiency": 0.80
                },
                "flow_config": {
                    "gas_flow_rate": 8.0,
                    "pressure_drop_limit": 1800.0
                }
            })

        logger.info(
            "Configuration templates retrieved",
            count=len(templates),
            regenerator_type=regenerator_type
        )

        return templates