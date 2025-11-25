from typing import List, Dict
from fastapi import APIRouter, HTTPException, status

from src.crud.crops import (
    get_all_crop_categories,
    get_crop_category,
    get_crop_names_by_category,
    get_all_crop_names,
    get_crops_grouped_by_category,
    get_crops_as_dict
)
from src.schemas.crops import (
    CropCategory,
    CropName,
    CropCategoryWithNames
)

router = APIRouter()


@router.get(
    "/crop-categories",
    response_model=List[CropCategory],
    status_code=status.HTTP_200_OK,
    tags=["Crops"]
)
async def read_crop_categories():
    """
    獲取所有作物類別
    """
    return await get_all_crop_categories()


@router.get(
    "/crop-categories/{category_id}",
    response_model=CropCategory,
    status_code=status.HTTP_200_OK,
    tags=["Crops"]
)
async def read_crop_category(category_id: int):
    """
    根據 ID 獲取單一作物類別
    """
    category = await get_crop_category(category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"作物類別 ID {category_id} 不存在"
        )
    return category


@router.get(
    "/crop-names",
    response_model=List[CropName],
    status_code=status.HTTP_200_OK,
    tags=["Crops"]
)
async def read_all_crop_names():
    """
    獲取所有作物名稱
    """
    return await get_all_crop_names()


@router.get(
    "/crop-names/category/{category_id}",
    response_model=List[CropName],
    status_code=status.HTTP_200_OK,
    tags=["Crops"]
)
async def read_crop_names_by_category(category_id: int):
    """
    根據作物類別 ID 獲取該類別下的所有作物名稱
    """
    return await get_crop_names_by_category(category_id)


@router.get(
    "/crops/grouped",
    response_model=List[CropCategoryWithNames],
    status_code=status.HTTP_200_OK,
    tags=["Crops"]
)
async def read_crops_grouped():
    """
    獲取作物類別及其對應的作物名稱（層級結構）
    適用於前端一次性獲取所有作物資料並在本地過濾
    """
    return await get_crops_grouped_by_category()


@router.get(
    "/crops/dict",
    response_model=Dict[str, List[str]],
    status_code=status.HTTP_200_OK,
    tags=["Crops"]
)
async def read_crops_as_dict():
    """
    返回作物資料的字典格式（與前端當前格式相容）
    格式：{"類別名稱": ["作物1", "作物2", ...]}

    這個端點提供了與前端現有硬編碼資料相同的格式，
    便於無縫遷移到資料庫驅動的資料源。
    """
    return await get_crops_as_dict()
