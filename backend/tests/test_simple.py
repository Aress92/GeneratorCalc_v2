"""
Simple tests to verify basic functionality.

Proste testy do weryfikacji podstawowej funkcjonalności.
"""

import pytest


def test_basic_math():
    """Test basic arithmetic."""
    assert 1 + 1 == 2
    assert 2 * 3 == 6


def test_string_operations():
    """Test string operations."""
    assert "hello".upper() == "HELLO"
    assert len("test") == 4


@pytest.mark.asyncio
async def test_async_operation():
    """Test async operations work."""
    async def async_func():
        return "async_result"

    result = await async_func()
    assert result == "async_result"


class TestBasicConfig:
    """Test basic configuration."""

    def test_environment_check(self):
        """Test we can import our app components."""
        from app.core.config import settings
        assert hasattr(settings, 'PROJECT_NAME')

    def test_models_import(self):
        """Test we can import models."""
        from app.models.user import User, UserRole
        assert UserRole.ADMIN == "ADMIN"
        assert UserRole.ENGINEER == "ENGINEER"
        assert UserRole.VIEWER == "VIEWER"