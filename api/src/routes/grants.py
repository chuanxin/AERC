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
    GrantCreateRequestSchema, ApplicantSubsidySummarySchema
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
        (grant_data, land_data, step3_data, step4_data)
    """
    # 提取各步驟資料（統一架構：UI step N → formData[N]）
    steps_data = version_data.get('steps', {}) if version_data else {}

    # Step 1: 申請人基本資料
    step1_data = steps_data.get('1', {})

    # Step 2: 土地資料
    step2_data = steps_data.get('2', {})
    land_list = step2_data.get('lands', []) or step2_data.get('landList', []) or step2_data.get('land_list', [])

    # Step 3: 灌溉調控設施（step3.vue → formData[4]）
    step3_data = steps_data.get('4', {})

    # Step 4: 田間管路（step4.vue → formData[5]）
    step4_data = steps_data.get('5', {})

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

        land_data.append({
            'land_county': land_county_name,
            'land_town': land_town_name,
            'land_section': land.get('landSecName', '') or land.get('landSection', '') or land.get('land_section', ''),
            'land_number': land.get('landNumber', '') or land.get('land_number', ''),
            'facility_area_m2': land.get('facilityArea', 0) or land.get('facility_area', 0)
        })

    return grant_data, land_data, step3_data, step4_data


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
        grant_data, land_data, step3_data, step4_data = await extract_completion_statement_data(grant, version_data)

        # 生成 PDF
        pdf_generator = CompletionStatementPDFGenerator()
        pdf_bytes = pdf_generator.generate_completion_statement(
            grant_data, land_data, step3_data, step4_data
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

    # 提取完成期限（從 step5 現場勘查資料或使用預設值）
    step5_data = steps_data.get('3', {})  # step5.vue → formData[3]
    completion_date_raw = step5_data.get('expectedCompletionDate', '')

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