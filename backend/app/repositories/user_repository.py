"""
User repository for database operations.

Repository pattern dla operacji na użytkownikach.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ResourceNotFoundError, ResourceConflictError
from app.models.user import User, UserRole
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model."""

    def __init__(self, session: AsyncSession):
        """Initialize user repository."""
        super().__init__(User, session)

    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.

        Args:
            username: Username to search for

        Returns:
            User if found, None otherwise
        """
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            email: Email to search for

        Returns:
            User if found, None otherwise
        """
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username_or_email(self, identifier: str) -> Optional[User]:
        """
        Get user by username or email.

        Args:
            identifier: Username or email to search for

        Returns:
            User if found, None otherwise
        """
        stmt = select(User).where(
            (User.username == identifier) | (User.email == identifier)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        full_name: Optional[str] = None,
        role: UserRole = UserRole.VIEWER,
        is_active: bool = True,
        is_verified: bool = False,
    ) -> User:
        """
        Create new user.

        Args:
            username: Unique username
            email: Unique email address
            password_hash: Hashed password
            full_name: Optional full name
            role: User role
            is_active: Whether user is active
            is_verified: Whether user is verified

        Returns:
            Created user

        Raises:
            ResourceConflictError: If username or email already exists
        """
        # Check if username already exists
        existing_user = await self.get_by_username(username)
        if existing_user:
            raise ResourceConflictError(f"Username '{username}' already exists")

        # Check if email already exists
        existing_email = await self.get_by_email(email)
        if existing_email:
            raise ResourceConflictError(f"Email '{email}' already exists")

        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            role=role,
            is_active=is_active,
            is_verified=is_verified,
        )

        return await self.create(user)

    async def update_password(self, user_id: UUID, password_hash: str) -> User:
        """
        Update user password.

        Args:
            user_id: User ID
            password_hash: New hashed password

        Returns:
            Updated user

        Raises:
            ResourceNotFoundError: If user not found
        """
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(password_hash=password_hash)
            .returning(User)
        )
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise ResourceNotFoundError("User", str(user_id))

        await self.session.commit()
        return user

    async def update_last_login(self, user_id: UUID) -> User:
        """
        Update user's last login timestamp.

        Args:
            user_id: User ID

        Returns:
            Updated user

        Raises:
            ResourceNotFoundError: If user not found
        """
        from datetime import datetime

        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(last_login=datetime.utcnow())
            .returning(User)
        )
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise ResourceNotFoundError("User", str(user_id))

        await self.session.commit()
        return user

    async def set_reset_token(
        self,
        user_id: UUID,
        reset_token: str,
        expires_at: datetime,
    ) -> User:
        """
        Set password reset token for user.

        Args:
            user_id: User ID
            reset_token: Reset token
            expires_at: Token expiration time

        Returns:
            Updated user

        Raises:
            ResourceNotFoundError: If user not found
        """
        from datetime import datetime

        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(
                reset_token=reset_token,
                reset_token_expires=expires_at,
            )
            .returning(User)
        )
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise ResourceNotFoundError("User", str(user_id))

        await self.session.commit()
        return user

    async def clear_reset_token(self, user_id: UUID) -> User:
        """
        Clear password reset token for user.

        Args:
            user_id: User ID

        Returns:
            Updated user

        Raises:
            ResourceNotFoundError: If user not found
        """
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(
                reset_token=None,
                reset_token_expires=None,
            )
            .returning(User)
        )
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise ResourceNotFoundError("User", str(user_id))

        await self.session.commit()
        return user

    async def get_by_reset_token(self, reset_token: str) -> Optional[User]:
        """
        Get user by reset token.

        Args:
            reset_token: Reset token to search for

        Returns:
            User if found and token not expired, None otherwise
        """
        from datetime import datetime

        stmt = select(User).where(
            and_(
                User.reset_token == reset_token,
                User.reset_token_expires > datetime.utcnow(),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_role(self, role: UserRole) -> List[User]:
        """
        Get all users with specific role.

        Args:
            role: User role to filter by

        Returns:
            List of users with specified role
        """
        stmt = select(User).where(User.role == role).order_by(User.username)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_active_users(self) -> List[User]:
        """
        Get all active users.

        Returns:
            List of active users
        """
        stmt = select(User).where(User.is_active == True).order_by(User.username)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def deactivate_user(self, user_id: UUID) -> User:
        """
        Deactivate user account.

        Args:
            user_id: User ID

        Returns:
            Updated user

        Raises:
            ResourceNotFoundError: If user not found
        """
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(is_active=False)
            .returning(User)
        )
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise ResourceNotFoundError("User", str(user_id))

        await self.session.commit()
        return user

    async def activate_user(self, user_id: UUID) -> User:
        """
        Activate user account.

        Args:
            user_id: User ID

        Returns:
            Updated user

        Raises:
            ResourceNotFoundError: If user not found
        """
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(is_active=True)
            .returning(User)
        )
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise ResourceNotFoundError("User", str(user_id))

        await self.session.commit()
        return user