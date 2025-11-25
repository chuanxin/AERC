from typing import List, Optional, Dict
from tortoise.exceptions import DoesNotExist

from src.database.models import CropCategories, CropNames
from src.schemas.crops import (
    CropCategory as CropCategorySchema,
    CropName as CropNameSchema,
    CropCategoryWithNames
)


async def get_all_crop_categories() -> List[CropCategorySchema]:
    """
    獲取所有作物類別
    """
    return await CropCategories.all()


async def get_crop_category(category_id: int) -> Optional[CropCategorySchema]:
    """
    根據 ID 獲取單一作物類別
    """
    return await CropCategories.get_or_none(id=category_id)


async def get_crop_names_by_category(category_id: int) -> List[CropNameSchema]:
    """
    根據作物類別 ID 獲取該類別下的所有作物名稱
    """
    return await CropNames.filter(category_id=category_id)


async def get_all_crop_names() -> List[CropNameSchema]:
    """
    獲取所有作物名稱
    """
    return await CropNames.all()


async def get_crops_grouped_by_category() -> List[CropCategoryWithNames]:
    """
    獲取作物類別及其對應的作物名稱（層級結構）
    適用於前端一次性獲取所有作物資料
    """
    categories = await CropCategories.all()
    result = []

    for category in categories:
        # 獲取該類別下的所有作物
        crop_names = await CropNames.filter(category_id=category.id)

        # 構建帶有作物名稱的類別對象
        category_data = {
            "id": category.id,
            "name": category.name,
            "crop_names": [
                {"id": crop.id, "name": crop.name, "category_id": crop.category_id}
                for crop in crop_names
            ]
        }
        result.append(CropCategoryWithNames(**category_data))

    return result


async def get_crops_as_dict() -> Dict[str, List[str]]:
    """
    返回作物資料的字典格式（與前端當前格式相容）
    格式：{"類別名稱": ["作物1", "作物2", ...]}
    """
    categories = await CropCategories.all()
    result = {}

    for category in categories:
        crop_names = await CropNames.filter(category_id=category.id)
        result[category.name] = [crop.name for crop in crop_names]

    return result
