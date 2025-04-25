from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from tortoise.exceptions import DoesNotExist

from src.database.models import Counties, Towns, Villages

# Counties CRUD
async def get_counties() -> List[Counties]:
    """Get all counties"""
    return await Counties.all()

async def get_county(county_id: int) -> Counties:
    """Get county by ID"""
    try:
        return await Counties.get(id=county_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="County not found")

async def create_county(data: Dict[str, Any]) -> Counties:
    """Create new county"""
    return await Counties.create(**data)

async def update_county(county_id: int, data: Dict[str, Any]) -> Counties:
    """Update county"""
    county = await get_county(county_id)
    for key, value in data.items():
        setattr(county, key, value)
    await county.save()
    return county

async def delete_county(county_id: int) -> None:
    """Delete county"""
    county = await get_county(county_id)
    await county.delete()

# Towns CRUD
async def get_towns(county_id: Optional[int] = None) -> List[Towns]:
    """Get all towns, optionally filtered by county"""
    query = Towns.all().prefetch_related("county")
    
    if county_id:
        query = query.filter(county_id=county_id)
    
    towns = await query
    
    # Convert to our schema format
    result = []
    for town in towns:
        town_dict = {
            "id": town.id,
            "name": town.name,
            "code": town.code,
            "is_indigenous": town.is_indigenous,
            "indigenous_type": town.indigenous_type,
            "county_id": town.county_id,
            "county_name": town.county.name if town.county else None
        }
        result.append(town_dict)
    
    return result

async def get_town(town_id: int) -> Towns:
    """Get town by ID"""
    try:
        return await Towns.get(id=town_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Town not found")

async def create_town(data: Dict[str, Any]) -> Towns:
    """Create new town"""
    # Verify county exists
    if "county_id" in data:
        await get_county(data["county_id"])
    return await Towns.create(**data)

async def update_town(town_id: int, data: Dict[str, Any]) -> Towns:
    """Update town"""
    town = await get_town(town_id)
    # Verify county exists if changing
    if "county_id" in data:
        await get_county(data["county_id"])
    for key, value in data.items():
        setattr(town, key, value)
    await town.save()
    return town

async def delete_town(town_id: int) -> None:
    """Delete town"""
    town = await get_town(town_id)
    await town.delete()

# Villages CRUD
async def get_villages(town_id: Optional[int] = None) -> List[dict]:
    """Get all villages, optionally filtered by town"""
    query = Villages.all().prefetch_related("town__county")
    
    if town_id:
        query = query.filter(town_id=town_id)
    
    villages = await query
    
    # Convert to our schema format
    result = []
    for village in villages:
        village_dict = {
            "id": village.id,
            "name": village.name,
            "code": village.code,
            "town_id": village.town_id,
            "town_name": village.town.name if village.town else None,
            "county_id": village.town.county_id if village.town else None,
            "county_name": village.town.county.name if village.town and village.town.county else None
        }
        result.append(village_dict)
    
    return result

async def get_village(village_id: int) -> Villages:
    """Get village by ID"""
    try:
        return await Villages.get(id=village_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Village not found")

async def create_village(data: Dict[str, Any]) -> Villages:
    """Create new village"""
    # Verify town exists
    if "town_id" in data:
        await get_town(data["town_id"])
    return await Villages.create(**data)

async def update_village(village_id: int, data: Dict[str, Any]) -> Villages:
    """Update village"""
    village = await get_village(village_id)
    # Verify town exists if changing
    if "town_id" in data:
        await get_town(data["town_id"])
    for key, value in data.items():
        setattr(village, key, value)
    await village.save()
    return village

async def delete_village(village_id: int) -> None:
    """Delete village"""
    village = await get_village(village_id)
    await village.delete()