from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from src.crud.irrigation_types import get_irrigation_types, get_irrigation_type, get_irrigation_type_options
from src.schemas.irrigation_types import IrrigationType, IrrigationTypeOptions# Using the Pydantic schema for response

router = APIRouter()

@router.get("/irrigation_types/", response_model=List[IrrigationType], tags=["Irrigation Types"])
async def read_irrigation_types(
    skip: int = Query(0, ge=0, description="Skip the specified number of records."),
    limit: int = Query(100, ge=1, le=200, description="Limit the number of records returned (max 200).")
):
    """
    Retrieve a list of irrigation types with pagination.
    """
    irrigation_types = await get_irrigation_types(skip=skip, limit=limit)
    return irrigation_types

@router.get("/irrigation_types/options", response_model=List[IrrigationTypeOptions])
async def read_irrigation_type_options():
    return await get_irrigation_type_options()

@router.get("/irrigation_types/{irrigation_type_id}", response_model=IrrigationType, tags=["Irrigation Types"])
async def read_irrigation_type(irrigation_type_id: int):
    """
    Retrieve a single irrigation type by its ID.
    """
    db_irrigation_type = await get_irrigation_type(irrigation_type_id=irrigation_type_id)
    if db_irrigation_type is None:
        raise HTTPException(status_code=404, detail="IrrigationType not found")
    return db_irrigation_type
# Since it's read-only, we are not implementing POST, PUT, DELETE endpoints for now.
