from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
# from sqlalchemy.ext.asyncio import AsyncSession # 如果您使用 SQLAlchemy
# from src.database.session import get_db # 假設這是您的 DB session 依賴

# 由於您使用 Tortoise ORM，不需要直接的 AsyncSession 依賴給 CRUD，
# Tortoise ORM 的模型方法是異步的。
# 如果您的項目有統一的 DB session 管理（例如用於事務），則可能需要。
# 為了與 pipe_fittings.py 的 CRUD 結構保持一致，這裡不直接注入 db session 到 CRUD。

from src.crud import pf_modules as crud_pf_modules # 更改路徑以匹配您的項目結構
from src.schemas import pf_modules as pf_module_schemas # 更改路徑

router = APIRouter(
    prefix="/pf_modules", # 或者 "/modules"
    tags=["PFModules"],   # 或者 "Modules"
)

@router.post("/", response_model=pf_module_schemas.PFModulesResponse, status_code=status.HTTP_201_CREATED)
async def create_pf_module(
    module_in: pf_module_schemas.PFModulesCreate,
):
    """
    Create a new PFModules.
    """
    return await crud_pf_modules.create_module(module_in=module_in)

@router.get("/", response_model=pf_module_schemas.PFModulesListResponse)
async def read_pf_modules(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(0, ge=0, le=500, description="Maximum number of records to return") # limit=0 for all
):
    """
    Retrieve a list of PFModules with pagination.
    Set limit=0 to retrieve all modules (use with caution for large datasets).
    """
    modules = await crud_pf_modules.get_modules(skip=skip, limit=limit)
    total_count = await crud_pf_modules.get_modules_count()
    if limit == 0 and skip == 0: # 如果請求所有，total 就是列表長度
        total_count = len(modules)
    elif limit == 0 and skip > 0: # 如果請求所有但有跳過，total 還是總數
        pass # total_count 已經是總數了

    return pf_module_schemas.PFModulesListResponse(items=modules, total=total_count)

@router.get("/{module_id}", response_model=pf_module_schemas.PFModulesResponse)
async def read_pf_module(
    module_id: int,
):
    """
    Retrieve a specific PFModules by its ID.
    """
    db_module = await crud_pf_modules.get_module(module_id=module_id)
    if db_module is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PFModules not found")
    return db_module

@router.put("/{module_id}", response_model=pf_module_schemas.PFModulesResponse)
async def update_pf_module(
    module_id: int,
    module_in: pf_module_schemas.PFModulesUpdate,
):
    """
    Update an existing PFModules.
    """
    updated_module = await crud_pf_modules.update_module(module_id=module_id, module_in=module_in)
    if updated_module is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PFModules not found")
    return updated_module

@router.delete("/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pf_module(
    module_id: int,
):
    """
    Delete a PFModules.
    """
    deleted = await crud_pf_modules.delete_module(module_id=module_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PFModules not found")
    return None # For 204 No Content