from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
# from sqlalchemy.ext.asyncio import AsyncSession # 如果您使用 SQLAlchemy
# from src.database.session import get_db # 假設這是您的 DB session 依賴

# 由於您使用 Tortoise ORM，不需要直接的 AsyncSession 依賴給 CRUD，
# Tortoise ORM 的模型方法是異步的。
# 如果您的項目有統一的 DB session 管理（例如用於事務），則可能需要。
# 為了與 pipe_fittings.py 的 CRUD 結構保持一致，這裡不直接注入 db session 到 CRUD。

from src.crud import pf_materials as crud_pf_materials # 更改路徑以匹配您的項目結構
from src.schemas import pf_materials as pf_materials_schemas # 更改路徑

router = APIRouter(
    prefix="/pf_materials",
    tags=["PFMaterials"],   
)

@router.post("/", response_model=pf_materials_schemas.PFMaterialsResponse, status_code=status.HTTP_201_CREATED)
async def create_pf_material(
    material_in: pf_materials_schemas.PFMaterialsCreate,
):
    """
    Create a new PFMaterial.
    """
    return await crud_pf_materials.create_material(material_in=material_in)

@router.get("/", response_model=pf_materials_schemas.PFMaterialsListResponse)
async def read_pf_materials(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(0, ge=0, le=500, description="Maximum number of records to return") # limit=0 for all
):
    """
    Retrieve a list of PFMaterials with pagination.
    Set limit=0 to retrieve all materials (use with caution for large datasets).
    """
    materials = await crud_pf_materials.get_materials(skip=skip, limit=limit)
    total_count = await crud_pf_materials.get_materials_count()
    if limit == 0 and skip == 0: # 如果請求所有，total 就是列表長度
        total_count = len(materials)
    elif limit == 0 and skip > 0: # 如果請求所有但有跳過，total 還是總數
        pass # total_count 已經是總數了

    return pf_materials_schemas.PFMaterialsListResponse(items=materials, total=total_count)

@router.get("/{material_id}", response_model=pf_materials_schemas.PFMaterialsResponse)
async def read_pf_material(
    material_id: int,
):
    """
    Retrieve a specific PFMaterial by its ID.
    """
    db_material = await crud_pf_materials.get_material(material_id=material_id)
    if db_material is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PFMaterials not found")
    return db_material

@router.put("/{material_id}", response_model=pf_materials_schemas.PFMaterialsResponse)
async def update_pf_material(
    material_id: int,
    material_in: pf_materials_schemas.PFMaterialsUpdate,
):
    """
    Update an existing PFMaterials.
    """
    updated_material = await crud_pf_materials.update_material(material_id=material_id, material_in=material_in)
    if updated_material is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PFMaterials not found")
    return updated_material

@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pf_material(
    material_id: int,
):
    """
    Delete a PFMaterials.
    """
    deleted = await crud_pf_materials.delete_material(material_id=material_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PFMaterials not found")
    return None # For 204 No Content