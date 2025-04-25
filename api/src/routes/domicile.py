from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from src.schemas.domicile import (
    CountySchema, TownSchema, VillageSchema,
    CountyCreateSchema, TownCreateSchema, VillageCreateSchema
)
import src.crud.domicile as crud
from src.auth.jwthandler import get_current_user
from src.schemas.users import UserOutSchema

# router = APIRouter(prefix="/domicile", tags=["domicile"])
router = APIRouter()

# Counties endpoints
@router.get("/counties", response_model=List[CountySchema])
async def get_counties():
    """Get all counties"""
    return await crud.get_counties()

@router.get("/counties/{county_id}", response_model=CountySchema)
async def get_county(county_id: int):
    """Get a county by ID"""
    return await crud.get_county(county_id)

@router.post("/counties", response_model=CountySchema)
async def create_county(
    county: CountyCreateSchema,
    current_user: UserOutSchema = Depends(get_current_user)
):
    """Create a new county (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return await crud.create_county(county.dict())

@router.put("/counties/{county_id}", response_model=CountySchema)
async def update_county(
    county_id: int,
    county: CountyCreateSchema,
    current_user: UserOutSchema = Depends(get_current_user)
):
    """Update a county (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return await crud.update_county(county_id, county.dict())

@router.delete("/counties/{county_id}")
async def delete_county(
    county_id: int,
    current_user: UserOutSchema = Depends(get_current_user)
):
    """Delete a county (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    await crud.delete_county(county_id)
    return {"message": "County deleted successfully"}

# Towns endpoints
@router.get("/towns", response_model=List[TownSchema])
async def get_towns(county_id: Optional[int] = Query(None, description="Filter by county ID")):
    """Get all towns, optionally filtered by county"""
    return await crud.get_towns(county_id)

@router.get("/towns/{town_id}", response_model=TownSchema)
async def get_town(town_id: int):
    """Get a town by ID"""
    return await crud.get_town(town_id)

@router.post("/towns", response_model=TownSchema)
async def create_town(
    town: TownCreateSchema,
    current_user: UserOutSchema = Depends(get_current_user)
):
    """Create a new town (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return await crud.create_town(town.dict())

@router.put("/towns/{town_id}", response_model=TownSchema)
async def update_town(
    town_id: int,
    town: TownCreateSchema,
    current_user: UserOutSchema = Depends(get_current_user)
):
    """Update a town (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return await crud.update_town(town_id, town.dict())

@router.delete("/towns/{town_id}")
async def delete_town(
    town_id: int,
    current_user: UserOutSchema = Depends(get_current_user)
):
    """Delete a town (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    await crud.delete_town(town_id)
    return {"message": "Town deleted successfully"}

# Villages endpoints
@router.get("/villages", response_model=List[VillageSchema])
async def get_villages(town_id: Optional[int] = Query(None, description="Filter by town ID")):
    """Get all villages, optionally filtered by town"""
    return await crud.get_villages(town_id)

@router.get("/villages/{village_id}", response_model=VillageSchema)
async def get_village(village_id: int):
    """Get a village by ID"""
    return await crud.get_village(village_id)

@router.post("/villages", response_model=VillageSchema)
async def create_village(
    village: VillageCreateSchema,
    current_user: UserOutSchema = Depends(get_current_user)
):
    """Create a new village (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return await crud.create_village(village.dict())

@router.put("/villages/{village_id}", response_model=VillageSchema)
async def update_village(
    village_id: int,
    village: VillageCreateSchema,
    current_user: UserOutSchema = Depends(get_current_user)
):
    """Update a village (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return await crud.update_village(village_id, village.dict())

@router.delete("/villages/{village_id}")
async def delete_village(
    village_id: int,
    current_user: UserOutSchema = Depends(get_current_user)
):
    """Delete a village (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    await crud.delete_village(village_id)
    return {"message": "Village deleted successfully"}