from typing import List, Optional
from pydantic import BaseModel


class CropCategoryBase(BaseModel):
    """作物類別基礎 Schema"""
    name: str


class CropCategory(CropCategoryBase):
    """作物類別輸出 Schema"""
    id: int

    class Config:
        from_attributes = True


class CropNameBase(BaseModel):
    """作物名稱基礎 Schema"""
    name: str
    category_id: int


class CropName(CropNameBase):
    """作物名稱輸出 Schema"""
    id: int

    class Config:
        from_attributes = True


class CropNameWithCategory(CropName):
    """作物名稱（含類別資訊）Schema"""
    category: CropCategory

    class Config:
        from_attributes = True


class CropCategoryWithNames(CropCategory):
    """作物類別（含作物名稱列表）Schema - 用於層級結構返回"""
    crop_names: List[CropName] = []

    class Config:
        from_attributes = True
