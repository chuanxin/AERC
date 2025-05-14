from typing import List, Optional
from tortoise.exceptions import DoesNotExist, IntegrityError
from fastapi import HTTPException

from src.database.models import PFMaterials # 假設您的模型在這裡
from src.schemas.pf_materials import PFMaterialsCreate, PFMaterialsUpdate

async def get_material(material_id: int) -> Optional[PFMaterials]:
    try:
        return await PFMaterials.get(id=material_id)
    except DoesNotExist:
        return None

async def get_materials(skip: int = 0, limit: int = 100) -> List[PFMaterials]:
    if limit == 0: # limit=0 表示獲取所有，這在字典表中可能有用
        return await PFMaterials.all().offset(skip)
    return await PFMaterials.all().offset(skip).limit(limit)

async def get_materials_count() -> int:
    return await PFMaterials.all().count()

async def create_material(material_in: PFMaterialsCreate) -> PFMaterials:
    try:
        material_obj = await PFMaterials.create(**material_in.dict())
        return material_obj
    except IntegrityError: # 通常是因為 name 字段的 unique 約束
        raise HTTPException(status_code=409, detail=f"Material with name '{material_in.name}' already exists.")

async def update_material(material_id: int, material_in: PFMaterialsUpdate) -> Optional[PFMaterials]:
    material_obj = await get_material(material_id)
    if not material_obj:
        return None

    update_data = material_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(material_obj, key, value)
    
    try:
        await material_obj.save()
        return material_obj
    except IntegrityError:
        # 確保如果 name 是 unique 的，這裡能正確處理
        # 這裡的 detail 信息可能需要根據實際的 unique 字段調整
        updated_name = update_data.get("name")
        if updated_name:
             raise HTTPException(status_code=409, detail=f"Material with name '{updated_name}' already exists.")
        else:
            raise HTTPException(status_code=409, detail="Update failed due to an integrity constraint.")


async def delete_material(material_id: int) -> bool:
    material_obj = await get_material(material_id)
    if not material_obj:
        return False

    await material_obj.delete()
    return True