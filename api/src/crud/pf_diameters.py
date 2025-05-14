from typing import List, Optional
from tortoise.exceptions import DoesNotExist, IntegrityError
from fastapi import HTTPException

from src.database.models import PFDiameters # 確保導入正確的模型
from src.schemas.pf_diameters import PFDiameterCreate, PFDiameterUpdate

async def get_diameter(diameter_id: int) -> Optional[PFDiameters]:
    try:
        return await PFDiameters.get(id=diameter_id)
    except DoesNotExist:
        return None

async def get_diameters(skip: int = 0, limit: int = 100) -> List[PFDiameters]:
    if limit == 0: # limit=0 表示獲取所有
        return await PFDiameters.all().offset(skip)
    return await PFDiameters.all().offset(skip).limit(limit)

async def get_diameters_count() -> int:
    return await PFDiameters.all().count()

async def create_diameter(diameter_in: PFDiameterCreate) -> PFDiameters:
    try:
        # 檢查 unique_together 約束: (("name", "value"),)
        existing_diameter = await PFDiameters.filter(name=diameter_in.name, value=diameter_in.value).first()
        if existing_diameter:
            raise HTTPException(status_code=409, detail=f"Diameter with name '{diameter_in.name}' and value '{diameter_in.value}' already exists.")
        
        diameter_obj = await PFDiameters.create(**diameter_in.dict())
        return diameter_obj
    except IntegrityError as e: # 捕獲其他可能的 IntegrityError
        # 這裡的錯誤信息可能需要更通用，因為 unique_together 已經在上面檢查了
        raise HTTPException(status_code=409, detail=f"Could not create diameter due to an integrity constraint: {e}")


async def update_diameter(diameter_id: int, diameter_in: PFDiameterUpdate) -> Optional[PFDiameters]:
    diameter_obj = await get_diameter(diameter_id)
    if not diameter_obj:
        return None

    update_data = diameter_in.dict(exclude_unset=True)

    # 如果要更新 name 或 value，需要檢查新的組合是否會違反 unique_together
    new_name = update_data.get("name", diameter_obj.name)
    new_value = update_data.get("value", diameter_obj.value)

    if (new_name != diameter_obj.name or new_value != diameter_obj.value):
        existing_diameter = await PFDiameters.filter(name=new_name, value=new_value).first()
        if existing_diameter and existing_diameter.id != diameter_id:
            raise HTTPException(status_code=409, detail=f"Diameter with name '{new_name}' and value '{new_value}' already exists.")

    for key, value in update_data.items():
        setattr(diameter_obj, key, value)
    
    try:
        await diameter_obj.save()
        return diameter_obj
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail=f"Update failed due to an integrity constraint: {e}")


async def delete_diameter(diameter_id: int) -> bool:
    diameter_obj = await get_diameter(diameter_id)
    if not diameter_obj:
        return False
    
    # 檢查是否有 PipeFittings 引用此管徑
    # from src.database.models import PipeFittings # 避免循環導入，考慮將此檢查移至 service 層或更謹慎處理
    # related_fittings_count = await PipeFittings.filter(
    #     Q(diameter1_id=diameter_id) | Q(diameter2_id=diameter_id) | Q(diameter3_id=diameter_id)
    # ).count() # 需要 from tortoise.queryset import Q
    # if related_fittings_count > 0:
    #     raise HTTPException(
    #         status_code=409, 
    #         detail=f"Cannot delete diameter {diameter_id} as it is referenced by {related_fittings_count} pipe fittings."
    #     )

    await diameter_obj.delete()
    return True