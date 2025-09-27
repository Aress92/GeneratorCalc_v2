"""
Regenerator management endpoints.

Endpointy zarządzania regeneratorami.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.regenerator import RegeneratorConfiguration, RegeneratorType, ConfigurationStatus
from app.schemas.regenerator_schemas import RegeneratorConfigurationCreate, RegeneratorConfigurationResponse
from app.services.regenerator_service import RegeneratorService

router = APIRouter()


@router.get("/", response_model=List[RegeneratorConfigurationResponse])
async def list_regenerators(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    List user's regenerator configurations.
    """
    try:
        regenerator_service = RegeneratorService(db)
        regenerators = await regenerator_service.list_user_regenerators(
            user_id=current_user.id,
            skip=skip,
            limit=limit
        )

        return [RegeneratorConfigurationResponse.model_validate(reg) for reg in regenerators]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list regenerators: {str(e)}")


@router.post("/", response_model=RegeneratorConfigurationResponse)
async def create_regenerator(
    regenerator_data: RegeneratorConfigurationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new regenerator configuration.

    Requires engineer or admin permissions.
    """
    # Check permissions
    if current_user.role not in ['ADMIN', 'ENGINEER']:
        raise HTTPException(status_code=403, detail="Engineer permissions required")

    try:
        regenerator_service = RegeneratorService(db)
        regenerator = await regenerator_service.create_regenerator(
            regenerator_data=regenerator_data,
            user_id=current_user.id
        )

        return RegeneratorConfigurationResponse.model_validate(regenerator)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create regenerator: {str(e)}")


@router.get("/{regenerator_id}", response_model=RegeneratorConfigurationResponse)
async def get_regenerator(
    regenerator_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get regenerator configuration by ID.
    """
    try:
        regenerator_service = RegeneratorService(db)
        regenerator = await regenerator_service.get_regenerator(
            regenerator_id=regenerator_id,
            user_id=current_user.id
        )

        if not regenerator:
            raise HTTPException(status_code=404, detail="Regenerator not found")

        return RegeneratorConfigurationResponse.model_validate(regenerator)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get regenerator: {str(e)}")


@router.put("/{regenerator_id}", response_model=RegeneratorConfigurationResponse)
async def update_regenerator(
    regenerator_id: str,
    regenerator_data: RegeneratorConfigurationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update regenerator configuration.
    """
    if current_user.role not in ['ADMIN', 'ENGINEER']:
        raise HTTPException(status_code=403, detail="Engineer permissions required")

    try:
        regenerator_service = RegeneratorService(db)
        regenerator = await regenerator_service.update_regenerator(
            regenerator_id=regenerator_id,
            regenerator_data=regenerator_data,
            user_id=current_user.id
        )

        if not regenerator:
            raise HTTPException(status_code=404, detail="Regenerator not found")

        return RegeneratorConfigurationResponse.model_validate(regenerator)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update regenerator: {str(e)}")


@router.delete("/{regenerator_id}")
async def delete_regenerator(
    regenerator_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete regenerator configuration.
    """
    if current_user.role not in ['ADMIN', 'ENGINEER']:
        raise HTTPException(status_code=403, detail="Engineer permissions required")

    try:
        regenerator_service = RegeneratorService(db)
        success = await regenerator_service.delete_regenerator(
            regenerator_id=regenerator_id,
            user_id=current_user.id
        )

        if not success:
            raise HTTPException(status_code=404, detail="Regenerator not found")

        return {"message": "Regenerator deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete regenerator: {str(e)}")