import logging
from typing import List, Optional
from tortoise.exceptions import DoesNotExist, IntegrityError
from fastapi import HTTPException

from src.database.models import PFMaterials # 假設您的模型在這裡
from src.schemas.pf_materials import PFMaterialsCreate, PFMaterialsUpdate

logger = logging.getLogger(__name__)

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
    except IntegrityError as e:
        # PFMaterials 僅 name 欄位為 unique；若非此欄位衝突（如 PK 序列問題），log 保留診斷
        logger.warning("[create_material] IntegrityError（name=%s）：%s", material_in.name, str(e))
        raise HTTPException(status_code=409, detail="管件材質名稱已存在")

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
    except IntegrityError as e:
        logger.warning("[update_material] IntegrityError（id=%s）：%s", material_id, str(e))
        raise HTTPException(status_code=409, detail="管件材質名稱已存在")


async def delete_material(material_id: int) -> bool:
    material_obj = await get_material(material_id)
    if not material_obj:
        return False

    await material_obj.delete()
    return True