"""
Database configuration and session management.

Konfiguracja bazy danych MySQL z obsługą asynchronicznych sesji.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
import structlog

from app.core.config import settings


logger = structlog.get_logger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


# Create async engine
engine_kwargs = {
    "echo": settings.DEBUG,
}

# Add pool settings only for MySQL/PostgreSQL, not for SQLite
if not settings.DATABASE_URL.startswith(("sqlite", "aiosqlite")):
    engine_kwargs.update({
        "pool_size": settings.DATABASE_POOL_SIZE,
        "max_overflow": settings.DATABASE_MAX_OVERFLOW,
        "pool_timeout": settings.DATABASE_POOL_TIMEOUT,
        "pool_recycle": settings.DATABASE_POOL_RECYCLE,
    })

engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """
    Get database session.

    Dependency for FastAPI endpoints to get database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database connection."""
    try:
        # Test database connection
        async with engine.begin() as conn:
            # Simple connection test
            await conn.execute(text("SELECT 1"))

        logger.info("Database connection established successfully")
    except Exception as e:
        logger.error("Failed to connect to database", error=str(e))
        raise


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
    logger.info("Database connections closed")