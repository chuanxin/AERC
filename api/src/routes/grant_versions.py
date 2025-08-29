from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from fastapi.responses import JSONResponse
from starlette import status

from src.auth.jwthandler import get_current_user
from src.schemas.users import UserOutSchema
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
    dependencies=[Depends(get_current_user)],
)
async def create_grant_version_api(
    version_data: GrantVersionCreateSchema,
    current_user: UserOutSchema = Depends(get_current_user)
):
    """建立新的補助申請案件版本"""
    try:
        return await crud.create_grant_version(version_data, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"建立版本失敗: {str(e)}",
        )


@router.get(
    "/grant/{grant_id}",
    response_model=List[GrantVersionListSchema],
    dependencies=[Depends(get_current_user)],
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
            detail=f"取得版本列表失敗: {str(e)}",
        )


@router.get(
    "/{version_id}",
    response_model=GrantVersionDetailSchema,
    dependencies=[Depends(get_current_user)],
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
            detail=f"取得版本詳細資料失敗: {str(e)}",
        )


@router.put(
    "/{version_id}",
    response_model=GrantVersionDetailSchema,
    dependencies=[Depends(get_current_user)],
)
async def update_grant_version_api(
    version_id: int = Path(..., description="版本ID"),
    version_data: GrantVersionUpdateSchema = Body(..., description="版本更新資料"),
    current_user: UserOutSchema = Depends(get_current_user)
):
    """更新版本資料（僅允許更新註解）"""
    try:
        return await crud.update_grant_version(version_id, version_data, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"更新版本失敗: {str(e)}",
        )


@router.delete(
    "/{version_id}",
    response_model=Status,
    dependencies=[Depends(get_current_user)],
)
async def delete_grant_version_api(
    version_id: int = Path(..., description="版本ID"),
    current_user: UserOutSchema = Depends(get_current_user)
):
    """刪除版本（僅允許刪除非現行版本）"""
    try:
        result = await crud.delete_grant_version(version_id, current_user)
        return {"message": result["message"]}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"刪除版本失敗: {str(e)}",
        )


@router.post(
    "/compare",
    response_model=GrantVersionCompareResultSchema,
    dependencies=[Depends(get_current_user)],
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
            detail=f"比較版本失敗: {str(e)}",
        )


@router.put(
    "/grant/{grant_id}/active-version/{version_id}",
    response_model=Dict[str, Any],
    dependencies=[Depends(get_current_user)],
)
async def set_active_version_api(
    grant_id: int = Path(..., description="補助申請案件ID"),
    version_id: int = Path(..., description="版本ID"),
    current_user: UserOutSchema = Depends(get_current_user)
):
    """設定現行版本"""
    try:
        return await crud.set_active_version(grant_id, version_id, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"設定現行版本失敗: {str(e)}",
        )


@router.get(
    "/grant/{grant_id}/active",
    response_model=Optional[GrantVersionDetailSchema],
    dependencies=[Depends(get_current_user)],
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
            detail=f"取得現行版本失敗: {str(e)}",
        )


@router.post(
    "/from-current/{case_number}",
    response_model=GrantVersionResponseSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
async def create_version_from_current_data_api(
    case_number: str = Path(..., description="案件編號"),
    comment: Optional[str] = Body(None, description="版本說明"),
    current_user: UserOutSchema = Depends(get_current_user)
):
    """從目前的申請資料建立新版本（用於結案前保存完整資料）"""
    try:
        # 這裡需要從現有的申請資料中收集所有步驟的資料
        # 這個功能需要與現有的資料結構整合
        
        # 目前先返回錯誤，提示需要實作完整的資料收集邏輯
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="此功能需要與現有資料結構整合後才能實作"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"從目前資料建立版本失敗: {str(e)}",
        )


@router.get(
    "/grant/{grant_id}/summary",
    response_model=Dict[str, Any],
    dependencies=[Depends(get_current_user)],
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
            detail=f"取得版本摘要失敗: {str(e)}",
        )
