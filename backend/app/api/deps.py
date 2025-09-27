"""
Dependency functions for FastAPI routes.

Zależności dla endpointów API, włączając autoryzację i dostęp do bazy danych.
"""

from typing import Generator, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.core.exceptions import AuthenticationError, AuthorizationError


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer credentials
        db: Database session

    Returns:
        Current authenticated user

    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Verify token
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise AuthenticationError("Invalid token")

        # Extract user ID from token
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise AuthenticationError("Invalid token: missing subject")

        try:
            user_id = UUID(user_id_str)
        except ValueError:
            raise AuthenticationError("Invalid token: invalid user ID format")

        # Get user from database
        user_repo = UserRepository(db)
        user = await user_repo.get_by_id(user_id)

        if user is None:
            raise AuthenticationError("User not found")

        if not user.is_active:
            raise AuthenticationError("User account is disabled")

        return user

    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user.

    Args:
        current_user: Current authenticated user

    Returns:
        Active user

    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_role(required_role: UserRole):
    """
    Create dependency that requires specific user role.

    Args:
        required_role: Required user role

    Returns:
        Dependency function
    """
    async def check_role(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if current_user.role != required_role and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user

    return check_role


def require_roles(required_roles: list[UserRole]):
    """
    Create dependency that requires one of the specified roles.

    Args:
        required_roles: List of acceptable user roles

    Returns:
        Dependency function
    """
    async def check_roles(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user

    return check_roles


# Common role dependencies
require_admin = require_role(UserRole.ADMIN)
require_engineer = require_roles([UserRole.ENGINEER, UserRole.ADMIN])
require_any_authenticated = Depends(get_current_active_user)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None.

    Args:
        credentials: Optional HTTP Bearer credentials
        db: Database session

    Returns:
        Current user or None if not authenticated
    """
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


class OwnershipChecker:
    """Helper class for checking resource ownership."""

    def __init__(self, allow_admin: bool = True):
        """
        Initialize ownership checker.

        Args:
            allow_admin: Whether to allow admin users access to all resources
        """
        self.allow_admin = allow_admin

    def check_ownership(
        self,
        resource_owner_id: UUID,
        current_user: User
    ) -> bool:
        """
        Check if user owns the resource or is admin.

        Args:
            resource_owner_id: ID of resource owner
            current_user: Current authenticated user

        Returns:
            True if user has access, False otherwise
        """
        # Admin can access everything (if enabled)
        if self.allow_admin and current_user.role == UserRole.ADMIN:
            return True

        # Owner can access their own resources
        return resource_owner_id == current_user.id

    def require_ownership(self, resource_owner_id: UUID):
        """
        Create dependency that checks resource ownership.

        Args:
            resource_owner_id: ID of resource owner

        Returns:
            Dependency function
        """
        async def check_ownership(
            current_user: User = Depends(get_current_active_user),
        ) -> User:
            if not self.check_ownership(resource_owner_id, current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions to access this resource"
                )
            return current_user

        return check_ownership


# Default ownership checker
ownership_checker = OwnershipChecker()