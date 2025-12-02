from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Path, UploadFile, File, Form, Body
from fastapi.responses import JSONResponse

from starlette import status

from src.auth.jwthandler import get_current_user
from src.schemas.users import UserOutSchema
from src.schemas.grants import (
    GrantInSchema, GrantOutSchema, GrantListSchema,
    GrantUpdateSchema, GrantCreateResponseSchema,
    GrantStepSchema, GrantLandInSchema, GrantSearchSchema,
    GrantCreateRequestSchema, ApplicantSubsidySummarySchema
)
# import src.crud.offices as crud
import src.crud.grants as crud
from src.schemas.token import Status
from src.crud.grants import get_grant_by_case_number, delete_grant  # Import the missing functions

import logging

logger = logging.getLogger(__name__)
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
    logger.info(f"📡 [read_grant_step] API 被調用: case_number={case_number}, step={step}")
    try:
        result = await crud.get_grant_step_data(case_number, step)
        logger.info(f"📡 [read_grant_step] 成功返回資料，欄位數量: {len(result) if result else 0}")
        return result
    except Exception as e:
        logger.error(f"📡 [read_grant_step] 錯誤: {str(e)}")
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

@router.patch(
    "/case/{case_number}/status",
    response_model=Dict[str, Any],
    dependencies=[Depends(get_current_user)],
)
async def update_grant_status_api(
    case_number: str = Path(..., description="案件編號"),
    status_data: Dict[str, str] = Body(..., description="狀態資料"),
    current_user: UserOutSchema = Depends(get_current_user)
):
    """更新補助申請案件的狀態"""
    try:
        return await crud.update_grant_status(case_number, status_data["status"], current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"更新案件狀態失敗: {str(e)}",
        )


@router.put(
    "/case/{case_number}/current-step",
    response_model=Dict[str, Any],
    dependencies=[Depends(get_current_user)],
)
async def update_current_step_api(
    case_number: str = Path(..., description="案件編號"),
    current_step_data: Dict[str, int] = Body(..., description="當前步驟資料"),
    current_user: UserOutSchema = Depends(get_current_user)
):
    """更新補助申請案件的當前步驟"""
    try:
        return await crud.update_grant_current_step(case_number, current_step_data["current_step"], current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"更新當前步驟失敗: {str(e)}",
        )
    
@router.get(
    "",
    response_model=List[Dict[str, Any]],  # 修改回應模型以支援動態欄位
    dependencies=[Depends(get_current_user)],
)
async def read_grants(
    status: Optional[str] = Query(None, description="案件狀態過濾"),
    year: Optional[int] = Query(None, description="申請年度過濾"),
    office_id: Optional[int] = Query(None, description="管理處過濾"),
    search: Optional[str] = Query(None, description="搜尋關鍵字"),
    skip: int = Query(0, description="分頁 - 跳過筆數"),
    limit: int = Query(10000, description="分頁 - 每頁筆數（預設不限制）"),
    current_user: UserOutSchema = Depends(get_current_user)
):
    """取得補助申請案件列表，可依條件過濾"""
    return await crud.get_grants(year, office_id, search, status, skip, limit, current_user)


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
    grant_data: GrantCreateRequestSchema,
    current_user: UserOutSchema = Depends(get_current_user)
):
    """建立新的補助申請案件 (Step 0 - 申請人資料)
    
    接受前端 GrantCreateRequest 格式的資料，自動映射到後端格式
    """
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
    limit: int = Query(10000, description="分頁 - 每頁筆數（預設不限制）")
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


@router.post(
    "/case/{case_number}/create-version",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
async def create_version_from_frontend_data_api(
    case_number: str = Path(..., description="案件編號"),
    all_steps_data: Dict[str, Any] = Body(..., description="所有步驟的完整資料"),
    comment: Optional[str] = Body(None, description="版本說明"),
    current_user: UserOutSchema = Depends(get_current_user)
):
    """從前端提供的完整資料建立新版本（適用於變更設計功能）"""
    try:
        # 取得案件資訊
        grant = await crud.get_grant_by_case_number(case_number)
        
        # 使用 grant_versions CRUD 建立版本
        from src.schemas.grant_versions import GrantVersionCreateSchema
        from src.crud.grant_versions import create_grant_version
        
        version_data = GrantVersionCreateSchema(
            grant_id=grant["id"],
            all_steps_data=all_steps_data,
            comment=comment or f"從前端資料建立版本 - {case_number}"
        )
        
        result = await create_grant_version(version_data, current_user)
        
        return {
            **result,
            "case_number": case_number,
            "message": "從前端資料建立版本成功"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"從前端資料建立版本失敗: {str(e)}",
        )


@router.get(
    "/case/{case_number}/papers",
    response_model=Dict[str, Any],
    dependencies=[Depends(get_current_user)],
)
async def get_grant_papers_by_case_number(
    case_number: str = Path(..., description="案件編號"),
    document_type: Optional[str] = Query("budget_statement", description="文件類型"),
    grants_id: Optional[int] = Query(None, description="案件ID（用於區分重複案件編號）")
):
    """依案件編號取得 grant_papers 文件資料（根據 active_version_id 匹配）
    
    對於歷史案件可能有重複案件編號的情況，可使用 grants_id 參數明確指定案件
    """
    try:
        result = await crud.get_grant_papers_by_case_number(case_number, document_type, grants_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"取得文件資料失敗: {str(e)}",
        )


@router.get(
    "/case/{case_number}/versions/compare",
    response_model=Dict[str, Any],
    dependencies=[Depends(get_current_user)],
)
async def compare_grant_versions_api(
    case_number: str = Path(..., description="案件編號")
):
    """比較案件的第一版本與最新版本設施差異"""
    try:
        result = await crud.compare_grant_versions(case_number)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"版本比較失敗: {str(e)}",
        )


@router.get(
    "/case/{case_number}/versions/summary",
    response_model=Dict[str, Any],
    dependencies=[Depends(get_current_user)],
)
async def get_grant_version_summary_api(
    case_number: str = Path(..., description="案件編號")
):
    """取得案件版本摘要資訊"""
    try:
        result = await crud.get_grant_version_summary(case_number)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"取得版本摘要失敗: {str(e)}",
        )


@router.post(
    "/batch-cross-year",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
async def batch_cross_year_grants_api(
    batch_data: Dict[str, Any] = Body(..., description="批次跨年度資料"),
    current_user: UserOutSchema = Depends(get_current_user)
):
    """批次跨年度處理 - 複製選取的案件並設定為跨年度狀態"""
    try:
        logger.info(f"🔄 批次跨年度處理開始，使用者: {current_user.username}")
        logger.info(f"📦 收到批次資料: {batch_data}")
        
        case_numbers = batch_data.get("case_numbers", [])
        grants_info = batch_data.get("grants_info", [])
        
        if not case_numbers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="未提供要處理的案件編號"
            )
        
        logger.info(f"📋 準備處理 {len(case_numbers)} 筆案件: {case_numbers}")
        
        # 調用 CRUD 函數進行批次跨年度處理
        results = await crud.batch_cross_year_grants(case_numbers, current_user)
        
        logger.info(f"✅ 批次跨年度處理完成，處理結果: {len(results)} 筆")
        return results
        
    except Exception as e:
        logger.error(f"❌ 批次跨年度處理失敗: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批次跨年度處理失敗: {str(e)}",
        )


@router.get(
    "/applicant-subsidy-summary/{applicant_id}/{year}",
    response_model=Dict[str, Any],
    dependencies=[Depends(get_current_user)],
)
async def get_applicant_subsidy_summary(
    applicant_id: str = Path(..., description="申請人身分證字號"),
    year: int = Path(..., description="申請年度（民國年）"),
    current_grant_id: Optional[int] = Query(None, description="當前案件ID（用於排除自己）"),
    current_user: UserOutSchema = Depends(get_current_user)
):
    """
    查詢申請人年度補助額度摘要

    業務規則：
    - 年度補助上限：50萬元
    - 計入狀態：submitted, under_review, approved, completed
    - 補助來源（雙軌制）：
        * 新系統案件 (is_legacy=False): step4(灌溉調控設施) + step5(田間管路)
        * 歷史案件 (is_legacy=True): pay_detail.amount - pay_detail.self_raised
    - 以 active_version 為準
    """
    try:
        logger.info(
            f"📊 查詢年度補助額度: "
            f"申請人={applicant_id}, 年度={year}, "
            f"排除案件ID={current_grant_id}"
        )

        result = await crud.calculate_applicant_yearly_subsidy(
            applicant_id=applicant_id,
            year=year,
            current_grant_id=current_grant_id
        )

        return result

    except Exception as e:
        logger.error(f"❌ 查詢年度補助額度失敗: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢年度補助額度失敗: {str(e)}",
        )