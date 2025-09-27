"""
Authentication and user management schemas.

Schematy dla uwierzytelniania i zarządzania użytkownikami.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=200)
    role: UserRole = UserRole.VIEWER


class UserCreate(UserBase):
    """Schema for creating new user."""

    password: str = Field(..., min_length=8, max_length=128)

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens and underscores')
        return v.lower()


class UserUpdate(BaseModel):
    """Schema for updating user."""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=200)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response."""

    id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    """Schema for user login."""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=1, max_length=128)


class LoginResponse(BaseModel):
    """Schema for login response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserResponse


class PasswordChange(BaseModel):
    """Schema for password change."""

    current_password: str = Field(..., min_length=1, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)


class PasswordReset(BaseModel):
    """Schema for password reset request."""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""

    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)


class Token(BaseModel):
    """Schema for JWT token."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token data."""

    user_id: Optional[UUID] = None
    username: Optional[str] = None
    role: Optional[UserRole] = None


class UserSession(BaseModel):
    """Schema for user session info."""

    user_id: UUID
    username: str
    role: UserRole
    session_id: str
    created_at: datetime
    last_activity: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogEntry(BaseModel):
    """Schema for audit log entry."""

    id: UUID
    user_id: Optional[UUID]
    username: Optional[str]
    action: str
    resource: str
    resource_id: Optional[str]
    details: Optional[dict]
    ip_address: Optional[str]
    user_agent: Optional[str]
    timestamp: datetime
    status: str  # success, failed, error

    model_config = {"from_attributes": True}


class UserActivity(BaseModel):
    """Schema for user activity summary."""

    total_logins: int
    successful_logins: int
    failed_logins: int
    last_login: Optional[datetime]
    last_failed_login: Optional[datetime]
    active_sessions: int
    total_actions: int


class UserStats(BaseModel):
    """Schema for user statistics."""

    total_users: int
    active_users: int
    verified_users: int
    admin_users: int
    engineer_users: int
    viewer_users: int
    recent_registrations: int  # last 30 days
    recent_logins: int  # last 24 hours