from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.crud import pf_modules as crud_pf_modules
from src.schemas import pf_modules as pf_module_schemas
from src.auth.guard import require_full_auth
from src.services.permission_service import permission_service
from src.schemas.permissions import ModuleName, PermissionAction
from src.exceptions import AppError

router = APIRouter(
    prefix="/pf_modules",
    tags=["PFModules"],
)

@router.post("/", response_model=pf_module_schemas.PFModulesResponse, status_code=status.HTTP_201_CREATED)
async def create_pf_module(
    module_in: pf_module_schemas.PFModulesCreate,
    current_user=Depends(require_full_auth),
):
    """Create a new PFModules."""
    allowed, _ = permission_service.check_permission(
        current_user.role, current_user.permissions, ModuleName.MATERIALS, PermissionAction.CREATE
    )
    if not allowed:
        raise AppError(403, "無此操作權限")
    return await crud_pf_modules.create_module(module_in=module_in)

@router.get("/", response_model=pf_module_schemas.PFModulesListResponse)
async def read_pf_modules(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(0, ge=0, le=500, description="Maximum number of records to return")
):
    """Retrieve a list of PFModules with pagination."""
    modules = await crud_pf_modules.get_modules(skip=skip, limit=limit)
    total_count = await crud_pf_modules.get_modules_count()
    if limit == 0 and skip == 0:
        total_count = len(modules)
    return pf_module_schemas.PFModulesListResponse(items=modules, total=total_count)

@router.get("/{module_id}", response_model=pf_module_schemas.PFModulesResponse)
async def read_pf_module(
    module_id: int,
):
    """Retrieve a specific PFModules by its ID."""
    db_module = await crud_pf_modules.get_module(module_id=module_id)
    if db_module is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PFModules not found")
    return db_module

@router.put("/{module_id}", response_model=pf_module_schemas.PFModulesResponse)
async def update_pf_module(
    module_id: int,
    module_in: pf_module_schemas.PFModulesUpdate,
    current_user=Depends(require_full_auth),
):
    """Update an existing PFModules."""
    allowed, _ = permission_service.check_permission(
        current_user.role, current_user.permissions, ModuleName.MATERIALS, PermissionAction.EDIT
    )
    if not allowed:
        raise AppError(403, "無此操作權限")
    updated_module = await crud_pf_modules.update_module(module_id=module_id, module_in=module_in)
    if updated_module is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PFModules not found")
    return updated_module

@router.delete("/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pf_module(
    module_id: int,
    current_user=Depends(require_full_auth),
):
    """Delete a PFModules."""
    allowed, _ = permission_service.check_permission(
        current_user.role, current_user.permissions, ModuleName.MATERIALS, PermissionAction.DELETE
    )
    if not allowed:
        raise AppError(403, "無此操作權限")
    deleted = await crud_pf_modules.delete_module(module_id=module_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PFModules not found")
    return None
