"""
Tests for authentication API endpoints.

Testy endpointów uwierzytelniania.
"""

import pytest
from httpx import AsyncClient

from app.models.user import User, UserRole
from app.core.security import get_password_hash


class TestAuthAPI:
    """Tests for authentication endpoints."""

    @pytest.mark.asyncio
    async def test_login_success(self, test_client: AsyncClient, test_db):
        """Test successful login."""
        # Create test user
        user = User(
            username="loginuser",
            email="login@test.com",
            full_name="Login User",
            password_hash=get_password_hash("loginpass123"),
            role=UserRole.ENGINEER,
            is_active=True,
            is_verified=True
        )

        test_db.add(user)
        await test_db.commit()

        # Test login
        response = await test_client.post(
            "/api/v1/auth/login",
            json={"username": "loginuser", "password": "loginpass123"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert "user" in data

        user_data = data["user"]
        assert user_data["username"] == "loginuser"
        assert user_data["email"] == "login@test.com"
        assert user_data["role"] == "ENGINEER"

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, test_client: AsyncClient, test_db):
        """Test login with invalid credentials."""
        # Create test user
        user = User(
            username="invaliduser",
            email="invalid@test.com",
            password_hash=get_password_hash("correctpass"),
            role=UserRole.VIEWER,
            is_active=True,
            is_verified=True
        )

        test_db.add(user)
        await test_db.commit()

        # Test login with wrong password
        response = await test_client.post(
            "/api/v1/auth/login",
            json={"username": "invaliduser", "password": "wrongpass"}
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_login_inactive_user(self, test_client: AsyncClient, test_db):
        """Test login with inactive user."""
        user = User(
            username="inactiveuser",
            email="inactive@test.com",
            password_hash=get_password_hash("testpass123"),
            role=UserRole.VIEWER,
            is_active=False,  # Inactive user
            is_verified=True
        )

        test_db.add(user)
        await test_db.commit()

        response = await test_client.post(
            "/api/v1/auth/login",
            json={"username": "inactiveuser", "password": "testpass123"}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, test_client: AsyncClient):
        """Test login with non-existent user."""
        response = await test_client.post(
            "/api/v1/auth/login",
            json={"username": "nonexistent", "password": "anypassword"}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_me_endpoint_with_token(self, test_client: AsyncClient, auth_headers):
        """Test /me endpoint with valid token."""
        response = await test_client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "username" in data
        assert "email" in data
        assert "role" in data
        assert data["username"] == "testadmin"

    @pytest.mark.asyncio
    async def test_me_endpoint_without_token(self, test_client: AsyncClient):
        """Test /me endpoint without token."""
        response = await test_client.get("/api/v1/auth/me")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_token(self, test_client: AsyncClient, test_db):
        """Test token refresh functionality."""
        # Create and login user
        user = User(
            username="refreshuser",
            email="refresh@test.com",
            password_hash=get_password_hash("refreshpass"),
            role=UserRole.ENGINEER,
            is_active=True,
            is_verified=True
        )

        test_db.add(user)
        await test_db.commit()

        # Login to get initial token
        login_response = await test_client.post(
            "/api/v1/auth/login",
            json={"username": "refreshuser", "password": "refreshpass"}
        )

        assert login_response.status_code == 200
        token_data = login_response.json()
        access_token = token_data["access_token"]

        # Test token refresh
        refresh_response = await test_client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert refresh_response.status_code == 200
        refresh_data = refresh_response.json()

        assert "access_token" in refresh_data
        assert "token_type" in refresh_data
        assert refresh_data["token_type"] == "bearer"

        # New token should be different
        assert refresh_data["access_token"] != access_token