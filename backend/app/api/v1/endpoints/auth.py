"""
Authentication endpoints.

Endpointy dla autoryzacji i autentykacji z JWT + HttpOnly cookies.
"""

from datetime import timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, Cookie, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user, require_admin
from app.models.user import User, UserRole
from app.services.auth_service import AuthService
from app.schemas.auth_schemas import (
    UserCreate,
    UserUpdate,
    UserLogin,
    LoginResponse,
    UserResponse,
    PasswordChange,
    PasswordReset,
    PasswordResetConfirm,
    UserStats
)
from app.core.config import settings

router = APIRouter()
security = HTTPBearer(auto_error=False)


@router.post("/login", response_model=LoginResponse)
async def login(
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Login user and set HttpOnly cookie with JWT token.

    Accepts both JSON body (Content-Type: application/json) and
    form-data (Content-Type: application/x-www-form-urlencoded).
    """
    auth_service = AuthService(db)

    # Check Content-Type to determine which format was used
    content_type = request.headers.get("content-type", "").lower()

    if "application/json" in content_type:
        # Parse JSON body
        body = await request.json()
        user_login = UserLogin(**body)
    else:
        # Parse form-data
        form = await request.form()
        user_login = UserLogin(
            username=form.get("username"),
            password=form.get("password")
        )

    login_response = await auth_service.login_user(user_login)

    # Set HttpOnly cookie with JWT token
    response.set_cookie(
        key="access_token",
        value=login_response.access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=True,  # Only over HTTPS in production
        samesite="lax"
    )

    return login_response


@router.post("/logout")
async def logout(response: Response):
    """Logout user by clearing the HttpOnly cookie."""
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="lax"
    )
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information."""
    return UserResponse.model_validate(current_user)


@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Register new user (admin only)."""
    auth_service = AuthService(db)
    return await auth_service.create_user(user_data, current_user)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user information."""
    auth_service = AuthService(db)
    return await auth_service.update_user(user_id, user_data, current_user)


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Change user password."""
    auth_service = AuthService(db)
    return await auth_service.change_password(current_user.id, password_data)


@router.post("/request-password-reset")
async def request_password_reset(
    reset_data: PasswordReset,
    db: AsyncSession = Depends(get_db)
):
    """Request password reset via email."""
    auth_service = AuthService(db)
    return await auth_service.request_password_reset(reset_data)


@router.post("/confirm-password-reset")
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """Confirm password reset with token."""
    auth_service = AuthService(db)
    return await auth_service.confirm_password_reset(reset_data)


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[UserRole] = None,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """List users (admin only)."""
    auth_service = AuthService(db)
    return await auth_service.list_users(
        skip=skip,
        limit=limit,
        role_filter=role,
        active_only=active_only
    )


@router.get("/stats", response_model=UserStats)
async def get_user_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get user statistics (admin only)."""
    auth_service = AuthService(db)
    return await auth_service.get_user_stats()


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user by ID."""
    # Users can view their own profile, admins can view any profile
    if user_id != current_user.id and not current_user.can_manage_users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse.model_validate(user)


@router.post("/verify-token")
async def verify_token(
    current_user: User = Depends(get_current_user)
):
    """Verify if current token is valid."""
    return {
        "valid": True,
        "user_id": str(current_user.id),
        "username": current_user.username,
        "role": current_user.role
    }


@router.post("/refresh")
async def refresh_token(
    response: Response,
    current_user: User = Depends(get_current_user)
):
    """Refresh JWT token (re-issue with new expiry)."""
    from app.core.security import create_access_token

    # Create new access token
    additional_claims = {
        "username": current_user.username,
        "role": current_user.role,
        "is_verified": current_user.is_verified
    }

    new_token = create_access_token(
        subject=str(current_user.id),
        additional_claims=additional_claims
    )

    # Set new HttpOnly cookie
    response.set_cookie(
        key="access_token",
        value=new_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=True,
        samesite="lax"
    )

    return {
        "access_token": new_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }