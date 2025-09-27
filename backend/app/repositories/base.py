"""
Base repository pattern implementation.

Bazowa implementacja wzorca Repository dla operacji CRUD.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Any, Dict
from uuid import UUID

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.core.exceptions import ResourceNotFoundError

T = TypeVar('T', bound=DeclarativeBase)


class BaseRepository(Generic[T], ABC):
    """Base repository class with common CRUD operations."""

    def __init__(self, model: type[T], session: AsyncSession):
        """
        Initialize repository.

        Args:
            model: SQLAlchemy model class
            session: Database session
        """
        self.model = model
        self.session = session

    async def create(self, entity: T) -> T:
        """
        Create new entity.

        Args:
            entity: Entity to create

        Returns:
            Created entity
        """
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def get_by_id(self, id: UUID) -> Optional[T]:
        """
        Get entity by ID.

        Args:
            id: Entity ID

        Returns:
            Entity if found, None otherwise
        """
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_or_raise(self, id: UUID) -> T:
        """
        Get entity by ID or raise exception.

        Args:
            id: Entity ID

        Returns:
            Entity

        Raises:
            ResourceNotFoundError: If entity not found
        """
        entity = await self.get_by_id(id)
        if entity is None:
            raise ResourceNotFoundError(self.model.__name__, str(id))
        return entity

    async def update(self, id: UUID, values: Dict[str, Any]) -> T:
        """
        Update entity by ID.

        Args:
            id: Entity ID
            values: Values to update

        Returns:
            Updated entity

        Raises:
            ResourceNotFoundError: If entity not found
        """
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**values)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        entity = result.scalar_one_or_none()

        if entity is None:
            raise ResourceNotFoundError(self.model.__name__, str(id))

        await self.session.commit()
        return entity

    async def delete(self, id: UUID) -> bool:
        """
        Delete entity by ID.

        Args:
            id: Entity ID

        Returns:
            True if entity was deleted, False if not found
        """
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        deleted_count = result.rowcount
        await self.session.commit()
        return deleted_count > 0

    async def delete_or_raise(self, id: UUID) -> None:
        """
        Delete entity by ID or raise exception.

        Args:
            id: Entity ID

        Raises:
            ResourceNotFoundError: If entity not found
        """
        deleted = await self.delete(id)
        if not deleted:
            raise ResourceNotFoundError(self.model.__name__, str(id))

    async def list(
        self,
        offset: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[T]:
        """
        List entities with pagination and filtering.

        Args:
            offset: Number of entities to skip
            limit: Maximum number of entities to return
            order_by: Column name to order by
            filters: Dictionary of column:value filters

        Returns:
            List of entities
        """
        stmt = select(self.model)

        # Apply filters
        if filters:
            for column, value in filters.items():
                if hasattr(self.model, column):
                    stmt = stmt.where(getattr(self.model, column) == value)

        # Apply ordering
        if order_by and hasattr(self.model, order_by):
            stmt = stmt.order_by(getattr(self.model, order_by))

        # Apply pagination
        stmt = stmt.offset(offset).limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count entities with optional filtering.

        Args:
            filters: Dictionary of column:value filters

        Returns:
            Number of entities
        """
        stmt = select(func.count(self.model.id))

        # Apply filters
        if filters:
            for column, value in filters.items():
                if hasattr(self.model, column):
                    stmt = stmt.where(getattr(self.model, column) == value)

        result = await self.session.execute(stmt)
        return result.scalar()

    async def exists(self, id: UUID) -> bool:
        """
        Check if entity exists.

        Args:
            id: Entity ID

        Returns:
            True if entity exists, False otherwise
        """
        stmt = select(func.count(self.model.id)).where(self.model.id == id)
        result = await self.session.execute(stmt)
        count = result.scalar()
        return count > 0

    async def bulk_create(self, entities: List[T]) -> List[T]:
        """
        Create multiple entities.

        Args:
            entities: List of entities to create

        Returns:
            List of created entities
        """
        self.session.add_all(entities)
        await self.session.commit()
        for entity in entities:
            await self.session.refresh(entity)
        return entities

    async def bulk_update(
        self,
        filters: Dict[str, Any],
        values: Dict[str, Any],
    ) -> int:
        """
        Update multiple entities matching filters.

        Args:
            filters: Dictionary of column:value filters
            values: Values to update

        Returns:
            Number of updated entities
        """
        stmt = update(self.model).values(**values)

        for column, value in filters.items():
            if hasattr(self.model, column):
                stmt = stmt.where(getattr(self.model, column) == value)

        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount

    async def bulk_delete(self, filters: Dict[str, Any]) -> int:
        """
        Delete multiple entities matching filters.

        Args:
            filters: Dictionary of column:value filters

        Returns:
            Number of deleted entities
        """
        stmt = delete(self.model)

        for column, value in filters.items():
            if hasattr(self.model, column):
                stmt = stmt.where(getattr(self.model, column) == value)

        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount