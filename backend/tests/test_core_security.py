"""
Tests for core security functionality.

Testy dla funkcjonalności bezpieczeństwa.
"""

import pytest
from datetime import datetime, timedelta
from jose import jwt

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    generate_reset_token,
    verify_reset_token,
    validate_password_strength
)
from app.core.config import settings


class TestSecurityFunctions:
    """Test security utility functions."""

    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "testpassword123"

        # Test hashing
        hashed = get_password_hash(password)
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")

        # Test verification with correct password
        assert verify_password(password, hashed) is True

        # Test verification with wrong password
        assert verify_password("wrongpassword", hashed) is False

    def test_password_hash_uniqueness(self):
        """Test that same password produces different hashes."""
        password = "samepassword"

        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Hashes should be different due to salt
        assert hash1 != hash2

        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_create_access_token(self):
        """Test JWT access token creation."""
        data = {"sub": "testuser", "user_id": "123"}

        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

        # Decode and verify token
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        assert decoded["sub"] == "testuser"
        assert decoded["user_id"] == "123"
        assert "exp" in decoded

    def test_create_access_token_with_expires_delta(self):
        """Test JWT token creation with custom expiration."""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=15)

        token = create_access_token(data, expires_delta)

        # Decode and check expiration
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        exp_timestamp = decoded["exp"]

        # Should expire in approximately 15 minutes
        now = datetime.utcnow()
        exp_time = datetime.fromtimestamp(exp_timestamp)
        time_diff = exp_time - now

        # Allow some tolerance for test execution time
        assert timedelta(minutes=14) < time_diff < timedelta(minutes=16)

    def test_validate_password_strength(self):
        """Test password strength validation."""
        # Strong password
        strong_password = "StrongPassword123!"
        is_valid, errors = validate_password_strength(strong_password)
        assert is_valid is True
        assert len(errors) == 0

        # Weak password
        weak_password = "123"
        is_valid, errors = validate_password_strength(weak_password)
        assert is_valid is False
        assert len(errors) > 0

        # Test various password criteria
        passwords_to_test = [
            ("", False),  # Empty password
            ("short", False),  # Too short
            ("longenoughbutnouppercaseordigits", False),  # No uppercase or digits
            ("ALLUPPERCASE123", False),  # No lowercase
            ("alllowercase123", False),  # No uppercase
            ("NoDigitsHere", False),  # No digits
            ("Valid123Password", True),  # Valid password
        ]

        for password, should_be_valid in passwords_to_test:
            is_valid, _ = validate_password_strength(password)
            if should_be_valid:
                assert is_valid is True, f"Password '{password}' should be valid"
            else:
                assert is_valid is False, f"Password '{password}' should be invalid"

    def test_verify_token_valid(self):
        """Test token verification with valid token."""
        data = {"sub": "testuser", "user_id": "123"}
        token = create_access_token(data)

        payload = verify_token(token)

        assert payload is not None
        assert payload["sub"] == "testuser"
        assert payload["user_id"] == "123"

    def test_verify_token_invalid(self):
        """Test token verification with invalid token."""
        invalid_token = "invalid.token.here"

        payload = verify_token(invalid_token)

        assert payload is None

    def test_verify_token_expired(self):
        """Test token verification with expired token."""
        data = {"sub": "testuser"}
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)  # Already expired

        token = create_access_token(data, expires_delta)

        payload = verify_token(token)

        assert payload is None

    def test_generate_reset_token(self):
        """Test password reset token generation."""
        token = generate_reset_token()

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_reset_token_valid(self):
        """Test reset token verification with valid token."""
        stored_token = generate_reset_token()
        expires_at = datetime.utcnow() + timedelta(hours=1)

        # Test with same token
        is_valid = verify_reset_token(stored_token, stored_token, expires_at)
        assert is_valid is True

    def test_verify_reset_token_invalid(self):
        """Test reset token verification with invalid token."""
        stored_token = generate_reset_token()
        wrong_token = generate_reset_token()  # Different token
        expires_at = datetime.utcnow() + timedelta(hours=1)

        is_valid = verify_reset_token(wrong_token, stored_token, expires_at)
        assert is_valid is False

    def test_verify_reset_token_expired(self):
        """Test reset token verification with expired token."""
        token = generate_reset_token()
        expires_at = datetime.utcnow() - timedelta(hours=1)  # Expired

        is_valid = verify_reset_token(token, token, expires_at)
        assert is_valid is False

    def test_token_security_properties(self):
        """Test token security properties."""
        data = {"sub": "testuser", "role": "admin"}

        # Create multiple tokens with same data
        token1 = create_access_token(data)
        token2 = create_access_token(data)

        # Tokens should be different (due to timestamps)
        assert token1 != token2

        # But both should verify to same data
        payload1 = verify_token(token1)
        payload2 = verify_token(token2)

        assert payload1["sub"] == payload2["sub"]
        assert payload1["role"] == payload2["role"]

    def test_password_edge_cases(self):
        """Test password hashing with edge cases."""
        # Empty password
        empty_hash = get_password_hash("")
        assert verify_password("", empty_hash) is True
        assert verify_password("notempty", empty_hash) is False

        # Very long password
        long_password = "a" * 1000
        long_hash = get_password_hash(long_password)
        assert verify_password(long_password, long_hash) is True

        # Unicode password
        unicode_password = "password123🔒"
        unicode_hash = get_password_hash(unicode_password)
        assert verify_password(unicode_password, unicode_hash) is True

    def test_token_data_types(self):
        """Test token creation with various data types."""
        # String values
        data1 = {"sub": "user", "name": "John Doe"}
        token1 = create_access_token(data1)
        payload1 = verify_token(token1)
        assert payload1["name"] == "John Doe"

        # Integer values
        data2 = {"sub": "user", "age": 30, "level": 5}
        token2 = create_access_token(data2)
        payload2 = verify_token(token2)
        assert payload2["age"] == 30
        assert payload2["level"] == 5

        # Boolean values
        data3 = {"sub": "user", "is_admin": True, "is_verified": False}
        token3 = create_access_token(data3)
        payload3 = verify_token(token3)
        assert payload3["is_admin"] is True
        assert payload3["is_verified"] is False

    def test_token_expiration_edge_cases(self):
        """Test token expiration edge cases."""
        data = {"sub": "testuser"}

        # Very short expiration
        short_expires = timedelta(milliseconds=1)
        token = create_access_token(data, short_expires)

        # Token might still be valid immediately
        payload = verify_token(token)
        # Don't assert on result as it depends on timing

        # Very long expiration
        long_expires = timedelta(days=365)
        long_token = create_access_token(data, long_expires)
        long_payload = verify_token(long_token)

        assert long_payload is not None
        assert long_payload["sub"] == "testuser"