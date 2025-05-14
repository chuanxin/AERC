from typing import List, Optional
from tortoise.exceptions import DoesNotExist, IntegrityError
from fastapi import HTTPException

from src.database.models import PFModules # 假設您的模型在這裡
from src.schemas.pf_modules import PFModulesCreate, PFModulesUpdate

async def get_module(module_id: int) -> Optional[PFModules]:
    try:
        return await PFModules.get(id=module_id)
    except DoesNotExist:
        return None

async def get_modules(skip: int = 0, limit: int = 100) -> List[PFModules]:
    if limit == 0: # limit=0 表示獲取所有，這在字典表中可能有用
        return await PFModules.all().offset(skip)
    return await PFModules.all().offset(skip).limit(limit)

async def get_modules_count() -> int:
    return await PFModules.all().count()

async def create_module(module_in: PFModulesCreate) -> PFModules:
    try:
        module_obj = await PFModules.create(**module_in.dict())
        return module_obj
    except IntegrityError: # 通常是因為 name 字段的 unique 約束
        raise HTTPException(status_code=409, detail=f"Module with name '{module_in.name}' already exists.")

async def update_module(module_id: int, module_in: PFModulesUpdate) -> Optional[PFModules]:
    module_obj = await get_module(module_id)
    if not module_obj:
        return None

    update_data = module_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(module_obj, key, value)
    
    try:
        await module_obj.save()
        return module_obj
    except IntegrityError:
        # 確保如果 name 是 unique 的，這裡能正確處理
        # 這裡的 detail 信息可能需要根據實際的 unique 字段調整
        updated_name = update_data.get("name")
        if updated_name:
             raise HTTPException(status_code=409, detail=f"Module with name '{updated_name}' already exists.")
        else:
            raise HTTPException(status_code=409, detail="Update failed due to an integrity constraint.")


async def delete_module(module_id: int) -> bool:
    module_obj = await get_module(module_id)
    if not module_obj:
        return False
    
    # 考慮：如果 PFModules 被其他表（如 PipeFittings）引用，直接刪除可能會失敗
    # 您可能需要檢查是否存在關聯的 PipeFittings，或者設置級聯刪除/置空策略
    # 例如:
    # from src.database.models import PipeFittings
    # related_fittings_count = await PipeFittings.filter(module_id=module_id).count()
    # if related_fittings_count > 0:
    #     raise HTTPException(
    #         status_code=409, 
    #         detail=f"Cannot delete module {module_id} as it is referenced by {related_fittings_count} pipe fittings."
    #     )

    await module_obj.delete()
    return True