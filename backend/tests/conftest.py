"""
Pytest configuration and fixtures.

Konfiguracja pytest i wspólne fixtures.
"""

import asyncio
import pytest
from uuid import uuid4
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings
from app.models.user import User


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
    from app.core.security import create_access_token

    # Create admin user with unique credentials
    unique_id = uuid4().hex[:8]
    admin_user = User(
        username=f"testadmin_{unique_id}",
        email=f"testadmin_{unique_id}@test.com",
        full_name="Test Administrator",
        password_hash=get_password_hash("TestPassword123!@#"),
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True
    )

    test_db.add(admin_user)
    await test_db.commit()
    await test_db.refresh(admin_user)

    # Create token directly instead of using login endpoint
    token = create_access_token(
        data={"sub": admin_user.username, "user_id": str(admin_user.id)}
    )
    return token


@pytest.fixture
def auth_headers(admin_token: str) -> dict:
    """Return authorization headers with admin token."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
async def test_admin_user(test_db: AsyncSession) -> User:
    """Create admin user for testing."""
    from app.models.user import User, UserRole
    from app.core.security import get_password_hash

    unique_id = uuid4().hex[:8]
    admin_user = User(
        username=f"testadmin_{unique_id}",
        email=f"testadmin_{unique_id}@test.com",
        full_name="Test Administrator",
        password_hash=get_password_hash("TestPassword123!@#"),
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True
    )

    test_db.add(admin_user)
    await test_db.commit()
    await test_db.refresh(admin_user)
    return admin_user


@pytest.fixture
async def test_engineer_user(test_db: AsyncSession) -> User:
    """Create engineer user for testing."""
    from app.models.user import User, UserRole
    from app.core.security import get_password_hash

    unique_id = uuid4().hex[:8]
    engineer_user = User(
        username=f"testengineer_{unique_id}",
        email=f"engineer_{unique_id}@test.com",
        full_name="Test Engineer",
        password_hash=get_password_hash("TestPassword123!@#"),
        role=UserRole.ENGINEER,
        is_active=True,
        is_verified=True
    )

    test_db.add(engineer_user)
    await test_db.commit()
    await test_db.refresh(engineer_user)
    return engineer_user


@pytest.fixture
async def test_viewer_user(test_db: AsyncSession) -> User:
    """Create viewer user for testing."""
    from app.models.user import User, UserRole
    from app.core.security import get_password_hash

    unique_id = uuid4().hex[:8]
    viewer_user = User(
        username=f"testviewer_{unique_id}",
        email=f"viewer_{unique_id}@test.com",
        full_name="Test Viewer",
        password_hash=get_password_hash("TestPassword123!@#"),
        role=UserRole.VIEWER,
        is_active=True,
        is_verified=True
    )

    test_db.add(viewer_user)
    await test_db.commit()
    await test_db.refresh(viewer_user)
    return viewer_user