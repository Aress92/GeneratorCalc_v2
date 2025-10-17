"""
Authentication service for user management and JWT operations.

Serwis uwierzytelniania z obsługą JWT i zarządzaniem sesją.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, func
from fastapi import HTTPException, status

from app.models.user import User, UserRole
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    validate_password_strength,
    generate_reset_token,
    verify_reset_token
)
from app.schemas.auth_schemas import (
    UserCreate,
    UserUpdate,
    UserLogin,
    LoginResponse,
    UserResponse,
    PasswordChange,
    PasswordReset,
    PasswordResetConfirm,
    TokenData,
    UserStats,
    UserActivity
)
from app.core.config import settings


class AuthService:
    """Authentication and user management service."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(
        self,
        user_data: UserCreate,
        created_by: Optional[User] = None
    ) -> UserResponse:
        """
        Create new user account.

        Args:
            user_data: User creation data
            created_by: User who created this account (for admin operations)

        Returns:
            Created user information

        Raises:
            HTTPException: If user already exists or validation fails
        """
        # Check if user already exists
        existing_user = await self.get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        existing_email = await self.get_user_by_email(user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Validate password strength
        is_valid, errors = validate_password_strength(user_data.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation failed: {'; '.join(errors)}"
            )

        # Hash password
        password_hash = get_password_hash(user_data.password)

        # Create user
        user = User(
            username=user_data.username.lower(),
            email=user_data.email.lower(),
            full_name=user_data.full_name,
            password_hash=password_hash,
            role=user_data.role,
            is_active=True,
            is_verified=False  # Admin needs to verify users
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return UserResponse.model_validate(user)

    async def authenticate_user(self, login_data: UserLogin) -> Optional[User]:
        """
        Authenticate user credentials.

        Args:
            login_data: User login credentials

        Returns:
            User object if credentials are valid, None otherwise
        """
        user = await self.get_user_by_username(login_data.username)
        if not user:
            return None

        if not user.is_active:
            return None

        if not verify_password(login_data.password, user.password_hash):
            return None

        # Update last login
        await self.db.execute(
            update(User)
            .where(User.id == user.id)
            .values(last_login=datetime.utcnow())
        )
        await self.db.commit()

        return user

    async def login_user(self, login_data: UserLogin) -> LoginResponse:
        """
        Login user and create access token.

        Args:
            login_data: User login credentials

        Returns:
            Login response with JWT token

        Raises:
            HTTPException: If credentials are invalid
        """
        user = await self.authenticate_user(login_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create access token with user info
        additional_claims = {
            "username": user.username,
            "role": user.role,
            "is_verified": user.is_verified
        }

        access_token = create_access_token(
            subject=str(user.id),
            additional_claims=additional_claims
        )

        # Refresh user to ensure all attributes are loaded
        await self.db.refresh(user)

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user)
        )

    async def get_current_user(self, token: str) -> User:
        """
        Get current user from JWT token.

        Args:
            token: JWT access token

        Returns:
            Current user

        Raises:
            HTTPException: If token is invalid or user not found
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        payload = verify_token(token)
        if payload is None:
            raise credentials_exception

        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        try:
            user_uuid = UUID(user_id)
        except ValueError:
            raise credentials_exception

        user = await self.get_user_by_id(user_uuid)
        if user is None:
            raise credentials_exception

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated"
            )

        return user

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        result = await self.db.execute(
            select(User).where(User.username == username.lower())
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def update_user(
        self,
        user_id: UUID,
        user_data: UserUpdate,
        current_user: User
    ) -> UserResponse:
        """
        Update user information.

        Args:
            user_id: ID of user to update
            user_data: Update data
            current_user: User performing the update

        Returns:
            Updated user information

        Raises:
            HTTPException: If user not found or permission denied
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Permission check
        if user_id != current_user.id and not current_user.can_manage_users:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

        # Only admins can change roles
        if user_data.role is not None and not current_user.can_manage_users:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can change user roles"
            )

        # Update user fields
        update_data = user_data.model_dump(exclude_unset=True)
        if update_data:
            if "email" in update_data:
                update_data["email"] = update_data["email"].lower()

            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(**update_data, updated_at=datetime.utcnow())
            )
            await self.db.commit()
            await self.db.refresh(user)

        return UserResponse.model_validate(user)

    async def change_password(
        self,
        user_id: UUID,
        password_data: PasswordChange
    ) -> dict:
        """
        Change user password.

        Args:
            user_id: User ID
            password_data: Password change data

        Returns:
            Success message

        Raises:
            HTTPException: If current password is wrong or new password is invalid
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Verify current password
        if not verify_password(password_data.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Validate new password
        is_valid, errors = validate_password_strength(password_data.new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"New password validation failed: {'; '.join(errors)}"
            )

        # Hash and update password
        password_hash = get_password_hash(password_data.new_password)
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                password_hash=password_hash,
                updated_at=datetime.utcnow()
            )
        )
        await self.db.commit()

        return {"message": "Password changed successfully"}

    async def request_password_reset(self, reset_data: PasswordReset) -> dict:
        """
        Request password reset for user.

        Args:
            reset_data: Password reset request data

        Returns:
            Success message
        """
        user = await self.get_user_by_email(reset_data.email)
        if not user:
            # Don't reveal if email exists
            return {"message": "If email exists, password reset instructions have been sent"}

        # Generate reset token
        reset_token = generate_reset_token()
        expires_at = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry

        await self.db.execute(
            update(User)
            .where(User.id == user.id)
            .values(
                reset_token=reset_token,
                reset_token_expires=expires_at,
                updated_at=datetime.utcnow()
            )
        )
        await self.db.commit()

        # TODO: Send email with reset link
        # send_password_reset_email(user.email, reset_token)

        return {"message": "If email exists, password reset instructions have been sent"}

    async def confirm_password_reset(self, reset_data: PasswordResetConfirm) -> dict:
        """
        Confirm password reset with token.

        Args:
            reset_data: Password reset confirmation data

        Returns:
            Success message

        Raises:
            HTTPException: If token is invalid or expired
        """
        # Find user with reset token
        result = await self.db.execute(
            select(User).where(User.reset_token == reset_data.token)
        )
        user = result.scalar_one_or_none()

        if not user or not user.reset_token_expires:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )

        # Verify token
        if not verify_reset_token(
            reset_data.token,
            user.reset_token,
            user.reset_token_expires
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )

        # Validate new password
        is_valid, errors = validate_password_strength(reset_data.new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation failed: {'; '.join(errors)}"
            )

        # Update password and clear reset token
        password_hash = get_password_hash(reset_data.new_password)
        await self.db.execute(
            update(User)
            .where(User.id == user.id)
            .values(
                password_hash=password_hash,
                reset_token=None,
                reset_token_expires=None,
                updated_at=datetime.utcnow()
            )
        )
        await self.db.commit()

        return {"message": "Password reset successfully"}

    async def get_user_stats(self) -> UserStats:
        """Get user statistics for admin dashboard."""
        # Total users
        total_result = await self.db.execute(select(func.count(User.id)))
        total_users = total_result.scalar()

        # Active users
        active_result = await self.db.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        active_users = active_result.scalar()

        # Verified users
        verified_result = await self.db.execute(
            select(func.count(User.id)).where(User.is_verified == True)
        )
        verified_users = verified_result.scalar()

        # Users by role
        admin_result = await self.db.execute(
            select(func.count(User.id)).where(User.role == UserRole.ADMIN)
        )
        admin_users = admin_result.scalar()

        engineer_result = await self.db.execute(
            select(func.count(User.id)).where(User.role == UserRole.ENGINEER)
        )
        engineer_users = engineer_result.scalar()

        viewer_result = await self.db.execute(
            select(func.count(User.id)).where(User.role == UserRole.VIEWER)
        )
        viewer_users = viewer_result.scalar()

        # Recent registrations (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_reg_result = await self.db.execute(
            select(func.count(User.id)).where(User.created_at >= thirty_days_ago)
        )
        recent_registrations = recent_reg_result.scalar()

        # Recent logins (last 24 hours)
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        recent_login_result = await self.db.execute(
            select(func.count(User.id)).where(User.last_login >= twenty_four_hours_ago)
        )
        recent_logins = recent_login_result.scalar()

        return UserStats(
            total_users=total_users or 0,
            active_users=active_users or 0,
            verified_users=verified_users or 0,
            admin_users=admin_users or 0,
            engineer_users=engineer_users or 0,
            viewer_users=viewer_users or 0,
            recent_registrations=recent_registrations or 0,
            recent_logins=recent_logins or 0
        )

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        role_filter: Optional[UserRole] = None,
        active_only: bool = True
    ) -> List[UserResponse]:
        """
        List users with filtering and pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            role_filter: Filter by user role
            active_only: Only return active users

        Returns:
            List of user responses
        """
        query = select(User)

        if active_only:
            query = query.where(User.is_active == True)

        if role_filter:
            query = query.where(User.role == role_filter)

        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())

        result = await self.db.execute(query)
        users = result.scalars().all()

        return [UserResponse.model_validate(user) for user in users]