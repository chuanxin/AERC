from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
import tempfile
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from src.config.upload_mappings import settings

class ExcelGeneratorService:
    """Excel 文件生成服務 - 基於範本驅動架構生成 .xlsx 檔案"""

    # 範本結構常數定義
    TEMPLATE_HEADER_ROWS = 3      # 標題區塊：第1-3列
    TEMPLATE_DATA_START_ROW = 4   # 資料區塊起始：第4列
    TEMPLATE_DATA_END_ROW = 19    # 資料區塊結束：第19列
    TEMPLATE_PAGE_ROW = 20        # 頁數列：第20列
    TEMPLATE_DATA_ROWS_PER_PAGE = 16  # 每頁資料列數：16列 (4-19)
    TEMPLATE_TOTAL_ROWS_PER_PAGE = 20 # 每頁總列數：20列 (1-20)

    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "aerc_excel_downloads"
        self.temp_dir.mkdir(exist_ok=True)

    async def generate_photograph_carry_form(self, data: List[Dict[str, Any]], year: str, enable_pagination: bool = True) -> str:
        """
        生成外出拍攝照片攜帶表 Excel 檔案 - 完全基於範本驅動

        範本結構定義：
        - 第1-3列：標題區塊（包含機構名稱、年度、表單標題、欄位標題）
        - 第4-19列：資料區塊樣本（16列資料格式範本）
        - 第20列：頁數列樣本

        Args:
            data: 案件資料列表
            year: 申請年度
            enable_pagination: 分頁模式控制
                - True: 分頁模式 - 每頁顯示標題列和頁數，每頁16筆資料
                - False: 不分頁模式 - 只有第一頁標題列，連續顯示所有資料，無頁數

        Returns:
            str: 生成的 Excel 檔案路徑
        """
        # 使用環境配置取得範本檔案路徑 - 跨平台相容
        template_path = settings.get_template_path("photograph_carry_form_template.xlsx")

        if not template_path.exists():
            raise FileNotFoundError(f"範本檔案不存在: {template_path}\n環境: {settings.environment}\n根目錄: {settings.data_root}")

        # 載入範本檔案
        from openpyxl import load_workbook
        workbook = load_workbook(str(template_path))
        worksheet = workbook.active

        # 更新年度
        worksheet['F1'] = year

        # 使用範本驅動的資料填寫邏輯
        return await self._fill_template_data(workbook, worksheet, data, year, enable_pagination)

    async def _fill_template_data(self, workbook, worksheet, data: List[Dict[str, Any]], year: str,
                                  enable_pagination: bool = True) -> str:
        """
        基於範本結構填寫資料 - 範本驅動架構

        範本結構參考（20列為一個完整頁面結構）：
        - 列1-3：標題區塊（機構名稱、年度、表單標題、欄位標題）
        - 列4-19：資料區塊（16列資料格式）
        - 列20：頁數列

        Args:
            workbook: Excel工作簿
            worksheet: 工作表
            data: 資料列表
            year: 年度
            enable_pagination: 分頁模式控制
                - True: 分頁模式 - 每頁16筆資料，複製範本結構到新頁
                - False: 不分頁模式 - 連續填充資料，只保留第一頁標題
        """
        # 根據分頁模式調整邏輯
        if enable_pagination:
            # 分頁模式：每頁資料列數由範本定義
            data_per_page = self.TEMPLATE_DATA_ROWS_PER_PAGE
            total_pages = max(1, (len(data) + data_per_page - 1) // data_per_page)
        else:
            # 不分頁模式：所有資料連續放置
            data_per_page = len(data)
            total_pages = 1

        # 輸出關鍵統計資訊
        print(f"=== Excel 生成統計 ===")
        print(f"分頁模式: {'啟用' if enable_pagination else '停用'}")
        print(f"總資料筆數: {len(data)}")
        print(f"計算總頁數: {total_pages}")
        print(f"===================")

        # 分頁模式：為每頁建立完整的標題組結構
        if enable_pagination:
            # 為第2頁及之後的每一頁建立標題組
            for page_num in range(2, total_pages + 1):
                # 每頁總列數由範本定義
                page_start_row = (page_num - 1) * self.TEMPLATE_TOTAL_ROWS_PER_PAGE + 1

                # 1. 複製主標題列
                self._copy_row_with_format(worksheet, 1, page_start_row)

                # 2. 複製空白列
                worksheet.row_dimensions[page_start_row + 1].height = worksheet.row_dimensions[2].height
                for col in range(1, 12):  # A-K 欄
                    empty_cell = worksheet.cell(row=page_start_row + 1, column=col)
                    empty_cell.value = None
                    empty_cell.border = Border()

                # 3. 複製欄位標題列
                self._copy_row_with_format(worksheet, self.TEMPLATE_HEADER_ROWS, page_start_row + 2)
        else:
            # 不分頁模式：預先清除範本的頁數資訊（避免干擾資料顯示）
            template_page_cell = worksheet.cell(row=self.TEMPLATE_PAGE_ROW, column=11)
            template_page_cell.value = None

        # 依序填入所有資料
        for item_idx, item in enumerate(data):
            if enable_pagination:
                # 分頁模式：計算當前是第幾頁和該頁的第幾筆資料
                current_page = item_idx // data_per_page + 1
                data_index_in_page = item_idx % data_per_page

                # 計算當前資料應該放在哪一列（基於範本結構）
                page_start_row = (current_page - 1) * self.TEMPLATE_TOTAL_ROWS_PER_PAGE
                current_row = page_start_row + self.TEMPLATE_DATA_START_ROW + data_index_in_page

                # 資料定位已計算完成
            else:
                # 不分頁模式：所有資料連續放置，從範本資料起始列開始
                current_row = self.TEMPLATE_DATA_START_ROW + item_idx
                # 資料定位已計算完成

            # 複製資料列格式（從範本資料起始列複製）
            # 注意：第一筆資料直接使用範本起始列，其他資料需要複製格式
            if item_idx > 0:  # 第一筆資料不需複製格式
                self._copy_row_with_format(worksheet, self.TEMPLATE_DATA_START_ROW, current_row)

            # 處理資料
            land_data = item.get('land_data', {})
            total_area = 0
            if isinstance(land_data, dict) and 'land_locations' in land_data:
                for location in land_data['land_locations']:
                    if isinstance(location, dict) and 'area' in location:
                        try:
                            total_area += float(location['area'])
                        except (ValueError, TypeError):
                            continue

            facility_data = item.get('facility_data', {})
            facility_types = []
            if isinstance(facility_data, dict):
                if 'irrigation_type' in facility_data:
                    facility_types.append(str(facility_data['irrigation_type']))
                if 'facility_type' in facility_data:
                    facility_types.append(str(facility_data['facility_type']))
            facility_type_str = ', '.join(facility_types) if facility_types else '未設定'

            # 填寫資料
            row_data = [
                str(item.get('case_number', '')),
                str(item.get('applicant_name', '')),
                '',  # 鄉鎮
                '',  # 段名
                '',  # 地號
                f"{total_area:.4f}" if total_area > 0 else '',
                facility_type_str,
                '',  # 末端型式
                '',  # 農作物
                '',  # 電話
                str(item.get('address', ''))
            ]

            for col_idx, value in enumerate(row_data, start=1):
                cell = worksheet.cell(row=current_row, column=col_idx, value=value)
                # 設定自動換行
                if cell.alignment:
                    alignment = cell.alignment.copy()
                    alignment.wrap_text = True
                    cell.alignment = alignment
                else:
                    cell.alignment = Alignment(wrap_text=True)

        # 輸出資料填寫結果統計
        print(f"=== 資料填寫結果 ===")
        print(f"總計填寫: {len(data)} 筆資料")
        if enable_pagination:
            print(f"分為 {total_pages} 頁顯示")
        else:
            print("不分頁連續顯示")
        print(f"=====================")

        # 根據分頁模式設定頁碼
        if enable_pagination:
            # 分頁模式：在每頁的頁數列顯示頁碼
            for page_num in range(1, total_pages + 1):
                # 計算頁數列位置：基於範本結構
                page_row = page_num * self.TEMPLATE_TOTAL_ROWS_PER_PAGE

                # 設定頁碼
                page_cell = worksheet.cell(row=page_row, column=11)
                page_cell.value = f'第{page_num}頁，共{total_pages}頁'

                # 複製頁碼格式（從範本頁數列）
                template_page_cell = worksheet.cell(row=self.TEMPLATE_PAGE_ROW, column=11)
                if template_page_cell.font:
                    page_cell.font = template_page_cell.font.copy()
                if template_page_cell.alignment:
                    page_cell.alignment = template_page_cell.alignment.copy()

                # 設定頁數列格式
                worksheet.row_dimensions[page_row].height = 14.3

                # 處理頁數列的邊框
                for col in range(1, 12):  # A-K 欄
                    cell = worksheet.cell(row=page_row, column=col)
                    if col == 11:  # K欄（頁碼欄）
                        if page_num == 1:
                            # 第一頁：移除左、右、下邊框，只保留上邊框
                            cell.border = Border(top=Side(style='thin'))
                        else:
                            # 其他頁：保持原有邊框
                            pass
                    else:
                        # A-J欄：清空內容並移除所有邊框
                        cell.value = None
                        cell.border = Border()
            print(f"頁碼設定完成: {total_pages} 頁")

        # 生成檔案
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"photograph_carry_form_{year}_{timestamp}.xlsx"
        file_path = self.temp_dir / filename

        try:
            workbook.save(str(file_path))
            return str(file_path)
        except Exception as e:
            print(f"Excel save error: {e}")
            print(f"File path: {file_path}")
            raise

    def _copy_row_with_format(self, worksheet, source_row, target_row):
        """複製整列的內容和格式"""
        for col in range(1, 12):  # A-K 欄
            source_cell = worksheet.cell(row=source_row, column=col)
            target_cell = worksheet.cell(row=target_row, column=col)

            # 複製內容和格式
            target_cell.value = source_cell.value
            if source_cell.font:
                target_cell.font = source_cell.font.copy()
            if source_cell.alignment:
                target_cell.alignment = source_cell.alignment.copy()
            if source_cell.border:
                target_cell.border = source_cell.border.copy()
            if source_cell.fill:
                target_cell.fill = source_cell.fill.copy()

        # 複製行高
        worksheet.row_dimensions[target_row].height = worksheet.row_dimensions[source_row].height

        # 如果是第1列（標題列），需要處理合併儲存格
        if source_row == 1:
            # 合併 C、D、E 欄為單一儲存格（財團法人農業工程研究中心）
            merge_range = f'C{target_row}:E{target_row}'
            worksheet.merge_cells(merge_range)

            # 合併 G、H、I 欄為單一儲存格（年度施工照片拍攝攜帶表）
            merge_range = f'G{target_row}:I{target_row}'
            worksheet.merge_cells(merge_range)

    def _remove_top_border(self, worksheet, row_num):
        """移除指定列的上邊框"""
        for col in range(1, 12):  # A-K 欄
            cell = worksheet.cell(row=row_num, column=col)
            if cell.border:
                # 保持其他邊框，只移除上邊框
                new_border = Border(
                    left=cell.border.left,
                    right=cell.border.right,
                    top=None,  # 移除上邊框
                    bottom=cell.border.bottom
                )
                cell.border = new_border

    def cleanup_temp_files(self, max_age_hours: int = 24):
        """清理超過指定時間的臨時檔案"""
        import time

        current_time = time.time()
        max_age_seconds = max_age_hours * 3600

        for file_path in self.temp_dir.glob("*.xls"):
            if current_time - file_path.stat().st_mtime > max_age_seconds:
                try:
                    file_path.unlink()
                except OSError:
                    pass  # 忽略刪除失敗的檔案