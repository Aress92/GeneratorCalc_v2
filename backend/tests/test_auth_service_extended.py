"""
Extended tests for auth service.

Rozszerzone testy dla serwisu uwierzytelniania.
"""

import pytest
from uuid import uuid4
from datetime import datetime, timedelta, UTC
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth_service import AuthService
from app.models.user import User, UserRole
from app.schemas.auth_schemas import UserCreate, UserLogin, Token
from app.core.security import verify_password, get_password_hash


class TestAuthServiceExtended:
    """Extended tests for AuthService functionality."""

    @pytest.fixture
    async def auth_service(self, test_db: AsyncSession) -> AuthService:
        """Create auth service instance."""
        return AuthService(test_db)

    @pytest.fixture
    async def test_user(self, test_db: AsyncSession) -> User:
        """Create test user."""
        unique_id = uuid4().hex[:8]
        user = User(
            username=f"authuser_{unique_id}",
            email=f"auth_{unique_id}@example.com",
            full_name="Auth Test User",
            password_hash=get_password_hash("testpass123"),
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
        """Create admin user."""
        unique_id = uuid4().hex[:8]
        user = User(
            username=f"adminuser_{unique_id}",
            email=f"admin_{unique_id}@example.com",
            full_name="Admin Test User",
            password_hash=get_password_hash("adminpass123"),
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        return user

    # === REGISTRATION TESTS ===

    async def test_register_new_user(self, auth_service: AuthService):
        """Test registering a new user."""
        unique_id = uuid4().hex[:8]
        user_data = UserCreate(
            username=f"newuser_{unique_id}",
            email=f"newuser_{unique_id}@example.com",
            full_name="New Test User",
            password="securepass123"
        )

        result = await auth_service.register_user(user_data)

        assert result is not None
        assert result.username == user_data.username
        assert result.email == user_data.email
        assert result.full_name == user_data.full_name
        assert result.role == UserRole.ENGINEER  # Default role
        assert result.is_active is True
        assert result.is_verified is False  # Requires verification

    async def test_register_duplicate_username(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """Test registering user with duplicate username."""
        user_data = UserCreate(
            username=test_user.username,  # Duplicate
            email="different@example.com",
            full_name="Duplicate Username",
            password="password123"
        )

        with pytest.raises(ValueError, match="Username .* already exists"):
            await auth_service.register_user(user_data)

    async def test_register_duplicate_email(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """Test registering user with duplicate email."""
        user_data = UserCreate(
            username="differentuser",
            email=test_user.email,  # Duplicate
            full_name="Duplicate Email",
            password="password123"
        )

        with pytest.raises(ValueError, match="Email .* already registered"):
            await auth_service.register_user(user_data)

    async def test_register_weak_password(self, auth_service: AuthService):
        """Test registering with weak password."""
        unique_id = uuid4().hex[:8]
        user_data = UserCreate(
            username=f"weakpass_{unique_id}",
            email=f"weak_{unique_id}@example.com",
            full_name="Weak Password User",
            password="123"  # Too short
        )

        with pytest.raises(ValueError, match="Password must be at least"):
            await auth_service.register_user(user_data)

    # === LOGIN TESTS ===

    async def test_login_success(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """Test successful login."""
        login_data = UserLogin(
            username=test_user.username,
            password="testpass123"
        )

        result = await auth_service.authenticate_user(login_data)

        assert result is not None
        assert result.id == test_user.id
        assert result.username == test_user.username

    async def test_login_with_email(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """Test login with email instead of username."""
        login_data = UserLogin(
            username=test_user.email,  # Use email
            password="testpass123"
        )

        result = await auth_service.authenticate_user(login_data)

        assert result is not None
        assert result.id == test_user.id

    async def test_login_wrong_password(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """Test login with wrong password."""
        login_data = UserLogin(
            username=test_user.username,
            password="wrongpassword"
        )

        result = await auth_service.authenticate_user(login_data)

        assert result is None

    async def test_login_nonexistent_user(self, auth_service: AuthService):
        """Test login with non-existent username."""
        login_data = UserLogin(
            username="nonexistentuser",
            password="anypassword"
        )

        result = await auth_service.authenticate_user(login_data)

        assert result is None

    async def test_login_inactive_user(
        self,
        auth_service: AuthService,
        test_db: AsyncSession,
        test_user: User
    ):
        """Test login with inactive account."""
        # Deactivate user
        test_user.is_active = False
        await test_db.commit()

        login_data = UserLogin(
            username=test_user.username,
            password="testpass123"
        )

        result = await auth_service.authenticate_user(login_data)

        assert result is None

    # === TOKEN GENERATION TESTS ===

    async def test_create_access_token(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """Test creating access token."""
        token_data = {
            "sub": str(test_user.id),
            "username": test_user.username,
            "role": test_user.role.value
        }

        token = await auth_service.create_access_token(token_data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    async def test_create_refresh_token(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """Test creating refresh token."""
        token_data = {
            "sub": str(test_user.id),
            "username": test_user.username
        }

        token = await auth_service.create_refresh_token(token_data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    async def test_verify_token_valid(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """Test verifying valid token."""
        # Create token
        token_data = {
            "sub": str(test_user.id),
            "username": test_user.username,
            "role": test_user.role.value
        }
        token = await auth_service.create_access_token(token_data)

        # Verify token
        payload = await auth_service.verify_token(token)

        assert payload is not None
        assert payload["sub"] == str(test_user.id)
        assert payload["username"] == test_user.username

    async def test_verify_token_expired(self, auth_service: AuthService):
        """Test verifying expired token."""
        with patch('app.services.auth_service.datetime') as mock_datetime:
            # Create token that expires immediately
            mock_datetime.now.return_value = datetime.now(UTC) - timedelta(hours=2)

            token_data = {"sub": str(uuid4()), "username": "testuser"}
            token = await auth_service.create_access_token(
                token_data,
                expires_delta=timedelta(minutes=-10)
            )

            # Reset datetime
            mock_datetime.now.return_value = datetime.now(UTC)

            # Verify - should fail
            payload = await auth_service.verify_token(token)
            assert payload is None

    async def test_verify_token_invalid(self, auth_service: AuthService):
        """Test verifying invalid token."""
        invalid_token = "invalid.jwt.token"

        payload = await auth_service.verify_token(invalid_token)

        assert payload is None

    # === USER MANAGEMENT TESTS ===

    async def test_get_user_by_id(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """Test getting user by ID."""
        result = await auth_service.get_user_by_id(str(test_user.id))

        assert result is not None
        assert result.id == test_user.id
        assert result.username == test_user.username

    async def test_get_user_by_username(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """Test getting user by username."""
        result = await auth_service.get_user_by_username(test_user.username)

        assert result is not None
        assert result.id == test_user.id
        assert result.username == test_user.username

    async def test_get_user_by_email(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """Test getting user by email."""
        result = await auth_service.get_user_by_email(test_user.email)

        assert result is not None
        assert result.id == test_user.id
        assert result.email == test_user.email

    async def test_update_user_profile(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """Test updating user profile."""
        update_data = {
            "full_name": "Updated Full Name",
            "email": f"updated_{uuid4().hex[:8]}@example.com"
        }

        result = await auth_service.update_user_profile(
            str(test_user.id),
            update_data
        )

        assert result is not None
        assert result.full_name == update_data["full_name"]
        assert result.email == update_data["email"]

    async def test_change_password(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """Test changing user password."""
        new_password = "newsecurepass456"

        success = await auth_service.change_password(
            str(test_user.id),
            "testpass123",  # Old password
            new_password
        )

        assert success is True

        # Verify new password works
        login_data = UserLogin(
            username=test_user.username,
            password=new_password
        )
        result = await auth_service.authenticate_user(login_data)
        assert result is not None

    async def test_change_password_wrong_old(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """Test changing password with wrong old password."""
        success = await auth_service.change_password(
            str(test_user.id),
            "wrongoldpass",
            "newpass123"
        )

        assert success is False

    async def test_reset_password_request(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """Test requesting password reset."""
        token = await auth_service.create_password_reset_token(test_user.email)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    async def test_reset_password_with_token(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """Test resetting password with valid token."""
        # Create reset token
        reset_token = await auth_service.create_password_reset_token(test_user.email)

        # Reset password
        new_password = "resetpass789"
        success = await auth_service.reset_password_with_token(
            reset_token,
            new_password
        )

        assert success is True

        # Verify new password works
        login_data = UserLogin(
            username=test_user.username,
            password=new_password
        )
        result = await auth_service.authenticate_user(login_data)
        assert result is not None

    # === ROLE & PERMISSION TESTS ===

    async def test_check_user_role_admin(
        self,
        auth_service: AuthService,
        admin_user: User
    ):
        """Test checking admin role."""
        is_admin = await auth_service.check_user_role(
            str(admin_user.id),
            UserRole.ADMIN
        )

        assert is_admin is True

    async def test_check_user_role_engineer(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """Test checking engineer role."""
        is_engineer = await auth_service.check_user_role(
            str(test_user.id),
            UserRole.ENGINEER
        )

        assert is_engineer is True

    async def test_check_user_role_mismatch(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """Test checking mismatched role."""
        is_admin = await auth_service.check_user_role(
            str(test_user.id),
            UserRole.ADMIN
        )

        assert is_admin is False

    async def test_promote_user_to_admin(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """Test promoting user to admin."""
        success = await auth_service.update_user_role(
            str(test_user.id),
            UserRole.ADMIN
        )

        assert success is True

        # Verify role changed
        updated_user = await auth_service.get_user_by_id(str(test_user.id))
        assert updated_user.role == UserRole.ADMIN

    # === ACCOUNT STATUS TESTS ===

    async def test_activate_user(
        self,
        auth_service: AuthService,
        test_db: AsyncSession,
        test_user: User
    ):
        """Test activating user account."""
        # Deactivate first
        test_user.is_active = False
        await test_db.commit()

        # Activate
        success = await auth_service.activate_user(str(test_user.id))

        assert success is True

        # Verify activated
        updated_user = await auth_service.get_user_by_id(str(test_user.id))
        assert updated_user.is_active is True

    async def test_deactivate_user(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """Test deactivating user account."""
        success = await auth_service.deactivate_user(str(test_user.id))

        assert success is True

        # Verify deactivated
        updated_user = await auth_service.get_user_by_id(str(test_user.id))
        assert updated_user.is_active is False

    async def test_verify_email(
        self,
        auth_service: AuthService,
        test_db: AsyncSession,
        test_user: User
    ):
        """Test email verification."""
        # Unverify first
        test_user.is_verified = False
        await test_db.commit()

        # Verify
        success = await auth_service.verify_email(str(test_user.id))

        assert success is True

        # Check verified
        updated_user = await auth_service.get_user_by_id(str(test_user.id))
        assert updated_user.is_verified is True

    # === SESSION MANAGEMENT TESTS ===

    async def test_update_last_login(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """Test updating last login timestamp."""
        before = test_user.last_login_at

        await auth_service.update_last_login(str(test_user.id))

        # Verify updated
        updated_user = await auth_service.get_user_by_id(str(test_user.id))
        assert updated_user.last_login_at is not None
        if before:
            assert updated_user.last_login_at > before

    async def test_get_active_users_count(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """Test getting active users count."""
        count = await auth_service.get_active_users_count()

        assert count >= 1
        assert isinstance(count, int)

    async def test_get_users_list(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """Test getting users list."""
        users = await auth_service.get_users(limit=10, offset=0)

        assert len(users) >= 1
        assert isinstance(users, list)
        user_ids = [u.id for u in users]
        assert test_user.id in user_ids

    async def test_get_users_with_role_filter(
        self,
        auth_service: AuthService,
        admin_user: User
    ):
        """Test getting users filtered by role."""
        admins = await auth_service.get_users(
            role=UserRole.ADMIN,
            limit=10,
            offset=0
        )

        assert len(admins) >= 1
        assert all(u.role == UserRole.ADMIN for u in admins)
        admin_ids = [u.id for u in admins]
        assert admin_user.id in admin_ids

    # === ERROR HANDLING TESTS ===

    async def test_register_with_invalid_email(self, auth_service: AuthService):
        """Test registration with invalid email format."""
        unique_id = uuid4().hex[:8]
        user_data = UserCreate(
            username=f"invalidmail_{unique_id}",
            email="not-an-email",
            full_name="Invalid Email User",
            password="password123"
        )

        with pytest.raises(ValueError, match="Invalid email format"):
            await auth_service.register_user(user_data)

    async def test_update_nonexistent_user(self, auth_service: AuthService):
        """Test updating non-existent user."""
        result = await auth_service.update_user_profile(
            str(uuid4()),
            {"full_name": "Does Not Exist"}
        )

        assert result is None

    async def test_delete_user(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """Test deleting user account."""
        success = await auth_service.delete_user(str(test_user.id))

        assert success is True

        # Verify user deleted
        deleted_user = await auth_service.get_user_by_id(str(test_user.id))
        assert deleted_user is None

    # === SECURITY TESTS ===

    async def test_password_hashing(self, auth_service: AuthService):
        """Test password is properly hashed."""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 50  # Bcrypt hashes are long
        assert verify_password(password, hashed) is True

    async def test_password_verification(self):
        """Test password verification."""
        password = "correctpassword"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False

    async def test_token_contains_required_fields(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """Test that JWT token contains required fields."""
        token_data = {
            "sub": str(test_user.id),
            "username": test_user.username,
            "role": test_user.role.value
        }

        token = await auth_service.create_access_token(token_data)
        payload = await auth_service.verify_token(token)

        assert payload is not None
        assert "sub" in payload
        assert "username" in payload
        assert "role" in payload
        assert "exp" in payload  # Expiration time
        assert "iat" in payload  # Issued at
