from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.crud import pf_diameters as crud_pf_diameters
from src.schemas import pf_diameters as pf_diameter_schemas

router = APIRouter(
    prefix="/pf_diameters", # 或者 "/diameters"
    tags=["PFDiameters"],   # 或者 "Diameters"
)

@router.post("/", response_model=pf_diameter_schemas.PFDiametersResponse, status_code=status.HTTP_201_CREATED)
async def create_pf_diameter(
    diameter_in: pf_diameter_schemas.PFDiameterCreate,
):
    """
    Create a new PFDiameter.
    """
    return await crud_pf_diameters.create_diameter(diameter_in=diameter_in)

@router.get("/", response_model=pf_diameter_schemas.PFDiametersListResponse)
async def read_pf_diameters(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(0, ge=0, le=500, description="Maximum number of records to return (0 for all)")
):
    """
    Retrieve a list of PFDiameters with pagination.
    Set limit=0 to retrieve all diameters (use with caution for large datasets).
    """
    diameter_orm_objects = await crud_pf_diameters.get_diameters(skip=skip, limit=limit)
    total_count = await crud_pf_diameters.get_diameters_count()
    
    diameter_responses = [pf_diameter_schemas.PFDiametersResponse.from_orm(orm_obj) for orm_obj in diameter_orm_objects]

    if limit == 0 and skip == 0:
        total_count = len(diameter_responses)
    
    return pf_diameter_schemas.PFDiametersListResponse(items=diameter_responses, total=total_count)

@router.get("/{diameter_id}", response_model=pf_diameter_schemas.PFDiametersResponse)
async def read_pf_diameter(
    diameter_id: int,
):
    """
    Retrieve a specific PFDiameter by its ID.
    """
    db_diameter = await crud_pf_diameters.get_diameter(diameter_id=diameter_id)
    if db_diameter is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PFDiameter not found")
    return db_diameter # FastAPI 會自動使用 from_orm 因為 response_model 和 from_attributes=True

@router.put("/{diameter_id}", response_model=pf_diameter_schemas.PFDiametersResponse)
async def update_pf_diameter(
    diameter_id: int,
    diameter_in: pf_diameter_schemas.PFDiameterUpdate,
):
    """
    Update an existing PFDiameter.
    """
    updated_diameter = await crud_pf_diameters.update_diameter(diameter_id=diameter_id, diameter_in=diameter_in)
    if updated_diameter is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PFDiameter not found")
    return updated_diameter

@router.delete("/{diameter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pf_diameter(
    diameter_id: int,
):
    """
    Delete a PFDiameter.
    """
    deleted = await crud_pf_diameters.delete_diameter(diameter_id=diameter_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PFDiameter not found")
    return None