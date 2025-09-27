"""
API dependencies for FastAPI endpoints.

Zależności API dla endpointów FastAPI z obsługą JWT HttpOnly cookies.
"""

from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import verify_token
from app.core.config import settings
from app.models.user import User, UserRole


security = HTTPBearer(auto_error=False)


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


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    access_token: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from Bearer token or HttpOnly cookie.

    Args:
        request: FastAPI request object
        credentials: Optional JWT token from Authorization header
        access_token: Optional JWT token from HttpOnly cookie
        db: Database session

    Returns:
        Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = None

    # Try to get token from Authorization header first
    if credentials:
        token = credentials.credentials
    # Fall back to HttpOnly cookie
    elif access_token:
        token = access_token

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify token
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user.

    Args:
        current_user: Current user from get_current_user

    Returns:
        Active user

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current admin user.

    Args:
        current_user: Current user from get_current_user

    Returns:
        Admin user

    Raises:
        HTTPException: If user is not admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def get_current_engineer_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current engineer or admin user.

    Args:
        current_user: Current user from get_current_user

    Returns:
        Engineer or admin user

    Raises:
        HTTPException: If user is not engineer or admin
    """
    if not current_user.can_create_scenarios:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Engineer permissions required"
        )
    return current_user


# Alias for backward compatibility and cleaner naming
require_admin = get_current_admin_user
require_engineer = get_current_engineer_user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if token is provided, otherwise return None.

    Args:
        credentials: Optional JWT token from Authorization header
        db: Database session

    Returns:
        Current user or None if no token provided
    """
    if not credentials:
        return None

    try:
        # Decode JWT token
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None

        # Get user from database
        result = db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user and user.is_active:
            return user

    except (jwt.JWTError, Exception):
        pass

    return None