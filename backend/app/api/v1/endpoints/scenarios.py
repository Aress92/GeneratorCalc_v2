"""
Scenario management endpoints.

Endpointy zarządzania scenariuszami optymalizacji.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_scenarios():
    """List scenarios placeholder."""
    return {"message": "List scenarios - to be implemented"}


@router.post("/")
async def create_scenario():
    """Create scenario placeholder."""
    return {"message": "Create scenario - to be implemented"}