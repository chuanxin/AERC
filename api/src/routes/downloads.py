from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from typing import Optional
from pydantic import BaseModel
from src.database.models import Grants, GrantVersions, Users, GrantAttachments
from src.auth.jwthandler import get_current_user
from src.services.excel_generator import ExcelGeneratorService
from src.services.budget_statement_pdf_generator import BudgetStatementPDFGenerator
from src.services.construction_photos_pdf_generator import ConstructionPhotosPDFGenerator
from src.services.closing_docs_pdf_generator import ClosingDocsPDFGenerator
from src.routes.grants import extract_budget_statement_data
from src.schemas.static_downloads import (
    StaticDownloadsListResponse,
    StaticDownloadsFilterRequest,
    FileGroup,
    StaticFileInfo,
    BatchDownloadRequest
)
from src.config.folder_mappings import settings
import logging
import os
import tempfile
import re
import hashlib
from urllib.parse import quote
from datetime import datetime
from pathlib import Path
import mimetypes
import zipfile
from collections import defaultdict
from decimal import Decimal, ROUND_DOWN

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/download", tags=["File Downloads"])

class DownloadRequest(BaseModel):
    year: str
    case_number_start: Optional[str] = None
    case_number_end: Optional[str] = None
    file_type: str
    enable_pagination: Optional[bool] = True  # 分頁模式控制，預設開啟
    tag: Optional[str] = None  # 自定義分類標籤篩選（部分比對）


class SubsidyDetailsListRequest(BaseModel):
    year: str
    case_number_start: Optional[str] = None
    case_number_end: Optional[str] = None
    tag: Optional[str] = None

@router.post("/photograph-carry-form")
async def download_photograph_carry_form(
    request: DownloadRequest,
    current_user: Users = Depends(get_current_user)
):
    """下載外出拍攝照片攜帶表"""
    try:
        # 驗證參數
        if not request.year:
            raise HTTPException(status_code=400, detail="年度參數為必填")

        # 建構查詢條件
        query = Grants.filter(year=int(request.year))
        if request.tag:
            query = query.filter(tag__icontains=request.tag)

        # 先取得所有該年度的案件
        all_grants = await query.select_related("active_version").order_by('case_number').all()

        # 在 Python 中進行案件編號範圍篩選
        grants = all_grants
        if request.case_number_start or request.case_number_end:
            grants = []
            for grant in all_grants:
                case_num = grant.case_number
                if case_num and case_num.isdigit():
                    case_num_int = int(case_num)

                    # 檢查範圍
                    in_range = True
                    if request.case_number_start and case_num_int < int(request.case_number_start):
                        in_range = False
                    if request.case_number_end and case_num_int > int(request.case_number_end):
                        in_range = False

                    if in_range:
                        grants.append(grant)

        # 輸出資料庫查詢結果統計
        print(f"=== 資料庫查詢結果 ===")
        print(f"查詢年度: {request.year}")
        if request.case_number_start or request.case_number_end:
            print(f"案件編號範圍: {request.case_number_start or '起始'} - {request.case_number_end or '結束'}")
        print(f"符合條件的案件數量: {len(grants)}")
        print(f"====================")

        if not grants:
            raise HTTPException(status_code=404, detail="找不到符合條件的案件")

        # 準備資料供 Excel 生成
        excel_data = []
        for grant in grants:
            version_data = grant.active_version.all_steps_data if grant.active_version else {}

            # 使用 extract_budget_statement_data 取得正確欄位資料
            grant_data = await extract_budget_statement_data(grant, version_data)

            steps_data = version_data.get('steps', {}) if version_data else {}
            step2_lands = steps_data.get('2', {}).get('lands', [])

            # G欄（設施類型）+ H欄（末端型式）：
            # extract_budget_statement_data 已計算 facility_type = "{安裝型式} {末端型式}"
            # 與 budget_statement_pdf_generator.py 使用相同來源，以空格分割取兩欄
            combined_facility = grant_data.get('facility_type', '')
            _parts = combined_facility.split(' ', 1)
            facility_type = _parts[0]                          # G欄：安裝型式
            irrigation_type = _parts[1] if len(_parts) > 1 else ''  # H欄：末端型式

            # 依 (鄉鎮, 段名) 聚合土地資料
            # 每組：地號「、」分隔、面積加總、農作物去重後「、」分隔
            conv_lands = grant_data.get('lands', [])
            land_groups_dict: dict = {}
            for raw_land, conv_land in zip(step2_lands, conv_lands):
                key = (conv_land.get('land_town', ''), conv_land.get('section', ''))
                lot_num = conv_land.get('lot_number', '')
                try:
                    area_ha = float(raw_land.get('facilityAreaHa', 0) or 0)
                except (ValueError, TypeError):
                    area_ha = 0.0
                if key not in land_groups_dict:
                    land_groups_dict[key] = {'lot_numbers': [], 'facility_area_ha': 0.0, 'crops': {}}
                if lot_num:
                    land_groups_dict[key]['lot_numbers'].append(lot_num)
                land_groups_dict[key]['facility_area_ha'] += area_ha
                for crop in raw_land.get('crops', []):
                    name = crop.get('name', '').strip()
                    if name:
                        land_groups_dict[key]['crops'][name] = None  # 插入順序去重

            land_groups = [
                {
                    'land_town': k[0],
                    'land_section': k[1],
                    'lot_numbers': '、'.join(v['lot_numbers']),
                    'facility_area_ha': v['facility_area_ha'],
                    'crops_text': '、'.join(f'□{n}' for n in v['crops'].keys()),
                }
                for k, v in land_groups_dict.items()
            ] or [{'land_town': '', 'land_section': '', 'lot_numbers': '', 'facility_area_ha': 0.0, 'crops_text': ''}]

            row_data = {
                'case_number': grant_data.get('case_number', ''),
                'applicant_name': grant_data.get('applicant_name', ''),
                'land_groups': land_groups,
                'facility_type': facility_type,
                'irrigation_type': irrigation_type,
                'phone': grant_data.get('phone', ''),
                'address': grant_data.get('address', ''),
                'office_name': grant_data.get('office_name', ''),
            }
            excel_data.append(row_data)

        # 生成 Excel 檔案
        excel_service = ExcelGeneratorService()
        excel_file_path = await excel_service.generate_photograph_carry_form(
            excel_data,
            request.year,
            request.enable_pagination if request.enable_pagination is not None else True
        )

        # 生成下載檔名 - 使用英文避免編碼問題
        filename = f"photograph_carry_form_{request.year}.xlsx"

        # 返回檔案
        # 正確的中文檔名編碼處理
        encoded_filename = quote(filename, safe='')

        return FileResponse(
            path=excel_file_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成檔案失敗: {str(e)}")

@router.post("/check-data")
async def check_data_availability(
    request: DownloadRequest,
    current_user: Users = Depends(get_current_user)
):
    """檢查指定條件下是否有可下載的資料"""
    try:
        # 驗證參數
        if not request.year:
            raise HTTPException(status_code=400, detail="年度參數為必填")

        # 建構查詢條件（與實際下載邏輯相同）
        query = Grants.filter(year=int(request.year))
        if request.tag:
            query = query.filter(tag__icontains=request.tag)

        # 先取得所有該年度的案件
        all_grants = await query.all()

        # 在 Python 中進行案件編號範圍篩選
        filtered_grants = all_grants
        if request.case_number_start or request.case_number_end:
            filtered_grants = []
            for grant in all_grants:
                case_num = grant.case_number
                if case_num and case_num.isdigit():
                    case_num_int = int(case_num)

                    # 檢查範圍
                    in_range = True
                    if request.case_number_start and case_num_int < int(request.case_number_start):
                        in_range = False
                    if request.case_number_end and case_num_int > int(request.case_number_end):
                        in_range = False

                    if in_range:
                        filtered_grants.append(grant)

        # 計算符合條件的案件數量
        total_count = len(filtered_grants)

        if total_count > 0:
            return {
                "has_data": True,
                "total_count": total_count,
                "message": f"找到 {total_count} 筆符合條件的案件"
            }
        else:
            return {
                "has_data": False,
                "total_count": 0,
                "message": "未找到符合條件的案件資料"
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"檢查資料失敗: {str(e)}")

@router.post("/budget-book")
async def download_budget_book(
    request: DownloadRequest,
    current_user: Users = Depends(get_current_user)
):
    """下載工程預算書PDF"""
    try:
        # 驗證參數
        if not request.year:
            raise HTTPException(status_code=400, detail="年度參數為必填")

        # 建構查詢條件
        query = Grants.filter(year=int(request.year))
        if request.tag:
            query = query.filter(tag__icontains=request.tag)

        # 先取得所有該年度的案件
        all_grants = await query.select_related("active_version").all()

        # 在 Python 中進行案件編號範圍篩選
        grants = all_grants
        if request.case_number_start or request.case_number_end:
            grants = []
            for grant in all_grants:
                case_num = grant.case_number
                if case_num and case_num.isdigit():
                    case_num_int = int(case_num)

                    # 檢查範圍
                    in_range = True
                    if request.case_number_start and case_num_int < int(request.case_number_start):
                        in_range = False
                    if request.case_number_end and case_num_int > int(request.case_number_end):
                        in_range = False

                    if in_range:
                        grants.append(grant)

        # 輸出資料庫查詢結果統計
        print(f"=== 工程預算書查詢結果 ===")
        print(f"查詢年度: {request.year}")
        if request.case_number_start or request.case_number_end:
            print(f"案件編號範圍: {request.case_number_start or '起始'} - {request.case_number_end or '結束'}")
        print(f"符合條件的案件數量: {len(grants)}")
        print(f"=======================")

        if not grants:
            raise HTTPException(status_code=404, detail="找不到符合條件的案件")

        # 如果只有一個案件，生成單一PDF
        if len(grants) == 1:
            grant = grants[0]
            version_data = grant.active_version.all_steps_data if grant.active_version else {}

            # 提取並生成工程預算書
            grant_data = await extract_budget_statement_data(grant, version_data)
            pdf_bytes = BudgetStatementPDFGenerator().generate(grant_data)

            temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_pdf.write(pdf_bytes)
            temp_pdf.close()
            pdf_file_path = temp_pdf.name

            # 生成下載檔名
            filename = f"budget_book_{grant_data['case_number']}_{request.year}.pdf"

            # 正確的中文檔名編碼處理
            encoded_filename = quote(filename, safe='')

            # 返回檔案
            return FileResponse(
                path=pdf_file_path,
                filename=filename,
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
            )

        else:
            # 多個案件時，生成ZIP包含多個PDF
            # 創建臨時ZIP檔案
            temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
            temp_zip.close()

            pdf_generator = BudgetStatementPDFGenerator()
            generated_files = []

            try:
                with zipfile.ZipFile(temp_zip.name, 'w') as zip_file:
                    for grant in grants:
                        version_data = grant.active_version.all_steps_data if grant.active_version else {}

                        # 提取並生成工程預算書
                        grant_data = await extract_budget_statement_data(grant, version_data)
                        pdf_bytes = pdf_generator.generate(grant_data)

                        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                        temp_pdf.write(pdf_bytes)
                        temp_pdf.close()
                        generated_files.append(temp_pdf.name)

                        # 加入ZIP檔案（附加 grant.id 避免重複案號蓋檔）
                        pdf_filename = f"budget_book_{grant_data['case_number']}_{grant.id}.pdf"
                        zip_file.write(temp_pdf.name, pdf_filename)

                # 生成ZIP下載檔名
                zip_filename = f"budget_books_{request.year}.zip"
                if request.case_number_start or request.case_number_end:
                    zip_filename = f"budget_books_{request.year}_{request.case_number_start or 'start'}-{request.case_number_end or 'end'}.zip"

                # 正確的中文檔名編碼處理
                encoded_zip_filename = quote(zip_filename, safe='')

                # 返回ZIP檔案
                return FileResponse(
                    path=temp_zip.name,
                    filename=zip_filename,
                    media_type="application/zip",
                    headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_zip_filename}"}
                )

            finally:
                # 清理臨時PDF檔案
                for file_path in generated_files:
                    if os.path.exists(file_path):
                        os.unlink(file_path)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成工程預算書失敗: {str(e)}")

@router.post("/construction-photos")
async def download_construction_photos(
    request: DownloadRequest,
    current_user: Users = Depends(get_current_user)
):
    """下載施工前後照片（PDF 範本 + 原始照片 ZIP）"""
    try:
        if not request.year:
            raise HTTPException(status_code=400, detail="年度參數為必填")

        query = Grants.filter(year=int(request.year))
        if request.tag:
            query = query.filter(tag__icontains=request.tag)
        all_grants = await query.all()

        grants = all_grants
        if request.case_number_start or request.case_number_end:
            grants = []
            for grant in all_grants:
                case_num = grant.case_number
                if case_num and case_num.isdigit():
                    case_num_int = int(case_num)
                    in_range = True
                    if request.case_number_start and case_num_int < int(request.case_number_start):
                        in_range = False
                    if request.case_number_end and case_num_int > int(request.case_number_end):
                        in_range = False
                    if in_range:
                        grants.append(grant)

        if not grants:
            raise HTTPException(status_code=404, detail="找不到符合條件的案件")

        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        temp_zip.close()

        pdf_generator = ConstructionPhotosPDFGenerator()

        try:
            with zipfile.ZipFile(temp_zip.name, 'w') as zip_file:
                for grant in grants:
                    if len(grants) == 1:
                        pdf_basename = f"construction_photos_{grant.case_number}_{request.year}"
                    else:
                        pdf_basename = f"construction_photos_{grant.case_number}_{grant.id}"

                    grant_data = {
                        "case_number": str(grant.case_number) if grant.case_number else "",
                        "applicant_name": str(grant.applicant_name) if grant.applicant_name else ""
                    }
                    pdf_bytes = pdf_generator.generate(grant_data)
                    zip_file.writestr(f"{pdf_basename}.pdf", pdf_bytes)

                    before_attachments = await GrantAttachments.filter(
                        grant_id=grant.id,
                        step=3,
                        category='inspection_before',
                        status='active'
                    ).order_by('uploaded_at').all()

                    for idx, att in enumerate(before_attachments, start=1):
                        ext = os.path.splitext(att.original_filename)[1]
                        abs_path = settings.get_absolute_path(att.filepath)
                        photo_filename = f"{pdf_basename}_before_{idx}{ext}"
                        try:
                            zip_file.write(abs_path, photo_filename)
                        except (OSError, IOError) as e:
                            print(f"[警告] 讀取附件 {att.id} 失敗，略過：{e}")

                    after_attachments = await GrantAttachments.filter(
                        grant_id=grant.id,
                        step=7,
                        category='inspection_after',
                        status='active'
                    ).order_by('uploaded_at').all()

                    for idx, att in enumerate(after_attachments, start=1):
                        ext = os.path.splitext(att.original_filename)[1]
                        abs_path = settings.get_absolute_path(att.filepath)
                        photo_filename = f"{pdf_basename}_after_{idx}{ext}"
                        try:
                            zip_file.write(abs_path, photo_filename)
                        except (OSError, IOError) as e:
                            print(f"[警告] 讀取附件 {att.id} 失敗，略過：{e}")

            zip_filename = f"construction_photos_{request.year}.zip"
            if request.case_number_start or request.case_number_end:
                zip_filename = f"construction_photos_{request.year}_{request.case_number_start or 'start'}-{request.case_number_end or 'end'}.zip"

            encoded_zip_filename = quote(zip_filename, safe='')

            return FileResponse(
                path=temp_zip.name,
                filename=zip_filename,
                media_type="application/zip",
                headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_zip_filename}"}
            )

        finally:
            pass  # temp_zip 由 FileResponse 使用中，不在此清理

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成施工前後照片ZIP失敗: {str(e)}")


@router.post("/address-labels")
async def download_address_labels(
    request: DownloadRequest,
    current_user: Users = Depends(get_current_user)
):
    """下載住址標籤 Excel"""
    if not request.year:
        raise HTTPException(status_code=400, detail="年度參數為必填")

    query = Grants.filter(year=int(request.year))
    if request.tag:
        query = query.filter(tag__icontains=request.tag)
    all_grants = await query.all()

    grants = all_grants
    if request.case_number_start or request.case_number_end:
        grants = []
        for grant in all_grants:
            case_num = grant.case_number
            if case_num and case_num.isdigit():
                case_num_int = int(case_num)
                in_range = True
                if request.case_number_start and case_num_int < int(request.case_number_start):
                    in_range = False
                if request.case_number_end and case_num_int > int(request.case_number_end):
                    in_range = False
                if in_range:
                    grants.append(grant)

    if not grants:
        raise HTTPException(status_code=404, detail="找不到符合條件的案件")

    grants_data = [
        {
            "case_number": str(g.case_number or ""),
            "applicant_name": str(g.applicant_name or ""),
            "county": str(g.county or ""),
            "town": str(g.town or ""),
            "village": str(g.village or "") if g.village else "",
            "address": str(g.address or ""),
        }
        for g in grants
    ]

    excel_service = ExcelGeneratorService()
    file_path = await excel_service.generate_address_labels(grants_data, request.year)

    filename = f"address_labels_{request.year}.xlsx"
    encoded_filename = quote(filename, safe='')
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
    )


@router.post("/closing-docs")
async def download_closing_docs(
    request: DownloadRequest,
    current_user: Users = Depends(get_current_user)
):
    """下載結案文件合併 PDF（切結書 + 收據 + 結案申報書）"""
    try:
        if not request.year:
            raise HTTPException(status_code=400, detail="年度參數為必填")

        if (request.case_number_start and request.case_number_end and
                int(request.case_number_start) > int(request.case_number_end)):
            raise HTTPException(status_code=400, detail="案件號碼起始值不得大於結束值")

        query = Grants.filter(year=int(request.year))
        if request.tag:
            query = query.filter(tag__icontains=request.tag)
        all_grants = await query.select_related("active_version").all()

        grants = all_grants
        if request.case_number_start or request.case_number_end:
            grants = []
            for grant in all_grants:
                case_num = grant.case_number
                if case_num and case_num.isdigit():
                    case_num_int = int(case_num)
                    in_range = True
                    if request.case_number_start and case_num_int < int(request.case_number_start):
                        in_range = False
                    if request.case_number_end and case_num_int > int(request.case_number_end):
                        in_range = False
                    if in_range:
                        grants.append(grant)

        if not grants:
            raise HTTPException(status_code=404, detail="找不到符合條件的案件")

        generator = ClosingDocsPDFGenerator()
        all_pdf_bytes = []

        for grant in grants:
            version_data = grant.active_version.all_steps_data if grant.active_version else {}
            grant_data = await extract_budget_statement_data(grant, version_data)

            steps_data = version_data.get('steps', {})
            step2_data = steps_data.get('2', {})
            land_data = step2_data.get('lands', [])
            step4_data = steps_data.get('4', {})
            step5_data = steps_data.get('5', {})

            grant_pdf = generator.generate_for_grant(grant_data, land_data, step4_data, step5_data)
            all_pdf_bytes.append(grant_pdf)

        final_pdf = generator.merge_pdfs(all_pdf_bytes)

        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_pdf.write(final_pdf)
        temp_pdf.close()

        filename = f"closing_docs_{request.year}.pdf"
        if request.case_number_start or request.case_number_end:
            start = request.case_number_start or 'start'
            end = request.case_number_end or 'end'
            filename = f"closing_docs_{request.year}_{start}-{end}.pdf"

        encoded_filename = quote(filename, safe='')
        return FileResponse(
            path=temp_pdf.name,
            filename=filename,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成結案文件失敗: {str(e)}")


@router.post("/receipts")
async def download_receipts(
    request: DownloadRequest,
    current_user: Users = Depends(get_current_user)
):
    """批次下載領款收據合併 PDF（每案件一頁）"""
    try:
        if not request.year:
            raise HTTPException(status_code=400, detail="年度參數為必填")

        if (request.case_number_start and request.case_number_end and
                int(request.case_number_start) > int(request.case_number_end)):
            raise HTTPException(status_code=400, detail="案件號碼起始值不得大於結束值")

        query = Grants.filter(year=int(request.year))
        if request.tag:
            query = query.filter(tag__icontains=request.tag)
        all_grants = await query.select_related("active_version").order_by('case_number').all()

        grants = all_grants
        if request.case_number_start or request.case_number_end:
            grants = []
            for grant in all_grants:
                case_num = grant.case_number
                if case_num and case_num.isdigit():
                    case_num_int = int(case_num)
                    in_range = True
                    if request.case_number_start and case_num_int < int(request.case_number_start):
                        in_range = False
                    if request.case_number_end and case_num_int > int(request.case_number_end):
                        in_range = False
                    if in_range:
                        grants.append(grant)

        if not grants:
            raise HTTPException(status_code=404, detail="找不到符合條件的案件")

        all_pdf_bytes = []
        receipt_generator = BudgetStatementPDFGenerator()
        merger = ClosingDocsPDFGenerator()

        for grant in grants:
            version_data = grant.active_version.all_steps_data if grant.active_version else {}
            grant_data = await extract_budget_statement_data(grant, version_data)
            all_pdf_bytes.append(receipt_generator.generate_receipt(grant_data))

        final_pdf = merger.merge_pdfs(all_pdf_bytes)

        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_pdf.write(final_pdf)
        temp_pdf.close()

        filename = f"receipts_{request.year}.pdf"
        if request.case_number_start or request.case_number_end:
            start = request.case_number_start or 'start'
            end = request.case_number_end or 'end'
            filename = f"receipts_{request.year}_{start}-{end}.pdf"

        encoded_filename = quote(filename, safe='')
        return FileResponse(
            path=temp_pdf.name,
            filename=filename,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成收據 PDF 失敗: {str(e)}")


@router.post("/test-reports")
async def download_test_reports(
    request: DownloadRequest,
    current_user: Users = Depends(get_current_user)
):
    """批次下載功能測試現地勘查報告書合併 PDF（每案件一頁）"""
    try:
        if not request.year:
            raise HTTPException(status_code=400, detail="年度參數為必填")

        if (request.case_number_start and request.case_number_end and
                int(request.case_number_start) > int(request.case_number_end)):
            raise HTTPException(status_code=400, detail="案件號碼起始值不得大於結束值")

        query = Grants.filter(year=int(request.year))
        if request.tag:
            query = query.filter(tag__icontains=request.tag)
        all_grants = await query.select_related("active_version").order_by('case_number').all()

        grants = all_grants
        if request.case_number_start or request.case_number_end:
            grants = []
            for grant in all_grants:
                case_num = grant.case_number
                if case_num and case_num.isdigit():
                    case_num_int = int(case_num)
                    in_range = True
                    if request.case_number_start and case_num_int < int(request.case_number_start):
                        in_range = False
                    if request.case_number_end and case_num_int > int(request.case_number_end):
                        in_range = False
                    if in_range:
                        grants.append(grant)

        if not grants:
            raise HTTPException(status_code=404, detail="找不到符合條件的案件")

        all_pdf_bytes = []
        test_report_generator = BudgetStatementPDFGenerator()
        merger = ClosingDocsPDFGenerator()

        for grant in grants:
            version_data = grant.active_version.all_steps_data if grant.active_version else {}
            grant_data = await extract_budget_statement_data(grant, version_data)
            all_pdf_bytes.append(test_report_generator.generate_test_report(grant_data))

        final_pdf = merger.merge_pdfs(all_pdf_bytes)

        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_pdf.write(final_pdf)
        temp_pdf.close()

        filename = f"test_reports_{request.year}.pdf"
        if request.case_number_start or request.case_number_end:
            start = request.case_number_start or 'start'
            end = request.case_number_end or 'end'
            filename = f"test_reports_{request.year}_{start}-{end}.pdf"

        encoded_filename = quote(filename, safe='')
        return FileResponse(
            path=temp_pdf.name,
            filename=filename,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成功能測試報告書 PDF 失敗: {str(e)}")


@router.post("/review-form")
async def download_review_form(
    request: DownloadRequest,
    current_user: Users = Depends(get_current_user)
):
    """批次下載書面審查表合併 PDF（每案件一頁）"""
    try:
        if not request.year:
            raise HTTPException(status_code=400, detail="年度參數為必填")

        if (request.case_number_start and request.case_number_end and
                int(request.case_number_start) > int(request.case_number_end)):
            raise HTTPException(status_code=400, detail="案件號碼起始值不得大於結束值")

        query = Grants.filter(year=int(request.year))
        if request.tag:
            query = query.filter(tag__icontains=request.tag)
        all_grants = await query.select_related("active_version").order_by('case_number').all()

        grants = all_grants
        if request.case_number_start or request.case_number_end:
            grants = []
            for grant in all_grants:
                case_num = grant.case_number
                if case_num and case_num.isdigit():
                    case_num_int = int(case_num)
                    in_range = True
                    if request.case_number_start and case_num_int < int(request.case_number_start):
                        in_range = False
                    if request.case_number_end and case_num_int > int(request.case_number_end):
                        in_range = False
                    if in_range:
                        grants.append(grant)

        if not grants:
            raise HTTPException(status_code=404, detail="找不到符合條件的案件")

        all_pdf_bytes = []
        review_checklist_generator = BudgetStatementPDFGenerator()
        merger = ClosingDocsPDFGenerator()

        for grant in grants:
            version_data = grant.active_version.all_steps_data if grant.active_version else {}
            grant_data = await extract_budget_statement_data(grant, version_data)
            all_pdf_bytes.append(review_checklist_generator.generate_review_checklist(grant_data))

        final_pdf = merger.merge_pdfs(all_pdf_bytes)

        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_pdf.write(final_pdf)
        temp_pdf.close()

        filename = f"review_checklists_{request.year}.pdf"
        if request.case_number_start or request.case_number_end:
            start = request.case_number_start or 'start'
            end = request.case_number_end or 'end'
            filename = f"review_checklists_{request.year}_{start}-{end}.pdf"

        encoded_filename = quote(filename, safe='')
        return FileResponse(
            path=temp_pdf.name,
            filename=filename,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成書面審查表 PDF 失敗: {str(e)}")


@router.post("/cover-page")
async def download_cover_page(
    request: DownloadRequest,
    current_user: Users = Depends(get_current_user)
):
    """批次下載封面合併 PDF（每案件一頁）"""
    try:
        if not request.year:
            raise HTTPException(status_code=400, detail="年度參數為必填")

        if (request.case_number_start and request.case_number_end and
                int(request.case_number_start) > int(request.case_number_end)):
            raise HTTPException(status_code=400, detail="案件號碼起始值不得大於結束值")

        query = Grants.filter(year=int(request.year))
        if request.tag:
            query = query.filter(tag__icontains=request.tag)
        all_grants = await query.select_related("active_version").order_by('case_number').all()

        grants = all_grants
        if request.case_number_start or request.case_number_end:
            grants = []
            for grant in all_grants:
                case_num = grant.case_number
                if case_num and case_num.isdigit():
                    case_num_int = int(case_num)
                    in_range = True
                    if request.case_number_start and case_num_int < int(request.case_number_start):
                        in_range = False
                    if request.case_number_end and case_num_int > int(request.case_number_end):
                        in_range = False
                    if in_range:
                        grants.append(grant)

        if not grants:
            raise HTTPException(status_code=404, detail="找不到符合條件的案件")

        all_pdf_bytes = []
        cover_page_generator = BudgetStatementPDFGenerator()
        merger = ClosingDocsPDFGenerator()

        for grant in grants:
            version_data = grant.active_version.all_steps_data if grant.active_version else {}
            grant_data = await extract_budget_statement_data(grant, version_data)
            all_pdf_bytes.append(cover_page_generator.generate_cover_page(grant_data))

        final_pdf = merger.merge_pdfs(all_pdf_bytes)

        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_pdf.write(final_pdf)
        temp_pdf.close()

        filename = f"covers_{request.year}.pdf"
        if request.case_number_start or request.case_number_end:
            start = request.case_number_start or 'start'
            end = request.case_number_end or 'end'
            filename = f"covers_{request.year}_{start}-{end}.pdf"

        encoded_filename = quote(filename, safe='')
        return FileResponse(
            path=temp_pdf.name,
            filename=filename,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成封面 PDF 失敗: {str(e)}")


# ── 管路補助金額明細表所需的灌溉型式正規化映射 ─────────────────────────────────
_IRRIGATION_TYPE_MAP = {1: '穿孔管', 2: '噴頭', 3: '微噴', 4: '滴灌'}
_FUNDING_SOURCE_SHEETS = {0: '農水署明細表', 16: '七星明細表', 17: '瑠公明細表'}


async def extract_subsidy_row_data(grant, version_data: dict) -> dict:
    """
    萃取單筆案件的管路補助金額明細表資料列。
    複用 extract_budget_statement_data() 的全部資料萃取邏輯，
    並額外讀取 fundingSourceId 與灌溉型式短名。
    """
    base = await extract_budget_statement_data(grant, version_data)
    budget = base.get('budget_items', {})

    # 灌溉型式短名（供 E 欄顯示及分組合計使用）
    irrigation_type_id = base.get('irrigation_type_id', 0)
    irrigation_type = _IRRIGATION_TYPE_MAP.get(irrigation_type_id, '其它')

    # 設計者：歷史案件從 legacy_data.designer_name，新系統案件從 steps["5"].designerName
    steps = version_data.get('steps', {}) if version_data else {}
    if getattr(grant, 'is_legacy', False):
        legacy = (version_data or {}).get('legacy_data', {})
        designer = legacy.get('designer_name', '') or '未設定'
    else:
        designer = steps.get('5', {}).get('designerName', '') or '未設定'

    # fundingSourceId：優先新系統 steps['4']['fundingSourceId']，歷史資料回退
    step4_data = steps.get('4', {})
    fid = step4_data.get('fundingSourceId')
    if not (isinstance(fid, int) and fid in _FUNDING_SOURCE_SHEETS):
        legacy = (version_data or {}).get('legacy_data', {})
        fid = legacy.get('fundingSourceId')
        if not (isinstance(fid, int) and fid in _FUNDING_SOURCE_SHEETS):
            fid = 0

    area_ha = float(base.get('facility_area_ha', 0) or 0)
    end_facility = int(budget.get('govt_subsidy_a', 0))          # 末端設施 = A 項政府補助（不含農戶自付）
    control_facility = int(budget.get('govt_subsidy_c', 0))      # 調控設施 = C 項政府補助
    reservoir = int(budget.get('govt_subsidy_e', 0))             # 蓄水池 = E 項政府補助
    power_equipment = int(budget.get('govt_subsidy_d', 0))       # 動力設備 = D 項政府補助
    design_fee = int(budget.get('actual_subsidized_design_fee', 0))  # 設計費 = 政府實際補助設計費（B 項）
    farmer_contribution = max(0, int(budget.get('farmer_contribution', 0)))

    govt_subtotal = end_facility + control_facility + reservoir + power_equipment  # H欄水源設施固定為0
    total = govt_subtotal + design_fee
    grand_total = farmer_contribution + total
    if area_ha > 0:
        _area = Decimal(str(area_ha))
        per_ha_subsidy     = int((Decimal(str(end_facility)) / _area).to_integral_value(rounding=ROUND_DOWN))
        per_ha_grand_total = int((Decimal(str(grand_total))  / _area).to_integral_value(rounding=ROUND_DOWN))
    else:
        per_ha_subsidy     = 0
        per_ha_grand_total = 0

    # Q 欄百分比：補助費 / 總工程費，Decimal 精確計算至小數第二位，無條件捨去
    if per_ha_grand_total > 0:
        per_ha_pct = float(
            (Decimal(str(per_ha_subsidy)) / Decimal(str(per_ha_grand_total)))
            .quantize(Decimal('0.0001'), rounding=ROUND_DOWN)
        )
    else:
        per_ha_pct = None

    return {
        'funding_source_id': fid,
        'case_number': base.get('case_number', ''),
        'applicant_name': base.get('applicant_name', ''),
        'area_ha': area_ha,
        'location': base.get('land_town', ''),
        'irrigation_type': irrigation_type,
        'farmer_contribution': farmer_contribution,
        'end_facility': end_facility,
        'water_source': 0,
        'control_facility': control_facility,
        'reservoir': reservoir,
        'power_equipment': power_equipment,
        'govt_subtotal': govt_subtotal,
        'design_fee': design_fee,
        'total': total,
        'grand_total': grand_total,
        'per_ha_subsidy': int(per_ha_subsidy),
        'per_ha_pct': per_ha_pct,
        'per_ha_grand_total': per_ha_grand_total,
        'designer': designer,
    }


@router.post("/subsidy-details-list")
async def download_subsidy_details_list(
    request: SubsidyDetailsListRequest,
    current_user: Users = Depends(get_current_user)
):
    """下載管路補助金額明細表 XLSX（3 個工作表，依 fundingSourceId 分類）"""
    if not request.year:
        raise HTTPException(status_code=400, detail="年度為必填欄位")

    try:
        query = Grants.filter(year=int(request.year))
        if request.tag:
            query = query.filter(tag__icontains=request.tag)

        all_grants = await query.select_related("active_version").order_by('case_number').all()

        # 案件號碼範圍篩選（沿用現有端點的 Python 層篩選模式）
        grants = all_grants
        if request.case_number_start or request.case_number_end:
            grants = []
            for grant in all_grants:
                case_num = grant.case_number
                if case_num and case_num.isdigit():
                    case_num_int = int(case_num)
                    in_range = True
                    if request.case_number_start and case_num_int < int(request.case_number_start):
                        in_range = False
                    if request.case_number_end and case_num_int > int(request.case_number_end):
                        in_range = False
                    if in_range:
                        grants.append(grant)

        # 狀態篩選：排除已刪除及退件案件
        filtered = []
        for grant in grants:
            if not grant.is_legacy:
                if grant.status == 'deleted':
                    continue
            else:
                if grant.status == '99':
                    continue
                if grant.status_detail and '退件' in (grant.status_detail or ''):
                    continue
            filtered.append(grant)

        # 依 fundingSourceId 分配至三個工作表
        grants_by_sheet: dict = {'農水署明細表': [], '瑠公明細表': [], '七星明細表': []}
        skipped_cases = []
        for grant in filtered:
            try:
                version_data = grant.active_version.all_steps_data if grant.active_version else {}
                row_data = await extract_subsidy_row_data(grant, version_data)
                sheet_name = _FUNDING_SOURCE_SHEETS.get(row_data['funding_source_id'], '農水署明細表')
                grants_by_sheet[sheet_name].append(row_data)
            except Exception as row_err:
                skipped_cases.append(grant.case_number or str(grant.id))
                logger.warning("subsidy-details-list: skipped grant %s due to error: %s", grant.case_number, row_err)
                continue

        # 取得使用者所屬單位名稱（get_current_user 已載入 office）
        if not current_user.office:
            raise HTTPException(status_code=400, detail="使用者未綁定所屬單位，無法生成明細表")
        office_name = current_user.office.name

        # 生成 Excel 並回傳
        excel_service = ExcelGeneratorService()
        file_path = await excel_service.generate_subsidy_details_list(
            grants_by_sheet=grants_by_sheet,
            year=request.year,
            office_name=office_name,
        )

        filename = f"subsidy_details_list_{request.year}.xlsx"
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
        raise HTTPException(status_code=500, detail=f"生成明細表失敗：{str(e)}")


@router.get("/test")
async def test_download_endpoint():
    """測試下載端點是否正常"""
    return {"message": "下載服務正常運作", "available_types": ["photograph-carry-form", "budget-book", "static-files"]}

# === 靜態檔案下載 API ===

# 格式優先級排序（全域常數）
FORMAT_PRIORITY = {
    'csv': 1, 'doc': 2, 'docx': 3, 'odt': 4, 'pdf': 5, 'ppt': 6, 'pptx': 7,
    'txt': 8, 'xls': 9, 'xlsx': 10, 'zip': 11, 'rar': 12, 'jpg': 13,
    'jpeg': 14, 'png': 15, 'gif': 16, 'mp4': 17, 'avi': 18
}

def _get_format_sort_key(file_info):
    """取得格式排序鍵值"""
    format_lower = file_info["format"].lower()
    return (FORMAT_PRIORITY.get(format_lower, 999), format_lower)

def _scan_downloads_directory() -> dict:
    """掃描 downloads 目錄並分析檔案結構"""
    downloads_path = Path(settings.downloads_dir)

    if not downloads_path.exists():
        return {"files": [], "file_groups": {}}

    files = []
    file_groups = defaultdict(list)

    # 掃描所有檔案
    for file_path in downloads_path.rglob("*"):
        if file_path.is_file():
            try:
                stat_info = file_path.stat()
                base_name = file_path.stem
                format_ext = file_path.suffix.lower().lstrip('.')

                # 生成檔案ID（基於檔案路徑的hash）
                file_id = hashlib.md5(str(file_path.relative_to(downloads_path)).encode()).hexdigest()

                # 推測檔案類型
                category = _categorize_file(file_path.name, format_ext)

                file_info = {
                    "id": file_id,
                    "base_name": base_name,
                    "filename": file_path.name,
                    "format": format_ext,
                    "size": stat_info.st_size,
                    "created_at": datetime.fromtimestamp(stat_info.st_ctime),
                    "modified_at": datetime.fromtimestamp(stat_info.st_mtime),
                    "category": category,
                    "description": None,
                    "download_url": f"/download/static-file/{file_id}",
                    "file_path": file_path  # 內部使用
                }

                files.append(file_info)
                file_groups[base_name].append(file_info)

            except Exception as e:
                print(f"掃描檔案失敗 {file_path}: {e}")
                continue

    # 對每個群組內的檔案進行排序
    for base_name, group_files in file_groups.items():
        group_files.sort(key=_get_format_sort_key)

    return {"files": files, "file_groups": file_groups}

def _categorize_file(filename: str, format_ext: str) -> str:
    """根據檔名和格式推測檔案類型"""
    filename_lower = filename.lower()

    # 根據檔名關鍵字分類
    if any(keyword in filename_lower for keyword in ['統計', '報表', 'report', 'statistics']):
        return '統計報表'
    elif any(keyword in filename_lower for keyword in ['材料', 'material', '清單', 'list']):
        return '材料清單'
    elif any(keyword in filename_lower for keyword in ['表單', '範本', 'form', 'template']):
        return '表單範本'
    elif any(keyword in filename_lower for keyword in ['gis', '地圖', 'map', '圖層']):
        return 'GIS資料'
    elif any(keyword in filename_lower for keyword in ['系統', 'system', '文件', 'document']):
        return '系統文件'
    elif any(keyword in filename_lower for keyword in ['說明', 'manual', '手冊', 'guide']):
        return '說明文件'

    # 根據格式分類
    if format_ext in ['pdf']:
        return '文件資料'
    elif format_ext in ['xlsx', 'xls', 'csv']:
        return '表格資料'
    elif format_ext in ['doc', 'docx']:
        return '文字文件'
    elif format_ext in ['zip', 'rar']:
        return '壓縮檔案'
    elif format_ext in ['jpg', 'jpeg', 'png', 'gif']:
        return '圖像檔案'

    return '其他檔案'

@router.post("/static-files")
async def list_static_files(
    filter_request: StaticDownloadsFilterRequest,
    current_user: Users = Depends(get_current_user)
):
    """取得靜態下載檔案清單"""
    try:
        scan_result = _scan_downloads_directory()
        files = scan_result["files"]
        file_groups_dict = scan_result["file_groups"]

        # 建構檔案群組
        file_groups = []
        for base_name, group_files in file_groups_dict.items():
            # 排序檔案（使用全域格式優先級）
            group_files.sort(key=_get_format_sort_key)

            # 找出最新修改時間（用於 latest_modified）
            latest_modified = max(group_files, key=lambda x: x["modified_at"])["modified_at"]

            # 建立群組
            group = FileGroup(
                base_name=base_name,
                display_name=base_name,
                formats=[StaticFileInfo(**file_info) for file_info in group_files],
                category=group_files[0]["category"],  # 使用第一個檔案的分類
                description=None,
                total_files=len(group_files),
                latest_modified=latest_modified
            )
            file_groups.append(group)

        # 套用篩選
        filtered_groups = file_groups

        # 類型篩選
        if filter_request.category:
            filtered_groups = [g for g in filtered_groups if g.category == filter_request.category]

        # 格式篩選
        if filter_request.format:
            filtered_groups = [g for g in filtered_groups
                             if any(f.format == filter_request.format for f in g.formats)]

        # 關鍵字搜尋
        if filter_request.search_keyword:
            keyword = filter_request.search_keyword.lower()
            filtered_groups = [g for g in filtered_groups
                             if keyword in g.base_name.lower() or
                                keyword in (g.description or "").lower() or
                                keyword in g.category.lower()]

        # TODO: 實作時間範圍篩選
        if filter_request.date_range:
            pass  # 暫時跳過時間篩選實作

        # 排序（按最新修改時間）
        filtered_groups.sort(key=lambda x: x.latest_modified, reverse=True)

        # 收集所有類型
        categories = list(set(group.category for group in file_groups if group.category))
        categories.sort()

        return StaticDownloadsListResponse(
            file_groups=filtered_groups,
            total_groups=len(filtered_groups),
            total_files=sum(group.total_files for group in filtered_groups),
            categories=categories
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"掃描檔案失敗: {str(e)}")

def _validate_file_security(file_path: Path) -> bool:
    """檔案安全性驗證"""
    try:
        downloads_path = Path(settings.downloads_dir).resolve()
        file_path_resolved = file_path.resolve()

        # 確保檔案路徑在 downloads_dir 範圍內（防止路徑遍歷攻擊）
        if not str(file_path_resolved).startswith(str(downloads_path)):
            return False

        # 確保檔案存在且為一般檔案
        if not file_path_resolved.exists() or not file_path_resolved.is_file():
            return False

        # 檔案大小限制（100MB）
        max_size = 100 * 1024 * 1024
        if file_path_resolved.stat().st_size > max_size:
            return False

        return True
    except Exception:
        return False

@router.get("/static-file/{file_id}")
async def download_static_file(
    file_id: str,
    current_user: Users = Depends(get_current_user)
):
    """下載靜態檔案"""
    try:
        # 輸入驗證
        if not file_id or len(file_id) != 32 or not file_id.isalnum():
            raise HTTPException(status_code=400, detail="無效的檔案識別碼")

        scan_result = _scan_downloads_directory()
        files = scan_result["files"]

        # 尋找對應檔案
        target_file = None
        for file_info in files:
            if file_info["id"] == file_id:
                target_file = file_info
                break

        if not target_file:
            raise HTTPException(status_code=404, detail="檔案不存在")

        file_path = target_file["file_path"]

        # 安全性檢查
        if not _validate_file_security(file_path):
            raise HTTPException(status_code=403, detail="檔案存取被拒絕")

        # 獲取安全的 MIME 類型
        mime_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"

        # 防止執行檔下載
        dangerous_mimetypes = [
            'application/x-executable',
            'application/x-msdos-program',
            'application/x-msdownload',
            'application/x-bat'
        ]
        if mime_type in dangerous_mimetypes:
            raise HTTPException(status_code=403, detail="不允許下載此類型檔案")

        # 安全的檔案名稱處理
        safe_filename = target_file["filename"].replace('../', '').replace('..\\', '')

        # 正確的中文檔名編碼處理
        encoded_filename = quote(safe_filename, safe='')

        return FileResponse(
            path=str(file_path),
            filename=safe_filename,
            media_type=mime_type,
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "Cache-Control": "no-cache, no-store, must-revalidate"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"下載檔案錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail="下載檔案失敗")

@router.post("/static-files/batch")
async def batch_download_static_files(
    request: BatchDownloadRequest,
    current_user: Users = Depends(get_current_user)
):
    """批量下載靜態檔案"""
    try:
        # 輸入驗證
        if not request.file_ids:
            raise HTTPException(status_code=400, detail="未指定要下載的檔案")

        if len(request.file_ids) > 50:
            raise HTTPException(status_code=400, detail="一次最多只能下載50個檔案")

        # 驗證所有檔案ID格式
        for file_id in request.file_ids:
            if not file_id or len(file_id) != 32 or not file_id.isalnum():
                raise HTTPException(status_code=400, detail="無效的檔案識別碼")

        scan_result = _scan_downloads_directory()
        files = scan_result["files"]

        # 尋找對應檔案並進行安全性檢查
        target_files = []
        total_size = 0
        max_total_size = 500 * 1024 * 1024  # 500MB 總限制

        for file_info in files:
            if file_info["id"] in request.file_ids:
                file_path = file_info["file_path"]

                # 安全性檢查
                if not _validate_file_security(file_path):
                    continue

                target_files.append(file_info)
                total_size += file_info["size"]

                # 檢查總檔案大小限制
                if total_size > max_total_size:
                    raise HTTPException(status_code=413, detail="選取檔案總大小超出限制")

        if not target_files:
            raise HTTPException(status_code=404, detail="找不到可下載的檔案")

        # 建立臨時ZIP檔案
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip', prefix='aerc_batch_')
        temp_zip.close()

        try:
            with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_info in target_files:
                    file_path = file_info["file_path"]
                    # 安全的檔案名稱處理
                    safe_filename = file_info["filename"].replace('../', '').replace('..\\', '')
                    zip_file.write(str(file_path), safe_filename)

            # 安全的下載檔名處理
            download_name = request.download_name or f"batch_download_{len(target_files)}files"
            download_name = download_name.replace('../', '').replace('..\\', '')
            if not download_name.endswith('.zip'):
                download_name += '.zip'

            # 正確的中文檔名編碼處理
            encoded_download_name = quote(download_name, safe='')

            return FileResponse(
                path=temp_zip.name,
                filename=download_name,
                media_type="application/zip",
                headers={
                    "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_download_name}",
                    "X-Content-Type-Options": "nosniff",
                    "X-Frame-Options": "DENY",
                    "Cache-Control": "no-cache, no-store, must-revalidate"
                }
            )

        except Exception as e:
            # 清理臨時檔案
            if os.path.exists(temp_zip.name):
                try:
                    os.unlink(temp_zip.name)
                except Exception:
                    pass
            raise e

    except HTTPException:
        raise
    except Exception as e:
        print(f"批量下載錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail="批量下載失敗")