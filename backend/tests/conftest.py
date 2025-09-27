"""
Pytest configuration and fixtures.

Konfiguracja pytest i wspólne fixtures.
"""

import asyncio
import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    TestSessionLocal = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def test_client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database override."""

    def override_get_db():
        return test_db

    app.dependency_overrides[get_db] = override_get_db

    from httpx import ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def admin_token(test_client: AsyncClient, test_db: AsyncSession) -> str:
    """Create admin user and return auth token."""
    from app.models.user import User, UserRole
    from app.core.security import get_password_hash

    # Create admin user
    admin_user = User(
        username="testadmin",
        email="testadmin@test.com",
        full_name="Test Administrator",
        password_hash=get_password_hash("testpassword"),
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True
    )

    test_db.add(admin_user)
    await test_db.commit()
    await test_db.refresh(admin_user)

    # Login and get token
    login_response = await test_client.post(
        "/api/v1/auth/login",
        json={"username": "testadmin", "password": "testpassword"}
    )

    token_data = login_response.json()
    return token_data["access_token"]


@pytest.fixture
def auth_headers(admin_token: str) -> dict:
    """Return authorization headers with admin token."""
    return {"Authorization": f"Bearer {admin_token}"}