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
from src.auth.jwthandler import get_current_user
from src.schemas.users import UserOutSchema

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
    dependencies=[Depends(get_current_user)]
)
async def add_office(
    office: OfficeInSchema,
    current_user: UserOutSchema = Depends(get_current_user)
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
    dependencies=[Depends(get_current_user)]
)
async def update_office_data(
    office_id: int,
    office: OfficeInSchema,
    current_user: UserOutSchema = Depends(get_current_user)
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
    dependencies=[Depends(get_current_user)]
)
async def remove_office(
    office_id: int,
    current_user: UserOutSchema = Depends(get_current_user)
):
    """刪除管理處/單位資料 (需要認證)"""
    # 檢查權限 (只有管理員可以刪除)
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="權限不足，只有管理員可以刪除管理處/單位資料"
        )
    
    return await crud.delete_office(office_id)