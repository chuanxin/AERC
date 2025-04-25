from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Path, UploadFile, File, Form, Body
from fastapi.responses import JSONResponse

from starlette import status

from src.auth.jwthandler import get_current_user
from src.schemas.users import UserOutSchema
from src.schemas.grants import (
    GrantInSchema, GrantOutSchema, GrantListSchema, 
    GrantUpdateSchema, GrantCreateResponseSchema, 
    GrantStepSchema, GrantLandInSchema, GrantSearchSchema
)
# import src.crud.offices as crud
import src.crud.grants as crud
from src.schemas.token import Status
from src.crud.grants import get_grant_by_case_number  # Import the missing function

router = APIRouter(prefix="/grants", tags=["grants"])

@router.get(
    "/case/{case_number}/step/{step}",
    response_model=Dict[str, Any],
    dependencies=[Depends(get_current_user)],
)
async def read_grant_step(
    case_number: str = Path(..., description="案件編號"),
    step: int = Path(..., description="步驟編號", ge=1, le=8)
):
    """取得特定補助申請案件的特定步驟資料"""
    try:
        return await crud.get_grant_step_data(case_number, step)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"取得步驟資料失敗: {str(e)}",
        )


@router.put(
    "/case/{case_number}/step/{step}",
    response_model=Dict[str, Any],
    dependencies=[Depends(get_current_user)],
)
async def update_grant_step_api(
    case_number: str = Path(..., description="案件編號"),
    step: int = Path(..., description="步驟編號", ge=1, le=8),
    step_data: Dict[str, Any] = Body(..., description="步驟資料"),
    current_user: UserOutSchema = Depends(get_current_user)
):
    """更新特定補助申請案件的特定步驟資料"""
    try:
        return await crud.update_grant_step_data(case_number, step, step_data, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"更新步驟資料失敗: {str(e)}",
        )
    
@router.get(
    "",
    response_model=List[GrantListSchema],
    dependencies=[Depends(get_current_user)],
)
async def read_grants(
    status: Optional[str] = Query(None, description="案件狀態過濾"),
    year: Optional[int] = Query(None, description="申請年度過濾"),
    office_id: Optional[int] = Query(None, description="管理處過濾"),
    search: Optional[str] = Query(None, description="搜尋關鍵字"),
    skip: int = Query(0, description="分頁 - 跳過筆數"),
    limit: int = Query(100, description="分頁 - 每頁筆數")
):
    """取得補助申請案件列表，可依條件過濾"""
    if status:
        return await get_grants_by_status(status, year, office_id, search, skip, limit)
    return await get_grants(year, office_id, search, skip, limit)


@router.get(
    "/{grant_id}",
    response_model=GrantOutSchema,
    dependencies=[Depends(get_current_user)],
)
async def read_grant(grant_id: int = Path(..., description="補助案件ID")):
    """依ID取得單一補助申請案件詳細資料"""
    try:
        return await get_grant(grant_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"案件不存在: {str(e)}",
        )


@router.get(
    "/case/{case_number}",
    # response_model=GrantOutSchema,
    response_model=Dict[str, Any],  # Change this from GrantOutSchema to Dict[str, Any]
    dependencies=[Depends(get_current_user)],
)
async def read_grant_by_case_number(case_number: str = Path(..., description="案件編號")):
    """依案件編號取得單一補助申請案件詳細資料"""
    try:
        return await get_grant_by_case_number(case_number)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"案件不存在: {str(e)}",
        )


@router.post(
    "",
    response_model=GrantCreateResponseSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
async def create_grant_api(
    grant_data: GrantInSchema,
    current_user: UserOutSchema = Depends(get_current_user)
):
    """建立新的補助申請案件 (Step 0 - 申請人資料)"""
    try:
        return await crud.create_grant(grant_data, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"建立案件失敗[CRUD]: {str(e)}",
        )


@router.put(
    "/{grant_id}",
    response_model=GrantOutSchema,
    dependencies=[Depends(get_current_user)],
)
async def update_grant_api(
    grant_id: int,
    grant_data: GrantUpdateSchema,
    current_user: UserOutSchema = Depends(get_current_user)
):
    """更新補助申請案件基本資料"""
    try:
        return await update_grant(grant_id, grant_data, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"更新案件失敗: {str(e)}",
        )


@router.patch(
    "/{grant_id}/step/{step}",
    response_model=GrantOutSchema,
    dependencies=[Depends(get_current_user)],
)
async def update_grant_step_api(
    grant_id: int,
    step: int,
    step_data: GrantStepSchema,
    current_user: UserOutSchema = Depends(get_current_user)
):
    """更新補助申請案件特定步驟資料"""
    try:
        return await update_grant_step(grant_id, step, step_data, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"更新案件步驟失敗: {str(e)}",
        )


@router.delete(
    "/{grant_id}",
    response_model=Status,
    dependencies=[Depends(get_current_user)],
)
async def delete_grant_api(
    grant_id: int,
    current_user: UserOutSchema = Depends(get_current_user)
):
    """刪除補助申請案件"""
    try:
        return await delete_grant(grant_id, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"刪除案件失敗: {str(e)}",
        )


@router.get(
    "/{grant_id}/land",
    response_model=dict,
    dependencies=[Depends(get_current_user)],
)
async def get_land_details(
    grant_id: int,
):
    """取得補助申請案件的土地資料"""
    try:
        return await get_grant_land_details(grant_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"取得土地資料失敗: {str(e)}",
        )


@router.post(
    "/{grant_id}/land",
    response_model=dict,
    dependencies=[Depends(get_current_user)],
)
async def create_land_api(
    grant_id: int,
    land_data: GrantLandInSchema,
    current_user: UserOutSchema = Depends(get_current_user)
):
    """建立/更新補助申請案件的土地資料 (Step 2 - 土地資料)"""
    try:
        return await create_grant_land(grant_id, land_data, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"更新土地資料失敗: {str(e)}",
        )


@router.post(
    "/search",
    response_model=List[GrantListSchema],
    dependencies=[Depends(get_current_user)],
)
async def search_grants_api(
    search_data: GrantSearchSchema,
    skip: int = Query(0, description="分頁 - 跳過筆數"),
    limit: int = Query(100, description="分頁 - 每頁筆數")
):
    """進階搜尋補助申請案件"""
    try:
        return await search_grants(search_data, skip, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"搜尋案件失敗: {str(e)}",
        )


@router.post(
    "/{grant_id}/documents",
    response_model=dict,
    dependencies=[Depends(get_current_user)]
)
async def upload_document(
    grant_id: int,
    document_type: str = Form(..., description="文件類型"),
    file: UploadFile = File(..., description="上傳檔案"),
    current_user: UserOutSchema = Depends(get_current_user)
):
    """上傳補助申請案件相關文件"""
    from src.crud.documents import upload_grant_document
    
    try:
        result = await upload_grant_document(grant_id, document_type, file, current_user)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"上傳檔案失敗: {str(e)}",
        )