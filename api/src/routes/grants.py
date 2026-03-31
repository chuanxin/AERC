from decimal import Decimal
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Path, UploadFile, File, Form, Body
from fastapi.responses import JSONResponse, FileResponse

from starlette import status

from src.auth.jwthandler import get_current_user
from src.schemas.users import UserOutSchema
from src.schemas.grants import (
    GrantInSchema, GrantOutSchema, GrantListSchema,
    GrantUpdateSchema, GrantCreateResponseSchema,
    GrantStepSchema, GrantLandInSchema, GrantSearchSchema,
    GrantCreateRequestSchema, ApplicantSubsidySummarySchema,
    GrantTagSetSchema
)
# import src.crud.offices as crud
import src.crud.grants as crud
import src.crud.domicile as domicile_crud
from src.schemas.token import Status
from src.crud.grants import get_grant_by_case_number, delete_grant  # Import the missing functions
from src.database.models import Grants
from src.services.completion_statement_pdf_generator import CompletionStatementPDFGenerator
from src.services.declaration_pdf_generator import DeclarationPDFGenerator
from src.services.authorization_pdf_generator import AuthorizationPDFGenerator
from src.services.budget_statement_pdf_generator import BudgetStatementPDFGenerator
from src.services.excel_generator import ExcelGeneratorService
from src.crud.grant_statistics import GrantStatisticsCRUD
from src.schemas.statistics import ExecutionProgressResponse, BudgetAnalysisResponse, B03StatsResponse

import logging
import tempfile
from urllib.parse import quote

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
    skip: int = Query(0, description="分頁用 - 跳過筆數"),
    limit: Optional[int] = Query(None, description="筆數上限（不設定則查詢全部）"),
    tag: Optional[str] = Query(None, description="標籤完全比對篩選"),
    current_user: UserOutSchema = Depends(get_current_user)
):
    """取得補助申請案件列表，可依條件過濾"""
    return await crud.get_grants(year, office_id, search, status, skip, limit, current_user, tag)


@router.patch(
    "/{grant_id}/tag",
    response_model=Dict[str, Any],
    dependencies=[Depends(get_current_user)],
)
async def set_grant_tag(
    grant_id: int = Path(..., description="補助案件ID"),
    tag_data: GrantTagSetSchema = Body(..., description="標籤資料"),
    current_user: UserOutSchema = Depends(get_current_user),
):
    """設定或清除案件標籤"""
    grant = await Grants.get_or_none(id=grant_id)
    if not grant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="案件不存在",
        )
    grant.tag = tag_data.tag
    await grant.save(update_fields=["tag", "modified_at"])
    return {"grant_id": grant_id, "tag": grant.tag}


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
async def read_grant_by_case_number(
    case_number: str = Path(..., description="案件編號"),
    grants_id: Optional[int] = Query(None, description="案件ID（用於區分重複案號）")
):
    """依案件編號取得單一補助申請案件詳細資料

    🔥 支援 grants_id 參數以區分重複的 case_number（歷史案件轉新系統時可能發生）
    """
    try:
        return await get_grant_by_case_number(case_number, grants_id)
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


@router.patch(
    "/{grant_id}/claim-ownership",
    response_model=Dict[str, Any],
    dependencies=[Depends(get_current_user)],
)
async def claim_inactive_grant_ownership(
    grant_id: int,
    current_user: UserOutSchema = Depends(get_current_user)
):
    """
    認領 inactive 案件的所有權

    當用戶進入編輯 inactive 狀態的案件時，自動將 created_by_id 更新為當前用戶
    這樣可以讓歷史案件被新用戶接管處理
    """
    try:
        return await crud.claim_inactive_grant_ownership(grant_id, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"認領案件所有權失敗: {str(e)}",
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
    limit: int = Query(None, description="筆數上限")
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


# === PDF 生成共用工具函數 ===

async def _convert_domicile_id_to_name(value: Any, converter_func) -> str:
    """
    轉換縣市或鄉鎮 ID 為名稱

    Args:
        value: 可能是 ID (int/str) 或已經是名稱 (str)
        converter_func: domicile_crud.get_county 或 domicile_crud.get_town

    Returns:
        名稱字串
    """
    if not value:
        return ''

    # 如果是數字（ID），轉換為名稱
    if isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
        try:
            entity = await converter_func(int(value))
            return entity.name if entity else str(value)
        except:
            return str(value)
    else:
        return str(value)


def _build_applicant_address(grant, step1_data: dict = None) -> str:
    """
    組合申請人完整地址
    優先使用 Grant 模型欄位，如果為空則回退到 step1_data

    Args:
        grant: Grant 模型實例
        step1_data: Step 1 資料字典（可選）

    Returns:
        完整地址字串
    """
    address_parts = []

    # 縣市
    if grant.county:
        address_parts.append(grant.county)
    elif step1_data and step1_data.get('county'):
        address_parts.append(step1_data.get('county'))

    # 鄉鎮
    if grant.town:
        address_parts.append(grant.town)
    elif step1_data and step1_data.get('town'):
        address_parts.append(step1_data.get('town'))

    # 村里
    if grant.village:
        address_parts.append(grant.village)
    elif step1_data and step1_data.get('village'):
        address_parts.append(step1_data.get('village'))

    # 詳細地址
    if grant.address:
        address_parts.append(grant.address)
    elif step1_data and step1_data.get('address'):
        address_parts.append(step1_data.get('address'))

    return ''.join(address_parts)


def _generate_pdf_file_response(
    pdf_bytes: bytes,
    case_number: str,
    year: str,
    applicant_name: str,
    doc_type: str
) -> FileResponse:
    """
    生成 PDF FileResponse

    Args:
        pdf_bytes: PDF 二進位資料
        case_number: 案號
        year: 年度
        applicant_name: 申請人姓名
        doc_type: 文件類型（如 "結案申報書" 或 "切結書"）

    Returns:
        FileResponse 物件
    """
    # 生成臨時檔案
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_pdf.write(pdf_bytes)
    temp_pdf.close()

    # 生成檔名
    filename = f"{year}-{case_number}-{applicant_name} - {doc_type}.pdf"
    encoded_filename = quote(filename, safe='')

    # 返回檔案
    return FileResponse(
        path=temp_pdf.name,
        filename=filename,
        media_type='application/pdf',
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }
    )


# === 結案申報書相關功能 ===

async def extract_completion_statement_data(grant, version_data: dict) -> tuple:
    """
    從 Grant 資料中提取結案申報書所需資料

    Returns:
        (grant_data, land_data, step4_data, step5_data)
    """
    # 提取各步驟資料（統一架構：UI step N → formData[N]）
    steps_data = version_data.get('steps', {}) if version_data else {}

    # Step 1: 申請人基本資料
    step1_data = steps_data.get('1', {})

    # Step 2: 土地資料
    step2_data = steps_data.get('2', {})
    land_list = step2_data.get('lands', []) or step2_data.get('landList', []) or step2_data.get('land_list', [])

    # Step 4: 灌溉調控設施（step3.vue → formData[4]）
    step4_data = steps_data.get('4', {})

    # Step 5: 田間管路（step4.vue → formData[5]）
    step5_data = steps_data.get('5', {})

    # 使用共用函數組合完整通訊地址
    full_address = _build_applicant_address(grant)

    # 組合補助案件基本資料
    grant_data = {
        'case_number': str(grant.case_number) if grant.case_number else "",
        'applicant_name': str(grant.applicant_name) if grant.applicant_name else "",
        'year': str(grant.year) if grant.year else "",
        'county': str(grant.county) if grant.county else "",
        'town': str(grant.town) if grant.town else "",
        'address': full_address,
        'phone': str(grant.applicant_phone) if grant.applicant_phone else "",
        'office_name': grant.office if grant.office else "石門管理處"  # office 是 CharField，直接使用
    }

    # 組合土地資料
    land_data = []
    for land in land_list:
        # 取得縣市和鄉鎮資訊（可能是 ID 或名稱）
        land_county_value = land.get('landCounty', '') or land.get('land_county', '')
        land_town_value = land.get('landTown', '') or land.get('land_town', '')

        # 使用共用函數轉換 ID → 名稱
        land_county_name = await _convert_domicile_id_to_name(land_county_value, domicile_crud.get_county)
        land_town_name = await _convert_domicile_id_to_name(land_town_value, domicile_crud.get_town)

        # 安全轉換面積為 float（處理前端可能傳來字串的情況）
        try:
            facility_area_value = float(land.get('facilityArea', 0) or land.get('facility_area', 0) or 0)
        except (ValueError, TypeError):
            facility_area_value = 0.0

        land_data.append({
            'land_county': land_county_name,
            'land_town': land_town_name,
            'land_section': land.get('landSecName', '') or land.get('landSection', '') or land.get('land_section', ''),
            'land_number': land.get('landNumber', '') or land.get('land_number', ''),
            'facility_area_m2': facility_area_value
        })

    return grant_data, land_data, step4_data, step5_data


@router.post("/case/{case_number}/completion-statement")
async def download_completion_statement(
    case_number: str = Path(..., description="案件編號"),
    current_user: UserOutSchema = Depends(get_current_user)
):
    """
    下載結案申報書 PDF

    檔名格式：[年度]-[案號]-[申請人姓名] - 結案申報書.pdf
    """
    try:
        logger.info(f"📋 [download_completion_statement] 生成結案申報書: case_number={case_number}")

        # 查詢補助案件（office 是 CharField，不需要 select_related）
        grant = await Grants.filter(case_number=case_number).select_related("active_version").first()

        if not grant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"找不到案號 {case_number} 的案件"
            )

        # 取得版本資料
        version_data = grant.active_version.all_steps_data if grant.active_version else {}

        # 提取結案申報書資料
        grant_data, land_data, step4_data, step5_data = await extract_completion_statement_data(grant, version_data)

        # 生成 PDF
        pdf_generator = CompletionStatementPDFGenerator()
        pdf_bytes = pdf_generator.generate_completion_statement(
            grant_data, land_data, step4_data, step5_data
        )

        # 使用共用函數生成並返回 PDF 檔案
        logger.info(f"📋 [download_completion_statement] 結案申報書生成成功")
        return _generate_pdf_file_response(
            pdf_bytes,
            case_number,
            grant_data.get('year', ''),
            grant_data.get('applicant_name', ''),
            "結案申報書"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [download_completion_statement] 生成結案申報書失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成結案申報書失敗: {str(e)}"
        )


# === 補助切結書相關功能 ===

async def extract_declaration_data(grant, version_data: dict) -> dict:
    """
    從 Grant 資料中提取補助切結書所需資料

    Returns:
        grant_data: 包含所有切結書欄位的字典
    """
    # 提取各步驟資料（統一架構：UI step N → formData[N]）
    steps_data = version_data.get('steps', {}) if version_data else {}

    # Step 1: 申請人基本資料
    step1_data = steps_data.get('1', {})

    # Step 2: 土地資料
    step2_data = steps_data.get('2', {})
    land_list = step2_data.get('lands', []) or step2_data.get('landList', []) or step2_data.get('land_list', [])

    # 提取第一筆土地資料
    first_land = land_list[0] if land_list else {}

    # 縣市、鄉鎮（需要轉換 ID 為名稱）
    land_county_value = first_land.get('landCounty', '') or first_land.get('land_county', '')
    land_town_value = first_land.get('landTown', '') or first_land.get('land_town', '')

    # 使用共用函數轉換 ID → 名稱
    land_county_name = await _convert_domicile_id_to_name(land_county_value, domicile_crud.get_county)
    land_town_name = await _convert_domicile_id_to_name(land_town_value, domicile_crud.get_town)

    # 提取完成期限（從 step3 現場勘查資料或使用預設值）
    step3_data = steps_data.get('3', {})  # step5.vue → formData[3]
    completion_date_raw = step3_data.get('expectedCompletionDate', '')

    # 轉換完成日期為「YYYY年MM月DD日」格式
    completion_date = ''
    if completion_date_raw:
        try:
            # 假設 expectedCompletionDate 格式為 "YYYY-MM-DD"
            from datetime import datetime
            date_obj = datetime.strptime(completion_date_raw, '%Y-%m-%d')
            roc_year = date_obj.year - 1911
            completion_date = f"{roc_year}年{date_obj.month}月{date_obj.day}日"
        except:
            completion_date = completion_date_raw

    # 使用共用函數組合通訊地址（優先使用 Grant 模型欄位，如果為空則回退到 step1_data）
    full_address = _build_applicant_address(grant, step1_data)

    # 組裝切結書資料
    grant_data = {
        'applicant_name': grant.applicant_name if grant.applicant_name else step1_data.get('name', ''),
        'county': land_county_name,
        'town': land_town_name,
        'land_section': first_land.get('landSecName', '') or first_land.get('landSection', '') or first_land.get('land_section', ''),
        'land_subsection': first_land.get('landSubsection', '') or first_land.get('land_subsection', ''),
        'land_number': first_land.get('landNumber', '') or first_land.get('land_number', ''),
        'land_count': len(land_list),
        'year': str(grant.year) if grant.year else '114',
        'completion_date': completion_date or '114年12月31日',  # 預設值
        'office_name': grant.office if grant.office else '石門管理處',  # office 是 CharField，直接使用
        'id_number': grant.applicant_id if grant.applicant_id else (step1_data.get('idNumber', '') or step1_data.get('id_number', '')),
        'address': full_address,
        'phone': grant.applicant_phone if grant.applicant_phone else (step1_data.get('phone', '') or step1_data.get('telephone', '')),
    }

    return grant_data


@router.post("/case/{case_number}/declaration")
async def download_declaration(
    case_number: str = Path(..., description="案件編號"),
    current_user: UserOutSchema = Depends(get_current_user)
):
    """
    下載補助切結書 PDF

    檔名格式：[年度]-[案號]-[申請人姓名] - 切結書.pdf
    """
    try:
        logger.info(f"📋 [download_declaration] 生成切結書: case_number={case_number}")

        # 查詢補助案件
        grant = await Grants.filter(case_number=case_number).select_related("active_version").first()

        if not grant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"找不到案號 {case_number} 的案件"
            )

        # 取得版本資料
        version_data = grant.active_version.all_steps_data if grant.active_version else {}

        # 提取切結書資料
        grant_data = await extract_declaration_data(grant, version_data)

        # 生成 PDF
        pdf_generator = DeclarationPDFGenerator()
        pdf_bytes = pdf_generator.generate(grant_data)

        # 使用共用函數生成並返回 PDF 檔案
        logger.info(f"📋 [download_declaration] 切結書生成成功")
        return _generate_pdf_file_response(
            pdf_bytes,
            case_number,
            grant_data.get('year', ''),
            grant_data.get('applicant_name', ''),
            "切結書"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [download_declaration] 生成切結書失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成切結書失敗: {str(e)}"
        )


async def extract_authorization_data(grant, version_data) -> dict:
    """
    從 Grant 資料中提取規劃委託書所需資料

    Returns:
        grant_data: 包含所有規劃委託書欄位的字典
    """
    # 提取各步驟資料（統一架構：UI step N → formData[N]）
    steps_data = version_data.get('steps', {}) if version_data else {}

    # Step 1: 申請人基本資料
    step1_data = steps_data.get('1', {})

    # 使用共用函數組合通訊地址（優先使用 Grant 模型欄位，如果為空則回退到 step1_data）
    full_address = _build_applicant_address(grant, step1_data)

    # 組裝規劃委託書資料
    grant_data = {
        'case_number': grant.case_number,
        'applicant_name': grant.applicant_name if grant.applicant_name else step1_data.get('name', ''),
        'id_number': grant.applicant_id if grant.applicant_id else (step1_data.get('idNumber', '') or step1_data.get('id_number', '')),
        'address': full_address,
        'phone': grant.applicant_phone if grant.applicant_phone else (step1_data.get('phone', '') or step1_data.get('telephone', '')),
        'year': str(grant.year) if grant.year else '114',
    }

    return grant_data


@router.post("/case/{case_number}/authorization")
async def download_authorization(
    case_number: str = Path(..., description="案件編號"),
    current_user: UserOutSchema = Depends(get_current_user)
):
    """
    下載規劃委託書 PDF

    檔名格式：[年度]-[案號]-[申請人姓名] - 規劃委託書.pdf
    """
    try:
        logger.info(f"📋 [download_authorization] 生成規劃委託書: case_number={case_number}")

        # 查詢補助案件
        grant = await Grants.filter(case_number=case_number).select_related("active_version").first()

        if not grant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"找不到案件編號: {case_number}"
            )

        # 提取資料
        version_data = grant.active_version.all_steps_data if grant.active_version else {}
        grant_data = await extract_authorization_data(grant, version_data)

        # 生成 PDF
        generator = AuthorizationPDFGenerator()
        pdf_bytes = generator.generate(grant_data)

        # 使用共用函數生成 FileResponse
        return _generate_pdf_file_response(
            pdf_bytes,
            case_number,
            grant_data.get('year', ''),
            grant_data.get('applicant_name', ''),
            "規劃委託書"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [download_authorization] 生成規劃委託書失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成規劃委託書失敗: {str(e)}"
        )


async def extract_budget_statement_data(grant, version_data) -> dict:
    """
    從 Grant 資料中提取工程預算書所需資料

    Returns:
        grant_data: 包含所有工程預算書欄位的字典
    """
    # 提取各步驟資料
    steps_data = version_data.get('steps', {}) if version_data else {}

    # Step 1: 申請人基本資料
    step1_data = steps_data.get('1', {})

    # Step 2: 土地資料
    step2_data = steps_data.get('2', {})
    lands = step2_data.get('lands', [])

    # Step 3: 現場勘查 (UI step 3 → data step 3)
    step3_data = steps_data.get('3', {})

    # Step 4: 灌溉調控設施 (UI step 4 → data step 4)
    step4_data = steps_data.get('4', {})

    # Step 5: 田間管路 (UI step 5 → data step 5)
    step5_data = steps_data.get('5', {})

    # 使用共用函數組合通訊地址
    full_address = _build_applicant_address(grant, step1_data)

    # 組裝土地清冊資料
    land_list = []
    total_land_area = Decimal('0')
    total_facility_area = Decimal('0')
    total_facility_area_ha = Decimal('0')

    for land in lands:
        # 取得縣市和鄉鎮資訊（可能是 ID 或名稱）
        land_county_value = land.get('landCounty', '') or land.get('land_county', '')
        land_town_value = land.get('landTown', '') or land.get('land_town', '')

        # 使用共用函數轉換 ID → 名稱
        land_county_name = await _convert_domicile_id_to_name(land_county_value, domicile_crud.get_county)
        land_town_name = await _convert_domicile_id_to_name(land_town_value, domicile_crud.get_town)

        # 取得地段和地號資訊（嘗試多個可能的欄位名稱）
        land_section = land.get('landSecName', '') or land.get('section', '') or land.get('landSection', '') or land.get('land_section', '')
        lot_number = land.get('landNumber', '') or land.get('lotNumber', '') or land.get('lot_number', '')

        # 安全轉換為 Decimal（處理前端可能傳來字串的情況）
        try:
            land_area_m2 = Decimal(str(land.get('landArea', 0) or 0))
        except Exception:
            land_area_m2 = Decimal('0')

        try:
            facility_area_m2 = Decimal(str(land.get('facilityArea', 0) or 0))
        except Exception:
            facility_area_m2 = Decimal('0')

        try:
            facility_area_ha = Decimal(str(land.get('facilityAreaHa', 0) or land.get('facility_area_ha', 0) or 0))
        except Exception:
            facility_area_ha = Decimal('0')

        land_list.append({
            'land_county': land_county_name,
            'land_town': land_town_name,
            'section': land_section,
            'lot_number': lot_number,
            'land_area': land_area_m2,
            'facility_area': facility_area_m2
        })

        total_land_area += land_area_m2
        total_facility_area += facility_area_m2
        total_facility_area_ha += facility_area_ha

    # 第一筆土地資訊（用於封面和表格）
    land_town = ''
    if land_list:
        first_land = land_list[0]
        land_county = first_land.get('land_county', '')
        land_town = first_land.get('land_town', '')
        land_section = first_land.get('section', '')
        first_lot_number = first_land.get('lot_number', '')
        # 組合完整的土地位置：縣市 + 鄉鎮 + "-" + 地段
        land_location = f"{land_county}{land_town}-{land_section}" if land_section else f"{land_county}{land_town}"
    else:
        land_location = ""
        land_town = ""
        first_lot_number = ""

    # 設施型式（組合「設施型式」+ 「灌溉型式」）
    installation_type_raw = step5_data.get('installationType', '')

    # 設施型式映射表（對應 UI step5 的 installationTypeOptions）
    installation_type_mapping = {
        1: '埋設固定式',
        2: '地表定置式',
        3: '附掛棚架式'
    }

    # 轉換設施型式（如果是 ID 則轉為名稱，否則直接使用）
    installation_type_part = installation_type_mapping.get(
        installation_type_raw,
        str(installation_type_raw) if installation_type_raw else ''
    )

    # 根據 irrigationTypeId 和相關 subtype ID 決定灌溉型式部分
    irrigation_type_id = step5_data.get('irrigationTypeId', 0)
    irrigation_type_raw = step5_data.get('irrigationType', '')
    sprinkler_subtype_id = step5_data.get('sprinklerSubtypeId', 0)
    dripper_subtype_id = step5_data.get('dripperSubtypeId', 0)

    if irrigation_type_id in [1, 3]:
        # irrigationTypeId = 1（穿孔管系統）或 3（微噴灌系統）：直接使用 irrigationType
        irrigation_type_part = irrigation_type_raw
    elif irrigation_type_id == 2:
        # irrigationTypeId = 2（噴頭系統）：根據 sprinklerSubtypeId 判斷
        if sprinkler_subtype_id == 6:
            irrigation_type_part = "高壓大型噴頭系統"
        elif sprinkler_subtype_id == 2:
            irrigation_type_part = "一般噴頭系統"
        else:
            irrigation_type_part = irrigation_type_raw
    elif irrigation_type_id == 4:
        # irrigationTypeId = 4（滴灌系統）：根據 dripperSubtypeId 判斷
        if dripper_subtype_id == 7:
            irrigation_type_part = "滴嘴滴灌系統"
        elif dripper_subtype_id == 8:
            irrigation_type_part = "滴水管滴灌系統"
        else:
            irrigation_type_part = irrigation_type_raw
    else:
        # 其他情況：直接使用 irrigationType
        irrigation_type_part = irrigation_type_raw

    # 組合兩個欄位，用空格分隔
    if installation_type_part and irrigation_type_part:
        facility_type = f"{installation_type_part} {irrigation_type_part}"
    # elif installation_type_part:
    #     facility_type = installation_type_part
    # elif irrigation_type_part:
    #     facility_type = irrigation_type_part
    else:
        facility_type = '其它'

    # 補助標準（從 step2_data 的第一筆土地資料 isAboriginalArea 判斷）
    first_land = lands[0] if lands else {}

    is_aboriginal_area = first_land.get('isAboriginalArea')

    subsidy_standard = '原民區域' if is_aboriginal_area else '一般地區'

    # 預算項目資料（從 step4 和 step5 資料中提取）

    # === A 項：田間管路設施費（從 step5_data 提取）===
    a_item_total = 0

    # 田間主管 1
    main_pipe_1_qty = int(step5_data.get('mainPipeQuantity', 0) or 0)
    main_pipe_1_price = float(step5_data.get('mainPipeUnitPrice', 0) or 0)
    main_pipe_1_total = main_pipe_1_qty * main_pipe_1_price
    main_pipe_1_length = int(step5_data.get('mainPipeLength', 0) or 0)
    a_item_total += main_pipe_1_total

    # 田間主管 2（如果啟用）
    # main_pipe_2_enabled = step5_data.get('mainPipe2Enabled', False)
    # main_pipe_2_qty = 0
    # main_pipe_2_price = 0
    # main_pipe_2_total = 0
    # main_pipe_2_length = 0
    # if main_pipe_2_enabled:
    main_pipe_2_qty = int(step5_data.get('mainPipe2Quantity', 0) or 0)
    main_pipe_2_price = float(step5_data.get('mainPipe2UnitPrice', 0) or 0)
    main_pipe_2_total = main_pipe_2_qty * main_pipe_2_price
    main_pipe_2_length = int(step5_data.get('mainPipe2Length', 0) or 0)
    a_item_total += main_pipe_2_total

    # 灌溉系統（pipes 陣列的總和）
    # 根據前端邏輯：只計算 groupId 為 2,3,4,5,6,7,8 或 (groupId=1 且 module!='主管') 的管路
    irrigation_system_total = 0
    pipes = step5_data.get('pipes', [])
    if pipes:
        for pipe in pipes:
            try:
                group_id = pipe.get('groupId', 0)
                module = pipe.get('module', '')

                # 過濾條件（與前端一致）
                if group_id in [2, 3, 4, 5, 6, 7, 8]:
                    should_include = True
                elif group_id == 1 and module != '主管':
                    should_include = True
                else:
                    should_include = False

                if should_include:
                    # 使用 totalPrice 欄位（與前端一致）
                    total_price = pipe.get('totalPrice', 0)
                    if isinstance(total_price, str):
                        # 移除千分位逗號
                        total_price = total_price.replace(',', '')
                    irrigation_system_total += float(total_price or 0)
            except (ValueError, TypeError):
                continue
    a_item_total += irrigation_system_total

    # === A 項工作費 ===
    a_work_fee = int(float(step5_data.get('workFee', 0) or 0))
    a_item_total += a_work_fee

    # === B 項：規劃設計費 ===
    # 直接從資料取得 designFee
    b_design_fee = step5_data.get('designFee', 0) or 0

    # === C、D、E 項：調控設施、動力設備、調蓄設施（從 step4_data 提取）===
    # 使用前端已計算的 subsidyAmount 和 selfPaidAmount
    c_control_total = 0
    c_control_subsidy = 0
    c_control_self_paid = 0
    c_control_quantity = 0  # 調控設施數量總和

    d_power_total = 0
    d_power_subsidy = 0
    d_power_self_paid = 0
    d_power_quantity = 0  # 動力設備數量總和

    e_storage_total = 0
    e_storage_subsidy = 0
    e_storage_self_paid = 0
    e_storage_tonnage = 0  # 調蓄設施噸位總和

    facilities = step4_data.get('facilities', [])
    if facilities:
        for facility in facilities:
            try:
                # 取得設施類別（避免與外層 facility_type 變數衝突，使用 fac_type）
                fac_type = facility.get('type', '')

                # 取得總價
                total_price_str = str(facility.get('totalPrice', '0') or '0')
                total_price_str = total_price_str.replace(',', '')
                total_price = int(float(total_price_str))

                # 取得補助金額和自備款（前端已計算）
                subsidy_amount = int(float(facility.get('subsidyAmount', 0) or 0))
                self_paid_amount = int(float(facility.get('selfPaidAmount', 0) or 0))

                # 根據設施類型累加
                if fac_type == 'power':
                    # D 項：動力設備
                    d_power_total += total_price
                    d_power_subsidy += subsidy_amount
                    d_power_self_paid += self_paid_amount
                    # 累加數量
                    quantity = int(float(facility.get('quantity', 1) or 1))
                    d_power_quantity += quantity
                elif fac_type == 'storage':
                    # E 項：調蓄設施
                    e_storage_total += total_price
                    e_storage_subsidy += subsidy_amount
                    e_storage_self_paid += self_paid_amount
                    # 累加噸位（噸位 × 數量）
                    tonnage = int(float(facility.get('tonnage', 0) or 0))
                    quantity = int(float(facility.get('quantity', 1) or 1))
                    e_storage_tonnage += tonnage * quantity
                elif fac_type == 'control':
                    # C 項：調節控制設施
                    c_control_total += total_price
                    c_control_subsidy += subsidy_amount
                    c_control_self_paid += self_paid_amount
                    # 累加數量
                    quantity = int(float(facility.get('quantity', 1) or 1))
                    c_control_quantity += quantity
            except (ValueError, TypeError):
                continue

    # === 取得 step5 的補助額度與自備款 ===
    step5_subsidy_amount = int(float(step5_data.get('subsidyAmount', 0) or 0))
    step5_self_paid_amount = int(float(step5_data.get('selfPaidAmount', 0) or 0))

    # === 判斷資料結構版本（legacy vs 新版）===
    data_schema_version = grant.active_version.data_schema_version if grant.active_version else None
    is_legacy_data = data_schema_version == 'legacy'

    # === 政府補助款（使用前端已計算的值）===
    # A 項：田間管路補助
    if is_legacy_data:
        # 歷史資料：subsidyAmount 不包含設計費，直接使用
        # 補助優先用於管路材料
        govt_subsidy_a = int(min(a_item_total, step5_subsidy_amount))
    else:
        # 新資料：subsidyAmount 包含設計費，需要扣除
        # A 項補助 = 總補助 - 設計費（不得小於 0）
        # govt_subsidy_a = int(max(0, step5_subsidy_amount - b_design_fee)) （0128_2026 修改）
        govt_subsidy_a = int(step5_subsidy_amount)
    
    govt_subsidy_c = c_control_subsidy  # C 項：調節控制設施（使用前端計算值）
    govt_subsidy_d = d_power_subsidy  # D 項：動力設備（使用前端計算值）
    govt_subsidy_e = e_storage_subsidy  # E 項：調蓄設施（使用前端計算值）

    # 實際獲得補助的規劃設計費
    # if is_legacy_data:
        # 歷史資料：subsidyAmount 不含設計費，設計費全額補助
        # actual_subsidized_design_fee = b_design_fee
    # else:
        # 新資料：subsidyAmount 包含設計費，取補助額度和設計費的最小值
        # actual_subsidized_design_fee = min(step5_subsidy_amount, b_design_fee)

    actual_subsidized_design_fee = b_design_fee

    # === 農戶配合款（使用前端已計算的值）===
    total_amount = a_item_total + b_design_fee + c_control_total + d_power_total + e_storage_total
    govt_subsidy_total = govt_subsidy_a + govt_subsidy_c + govt_subsidy_d + govt_subsidy_e
    # 農戶配合款 = C/D/E 項的自備款總和 + step5 的自備款
    farmer_contribution = c_control_self_paid + d_power_self_paid + e_storage_self_paid + step5_self_paid_amount

    budget_items = {
        'a_item_total': int(a_item_total),
        'a_materials': int(a_item_total),
        'a_work_fee': int(a_work_fee),
        'main_pipe_1_length': main_pipe_1_length,
        'main_pipe_1_qty': main_pipe_1_qty,
        'main_pipe_1_price': int(main_pipe_1_price),
        'main_pipe_1_total': int(main_pipe_1_total),
        'main_pipe_2_length': main_pipe_2_length,
        'main_pipe_2_qty': main_pipe_2_qty,
        'main_pipe_2_price': int(main_pipe_2_price),
        'main_pipe_2_total': int(main_pipe_2_total),
        'irrigation_system_total': int(irrigation_system_total),
        'b_design_fee': b_design_fee,
        'actual_subsidized_design_fee': int(actual_subsidized_design_fee),  # 實際獲得補助的設計費
        'c_control_total': int(c_control_total),
        'c_control_quantity': int(c_control_quantity),  # 調控設施數量總和
        'd_power_total': int(d_power_total),
        'd_power_quantity': int(d_power_quantity),  # 動力設備數量總和
        'e_storage_total': int(e_storage_total),
        'e_storage_tonnage': int(e_storage_tonnage),  # 調蓄設施噸位總和
        'farmer_contribution': max(0, int(farmer_contribution)),  # 確保不為負數
        'govt_subsidy_a': int(govt_subsidy_a),
        'govt_subsidy_c': int(govt_subsidy_c),
        'govt_subsidy_d': int(govt_subsidy_d),
        'govt_subsidy_e': int(govt_subsidy_e),
        'govt_subsidy_total': int(govt_subsidy_total),
    }

    # === 動力設施（從 step4_data.facilities 提取 type='power'）===
    power_items = []
    power_facilities = [f for f in facilities if f.get('type') == 'power']

    for facility in power_facilities:
        power_items.append({
            'name': (facility.get('name', '') or '').strip(),  # 動力設備名稱（清除前後空格）
            'quantity': int(float(facility.get('quantity', 1) or 1)),  # 數量
            'amount': int(float(facility.get('totalPrice', 0) or 0))  # 金額（總價）
        })

    # === 調蓄設施（從 step4_data.facilities 提取 type='storage'）===
    storage_items = []
    storage_facilities = [f for f in facilities if f.get('type') == 'storage']

    for facility in storage_facilities:
        storage_items.append({
            'material': (facility.get('storageType', '') or '').strip(),  # 材質類型（清除前後空格）
            'tonnage': int(float(facility.get('tonnage', 0) or 0)),  # 噸位
            'quantity': int(float(facility.get('quantity', 1) or 1)),  # 數量
            'amount': int(float(facility.get('totalPrice', 0) or 0))  # 金額（總價）
        })

    # === 管路材料（從 step5_data.pipes 提取並按 groupId 分組）===
    pipe_materials = []

    # 從 step5_data 中提取 pipes 陣列
    pipes = step5_data.get('pipes', [])

    if pipes:
        # 過濾掉無單價的材料（matprice 為 null 或 0）
        valid_pipes = [p for p in pipes if p.get('matprice') and float(p.get('matprice', 0) or 0) > 0]

        if valid_pipes:
            # 按 groupId 分組
            from collections import defaultdict
            grouped_by_group = defaultdict(list)

            for pipe in valid_pipes:
                group_id = pipe.get('groupId', 0)
                grouped_by_group[group_id].append(pipe)

            # 對每個群組內的材料按 order 排序，並生成材料清單
            # 使用連續的群組編號（1, 2, 3...），而非原始的 groupId（可能是 1, 3, 4...）
            sequential_group_number = 1
            for group_id in sorted(grouped_by_group.keys()):
                pipes_in_group = grouped_by_group[group_id]
                # 按 order 排序
                pipes_in_group.sort(key=lambda x: x.get('order', 0))

                # 取得群組名稱（從第一個項目）
                group_name = pipes_in_group[0].get('groupName', f'群組{sequential_group_number}')

                item_number = 1
                for pipe in pipes_in_group:
                    # 項目編號格式：1-1, 1-2, 2-1, 2-2...（使用連續群組編號）
                    item_id = f"{sequential_group_number}-{item_number}"

                    # 格式化規格（∮ {spec1}"）
                    spec1 = pipe.get('spec1', '')
                    spec_formatted = f"∮ {spec1}" if spec1 else ''

                    pipe_materials.append({
                        'category': f"{sequential_group_number}. {group_name}",  # 連續群組編號 + groupName
                        'item_id': item_id,  # 項目編號（1-1, 1-2, 2-1...）
                        'name': (pipe.get('matname', '') or '').strip(),  # 材料名稱（清除前後空格）
                        'spec': spec_formatted,  # 規格（∮ {spec1}"）
                        'unit': (pipe.get('itemunit', '') or '').strip(),  # 單位（清除前後空格）
                        'price': int(float(pipe.get('matprice', 0) or 0)),  # 單價
                        'quantity': int(float(pipe.get('matamount', 0) or 0)),  # 數量
                        'total': int(float(pipe.get('totalPrice', 0) or 0)),  # 總價
                        'is_first_in_group': (item_number == 1)  # 標記是否為該群組的第一個項目
                    })
                    item_number += 1

                sequential_group_number += 1

    # === 調控設施材料（從 step4_data.facilities 提取 type='control' 並按 controlType 分組）===
    control_materials = []

    # 從 facilities 中提取所有調控設施
    control_facilities = [f for f in facilities if f.get('type') == 'control']

    if control_facilities:
        # 按 controlType 分組
        from collections import defaultdict
        grouped_by_type = defaultdict(list)

        for facility in control_facilities:
            control_type = facility.get('controlType', '未分類')
            grouped_by_type[control_type].append(facility)

        # 生成材料清單（按 controlType 分組）
        group_number = 1
        for control_type, facilities_in_group in grouped_by_type.items():
            item_number = 1
            for facility in facilities_in_group:
                # 項目編號格式：始終使用 "群組-序號" 格式（1-1, 1-2, 2-1, 2-2...）
                item_id = f"{group_number}-{item_number}"

                control_materials.append({
                    'category': f"{group_number}. {control_type}",  # 群組編號 + controlType 名稱
                    'item_id': item_id,  # 項目編號（1-1, 1-2, 2-1...）
                    'name': (facility.get('name', '') or '').strip(),  # 材料名稱（清除前後空格）
                    'spec': '',  # 規格（目前未使用）
                    'unit': '',  # 單位（目前未使用）
                    'price': int(float(facility.get('unitPrice', 0) or 0)),  # 單價
                    'quantity': int(float(facility.get('quantity', 1) or 1)),  # 數量
                    'total': int(float(facility.get('totalPrice', 0) or 0)),  # 總價
                    'is_first_in_group': (item_number == 1)  # 標記是否為該群組的第一個項目
                })
                item_number += 1

            group_number += 1

    # 坵塊形狀（從 ui step5（田間管路）→ step5_data 提取）
    field_length = step5_data.get('fieldLength', 0)
    field_width = step5_data.get('fieldWidth', 0)
    block_shape = f"{field_length}m × {field_width}m" if field_length and field_width else ''

    # 噴頭配置間距（從 ui step5（田間管路）→ step5_data 提取）
    sprinkler_spacing_ss = step5_data.get('sprinklerSpacing_SS', '')
    branch_pipe_spacing_sl = step5_data.get('branchPipeSpacing_SL', '')
    irrigation_type_id = step5_data.get('irrigationTypeId', 0)
    dripper_subtype_id = step5_data.get('dripperSubtypeId', 0)

    # 根據灌溉型式 ID 決定 nozzle_spacing 的顯示格式
    if irrigation_type_id == 1 or dripper_subtype_id == 8:
        # 穿孔管系統：僅顯示 SL
        nozzle_spacing = f"{branch_pipe_spacing_sl}" if branch_pipe_spacing_sl else ''
        nozzle_spacing_label = f"噴頭配置間距(SL)" if branch_pipe_spacing_sl else ''
    else:
        # 其他系統：顯示 SS × SL
        if sprinkler_spacing_ss and branch_pipe_spacing_sl:
            nozzle_spacing = f"{sprinkler_spacing_ss} × {branch_pipe_spacing_sl}"
            nozzle_spacing_label = f"噴頭配置間距(SS × SL)"
        else:
            nozzle_spacing = ''
            nozzle_spacing_label = ''

    # 組裝完整資料
    grant_data = {
        # 基本資訊
        'case_number': grant.case_number,
        'applicant_name': grant.applicant_name if grant.applicant_name else step1_data.get('name', ''),
        'id_number': grant.applicant_id if grant.applicant_id else (step1_data.get('idNumber', '') or step1_data.get('id_number', '')),
        'address': full_address,
        'phone': grant.applicant_phone if grant.applicant_phone else (step1_data.get('phone', '') or step1_data.get('telephone', '')),
        'year': str(grant.year) if grant.year else '',
        'office_name': grant.office if grant.office else '',  # office 是 CharField，直接使用

        # 土地資訊
        'land_location': land_location,
        'land_town': land_town,
        'first_lot_number': first_lot_number,
        'land_count': len(lands),
        'facility_area_ha': total_facility_area_ha,  # 原始數值，顯示層再格式化
        'total_facility_area_m2': total_facility_area,
        'lands': land_list,

        # 設施資訊
        'facility_type': facility_type,
        'subsidy_standard': subsidy_standard,
        'block_shape': block_shape,
        'nozzle_spacing': nozzle_spacing,
        'nozzle_spacing_label': nozzle_spacing_label,
        'irrigation_type_id': irrigation_type_id,  # 灌溉型式 ID（用於判斷顯示邏輯）
        'dripper_subtype_id': dripper_subtype_id,  # 滴灌型式 ID（用於判斷顯示邏輯）
        'sprinkler_spacing_ss': sprinkler_spacing_ss,  # 噴頭間距 SS
        'branch_pipe_spacing_sl': branch_pipe_spacing_sl,  # 支管行距 SL
        'main_pipe_1_length': main_pipe_1_length,  # 田間主管1管長

        # 預算資料
        'budget_items': budget_items,
        'power_items': power_items,
        'storage_items': storage_items,
        'pipe_materials': pipe_materials,
        'control_materials': control_materials,

        # 補助金額（農戶請領款：A+C+D+E 項，不包含規劃設計費）
        'govt_subsidy_total': govt_subsidy_total,
    }

    return grant_data


@router.post("/case/{case_number}/budget-statement")
async def download_budget_statement(
    case_number: str = Path(..., description="案件編號"),
    grants_id: Optional[int] = Query(None, description="案件ID（用於區分重複案件編號）"),
    current_user: UserOutSchema = Depends(get_current_user)
):
    """
    下載工程預算書 PDF（11頁完整版本）

    檔名格式：[年度]-[案號]-[申請人姓名] - 工程預算書.pdf

    對於歷史案件可能有重複案件編號的情況，可使用 grants_id 參數明確指定案件
    """
    try:
        logger.info(f"📋 [download_budget_statement] 生成工程預算書: case_number={case_number}, grants_id={grants_id}")

        # 查詢補助案件 - 優先使用 grants_id（用於區分重複案號）
        if grants_id:
            grant = await Grants.filter(id=grants_id).select_related("active_version").first()
            if not grant:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"找不到案件ID: {grants_id}"
                )
            # 驗證 case_number 是否匹配（防止 ID 與 case_number 不一致）
            if grant.case_number != case_number:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"案件ID {grants_id} 與案號 {case_number} 不匹配"
                )
        else:
            grant = await Grants.filter(case_number=case_number).select_related("active_version").first()
            if not grant:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"找不到案件編號: {case_number}"
                )

        # 提取資料
        version_data = grant.active_version.all_steps_data if grant.active_version else {}
        grant_data = await extract_budget_statement_data(grant, version_data)

        # 生成 PDF
        generator = BudgetStatementPDFGenerator()
        pdf_bytes = generator.generate(grant_data)

        # 使用共用函數生成 FileResponse
        return _generate_pdf_file_response(
            pdf_bytes,
            case_number,
            grant_data.get('year', ''),
            grant_data.get('applicant_name', ''),
            "工程預算書"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [download_budget_statement] 生成工程預算書失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成工程預算書失敗: {str(e)}"
        )


# ==================== 統計功能端點 ====================

@router.get(
    "/statistics/execution-progress",
    response_model=ExecutionProgressResponse,
    summary="取得即時執行進度統計",
    description="取得指定年度的即時執行進度統計，包含各辦公室的核定預算、已結案案件數、總補助面積和金額等資訊"
)
async def get_execution_progress_statistics(
    year: int = Query(..., description="統計年度（民國年）", ge=100, le=200),
    current_user: UserOutSchema = Depends(get_current_user)
):
    """
    取得即時執行進度統計

    權限控制：
    - admin: 查看所有辦公室的統計
    - 其他角色: 只能查看自己辦公室的統計
    """
    try:
        logger.info(f"📊 [get_execution_progress_statistics] 查詢執行進度統計: year={year}, user={current_user.username}, role={current_user.role}")

        # 權限控制：admin 查看全部，其他角色只查看自己辦公室
        if current_user.role == "admin":
            query_office_id = None
        else:
            query_office_id = current_user.office.id if current_user.office else None

        result = await GrantStatisticsCRUD.get_execution_progress(
            year=year,
            office_id=query_office_id,
        )

        logger.info(f"✅ [get_execution_progress_statistics] 成功取得統計資料: {len(result.offices)} 個辦公室")
        return result

    except Exception as e:
        logger.error(f"❌ [get_execution_progress_statistics] 查詢失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢執行進度統計失敗: {str(e)}"
        )


@router.get(
    "/statistics/budget-analysis",
    response_model=BudgetAnalysisResponse,
    summary="取得即時經費統計分析",
    description="取得指定年度的即時經費統計分析，包含預定執行、已編預算、已驗收等資訊"
)
async def get_budget_analysis_statistics(
    year: int = Query(..., description="統計年度（民國年）", ge=100, le=200),
    current_user: UserOutSchema = Depends(get_current_user)
):
    """
    取得即時經費統計分析

    權限控制：
    - admin: 查看所有辦公室的統計
    - 其他角色: 只能查看自己辦公室的統計
    """
    try:
        logger.info(f"📊 [get_budget_analysis_statistics] 查詢經費分析統計: year={year}, user={current_user.username}, role={current_user.role}")

        # 權限控制：admin 查看全部，其他角色只查看自己辦公室
        if current_user.role == "admin":
            query_office_id = None
        else:
            query_office_id = current_user.office.id if current_user.office else None

        result = await GrantStatisticsCRUD.get_budget_analysis(
            year=year,
            office_id=query_office_id,
        )

        logger.info(f"✅ [get_budget_analysis_statistics] 成功取得統計資料: {len(result.offices)} 個辦公室")
        return result

    except Exception as e:
        logger.error(f"❌ [get_budget_analysis_statistics] 查詢失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢經費分析統計失敗: {str(e)}"
        )


@router.get(
    "/statistics/execution-progress/excel",
    summary="下載 A01 各管理處執行進度報表 Excel",
    description="生成並下載指定年度的 A01 各管理處執行進度報表（Excel 格式）"
)
async def download_execution_progress_excel(
    year: int = Query(..., description="統計年度（民國年）", ge=100, le=200),
    office_id: Optional[int] = Query(None, description="管理處 ID（選填，預設查詢全部）"),
    current_user: UserOutSchema = Depends(get_current_user)
):
    """
    下載 A01 各管理處執行進度報表 Excel

    計算邏輯與首頁「管理處執行進度」相同，包含：
    - 管理處名稱
    - 核定金額（元）
    - 補助案件數（已結案）
    - 補助面積（公頃）
    - 補助金額（元）
    - 補助款執行率%
    """
    try:
        logger.info(f"📊 [download_execution_progress_excel] 生成 A01 報表: year={year}, office_id={office_id}, user={current_user.username}")

        # Phase 1: 直接傳遞前端選取的條件（office_id=None 表示全部）
        # TODO Phase 2: 加入使用者權限控制（非 admin 限制可查詢的 office 範圍）
        result = await GrantStatisticsCRUD.get_execution_progress(
            year=year,
            office_id=office_id,
        )

        # 將 Pydantic model 轉換為 dict
        data = result.model_dump()

        # 生成 Excel 檔案
        excel_service = ExcelGeneratorService()
        excel_file_path = await excel_service.generate_a01_execution_progress_report(
            data=data,
            year=year
        )

        # 生成下載檔名
        filename = f"A01_各管理處執行進度_{year}年度.xlsx"
        encoded_filename = quote(filename, safe='')

        logger.info(f"✅ [download_execution_progress_excel] 成功生成報表: {excel_file_path}")

        return FileResponse(
            path=excel_file_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )

    except Exception as e:
        logger.error(f"❌ [download_execution_progress_excel] 生成報表失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成 A01 報表失敗: {str(e)}"
        )


# ==================== A03 管理處經費統計報表 ====================


@router.get(
    "/statistics/budget-analysis/excel",
    summary="下載 A03 各管理處經費統計報表 Excel",
    description="生成並下載指定年度的 A03 各管理處經費統計報表（Excel 格式），包含預定執行、已編列、已驗收、執行率等 12 個欄位"
)
async def download_budget_analysis_excel(
    year: int = Query(..., description="統計年度（民國年）", ge=100, le=200),
    office_id: Optional[int] = Query(None, description="管理處 ID（選填）"),
    current_user: UserOutSchema = Depends(get_current_user)
):
    """
    下載 A03 各管理處經費統計報表 Excel

    報表包含 12 個欄位：
    - 管理處
    - 預定執行面積（公頃）
    - 預定執行預算（元）
    - 已編預算案件數
    - 已編預算面積（公頃）
    - 已編列補助款（元）
    - 未編列補助款（元）
    - 已驗收案件數
    - 已驗收面積（公頃）
    - 已驗收金額（元）
    - 面積執行率（%）
    - 預算執行率（%）

    權限控制：
    - admin: 可下載所有管理處資料
    - 其他角色: 僅能下載所屬管理處資料
    """
    try:
        logger.info(f"📊 [download_budget_analysis_excel] 生成 A03 報表: year={year}, office_id={office_id}, user={current_user.username}")

        # 權限控制：非 admin 使用者只能查詢自己的辦公室
        if current_user.role != "admin":
            if office_id is not None and office_id != current_user.office.id:
                logger.warning(f"⚠️ [download_budget_analysis_excel] 權限不足: user={current_user.username} 嘗試查詢 office_id={office_id}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="您沒有權限查詢此管理處資料"
                )
            # 強制設定為使用者自己的辦公室
            office_id = current_user.office.id if current_user.office else None

        # 查詢經費統計資料（複用現有 CRUD 方法）
        result = await GrantStatisticsCRUD.get_budget_analysis(
            year=year,
            office_id=office_id,
        )

        # 將 Pydantic model 轉換為 dict
        data = result.model_dump()

        # 生成 Excel 檔案
        excel_service = ExcelGeneratorService()
        excel_file_path = await excel_service.generate_a03_budget_analysis_report(
            data=data,
            year=year
        )

        # 生成下載檔名（根據是否篩選辦公室調整檔名）
        if office_id is None:
            filename = f"A03_各管理處經費統計_{year}年度.xlsx"
        else:
            office_name = data['offices'][0].get('office_name', '管理處') if data.get('offices') else '管理處'
            filename = f"A03_{office_name}經費統計_{year}年度.xlsx"
        
        encoded_filename = quote(filename, safe='')

        logger.info(f"✅ [download_budget_analysis_excel] 成功生成報表: {excel_file_path}")

        return FileResponse(
            path=excel_file_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [download_budget_analysis_excel] 生成報表失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成 A03 報表失敗: {str(e)}"
        )


# ==================== A02 系列統計報表 ====================


@router.get(
    "/statistics/county-town/excel",
    summary="下載 A02-1 各縣市鄉鎮區統計報表 Excel",
)
async def download_county_town_excel(
    year: int = Query(..., description="統計年度（民國年）", ge=100, le=200),
    office_id: Optional[int] = Query(None, description="管理處 ID（選填）"),
    current_user: UserOutSchema = Depends(get_current_user)
):
    """下載 A02-1 各縣市鄉鎮區統計報表"""
    try:
        logger.info(f"📊 [A02-1] 生成報表: year={year}, office_id={office_id}")
        result = await GrantStatisticsCRUD.get_county_town_stats(year=year, office_id=office_id)
        data = result.model_dump()
        excel_service = ExcelGeneratorService()
        excel_file_path = await excel_service.generate_a02_1_report(data=data, year=year)
        filename = f"A02-1_{year}年度.xlsx"
        encoded_filename = quote(filename, safe='')
        return FileResponse(
            path=excel_file_path, filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )
    except Exception as e:
        logger.error(f"❌ [A02-1] 生成報表失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"生成 A02-1 報表失敗: {str(e)}")


@router.get(
    "/statistics/office-summary/excel",
    summary="下載 A02-2 各管理處統計報表 Excel",
)
async def download_office_summary_excel(
    year: int = Query(..., description="統計年度（民國年）", ge=100, le=200),
    office_id: Optional[int] = Query(None, description="管理處 ID（選填）"),
    current_user: UserOutSchema = Depends(get_current_user)
):
    """下載 A02-2 各管理處統計報表"""
    try:
        logger.info(f"📊 [A02-2] 生成報表: year={year}, office_id={office_id}")
        result = await GrantStatisticsCRUD.get_office_summary_stats(year=year, office_id=office_id)
        data = result.model_dump()
        excel_service = ExcelGeneratorService()
        excel_file_path = await excel_service.generate_a02_2_report(data=data, year=year)
        filename = f"A02-2_{year}年度.xlsx"
        encoded_filename = quote(filename, safe='')
        return FileResponse(
            path=excel_file_path, filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )
    except Exception as e:
        logger.error(f"❌ [A02-2] 生成報表失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"生成 A02-2 報表失敗: {str(e)}")


@router.get(
    "/statistics/county-town-yearly/excel",
    summary="下載 A02-3 歷年各縣市鄉鎮區統計報表 Excel",
)
async def download_county_town_yearly_excel(
    start_year: int = Query(..., description="起始年度（民國年）", ge=97, le=200),
    end_year: int = Query(..., description="結束年度（民國年）", ge=97, le=200),
    office_id: Optional[int] = Query(None, description="管理處 ID（選填）"),
    current_user: UserOutSchema = Depends(get_current_user)
):
    """下載 A02-3 歷年各縣市鄉鎮區統計報表"""
    if start_year > end_year:
        raise HTTPException(status_code=400, detail="起始年度不得大於結束年度")
    try:
        logger.info(f"📊 [A02-3] 生成報表: {start_year}-{end_year}, office_id={office_id}")
        result = await GrantStatisticsCRUD.get_county_town_stats_yearly(
            start_year=start_year, end_year=end_year, office_id=office_id
        )
        data = result.model_dump()
        excel_service = ExcelGeneratorService()
        excel_file_path = await excel_service.generate_a02_3_report(data=data)
        filename = f"A02-3_{start_year}-{end_year}年度.xlsx"
        encoded_filename = quote(filename, safe='')
        return FileResponse(
            path=excel_file_path, filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [A02-3] 生成報表失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"生成 A02-3 報表失敗: {str(e)}")


@router.get(
    "/statistics/office-summary-yearly/excel",
    summary="下載 A02-4 歷年各管理處統計報表 Excel",
)
async def download_office_summary_yearly_excel(
    start_year: int = Query(..., description="起始年度（民國年）", ge=97, le=200),
    end_year: int = Query(..., description="結束年度（民國年）", ge=97, le=200),
    office_id: Optional[int] = Query(None, description="管理處 ID（選填）"),
    current_user: UserOutSchema = Depends(get_current_user)
):
    """下載 A02-4 歷年各管理處統計報表"""
    if start_year > end_year:
        raise HTTPException(status_code=400, detail="起始年度不得大於結束年度")
    try:
        logger.info(f"📊 [A02-4] 生成報表: {start_year}-{end_year}, office_id={office_id}")
        result = await GrantStatisticsCRUD.get_office_summary_stats_yearly(
            start_year=start_year, end_year=end_year, office_id=office_id
        )
        data = result.model_dump()
        excel_service = ExcelGeneratorService()
        excel_file_path = await excel_service.generate_a02_4_report(data=data)
        filename = f"A02-4_{start_year}-{end_year}年度.xlsx"
        encoded_filename = quote(filename, safe='')
        return FileResponse(
            path=excel_file_path, filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [A02-4] 生成報表失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"生成 A02-4 報表失敗: {str(e)}")


# ==================== A04 原民區域統計報表 ====================


@router.get(
    "/statistics/aboriginal/excel",
    summary="下載 A04 原民區域統計報表 Excel",
    description="生成並下載指定年度的 A04 原民區域統計報表（Excel 格式），統計 isAboriginalArea = true 的補助案件"
)
async def download_aboriginal_statistics_excel(
    year: int = Query(..., description="統計年度（民國年）", ge=100, le=200),
    strict_first_land: bool = Query(
        False,
        description="嚴格第一筆土地模式：True=與A02-1一致，第一筆有效土地必須為原民才計入；False=找第一筆原民有效土地歸屬"
    ),
    current_user: UserOutSchema = Depends(get_current_user)
):
    """
    下載 A04 原民區域統計報表 Excel

    報表包含 5 個欄位：
    - 縣市、鄉鎮區、補助案件數、補助面積（公頃）、補助金額（元）

    篩選規則（兩種模式）：
    - strict_first_land=false (預設): 找第一筆原民有效土地歸屬
    - strict_first_land=true: 與 A02-1 一致，第一筆有效土地須為原民才計入
    """
    try:
        mode_desc = "嚴格第一筆土地" if strict_first_land else "第一筆原民土地"
        logger.info(f"📊 [A04] 生成原民區域統計報表: year={year}, mode={mode_desc}, user={current_user.username}")

        data = await GrantStatisticsCRUD.get_aboriginal_statistics(
            year=year, strict_first_land=strict_first_land
        )

        if not data.get('stats'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{year} 年度無原民區域案件資料"
            )

        excel_service = ExcelGeneratorService()
        excel_file_path = await excel_service.generate_a04_aboriginal_report(
            data=data,
            year=year
        )

        filename = f"A04_原民區域統計_{year}年度.xlsx"
        encoded_filename = quote(filename, safe='')

        logger.info(f"✅ [A04] 成功生成報表: {excel_file_path}")

        return FileResponse(
            path=excel_file_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [A04] 生成報表失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"生成 A04 報表失敗: {str(e)}")


# ==================== A08 歷年原民區域統計報表 ====================


@router.get(
    "/statistics/aboriginal-yearly/excel",
    summary="下載 A08 歷年原民區域統計報表 Excel",
    description="生成並下載指定年度區間的 A08 歷年原民區域推動成果統計表（Excel 格式），橫向展開各年度，僅統計 isAboriginalArea = true 的補助案件"
)
async def download_aboriginal_yearly_excel(
    start_year: int = Query(..., description="起始年度（民國年）", ge=97, le=200),
    end_year: int = Query(..., description="結束年度（民國年）", ge=97, le=200),
    strict_first_land: bool = Query(
        False,
        description="嚴格第一筆土地模式：True=第一筆有效土地必須為原民；False=找第一筆原民有效土地歸屬"
    ),
    current_user: UserOutSchema = Depends(get_current_user)
):
    """下載 A08 歷年原民區域統計報表 Excel"""
    if start_year > end_year:
        raise HTTPException(status_code=400, detail="起始年度不得大於結束年度")
    try:
        logger.info(f"📊 [A08] 生成報表: {start_year}-{end_year}, strict={strict_first_land}")
        result = await GrantStatisticsCRUD.get_aboriginal_statistics_yearly(
            start_year=start_year, end_year=end_year, strict_first_land=strict_first_land
        )
        data = result.model_dump()
        excel_service = ExcelGeneratorService()
        excel_file_path = await excel_service.generate_a08_aboriginal_yearly_report(data=data)
        filename = f"A08_歷年原民區域統計_{start_year}-{end_year}年度.xlsx"
        encoded_filename = quote(filename, safe='')
        return FileResponse(
            path=excel_file_path, filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [A08] 生成報表失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"生成 A08 報表失敗: {str(e)}")


# ==================== A09/A10 事業區域內外推動成果統計報表 ====================


@router.get(
    "/statistics/a09/excel",
    summary="下載 A09 各縣市事業區域內外統計報表 Excel",
    description="生成並下載指定年度的 A09 各縣市推動成果統計表（Excel 格式），按事業區域內/外分組統計（任一土地規則）"
)
async def download_a09_county_irrigation_area_excel(
    year: int = Query(..., description="統計年度（民國年）", ge=100, le=200),
    current_user: UserOutSchema = Depends(get_current_user)
) -> FileResponse:
    """下載 A09 各縣市事業區域內外統計報表 Excel"""
    try:
        logger.info(f"📊 [A09] 生成報表: year={year}")
        stats_response = await GrantStatisticsCRUD.get_a09_county_stats(year=year)
        excel_service = ExcelGeneratorService()
        file_path = await excel_service.generate_a09_report(
            data=stats_response.model_dump(),
            year=year
        )
        filename = f"A09_{year}年度各縣市事業區域內外推動成果統計.xlsx"
        encoded_filename = quote(filename, safe='')
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [A09] 生成報表失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"生成 A09 報表失敗: {str(e)}")


@router.get(
    "/statistics/a10/excel",
    summary="下載 A10 各管理處事業區域內外統計報表 Excel",
    description="生成並下載指定年度的 A10 各管理處推動成果統計表（Excel 格式），按事業區域內/外分組統計（任一土地規則）"
)
async def download_a10_office_irrigation_area_excel(
    year: int = Query(..., description="統計年度（民國年）", ge=100, le=200),
    current_user: UserOutSchema = Depends(get_current_user)
) -> FileResponse:
    """下載 A10 各管理處事業區域內外統計報表 Excel"""
    try:
        logger.info(f"📊 [A10] 生成報表: year={year}")
        stats_response = await GrantStatisticsCRUD.get_a10_office_stats(year=year)
        excel_service = ExcelGeneratorService()
        file_path = await excel_service.generate_a10_report(
            data=stats_response.model_dump(),
            year=year
        )
        filename = f"A10_{year}年度各管理處事業區域內外推動成果統計.xlsx"
        encoded_filename = quote(filename, safe='')
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [A10] 生成報表失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"生成 A10 報表失敗: {str(e)}")


# ==================== B01 系列推動成果統計報表（管理區內外分組） ====================


@router.get(
    "/statistics/b01-1/excel",
    summary="下載 B01-1 各縣市管理區內外統計報表 Excel（單年度）",
    description="生成並下載指定年度的 B01-1 各縣市推動成果統計表（Excel 格式），按管理區內/外分組統計"
)
async def download_b01_1_county_management_area_excel(
    year: int = Query(..., description="統計年度（民國年）", ge=100, le=200),
    office_id: Optional[int] = Query(None, description="管理處 ID（選填）"),
    current_user: UserOutSchema = Depends(get_current_user)
) -> FileResponse:
    """
    下載 B01-1 各縣市管理區內外統計報表 Excel

    統計維度：縣市 × 管理區內外（isIrrigationArea）
    """
    # 取得統計資料
    stats_response = await GrantStatisticsCRUD.get_b01_1_county_management_area_stats(
        year=year,
        office_id=office_id
    )

    # 生成 Excel
    excel_service = ExcelGeneratorService()
    file_path = await excel_service.generate_b01_1_report(
        data=stats_response.dict(),
        year=year
    )

    return FileResponse(
        path=file_path,
        filename=f"B01-1_{year}年度.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.get(
    "/statistics/b01-2/excel",
    summary="下載 B01-2 各管理處管理區內外統計報表 Excel（單年度）",
    description="生成並下載指定年度的 B01-2 各管理處推動成果統計表（Excel 格式），按管理區內/外分組統計"
)
async def download_b01_2_office_management_area_excel(
    year: int = Query(..., description="統計年度（民國年）", ge=100, le=200),
    office_id: Optional[int] = Query(None, description="管理處 ID（選填）"),
    current_user: UserOutSchema = Depends(get_current_user)
) -> FileResponse:
    """
    下載 B01-2 各管理處管理區內外統計報表 Excel

    統計維度：管理處 × 管理區內外（isIrrigationArea）
    """
    # 取得統計資料
    stats_response = await GrantStatisticsCRUD.get_b01_2_office_management_area_stats(
        year=year,
        office_id=office_id
    )

    # 生成 Excel
    excel_service = ExcelGeneratorService()
    file_path = await excel_service.generate_b01_2_report(
        data=stats_response.dict(),
        year=year
    )

    return FileResponse(
        path=file_path,
        filename=f"B01-2_{year}年度.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.get(
    "/statistics/b01-3/excel",
    summary="下載 B01-3 歷年各縣市管理區內外統計報表 Excel",
    description="生成並下載歷年累計的 B01-3 各縣市推動成果統計表（Excel 格式），按管理區內/外分組統計"
)
async def download_b01_3_county_management_area_yearly_excel(
    start_year: int = Query(..., description="起始年度（民國年）", ge=97, le=200),
    end_year: int = Query(..., description="結束年度（民國年）", ge=97, le=200),
    office_id: Optional[int] = Query(None, description="管理處 ID（選填）"),
    current_user: UserOutSchema = Depends(get_current_user)
) -> FileResponse:
    """
    下載 B01-3 歷年各縣市管理區內外統計報表 Excel

    統計維度：縣市 × 管理區內外（isIrrigationArea），歷年累計
    """
    # 驗證年度範圍
    if start_year > end_year:
        raise HTTPException(status_code=400, detail="起始年度不得大於結束年度")

    # 取得統計資料
    stats_response = await GrantStatisticsCRUD.get_b01_3_county_management_area_stats_yearly(
        start_year=start_year,
        end_year=end_year,
        office_id=office_id
    )

    # 生成 Excel
    excel_service = ExcelGeneratorService()
    file_path = await excel_service.generate_b01_3_report(
        data=stats_response.dict(),
        start_year=start_year,
        end_year=end_year
    )

    return FileResponse(
        path=file_path,
        filename=f"B01-3_{start_year}-{end_year}年度.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.get(
    "/statistics/b01-4/excel",
    summary="下載 B01-4 歷年各管理處管理區內外統計報表 Excel",
    description="生成並下載歷年累計的 B01-4 各管理處推動成果統計表（Excel 格式），按管理區內/外分組統計"
)
async def download_b01_4_office_management_area_yearly_excel(
    start_year: int = Query(..., description="起始年度（民國年）", ge=97, le=200),
    end_year: int = Query(..., description="結束年度（民國年）", ge=97, le=200),
    office_id: Optional[int] = Query(None, description="管理處 ID（選填）"),
    current_user: UserOutSchema = Depends(get_current_user)
) -> FileResponse:
    """
    下載 B01-4 歷年各管理處管理區內外統計報表 Excel

    統計維度：管理處 × 管理區內外（isIrrigationArea），歷年累計
    """
    # 驗證年度範圍
    if start_year > end_year:
        raise HTTPException(status_code=400, detail="起始年度不得大於結束年度")

    # 取得統計資料
    stats_response = await GrantStatisticsCRUD.get_b01_4_office_management_area_stats_yearly(
        start_year=start_year,
        end_year=end_year,
        office_id=office_id
    )

    # 生成 Excel
    excel_service = ExcelGeneratorService()
    file_path = await excel_service.generate_b01_4_report(
        data=stats_response.dict(),
        start_year=start_year,
        end_year=end_year
    )

    return FileResponse(
        path=file_path,
        filename=f"B01-4_{start_year}-{end_year}年度.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# ==================== B03 各縣市鄉鎮區各類補助項目統計報表 ====================


@router.get(
    "/statistics/b03/excel",
    summary="下載 B03 各縣市鄉鎮區各類補助項目統計表 Excel",
    description="生成並下載指定年度的 B03 各縣市鄉鎮區各類補助項目統計表（Excel 格式）"
)
async def download_b03_county_town_subsidy_excel(
    year: int = Query(..., description="統計年度（民國年）", ge=100, le=200),
    office_id: Optional[int] = Query(None, description="管理處 ID（選填）"),
    current_user: UserOutSchema = Depends(get_current_user)
) -> FileResponse:
    """
    下載 B03 各縣市鄉鎮區各類補助項目統計表 Excel

    統計維度：縣市 × 鄉鎮區 × 灌溉型式
    """
    stats_response = await GrantStatisticsCRUD.get_b03_county_town_subsidy_stats(
        year=year,
        office_id=office_id
    )

    excel_service = ExcelGeneratorService()
    file_path = await excel_service.generate_b03_report(
        data=stats_response.dict(),
        year=year
    )

    return FileResponse(
        path=file_path,
        filename=f"B03_{year}年度各縣市鄉鎮區各類補助項目統計.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )