"""
User management endpoints.

Endpointy zarządzania użytkownikami.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/me")
async def get_current_user():
    """Get current user placeholder."""
    return {"message": "Get current user - to be implemented"}


@router.get("/")
async def list_users():
    """List users placeholder."""
    return {"message": "List users - to be implemented"}