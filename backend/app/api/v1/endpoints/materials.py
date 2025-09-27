"""
Materials management endpoints.

Endpointy zarządzania materiałami.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db, get_current_admin_user
from app.models.user import User
from app.schemas.regenerator_schemas import (
    MaterialCreate, MaterialUpdate, MaterialResponse, MaterialFilter
)
from app.services.materials_service import MaterialsService

router = APIRouter()


@router.post("/", response_model=MaterialResponse)
async def create_material(
    material_data: MaterialCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new material.

    Requires engineer or admin permissions.
    """
    if not current_user.can_create_scenarios:
        raise HTTPException(status_code=403, detail="Engineer permissions required")

    try:
        materials_service = MaterialsService(db)
        material = await materials_service.create_material(material_data, current_user.id)

        return MaterialResponse(
            id=material.id,
            name=material.name,
            description=material.description,
            manufacturer=material.manufacturer,
            material_code=material.material_code,
            material_type=material.material_type,
            category=material.category,
            application=material.application,
            properties=material.properties,
            chemical_composition=material.chemical_composition,
            cost_per_unit=material.cost_per_unit,
            cost_unit=material.cost_unit,
            availability=material.availability,
            version=material.version,
            approval_status=material.approval_status,
            is_active=material.is_active,
            is_standard=material.is_standard,
            created_by_user_id=material.created_by_user_id,
            approved_by_user_id=material.approved_by_user_id,
            approved_at=material.approved_at,
            created_at=material.created_at,
            updated_at=material.updated_at
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create material: {str(e)}")


@router.get("/", response_model=List[MaterialResponse])
async def search_materials(
    search: Optional[str] = Query(None, description="Search term"),
    material_type: Optional[str] = Query(None, description="Filter by material type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    application: Optional[str] = Query(None, description="Filter by application"),
    manufacturer: Optional[str] = Query(None, description="Filter by manufacturer"),
    min_max_temperature: Optional[float] = Query(None, description="Minimum max temperature"),
    max_max_temperature: Optional[float] = Query(None, description="Maximum max temperature"),
    approval_status: Optional[str] = Query(None, description="Filter by approval status"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    is_standard: Optional[bool] = Query(None, description="Filter by standard materials"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search and filter materials.

    Returns paginated list of materials matching the criteria.
    """
    materials_service = MaterialsService(db)

    filters = MaterialFilter(
        search=search,
        material_type=material_type,
        category=category,
        application=application,
        manufacturer=manufacturer,
        min_max_temperature=min_max_temperature,
        max_max_temperature=max_max_temperature,
        approval_status=approval_status,
        is_active=is_active,
        is_standard=is_standard
    )

    materials, total_count = await materials_service.search_materials(filters, limit, offset)

    # Add pagination headers
    response_materials = []
    for material in materials:
        response_materials.append(MaterialResponse(
            id=material.id,
            name=material.name,
            description=material.description,
            manufacturer=material.manufacturer,
            material_code=material.material_code,
            material_type=material.material_type,
            category=material.category,
            application=material.application,
            properties=material.properties,
            chemical_composition=material.chemical_composition,
            cost_per_unit=material.cost_per_unit,
            cost_unit=material.cost_unit,
            availability=material.availability,
            version=material.version,
            approval_status=material.approval_status,
            is_active=material.is_active,
            is_standard=material.is_standard,
            created_by_user_id=material.created_by_user_id,
            approved_by_user_id=material.approved_by_user_id,
            approved_at=material.approved_at,
            created_at=material.created_at,
            updated_at=material.updated_at
        ))

    return response_materials


@router.get("/{material_id}", response_model=MaterialResponse)
async def get_material(
    material_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get material by ID."""
    materials_service = MaterialsService(db)
    material = await materials_service.get_material(material_id)

    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    return MaterialResponse(
        id=material.id,
        name=material.name,
        description=material.description,
        manufacturer=material.manufacturer,
        material_code=material.material_code,
        material_type=material.material_type,
        category=material.category,
        application=material.application,
        properties=material.properties,
        chemical_composition=material.chemical_composition,
        cost_per_unit=material.cost_per_unit,
        cost_unit=material.cost_unit,
        availability=material.availability,
        version=material.version,
        approval_status=material.approval_status,
        is_active=material.is_active,
        is_standard=material.is_standard,
        created_by_user_id=material.created_by_user_id,
        approved_by_user_id=material.approved_by_user_id,
        approved_at=material.approved_at,
        created_at=material.created_at,
        updated_at=material.updated_at
    )


@router.put("/{material_id}", response_model=MaterialResponse)
async def update_material(
    material_id: str,
    material_data: MaterialUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing material.

    Requires engineer or admin permissions.
    """
    if not current_user.can_create_scenarios:
        raise HTTPException(status_code=403, detail="Engineer permissions required")

    materials_service = MaterialsService(db)
    material = await materials_service.update_material(material_id, material_data, current_user.id)

    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    return MaterialResponse(
        id=material.id,
        name=material.name,
        description=material.description,
        manufacturer=material.manufacturer,
        material_code=material.material_code,
        material_type=material.material_type,
        category=material.category,
        application=material.application,
        properties=material.properties,
        chemical_composition=material.chemical_composition,
        cost_per_unit=material.cost_per_unit,
        cost_unit=material.cost_unit,
        availability=material.availability,
        version=material.version,
        approval_status=material.approval_status,
        is_active=material.is_active,
        is_standard=material.is_standard,
        created_by_user_id=material.created_by_user_id,
        approved_by_user_id=material.approved_by_user_id,
        approved_at=material.approved_at,
        created_at=material.created_at,
        updated_at=material.updated_at
    )


@router.delete("/{material_id}")
async def delete_material(
    material_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a material (soft delete).

    Requires engineer or admin permissions.
    """
    if not current_user.can_create_scenarios:
        raise HTTPException(status_code=403, detail="Engineer permissions required")

    materials_service = MaterialsService(db)
    success = await materials_service.delete_material(material_id, current_user.id)

    if not success:
        raise HTTPException(status_code=404, detail="Material not found")

    return {"message": "Material deleted successfully"}


@router.get("/types/{material_type}", response_model=List[MaterialResponse])
async def get_materials_by_type(
    material_type: str,
    is_active: bool = Query(True, description="Filter by active status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get materials by type."""
    materials_service = MaterialsService(db)
    materials = await materials_service.get_materials_by_type(material_type, is_active)

    return [
        MaterialResponse(
            id=material.id,
            name=material.name,
            description=material.description,
            manufacturer=material.manufacturer,
            material_code=material.material_code,
            material_type=material.material_type,
            category=material.category,
            application=material.application,
            properties=material.properties,
            chemical_composition=material.chemical_composition,
            cost_per_unit=material.cost_per_unit,
            cost_unit=material.cost_unit,
            availability=material.availability,
            version=material.version,
            approval_status=material.approval_status,
            is_active=material.is_active,
            is_standard=material.is_standard,
            created_by_user_id=material.created_by_user_id,
            approved_by_user_id=material.approved_by_user_id,
            approved_at=material.approved_at,
            created_at=material.created_at,
            updated_at=material.updated_at
        )
        for material in materials
    ]


@router.get("/popular/standard", response_model=List[MaterialResponse])
async def get_popular_materials(
    limit: int = Query(20, ge=1, le=50, description="Maximum number of results"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get popular/standard materials."""
    materials_service = MaterialsService(db)
    materials = await materials_service.get_popular_materials(limit)

    return [
        MaterialResponse(
            id=material.id,
            name=material.name,
            description=material.description,
            manufacturer=material.manufacturer,
            material_code=material.material_code,
            material_type=material.material_type,
            category=material.category,
            application=material.application,
            properties=material.properties,
            chemical_composition=material.chemical_composition,
            cost_per_unit=material.cost_per_unit,
            cost_unit=material.cost_unit,
            availability=material.availability,
            version=material.version,
            approval_status=material.approval_status,
            is_active=material.is_active,
            is_standard=material.is_standard,
            created_by_user_id=material.created_by_user_id,
            approved_by_user_id=material.approved_by_user_id,
            approved_at=material.approved_at,
            created_at=material.created_at,
            updated_at=material.updated_at
        )
        for material in materials
    ]


@router.post("/{material_id}/approve", response_model=MaterialResponse)
async def approve_material(
    material_id: str,
    approval_status: str = Query(..., pattern="^(approved|rejected)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Approve or reject a material.

    Only administrators can approve materials.
    """
    materials_service = MaterialsService(db)
    material = await materials_service.approve_material(
        material_id, current_user.id, approval_status
    )

    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    return MaterialResponse(
        id=material.id,
        name=material.name,
        description=material.description,
        manufacturer=material.manufacturer,
        material_code=material.material_code,
        material_type=material.material_type,
        category=material.category,
        application=material.application,
        properties=material.properties,
        chemical_composition=material.chemical_composition,
        cost_per_unit=material.cost_per_unit,
        cost_unit=material.cost_unit,
        availability=material.availability,
        version=material.version,
        approval_status=material.approval_status,
        is_active=material.is_active,
        is_standard=material.is_standard,
        created_by_user_id=material.created_by_user_id,
        approved_by_user_id=material.approved_by_user_id,
        approved_at=material.approved_at,
        created_at=material.created_at,
        updated_at=material.updated_at
    )


@router.post("/{material_id}/initialize/standard")
async def initialize_standard_materials(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Initialize standard industry materials.

    Only administrators can initialize standard materials.
    """
    materials_service = MaterialsService(db)
    count = await materials_service.initialize_standard_materials()

    return {
        "message": f"Initialized {count} standard materials",
        "count": count
    }