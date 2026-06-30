from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.crud import pf_materials as crud_pf_materials
from src.schemas import pf_materials as pf_materials_schemas
from src.auth.guard import require_full_auth
from src.services.permission_service import permission_service
from src.schemas.permissions import ModuleName, PermissionAction
from src.exceptions import AppError

router = APIRouter(
    prefix="/pf_materials",
    tags=["PFMaterials"],   
)

@router.post("/", response_model=pf_materials_schemas.PFMaterialsResponse, status_code=status.HTTP_201_CREATED)
async def create_pf_material(
    material_in: pf_materials_schemas.PFMaterialsCreate,
    current_user=Depends(require_full_auth),
):
    """Create a new PFMaterial."""
    allowed, _ = permission_service.check_permission(
        current_user.role, current_user.permissions, ModuleName.MATERIALS, PermissionAction.CREATE
    )
    if not allowed:
        raise AppError(403, "無此操作權限")
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
    current_user=Depends(require_full_auth),
):
    """Update an existing PFMaterials."""
    allowed, _ = permission_service.check_permission(
        current_user.role, current_user.permissions, ModuleName.MATERIALS, PermissionAction.EDIT
    )
    if not allowed:
        raise AppError(403, "無此操作權限")
    updated_material = await crud_pf_materials.update_material(material_id=material_id, material_in=material_in)
    if updated_material is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PFMaterials not found")
    return updated_material


@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pf_material(
    material_id: int,
    current_user=Depends(require_full_auth),
):
    """Delete a PFMaterials."""
    allowed, _ = permission_service.check_permission(
        current_user.role, current_user.permissions, ModuleName.MATERIALS, PermissionAction.DELETE
    )
    if not allowed:
        raise AppError(403, "無此操作權限")
    deleted = await crud_pf_materials.delete_material(material_id=material_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PFMaterials not found")
    return None