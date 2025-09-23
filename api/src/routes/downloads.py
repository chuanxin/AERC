from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from typing import Optional
from pydantic import BaseModel
from src.database.models import Grants, GrantVersions, Users
from src.auth.jwthandler import get_current_user
from src.services.excel_generator import ExcelGeneratorService
import os
import tempfile
import re

router = APIRouter(prefix="/download", tags=["File Downloads"])

class DownloadRequest(BaseModel):
    year: str
    case_number_start: Optional[str] = None
    case_number_end: Optional[str] = None
    file_type: str
    enable_pagination: Optional[bool] = True  # 分頁模式控制，預設開啟

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
            # 解析需要的欄位（從版本資料中取得）
            version_data = grant.active_version.all_steps_data if grant.active_version else {}
            row_data = {
                "case_number": str(grant.case_number) if grant.case_number else "",
                "applicant_name": str(grant.applicant_name) if grant.applicant_name else "",
                "county": str(grant.county) if grant.county else "",
                "town": str(grant.town) if grant.town else "",
                "address": str(grant.address) if grant.address else "",
                "office": str(grant.office) if grant.office else "",
                "undertracker": str(grant.undertracker) if grant.undertracker else "",
                "received_date": str(grant.received_date) if grant.received_date else "",
                "land_data": version_data.get("step2", {}) if version_data else {},
                "facility_data": version_data.get("step3", {}) if version_data else {},
            }
            excel_data.append(row_data)

        # 生成 Excel 檔案
        excel_service = ExcelGeneratorService()
        excel_file_path = await excel_service.generate_photograph_carry_form(
            excel_data,
            request.year,
            request.enable_pagination
        )

        # 生成下載檔名 - 使用英文避免編碼問題
        filename = f"photograph_carry_form_{request.year}.xlsx"

        # 返回檔案
        return FileResponse(
            path=excel_file_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
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

@router.get("/test")
async def test_download_endpoint():
    """測試下載端點是否正常"""
    return {"message": "下載服務正常運作", "available_types": ["photograph-carry-form"]}