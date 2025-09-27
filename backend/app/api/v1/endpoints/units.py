"""
Unit conversion endpoints.

Endpointy konwersji jednostek.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db, get_current_admin_user
from app.models.user import User
from app.schemas.import_schemas import UnitConversionCreate, UnitConversionResponse
from app.services.unit_conversion import UnitConversionService, UnitType

router = APIRouter()


@router.post("/convert")
async def convert_value(
    value: float,
    from_unit: str,
    to_unit: str,
    unit_type: UnitType,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Convert a value from one unit to another.

    Returns the converted value.
    """
    try:
        conversion_service = UnitConversionService(db)
        converted_value = await conversion_service.convert_value(
            value, from_unit, to_unit, unit_type
        )

        return {
            "original_value": value,
            "original_unit": from_unit,
            "converted_value": converted_value,
            "converted_unit": to_unit,
            "unit_type": unit_type
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


@router.get("/supported")
async def get_supported_units(
    unit_type: Optional[UnitType] = Query(None, description="Filter by unit type"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get supported units for conversion.

    Returns a dictionary of supported units by type.
    """
    conversion_service = UnitConversionService(db)

    if unit_type:
        units = await conversion_service.get_supported_units(unit_type)
        return {unit_type: units}
    else:
        # Get all unit types
        all_units = {}
        for unit_type_enum in UnitType:
            units = await conversion_service.get_supported_units(unit_type_enum)
            all_units[unit_type_enum.value] = units

        return all_units


@router.get("/examples")
async def get_conversion_examples(
    current_user: User = Depends(get_current_user)
):
    """
    Get examples of supported conversions.

    Returns conversion examples for documentation purposes.
    """
    conversion_service = UnitConversionService(None)  # No DB needed for examples
    return conversion_service.get_conversion_examples()


@router.post("/rules", response_model=UnitConversionResponse)
async def create_conversion_rule(
    rule_data: UnitConversionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new unit conversion rule.

    Only administrators can create custom conversion rules.
    """
    try:
        conversion_service = UnitConversionService(db)
        rule = await conversion_service.create_conversion_rule(rule_data)

        return UnitConversionResponse(
            id=rule.id,
            from_unit=rule.from_unit,
            to_unit=rule.to_unit,
            conversion_factor=rule.conversion_factor,
            conversion_offset=rule.conversion_offset,
            unit_type=rule.unit_type,
            description=rule.description,
            is_active=rule.is_active,
            created_at=rule.created_at,
            updated_at=rule.updated_at
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create conversion rule: {str(e)}")


@router.get("/rules", response_model=List[UnitConversionResponse])
async def get_conversion_rules(
    unit_type: Optional[UnitType] = Query(None, description="Filter by unit type"),
    is_active: bool = Query(True, description="Filter by active status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get conversion rules from database.

    Returns custom conversion rules that have been created.
    """
    conversion_service = UnitConversionService(db)
    rules = await conversion_service.get_conversion_rules(unit_type, is_active)

    return [
        UnitConversionResponse(
            id=rule.id,
            from_unit=rule.from_unit,
            to_unit=rule.to_unit,
            conversion_factor=rule.conversion_factor,
            conversion_offset=rule.conversion_offset,
            unit_type=rule.unit_type,
            description=rule.description,
            is_active=rule.is_active,
            created_at=rule.created_at,
            updated_at=rule.updated_at
        )
        for rule in rules
    ]


@router.put("/rules/{rule_id}", response_model=UnitConversionResponse)
async def update_conversion_rule(
    rule_id: str,
    is_active: bool,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update a conversion rule (enable/disable).

    Only administrators can update conversion rules.
    """
    from sqlalchemy import select, update
    from app.models.import_job import UnitConversion

    # Check if rule exists
    result = await db.execute(select(UnitConversion).where(UnitConversion.id == rule_id))
    rule = result.scalar_one_or_none()

    if not rule:
        raise HTTPException(status_code=404, detail="Conversion rule not found")

    # Update rule
    await db.execute(
        update(UnitConversion)
        .where(UnitConversion.id == rule_id)
        .values(is_active=is_active)
    )
    await db.commit()
    await db.refresh(rule)

    return UnitConversionResponse(
        id=rule.id,
        from_unit=rule.from_unit,
        to_unit=rule.to_unit,
        conversion_factor=rule.conversion_factor,
        conversion_offset=rule.conversion_offset,
        unit_type=rule.unit_type,
        description=rule.description,
        is_active=rule.is_active,
        created_at=rule.created_at,
        updated_at=rule.updated_at
    )


@router.post("/batch-convert")
async def batch_convert_values(
    conversions: List[Dict[str, Any]],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Convert multiple values in batch.

    Each conversion should have: value, from_unit, to_unit, unit_type
    """
    conversion_service = UnitConversionService(db)
    results = []
    errors = []

    for i, conversion in enumerate(conversions):
        try:
            # Validate required fields
            required_fields = ["value", "from_unit", "to_unit", "unit_type"]
            for field in required_fields:
                if field not in conversion:
                    raise ValueError(f"Missing required field: {field}")

            # Perform conversion
            converted_value = await conversion_service.convert_value(
                conversion["value"],
                conversion["from_unit"],
                conversion["to_unit"],
                UnitType(conversion["unit_type"])
            )

            results.append({
                "index": i,
                "original_value": conversion["value"],
                "original_unit": conversion["from_unit"],
                "converted_value": converted_value,
                "converted_unit": conversion["to_unit"],
                "unit_type": conversion["unit_type"],
                "success": True
            })

        except Exception as e:
            errors.append({
                "index": i,
                "error": str(e),
                "success": False
            })

    return {
        "results": results,
        "errors": errors,
        "total_conversions": len(conversions),
        "successful_conversions": len(results),
        "failed_conversions": len(errors)
    }