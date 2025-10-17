"""
Tests for authentication service.

Testy dla serwisu uwierzytelniania.
"""

import pytest
from uuid import uuid4
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.services.auth_service import AuthService
from app.models.user import User, UserRole
from app.core.security import verify_password, get_password_hash
from app.schemas.auth_schemas import UserCreate, UserLogin, Token


class TestAuthService:
    """Test authentication service functionality."""

    @pytest.fixture
    async def auth_service(self, test_db: AsyncSession) -> AuthService:
        """Create auth service instance."""
        return AuthService(test_db)

    @pytest.fixture
    async def test_user(self, test_db: AsyncSession) -> User:
        """Create test user."""
        unique_id = uuid4().hex[:8]
        user = User(
            username=f"testuser_{unique_id}",
            email=f"test_{unique_id}@example.com",
            full_name="Test User",
            password_hash=get_password_hash("TestPassword123!@#"),
            role=UserRole.ENGINEER,
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        return user

    @pytest.fixture
    async def admin_user(self, test_db: AsyncSession) -> User:
        """Create admin test user."""
        unique_id = uuid4().hex[:8]
        user = User(
            username=f"adminuser_{unique_id}",
            email=f"admin_{unique_id}@example.com",
            full_name="Admin User",
            password_hash=get_password_hash("AdminPassword123!@#"),
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        return user

    async def test_create_user(self, auth_service: AuthService):
        """Test creating a new user."""
        unique_id = uuid4().hex[:8]
        user_data = UserCreate(
            username=f"newuser_{unique_id}",
            email=f"newuser_{unique_id}@example.com",
            full_name="New Test User",
            password="NewPassword123!@#",
            role=UserRole.VIEWER
        )

        result = await auth_service.create_user(user_data)

        assert result.username == f"newuser_{unique_id}"
        assert result.email == f"newuser_{unique_id}@example.com"
        assert result.role == UserRole.VIEWER
        assert result.is_active is True
        assert result.is_verified is False  # New users need verification
        assert verify_password("NewPassword123!@#", result.password_hash)

    async def test_create_user_duplicate_username(self, auth_service: AuthService, test_user: User):
        """Test creating user with duplicate username."""
        user_data = UserCreate(
            username=test_user.username,  # Duplicate username
            email="different@example.com",
            full_name="Different User",
            password="password123",
            role=UserRole.VIEWER
        )

        with pytest.raises(ValueError, match="Username already exists"):
            await auth_service.create_user(user_data)

    async def test_create_user_duplicate_email(self, auth_service: AuthService, test_user: User):
        """Test creating user with duplicate email."""
        user_data = UserCreate(
            username="differentuser",
            email=test_user.email,  # Duplicate email
            full_name="Different User",
            password="password123",
            role=UserRole.VIEWER
        )

        with pytest.raises(ValueError, match="Email already exists"):
            await auth_service.create_user(user_data)

    async def test_authenticate_user_success(self, auth_service: AuthService, test_user: User):
        """Test successful user authentication."""
        login_data = UserLogin(
            username=test_user.username,
            password="testpassword"
        )

        result = await auth_service.authenticate_user(login_data)

        assert result is not None
        assert result.username == test_user.username
        assert result.email == test_user.email

    async def test_authenticate_user_wrong_password(self, auth_service: AuthService, test_user: User):
        """Test authentication with wrong password."""
        login_data = UserLogin(
            username=test_user.username,
            password="wrongpassword"
        )

        result = await auth_service.authenticate_user(login_data)
        assert result is None

    async def test_authenticate_user_nonexistent(self, auth_service: AuthService):
        """Test authentication with non-existent user."""
        login_data = UserLogin(
            username="nonexistent",
            password="anypassword"
        )

        result = await auth_service.authenticate_user(login_data)
        assert result is None

    async def test_authenticate_inactive_user(self, auth_service: AuthService, test_db: AsyncSession):
        """Test authentication with inactive user."""
        inactive_user = User(
            username="inactiveuser",
            email="inactive@example.com",
            full_name="Inactive User",
            password_hash=get_password_hash("password"),
            role=UserRole.VIEWER,
            is_active=False,  # Inactive user
            is_verified=True
        )
        test_db.add(inactive_user)
        await test_db.commit()

        login_data = UserLogin(
            username="inactiveuser",
            password="password"
        )

        result = await auth_service.authenticate_user(login_data)
        assert result is None

    async def test_get_user_by_username(self, auth_service: AuthService, test_user: User):
        """Test getting user by username."""
        result = await auth_service.get_user_by_username(test_user.username)

        assert result is not None
        assert result.id == test_user.id
        assert result.username == test_user.username

    async def test_get_user_by_email(self, auth_service: AuthService, test_user: User):
        """Test getting user by email."""
        result = await auth_service.get_user_by_email(test_user.email)

        assert result is not None
        assert result.id == test_user.id
        assert result.email == test_user.email

    async def test_get_user_by_id(self, auth_service: AuthService, test_user: User):
        """Test getting user by ID."""
        result = await auth_service.get_user_by_id(str(test_user.id))

        assert result is not None
        assert result.id == test_user.id
        assert result.username == test_user.username

    async def test_update_user_password(self, auth_service: AuthService, test_user: User):
        """Test updating user password."""
        new_password = "newpassword123"

        success = await auth_service.update_user_password(str(test_user.id), new_password)

        assert success is True

        # Verify new password works
        updated_user = await auth_service.get_user_by_id(str(test_user.id))
        assert verify_password(new_password, updated_user.password_hash)

    async def test_update_last_login(self, auth_service: AuthService, test_user: User):
        """Test updating user's last login timestamp."""
        await auth_service.update_last_login(str(test_user.id))

        updated_user = await auth_service.get_user_by_id(str(test_user.id))
        assert updated_user.last_login is not None
        assert updated_user.last_login > test_user.created_at

    async def test_deactivate_user(self, auth_service: AuthService, test_user: User):
        """Test deactivating user account."""
        success = await auth_service.deactivate_user(str(test_user.id))

        assert success is True

        deactivated_user = await auth_service.get_user_by_id(str(test_user.id))
        assert deactivated_user.is_active is False

    async def test_activate_user(self, auth_service: AuthService, test_db: AsyncSession):
        """Test activating user account."""
        # Create inactive user
        inactive_user = User(
            username="toactivate",
            email="activate@example.com",
            full_name="To Activate",
            password_hash=get_password_hash("password"),
            role=UserRole.VIEWER,
            is_active=False,
            is_verified=True
        )
        test_db.add(inactive_user)
        await test_db.commit()
        await test_db.refresh(inactive_user)

        success = await auth_service.activate_user(str(inactive_user.id))

        assert success is True

        activated_user = await auth_service.get_user_by_id(str(inactive_user.id))
        assert activated_user.is_active is True

    async def test_verify_user_email(self, auth_service: AuthService, test_db: AsyncSession):
        """Test verifying user email."""
        # Create unverified user
        unverified_user = User(
            username="unverified",
            email="unverified@example.com",
            full_name="Unverified User",
            password_hash=get_password_hash("password"),
            role=UserRole.VIEWER,
            is_active=True,
            is_verified=False
        )
        test_db.add(unverified_user)
        await test_db.commit()
        await test_db.refresh(unverified_user)

        success = await auth_service.verify_user_email(str(unverified_user.id))

        assert success is True

        verified_user = await auth_service.get_user_by_id(str(unverified_user.id))
        assert verified_user.is_verified is True

    async def test_generate_reset_token(self, auth_service: AuthService, test_user: User):
        """Test generating password reset token."""
        token = await auth_service.generate_reset_token(test_user.email)

        assert token is not None
        assert len(token) > 0

        # Verify token is stored
        user_with_token = await auth_service.get_user_by_id(str(test_user.id))
        assert user_with_token.reset_token is not None
        assert user_with_token.reset_token_expires is not None

    async def test_verify_reset_token(self, auth_service: AuthService, test_user: User):
        """Test verifying password reset token."""
        # Generate token first
        token = await auth_service.generate_reset_token(test_user.email)

        # Verify token
        user = await auth_service.verify_reset_token(token)

        assert user is not None
        assert user.id == test_user.id

    async def test_verify_expired_reset_token(self, auth_service: AuthService, test_user: User):
        """Test verifying expired reset token."""
        # Generate token and manually expire it
        token = await auth_service.generate_reset_token(test_user.email)

        # Manually set expiration in the past
        test_user.reset_token_expires = datetime.utcnow() - timedelta(hours=1)
        await auth_service.db.commit()

        # Verify expired token
        user = await auth_service.verify_reset_token(token)
        assert user is None

    async def test_reset_password_with_token(self, auth_service: AuthService, test_user: User):
        """Test resetting password with valid token."""
        # Generate token first
        token = await auth_service.generate_reset_token(test_user.email)
        new_password = "newresetpassword"

        success = await auth_service.reset_password_with_token(token, new_password)

        assert success is True

        # Verify new password works and token is cleared
        updated_user = await auth_service.get_user_by_id(str(test_user.id))
        assert verify_password(new_password, updated_user.password_hash)
        assert updated_user.reset_token is None
        assert updated_user.reset_token_expires is None

    async def test_check_user_permissions(self, auth_service: AuthService, test_user: User, admin_user: User):
        """Test checking user permissions."""
        # Test regular user permissions
        assert await auth_service.check_user_permissions(str(test_user.id), "read") is True
        assert await auth_service.check_user_permissions(str(test_user.id), "write") is True
        assert await auth_service.check_user_permissions(str(test_user.id), "admin") is False

        # Test admin permissions
        assert await auth_service.check_user_permissions(str(admin_user.id), "read") is True
        assert await auth_service.check_user_permissions(str(admin_user.id), "write") is True
        assert await auth_service.check_user_permissions(str(admin_user.id), "admin") is True

    async def test_change_user_role(self, auth_service: AuthService, test_user: User, admin_user: User):
        """Test changing user role."""
        success = await auth_service.change_user_role(str(test_user.id), UserRole.ADMIN, str(admin_user.id))

        assert success is True

        updated_user = await auth_service.get_user_by_id(str(test_user.id))
        assert updated_user.role == UserRole.ADMIN

    async def test_change_user_role_unauthorized(self, auth_service: AuthService, test_user: User):
        """Test changing user role without admin permissions."""
        # Non-admin trying to change role
        success = await auth_service.change_user_role(str(test_user.id), UserRole.ADMIN, str(test_user.id))

        assert success is False

    async def test_get_user_activity_log(self, auth_service: AuthService, test_user: User):
        """Test getting user activity log."""
        # Log some activities first
        await auth_service.log_user_activity(str(test_user.id), "login", "User logged in")
        await auth_service.log_user_activity(str(test_user.id), "update_profile", "User updated profile")

        activities = await auth_service.get_user_activity_log(str(test_user.id), limit=10)

        assert len(activities) >= 2
        assert any(activity["action"] == "login" for activity in activities)
        assert any(activity["action"] == "update_profile" for activity in activities)

    async def test_validate_user_data(self, auth_service: AuthService):
        """Test user data validation."""
        # Valid data
        valid_data = {
            "username": "validuser",
            "email": "valid@example.com",
            "full_name": "Valid User",
            "password": "validpassword123"
        }

        result = await auth_service._validate_user_data(valid_data)
        assert result["is_valid"] is True

        # Invalid data
        invalid_data = {
            "username": "ab",  # Too short
            "email": "invalid-email",  # Invalid email format
            "full_name": "",  # Empty name
            "password": "123"  # Too short
        }

        result = await auth_service._validate_user_data(invalid_data)
        assert result["is_valid"] is False
        assert len(result["errors"]) > 0

    async def test_bulk_user_operations(self, auth_service: AuthService, admin_user: User, test_db: AsyncSession):
        """Test bulk user operations."""
        # Create multiple users
        user_ids = []
        for i in range(3):
            user = User(
                username=f"bulkuser{i}",
                email=f"bulk{i}@example.com",
                full_name=f"Bulk User {i}",
                password_hash=get_password_hash("password"),
                role=UserRole.VIEWER,
                is_active=True,
                is_verified=True
            )
            test_db.add(user)
            user_ids.append(str(user.id))

        await test_db.commit()

        # Test bulk deactivation
        deactivated_count = await auth_service.bulk_deactivate_users(user_ids, str(admin_user.id))

        assert deactivated_count == 3

    async def test_user_session_management(self, auth_service: AuthService, test_user: User):
        """Test user session management."""
        session_id = "test-session-123"

        # Create session
        await auth_service.create_user_session(str(test_user.id), session_id)

        # Verify session exists
        session_exists = await auth_service.verify_user_session(str(test_user.id), session_id)
        assert session_exists is True

        # Invalidate session
        await auth_service.invalidate_user_session(str(test_user.id), session_id)

        # Verify session is invalidated
        session_exists = await auth_service.verify_user_session(str(test_user.id), session_id)
        assert session_exists is False

    async def test_get_user_statistics(self, auth_service: AuthService):
        """Test getting user statistics."""
        stats = await auth_service.get_user_statistics()

        assert "total_users" in stats
        assert "active_users" in stats
        assert "verified_users" in stats
        assert "by_role" in stats
        assert "recent_registrations" in stats

        assert stats["total_users"] >= 0
        assert stats["active_users"] >= 0