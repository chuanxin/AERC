from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from fastapi.responses import JSONResponse
from starlette import status

from src.auth.guard import require_full_auth
from src.auth.route_guards import (
    require_permission,
    require_grant_scope_by_id,
    require_grant_scope_by_case_number,
)
from src.schemas.permissions import ModuleName, PermissionAction
from src.schemas.users import UserOutSchema, UserInfoSchema
from src.schemas.grant_versions import (
    GrantVersionCreateSchema, GrantVersionUpdateSchema,
    GrantVersionListSchema, GrantVersionDetailSchema,
    GrantVersionCompareSchema, GrantVersionCompareResultSchema,
    GrantVersionResponseSchema
)
import src.crud.grant_versions as crud
from src.schemas.token import Status

router = APIRouter(prefix="/grant-versions", tags=["grant-versions"])


@router.post(
    "",
    response_model=GrantVersionResponseSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(ModuleName.GRANTS, PermissionAction.EDIT))],
)
async def create_grant_version_api(
    version_data: GrantVersionCreateSchema,
    current_user: UserInfoSchema = Depends(require_full_auth)
):
    """建立新的補助申請案件版本"""
    try:
        return await crud.create_grant_version(version_data, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="建立版本失敗",
        )


@router.get(
    "/grant/{grant_id}",
    response_model=List[GrantVersionListSchema],
    dependencies=[Depends(require_full_auth)],
)
async def get_grant_versions_api(
    grant_id: int = Path(..., description="補助申請案件ID"),
    skip: int = Query(0, description="分頁 - 跳過筆數"),
    limit: int = Query(100, description="分頁 - 每頁筆數")
):
    """取得補助申請案件的所有版本列表"""
    try:
        return await crud.get_grant_versions(grant_id, skip, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="取得版本列表失敗",
        )


@router.get(
    "/{version_id}",
    response_model=GrantVersionDetailSchema,
    dependencies=[Depends(require_full_auth)],
)
async def get_grant_version_api(
    version_id: int = Path(..., description="版本ID")
):
    """取得單一版本的詳細資料"""
    try:
        return await crud.get_grant_version(version_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="取得版本詳細資料失敗",
        )


@router.put(
    "/{version_id}",
    response_model=GrantVersionDetailSchema,
    dependencies=[Depends(require_permission(ModuleName.GRANTS, PermissionAction.EDIT))],
)
async def update_grant_version_api(
    version_id: int = Path(..., description="版本ID"),
    version_data: GrantVersionUpdateSchema = Body(..., description="版本更新資料"),
    current_user: UserInfoSchema = Depends(require_full_auth)
):
    """更新版本資料（僅允許更新註解）"""
    try:
        return await crud.update_grant_version(version_id, version_data, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="更新版本失敗",
        )


@router.delete(
    "/{version_id}",
    response_model=Status,
    dependencies=[Depends(require_permission(ModuleName.GRANTS, PermissionAction.DELETE))],
)
async def delete_grant_version_api(
    version_id: int = Path(..., description="版本ID"),
    current_user: UserInfoSchema = Depends(require_full_auth)
):
    """刪除版本（僅允許刪除非現行版本）"""
    try:
        result = await crud.delete_grant_version(version_id, current_user)
        return {"message": result["message"]}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="刪除版本失敗",
        )


@router.post(
    "/compare",
    response_model=GrantVersionCompareResultSchema,
    dependencies=[Depends(require_permission(ModuleName.GRANTS, PermissionAction.VIEW))],
)
async def compare_grant_versions_api(
    compare_data: GrantVersionCompareSchema = Body(..., description="版本比較資料")
):
    """比較兩個版本的差異"""
    try:
        return await crud.compare_grant_versions(
            compare_data.version_a_id, 
            compare_data.version_b_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="比較版本失敗",
        )


@router.put(
    "/grant/{grant_id}/active-version/{version_id}",
    response_model=Dict[str, Any],
    dependencies=[
        Depends(require_grant_scope_by_id),
        Depends(require_permission(ModuleName.GRANTS, PermissionAction.APPROVE)),
    ],
)
async def set_active_version_api(
    grant_id: int = Path(..., description="補助申請案件ID"),
    version_id: int = Path(..., description="版本ID"),
    current_user: UserInfoSchema = Depends(require_full_auth)
):
    """設定現行版本"""
    try:
        return await crud.set_active_version(grant_id, version_id, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="設定現行版本失敗",
        )


@router.get(
    "/grant/{grant_id}/active",
    response_model=Optional[GrantVersionDetailSchema],
    dependencies=[Depends(require_full_auth)],
)
async def get_active_version_api(
    grant_id: int = Path(..., description="補助申請案件ID")
):
    """取得補助申請案件的現行版本"""
    try:
        return await crud.get_active_version(grant_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="取得現行版本失敗",
        )


@router.put(
    "/{version_id}/schema-version",
    response_model=Dict[str, Any],
    dependencies=[Depends(require_permission(ModuleName.GRANTS, PermissionAction.EDIT))],
)
async def update_schema_version_api(
    version_id: int = Path(..., description="版本ID"),
    schema_version: str = Body(..., embed=True, description="新的資料結構版本 (v1.0, legacy)"),
    current_user: UserInfoSchema = Depends(require_full_auth)
):
    """更新版本的資料結構版本標記"""
    try:
        return await crud.update_schema_version(version_id, schema_version, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="更新資料結構版本失敗",
        )


@router.post(
    "/from-current/{case_number}",
    response_model=GrantVersionResponseSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_grant_scope_by_case_number),
        Depends(require_permission(ModuleName.GRANTS, PermissionAction.EDIT)),
    ],
)
async def create_version_from_current_data_api(
    case_number: str = Path(..., description="案件編號"),
    comment: Optional[str] = Body(None, description="版本說明"),
    current_user: UserInfoSchema = Depends(require_full_auth)
):
    """從目前的申請資料建立新版本（用於結案前保存完整資料）"""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="此功能需要與現有資料結構整合後才能實作"
    )


@router.get(
    "/grant/{grant_id}/summary",
    response_model=Dict[str, Any],
    dependencies=[Depends(require_full_auth)],
)
async def get_grant_versions_summary_api(
    grant_id: int = Path(..., description="補助申請案件ID")
):
    """取得補助申請案件版本摘要資訊"""
    try:
        # 取得版本列表
        versions = await crud.get_grant_versions(grant_id, skip=0, limit=1000)
        
        # 取得現行版本
        active_version = await crud.get_active_version(grant_id)
        
        # 統計資訊
        total_versions = len(versions)
        latest_version = versions[0] if versions else None
        
        return {
            "grant_id": grant_id,
            "total_versions": total_versions,
            "latest_version": latest_version,
            "active_version": {
                "id": active_version["id"] if active_version else None,
                "version": active_version["version"] if active_version else None,
                "comment": active_version["comment"] if active_version else None,
                "created_at": active_version["created_at"] if active_version else None
            },
            "has_versions": total_versions > 0,
            "versions_list": versions[:10]  # 最新的10個版本
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="取得版本摘要失敗",
        )
