"""
Security utilities for authentication and authorization.

Moduł bezpieczeństwa z obsługą JWT i haszowania haseł.
"""

from datetime import datetime, timedelta, UTC
from typing import Any, Dict, Optional, Union
import hashlib
import base64

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


# Password hashing context
# Using bcrypt with explicit rounds to avoid compatibility issues
# SHA-256 pre-hashing is applied for passwords > 72 bytes
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Explicit rounds for better compatibility
    bcrypt__ident="2b"   # Use 2b variant for better compatibility
)


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create JWT access token.

    Args:
        subject: Token subject (usually user ID)
        expires_delta: Token expiration time
        additional_claims: Additional claims to include in token

    Returns:
        Encoded JWT token
    """
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "iat": datetime.now(UTC),
        "type": "access",
    }

    if additional_claims:
        to_encode.update(additional_claims)

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode JWT token.

    Args:
        token: JWT token to verify

    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        return payload
    except JWTError:
        return None


def _normalize_password(password: str) -> str:
    """
    Normalize password for bcrypt (handle passwords > 72 bytes).

    Uses SHA-256 to hash long passwords before bcrypt to avoid truncation.
    This is a security best practice for bcrypt.

    Args:
        password: Plain text password

    Returns:
        Normalized password suitable for bcrypt (max 72 bytes)
    """
    # Encode to bytes to check actual byte length
    password_bytes = password.encode('utf-8')

    # If password is longer than 72 bytes, use SHA-256 hash
    if len(password_bytes) > 72:
        # Hash with SHA-256 and encode as base64 to get printable string
        sha_hash = hashlib.sha256(password_bytes).digest()
        return base64.b64encode(sha_hash).decode('ascii')

    return password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify plain password against hashed password.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database

    Returns:
        True if password matches, False otherwise
    """
    normalized_password = _normalize_password(plain_password)
    return pwd_context.verify(normalized_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash password using bcrypt.

    Automatically handles passwords longer than 72 bytes by using SHA-256
    pre-hashing to avoid bcrypt truncation issues.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    normalized_password = _normalize_password(password)
    return pwd_context.hash(normalized_password)


def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    Validate password strength according to security policy.

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")

    if len(password) > 128:
        errors.append("Password must be less than 128 characters long")

    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")

    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")

    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit")

    # Check for special characters
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        errors.append("Password must contain at least one special character")

    # Check for common patterns
    common_patterns = [
        "password",
        "123456",
        "qwerty",
        "abc123",
        "admin",
        "user",
    ]

    password_lower = password.lower()
    for pattern in common_patterns:
        if pattern in password_lower:
            errors.append(f"Password cannot contain common pattern: {pattern}")

    return len(errors) == 0, errors


def generate_reset_token() -> str:
    """
    Generate secure password reset token.

    Returns:
        Random token for password reset
    """
    import secrets
    return secrets.token_urlsafe(32)


def verify_reset_token(token: str, stored_token: str, expires_at: datetime) -> bool:
    """
    Verify password reset token.

    Args:
        token: Token from user
        stored_token: Token stored in database
        expires_at: Token expiration time

    Returns:
        True if token is valid, False otherwise
    """
    if datetime.now(UTC) > expires_at:
        return False

    return token == stored_token