from typing import Optional, List
from fastapi import APIRouter, HTTPException, status, Depends, Query

from src.schemas.offices import (
    OfficeInSchema,
    OfficeOutSchema
)
# from src.crud.offices import (
#     get_all_offices,
#     get_office_by_id,
#     create_office,
#     update_office,
#     delete_office
# )
import src.crud.offices as crud
from src.auth.guard import require_full_auth
from src.schemas.users import UserOutSchema
from src.database.geo_models import OfficeBoundaries

router = APIRouter()


@router.get(
    "/offices",
    response_model=List[OfficeOutSchema],
    status_code=status.HTTP_200_OK,
)
async def get_offices():
    """獲取所有管理處/單位資料"""
    return await crud.get_all_offices()

@router.post(
    "/offices",
    response_model=OfficeOutSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_full_auth)]
)
async def add_office(
    office: OfficeInSchema,
    current_user: UserOutSchema = Depends(require_full_auth)
):
    """新增管理處/單位資料 (需要認證)"""
    # 檢查權限 (只有管理員可以新增)
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="權限不足，只有管理員可以新增管理處/單位資料"
        )
    
    return await crud.create_office(office.dict(exclude_unset=True))


@router.put(
    "/offices/{office_id}",
    response_model=OfficeOutSchema,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_full_auth)]
)
async def update_office_data(
    office_id: int,
    office: OfficeInSchema,
    current_user: UserOutSchema = Depends(require_full_auth)
):
    """更新管理處/單位資料 (需要認證)"""
    # 檢查權限 (只有管理員可以更新)
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="權限不足，只有管理員可以更新管理處/單位資料"
        )
    
    return await crud.update_office(office_id, office.dict(exclude_unset=True))


@router.delete(
    "/offices/{office_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_full_auth)]
)
async def remove_office(
    office_id: int,
    current_user: UserOutSchema = Depends(require_full_auth)
):
    """刪除管理處/單位資料 (需要認證)"""
    # 檢查權限 (只有管理員可以刪除)
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="權限不足，只有管理員可以刪除管理處/單位資料"
        )
    
    return await crud.delete_office(office_id)


@router.get(
    "/offices/branches/{office_id}",
    status_code=status.HTTP_200_OK,
    summary="取得管理處的分處列表",
    description="根據管理處 ID 從 office_boundaries 取得分處列表"
)
async def get_office_branches(office_id: int):
    """取得指定管理處的分處列表"""
    try:
        # 查詢該管理處的所有分處
        branches = await OfficeBoundaries.filter(
            ia_code=str(office_id).zfill(2)
        ).distinct().values('mng_code', 'mng_name')

        # 過濾掉空值並格式化回傳
        result = [
            {"code": b['mng_code'], "name": b['mng_name']}
            for b in branches
            if b['mng_name']
        ]

        # 依 code 排序
        result.sort(key=lambda x: x['code'])

        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢分處列表失敗: {str(e)}"
        )


@router.get(
    "/offices/stations/{office_id}",
    status_code=status.HTTP_200_OK,
    summary="取得管理處的所有工作站列表",
    description="根據管理處 ID 從 office_boundaries 取得所有工作站列表（不區分是否有分處）"
)
async def get_office_stations(office_id: int):
    """取得指定管理處的所有工作站列表"""
    try:
        # 查詢該管理處的所有工作站
        stations = await OfficeBoundaries.filter(
            ia_code=str(office_id).zfill(2)
        ).distinct().values('stn_code', 'stn_name')

        # 過濾掉空值並格式化回傳
        result = [
            {"code": s['stn_code'], "name": s['stn_name']}
            for s in stations
            if s['stn_name']
        ]

        # 依 code 排序
        result.sort(key=lambda x: x['code'])

        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢工作站列表失敗: {str(e)}"
        )


@router.get(
    "/offices/stations/{office_id}/{branch_code}",
    status_code=status.HTTP_200_OK,
    summary="取得分處的工作站列表",
    description="根據管理處 ID 和分處代碼從 office_boundaries 取得工作站列表"
)
async def get_branch_stations(office_id: int, branch_code: str):
    """取得指定分處的工作站列表"""
    try:
        # 查詢該分處的所有工作站
        stations = await OfficeBoundaries.filter(
            ia_code=str(office_id).zfill(2),
            mng_code=branch_code
        ).distinct().values('stn_code', 'stn_name')

        # 過濾掉空值並格式化回傳
        result = [
            {"code": s['stn_code'], "name": s['stn_name']}
            for s in stations
            if s['stn_name']
        ]

        # 依 code 排序
        result.sort(key=lambda x: x['code'])

        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢工作站列表失敗: {str(e)}"
        )