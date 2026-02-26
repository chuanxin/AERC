from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
import tempfile
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from copy import copy
from src.config.folder_mappings import settings

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
                    alignment = copy(cell.alignment)
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
                    page_cell.font = copy(template_page_cell.font)
                if template_page_cell.alignment:
                    page_cell.alignment = copy(template_page_cell.alignment)

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
                target_cell.font = copy(source_cell.font)
            if source_cell.alignment:
                target_cell.alignment = copy(source_cell.alignment)
            if source_cell.border:
                target_cell.border = copy(source_cell.border)
            if source_cell.fill:
                target_cell.fill = copy(source_cell.fill)

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

    async def generate_a01_execution_progress_report(
        self,
        data: Dict[str, Any],
        year: int
    ) -> str:
        """
        生成 A01 各管理處執行進度報表 Excel 檔案

        範本驅動 + 動態增長架構：
        - 範本 A01.xlsx 提供：標題格式、欄寬、資料列樣式參考（Row 4）、備註文字
        - 程式碼負責：清除範例資料 → 動態寫入實際資料 → 備註跟隨資料尾端

        Args:
            data: ExecutionProgressResponse 資料（包含 offices、total_* 等欄位）
            year: 統計年度（民國年）

        Returns:
            str: 生成的 Excel 檔案路徑
        """
        from openpyxl import load_workbook
        from openpyxl.styles import Border

        template_path = settings.get_template_path("A01.xlsx")
        if not template_path.exists():
            raise FileNotFoundError(f"範本檔案不存在: {template_path}")

        workbook = load_workbook(str(template_path))
        worksheet = workbook.active

        DATA_START_ROW = 4  # 範本中資料區塊起始列（同時作為樣式參考列）

        # 1. 從範本擷取樣式參考（Row 4 的每欄格式 + 表頭外框粗細）
        HEADER_ROW = 3
        col_styles = {}
        frame_bottom_sides = {}
        for col in range(1, 7):
            ref_cell = worksheet.cell(row=DATA_START_ROW, column=col)
            col_styles[col] = {
                'font': copy(ref_cell.font) if ref_cell.font else None,
                'alignment': copy(ref_cell.alignment) if ref_cell.alignment else None,
                'border': copy(ref_cell.border) if ref_cell.border else None,
                'fill': copy(ref_cell.fill) if ref_cell.fill else None,
                'number_format': ref_cell.number_format,
            }
            # 表頭底部邊框 = 表格外框粗細（用於最後一列資料的底線）
            header_cell = worksheet.cell(row=HEADER_ROW, column=col)
            if header_cell.border and header_cell.border.bottom:
                frame_bottom_sides[col] = header_cell.border.bottom

        # 2. 擷取備註（解除 Row 4 以下的所有合併儲存格）
        footnote_text = None
        footnote_font = None
        footnote_alignment = None
        footnote_row_height = None
        footnote_rich_text = None  # 保存 Rich Text 數據
        for merge in list(worksheet.merged_cells.ranges):
            if merge.min_row >= DATA_START_ROW:
                cell = worksheet.cell(row=merge.min_row, column=1)
                # 檢查是否為 Rich Text（部分文字有不同格式）
                if hasattr(cell, '_value') and hasattr(cell._value, '__iter__') and not isinstance(cell._value, str):
                    # 保存 Rich Text 數據（包含所有格式信息）
                    footnote_rich_text = cell._value
                    footnote_text = cell.value  # 保存純文字作為後備
                else:
                    footnote_text = cell.value
                footnote_font = copy(cell.font) if cell.font else None
                footnote_alignment = copy(cell.alignment) if cell.alignment else None
                footnote_row_height = worksheet.row_dimensions[merge.min_row].height
                worksheet.unmerge_cells(str(merge))

        # 3. 清除範本的範例資料（Row 4 到最後一行：內容、邊框、行高）
        max_row = worksheet.max_row
        for row in range(DATA_START_ROW, max_row + 1):
            for col in range(1, 7):
                cell = worksheet.cell(row=row, column=col)
                cell.value = None
                cell.border = Border()
            # 重置行高（移除範本殘留的自訂行高）
            if row in worksheet.row_dimensions:
                del worksheet.row_dimensions[row]

        # 4. 更新標題和製表日期
        worksheet['A1'].value = (
            f"農業部農田水利署\n推廣管路灌溉設施計畫\n{year}年度各管理處執行進度"
        )
        today = datetime.now()
        date_str = f"製表日期：{today.year - 1911}年{today.month:02d}月{today.day:02d}日"
        self._set_cell_value_safe(worksheet, 'E2', date_str)

        # 5. 動態寫入資料列（套用範本樣式）
        offices = data.get('offices', [])
        for idx, office in enumerate(offices):
            row = DATA_START_ROW + idx
            row_values = [
                office.get('office_name', ''),
                office.get('approved_budget', 0) or 0,
                office.get('completed_cases', 0) or 0,
                float(office.get('total_area', 0) or 0),
                office.get('total_subsidy', 0) or 0,
                float(office.get('execution_rate', 0) or 0),
            ]
            for col, value in enumerate(row_values, start=1):
                cell = worksheet.cell(row=row, column=col, value=value)
                style = col_styles[col]
                if style['font']:
                    cell.font = style['font']
                if style['alignment']:
                    cell.alignment = style['alignment']
                if style['border']:
                    cell.border = style['border']
                if style['fill']:
                    cell.fill = style['fill']
                if style['number_format']:
                    cell.number_format = style['number_format']

        # 5.1 最後一列資料套用表格外框底線（與表頭粗細一致）
        if offices:
            last_row = DATA_START_ROW + len(offices) - 1
            for col in range(1, 7):
                cell = worksheet.cell(row=last_row, column=col)
                if col in frame_bottom_sides and cell.border:
                    cell.border = Border(
                        left=cell.border.left,
                        right=cell.border.right,
                        top=cell.border.top,
                        bottom=frame_bottom_sides[col],
                    )

        # 6. 動態定位備註（緊跟資料尾端，空一行）
        if footnote_text:
            footnote_row = DATA_START_ROW + len(offices) + 1
            worksheet.merge_cells(f"A{footnote_row}:F{footnote_row}")
            cell = worksheet.cell(row=footnote_row, column=1)
            
            # 優先使用 Rich Text（保留底線等格式），否則使用純文字
            if footnote_rich_text:
                cell._value = footnote_rich_text
                cell.data_type = 's'  # 設定為字串類型
            else:
                cell.value = footnote_text
                
            if footnote_font:
                cell.font = footnote_font
            if footnote_alignment:
                cell.alignment = footnote_alignment
            if footnote_row_height:
                worksheet.row_dimensions[footnote_row].height = footnote_row_height

        # 7. 生成檔案
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"A01_execution_progress_{year}_{timestamp}.xlsx"
        file_path = self.temp_dir / filename

        try:
            workbook.save(str(file_path))
            return str(file_path)
        except Exception as e:
            print(f"Excel save error: {e}")
            raise

    # ==================== A02 系列統計報表 ====================

    def _set_cell_value_safe(self, worksheet, cell_ref: str, value):
        """
        安全地設定單元格值（處理合併單元格）

        如果目標單元格是合併單元格的一部分，會自動使用合併區域的左上角單元格
        """
        from openpyxl.utils import coordinate_to_tuple

        row, col = coordinate_to_tuple(cell_ref)

        # 檢查是否在合併單元格中
        for merge_range in worksheet.merged_cells.ranges:
            if (merge_range.min_row <= row <= merge_range.max_row and
                merge_range.min_col <= col <= merge_range.max_col):
                # 使用合併區域的左上角單元格
                worksheet.cell(row=merge_range.min_row, column=merge_range.min_col).value = value
                return

        # 不在合併單元格中，直接賦值
        worksheet[cell_ref] = value

    def _set_cell_value_safe_by_position(self, worksheet, row: int, col: int, value):
        """
        安全地設定單元格值（使用行列位置，處理合併單元格）

        Args:
            worksheet: Excel worksheet
            row: 行號（1-based）
            col: 列號（1-based）
            value: 要設定的值
        """
        from openpyxl.cell.cell import MergedCell

        cell = worksheet.cell(row=row, column=col)

        # 如果是合併單元格，找到合併區域的左上角單元格
        if isinstance(cell, MergedCell):
            for merge_range in worksheet.merged_cells.ranges:
                if (merge_range.min_row <= row <= merge_range.max_row and
                    merge_range.min_col <= col <= merge_range.max_col):
                    worksheet.cell(row=merge_range.min_row, column=merge_range.min_col).value = value
                    return
        else:
            # 不是合併單元格，直接設定
            cell.value = value

    # ── 範本一致性工具組 ─────────────────────────────────────────────────────
    # 以下六個靜態方法封裝了「範本驅動 Excel 生成」時常見的樣式一致性問題，
    # 供所有動態報表方法複用，避免在每份報表中重複解決相同的 openpyxl 陷阱。

    @staticmethod
    def _tpl_save_col_widths(ws) -> dict:
        """
        讀取工作表所有欄寬並展開為 {欄索引: 寬度} 字典。

        必要性：openpyxl 的 DimensionHolder 可能以 min/max 範圍儲存欄寬
        （例如 min=3, max=5, width=12.5 表示第3~5欄都是12.5），
        直接用欄字母查詢只能取到範圍的代表欄，其他欄無法命中。
        本方法將範圍展開為扁平字典，讓任意欄索引都可查到正確寬度。

        使用時機：在任何修改工作表之前呼叫，以保留範本原始欄寬。
        """
        from openpyxl.utils import column_index_from_string
        widths: dict[int, float] = {}
        for col_letter, dim in ws.column_dimensions.items():
            min_col = dim.min or column_index_from_string(col_letter)
            max_col = dim.max or min_col
            if dim.width and dim.width > 0:
                for idx in range(min_col, max_col + 1):
                    widths[idx] = dim.width
        return widths

    @staticmethod
    def _tpl_apply_col_widths(
        ws,
        saved_widths: dict,
        src_col_start: int,
        src_count: int,
        dst_col_start: int,
    ) -> None:
        """
        將已儲存的欄寬套用到動態新增的欄位群。

        Args:
            ws: 工作表
            saved_widths: _tpl_save_col_widths 回傳的字典
            src_col_start: 來源欄群的起始欄索引（範本中的樣本欄）
            src_count: 欄群欄數（每個重複單元的欄數）
            dst_col_start: 目標欄群的起始欄索引（新增的欄）
        """
        from openpyxl.utils import get_column_letter
        for j in range(src_count):
            src_idx = src_col_start + j
            dst_letter = get_column_letter(dst_col_start + j)
            if src_idx in saved_widths:
                ws.column_dimensions[dst_letter].width = saved_widths[src_idx]

    @staticmethod
    def _tpl_capture_row_borders(ws, row: int, col_start: int, count: int) -> list:
        """
        擷取指定列連續欄的邊框（必須在 unmerge 之後呼叫）。

        必要性：openpyxl 讀取合併格非左上角格的邊框會得到空值（MergedCell 無樣式），
        必須先 unmerge_cells 讓這些格恢復為普通格，才能正確讀取右邊界欄的外框線。

        Returns:
            list[Border]：長度為 count 的邊框列表（deep copy）
        """
        return [copy(ws.cell(row, col_start + j).border) for j in range(count)]

    @staticmethod
    def _tpl_merge_horizontal(
        ws,
        row: int,
        col_start: int,
        col_count: int,
        borders: list,
    ) -> None:
        """
        橫向合併儲存格並保留各欄邊框。

        必要性：openpyxl 的 merge_cells 會保留合併範圍各欄的 border 資料並寫入 XML，
        但若在合併之後才設定邊框，右邊界欄的右外框可能遺失。
        正確做法：先對每欄設定邊框，再執行合併，Excel 即可正確顯示四邊完整框線。

        Args:
            ws: 工作表
            row: 列號
            col_start: 合併起始欄索引
            col_count: 合併欄數
            borders: 長度為 col_count 的邊框列表（對應每欄的邊框）
        """
        for j in range(col_count):
            ws.cell(row, col_start + j).border = borders[j]
        ws.merge_cells(
            start_row=row, start_column=col_start,
            end_row=row, end_column=col_start + col_count - 1,
        )

    @staticmethod
    def _tpl_force_interior_border(ws, row: int, col: int, border) -> None:
        """
        強制注入邊框到垂直合併格的底端格。

        必要性：openpyxl 的 merge_cells 會從 ws._cells 中刪除非左上角格（底端格），
        導致對底端格設定的邊框在合併後消失。
        Excel 讀取垂直合併格時，底端格若無明確 XML 樣式，該格行高區域的左/下框線不顯示。
        本方法在合併之後建立新的 Cell 物件並直接注入 ws._cells，繞過此限制。

        使用時機：固定欄（縱向合併 HDR1:HDR2）的底端列邊框設定，須在 merge_cells 之後呼叫。

        Args:
            ws: 工作表
            row: 底端格的列號
            col: 底端格的欄號
            border: 要注入的 Border 物件
        """
        from openpyxl.cell.cell import Cell as _OxlCell
        interior = _OxlCell(worksheet=ws, row=row, column=col)
        interior.border = border
        ws._cells[(row, col)] = interior

    @staticmethod
    def _tpl_inner_style(style_dict: dict) -> dict:
        """
        將資料列樣式的 thick/medium 邊框降為 thin（用於表格內部分隔線）。

        必要性（雙重陷阱）：
        1. bottom：範本最後一筆資料列通常帶粗底線（外框底線），若原樣套用到所有資料列，
           每列底部都會變粗。
        2. top：相鄰列視覺邊框 = MAX(上列.bottom, 本列.top)。若本列.top 為粗線
           （HDR2↔資料列的外框上線），後續列的分隔線也會顯示為粗線。
        本方法同時處理 top 和 bottom，確保表格內部所有分隔線維持細線。
        最末列的粗底線由呼叫端統一套用（_tpl_frame_bottom），不在此處處理。

        Returns:
            新的樣式字典（不修改原字典）
        """
        b = style_dict.get('border')
        if not b:
            return style_dict

        def _thin_if_heavy(side):
            if side and getattr(side, 'style', None) in ('thick', 'medium'):
                return Side(style='thin')
            return side

        s2 = dict(style_dict)
        s2['border'] = Border(
            left=b.left,
            right=b.right,
            top=_thin_if_heavy(b.top),
            bottom=_thin_if_heavy(b.bottom),
        )
        return s2

    def _generate_a02_report(
        self,
        template_name: str,
        col_count: int,
        title_text: str,
        date_text: str,
        rows: List[List[Any]],
        filename_prefix: str,
    ) -> str:
        """
        A02 報表通用生成邏輯（範本驅動 + 動態增長）

        架構與 A01 完全一致：
        - 範本提供：標題格式、欄寬、Row 4 樣式參考、備註文字
        - 程式碼：清除範例 → 動態寫入 → 備註跟隨尾端
        """
        from openpyxl import load_workbook
        from openpyxl.styles import Border
        from openpyxl.cell.cell import MergedCell

        template_path = settings.get_template_path(template_name)
        if not template_path.exists():
            raise FileNotFoundError(f"範本檔案不存在: {template_path}")

        workbook = load_workbook(str(template_path))
        worksheet = workbook.active

        # 移除 Print Area 定義以避免警告
        if 'Print_Area' in workbook.defined_names:
            del workbook.defined_names['Print_Area']

        DATA_START_ROW = 4
        HEADER_ROW = 3

        # 1. 從範本擷取樣式參考（Row 4）
        col_styles = {}
        frame_bottom_sides = {}
        for col in range(1, col_count + 1):
            ref_cell = worksheet.cell(row=DATA_START_ROW, column=col)
            col_styles[col] = {
                'font': copy(ref_cell.font) if ref_cell.font else None,
                'alignment': copy(ref_cell.alignment) if ref_cell.alignment else None,
                'border': copy(ref_cell.border) if ref_cell.border else None,
                'fill': copy(ref_cell.fill) if ref_cell.fill else None,
                'number_format': ref_cell.number_format,
            }
            # 表頭底部邊框 = 表格外框粗細（用於最後一列資料的底線）
            header_cell = worksheet.cell(row=HEADER_ROW, column=col)
            if (header_cell.border and header_cell.border.bottom
                    and getattr(header_cell.border.bottom, 'style', None)):
                frame_bottom_sides[col] = header_cell.border.bottom

        # 2. 擷取備註
        footnote_text = None
        footnote_font = None
        footnote_alignment = None
        footnote_row_height = None
        footnote_rich_text = None
        last_col_letter = get_column_letter(col_count)
        for merge in list(worksheet.merged_cells.ranges):
            if merge.min_row >= DATA_START_ROW:
                cell = worksheet.cell(row=merge.min_row, column=1)
                if hasattr(cell, '_value') and hasattr(cell._value, '__iter__') and not isinstance(cell._value, str):
                    footnote_rich_text = cell._value
                    footnote_text = cell.value
                else:
                    footnote_text = cell.value
                footnote_font = copy(cell.font) if cell.font else None
                footnote_alignment = copy(cell.alignment) if cell.alignment else None
                footnote_row_height = worksheet.row_dimensions[merge.min_row].height
                worksheet.unmerge_cells(str(merge))

        # 3. 清除範例資料
        max_row = worksheet.max_row
        for row in range(DATA_START_ROW, max_row + 1):
            for col in range(1, col_count + 1):
                cell = worksheet.cell(row=row, column=col)
                # 跳過合併單元格（MergedCell 的 value 是唯讀的）
                if not isinstance(cell, MergedCell):
                    cell.value = None
                    cell.border = Border()
            if row in worksheet.row_dimensions:
                del worksheet.row_dimensions[row]

        # 4. 更新標題和日期
        self._set_cell_value_safe_by_position(worksheet, 1, 1, title_text)
        self._set_cell_value_safe(worksheet, f'{last_col_letter}2', date_text)

        # 5. 動態寫入資料列
        for idx, row_values in enumerate(rows):
            row = DATA_START_ROW + idx
            for col, value in enumerate(row_values, start=1):
                cell = worksheet.cell(row=row, column=col, value=value)
                style = col_styles[col]
                
                # 套用字體、對齊、填充、數字格式
                if style['font']:
                    cell.font = style['font']
                if style['alignment']:
                    cell.alignment = style['alignment']
                if style['border']:
                    cell.border = style['border']
                if style['fill']:
                    cell.fill = style['fill']
                if style['number_format']:
                    cell.number_format = style['number_format']

        # 5.1 最後一列資料套用表格外框底線（與表頭粗細一致，同 A01 邏輯）
        if rows:
            from openpyxl.styles import Side as BottomSide
            default_bottom = BottomSide(style='medium')
            last_row = DATA_START_ROW + len(rows) - 1
            for col in range(1, col_count + 1):
                cell = worksheet.cell(row=last_row, column=col)
                bottom_side = frame_bottom_sides.get(col)
                if not bottom_side or not getattr(bottom_side, 'style', None):
                    bottom_side = default_bottom
                if cell.border:
                    cell.border = Border(
                        left=cell.border.left,
                        right=cell.border.right,
                        top=cell.border.top,
                        bottom=bottom_side,
                    )
                else:
                    cell.border = Border(bottom=bottom_side)

        # 6. 動態定位備註
        if footnote_text:
            footnote_row = DATA_START_ROW + len(rows) + 1
            worksheet.merge_cells(f"A{footnote_row}:{last_col_letter}{footnote_row}")
            cell = worksheet.cell(row=footnote_row, column=1)
            if footnote_rich_text:
                cell._value = footnote_rich_text
                cell.data_type = 's'
            else:
                cell.value = footnote_text
            if footnote_font:
                cell.font = footnote_font
            if footnote_alignment:
                cell.alignment = footnote_alignment
            if footnote_row_height:
                worksheet.row_dimensions[footnote_row].height = footnote_row_height

        # 7. 儲存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.xlsx"
        file_path = self.temp_dir / filename
        workbook.save(str(file_path))
        return str(file_path)

    async def generate_a02_1_report(self, data: Dict[str, Any], year: int) -> str:
        """生成 A02-1 各縣市鄉鎮區統計報表"""
        today = datetime.now()
        rows = []
        for s in data.get('stats', []):
            rows.append([
                s.get('county_name', ''),
                s.get('town_name', ''),
                s.get('completed_cases', 0) or 0,
                float(s.get('total_area', 0) or 0),
                s.get('total_subsidy', 0) or 0,
            ])
        return self._generate_a02_report(
            template_name="A02-1.xlsx",
            col_count=5,
            title_text=f"農業部農田水利署\n推廣管路灌溉設施計畫\n{year}年度各縣市鄉鎮區統計",
            date_text=f"製表日期：{today.year - 1911}年{today.month:02d}月{today.day:02d}日",
            rows=rows,
            filename_prefix=f"A02-1_{year}",
        )

    async def generate_a02_2_report(self, data: Dict[str, Any], year: int) -> str:
        """生成 A02-2 各管理處統計報表"""
        today = datetime.now()
        rows = []
        for s in data.get('stats', []):
            rows.append([
                s.get('office_name', ''),
                s.get('completed_cases', 0) or 0,
                float(s.get('total_area', 0) or 0),
                s.get('total_subsidy', 0) or 0,
            ])
        return self._generate_a02_report(
            template_name="A02-2.xlsx",
            col_count=4,
            title_text=f"農業部農田水利署\n推廣管路灌溉設施計畫\n{year}年度各管理處統計",
            date_text=f"製表日期：{today.year - 1911}年{today.month:02d}月{today.day:02d}日",
            rows=rows,
            filename_prefix=f"A02-2_{year}",
        )

    async def generate_a02_3_report(self, data: Dict[str, Any]) -> str:
        """生成 A02-3 歷年各縣市鄉鎮區統計報表（範本驅動橫向年度展開）"""
        return self._generate_a02_yearly_report(
            template_name="A02-3.xlsx",
            fixed_cols=2,
            data=data,
            filename_prefix=f"A02-3_{data.get('start_year', '')}-{data.get('end_year', '')}",
            show_total=False,
        )

    async def generate_a02_4_report(self, data: Dict[str, Any]) -> str:
        """生成 A02-4 歷年各管理處統計報表（範本驅動橫向年度展開）"""
        return self._generate_a02_yearly_report(
            template_name="A02-4.xlsx",
            fixed_cols=1,
            data=data,
            filename_prefix=f"A02-4_{data.get('start_year', '')}-{data.get('end_year', '')}",
            show_total=False,
        )

    def _generate_a02_yearly_report(
        self,
        template_name: str,
        fixed_cols: int,
        data: Dict[str, Any],
        filename_prefix: str,
        show_total: bool = True,
    ) -> str:
        """
        A02-3/A02-4 橫向年度展開報表生成（範本驅動 + 橫向欄組動態擴展）

        範本結構（7 列固定）：
          Row 1: 標題（合併全欄）
          Row 2: 表號(A2) + 製表日期（右側合併）
          Row 3: 固定欄頭（合併 row3:4）+ 樣本年度合併欄頭
          Row 4: 指標子欄頭（補助案件數 / 補助面積 / 補助金額）
          Row 5: 樣本資料列（邊框樣式參考）
          Row 6: 樣本合計列（邊框樣式參考）
          Row 7: 備註（合併全欄）

        生成步驟：
          1. 擷取所有樣式（Rows 3-7）
          2. unmerge_all + 清除 Row 3+ 內容
          3. 重建 Row 1 合併至 total_cols
          4. 重建 Row 2 日期（最後兩欄合併）
          5. 重建 Row 3（固定欄頭合併 row3:4 + N 年度合併欄頭）
          6. 重建 Row 4（N×3 指標子欄頭）
          7. 寫入資料列（Row 5+）
          8. 寫入合計列
          9. 寫入備註列（合併至 total_cols）
        """
        from openpyxl import load_workbook
        from openpyxl.styles import Border
        from openpyxl.cell.cell import MergedCell
        from decimal import Decimal as _Decimal
        import re

        template_path = settings.get_template_path(template_name)
        if not template_path.exists():
            raise FileNotFoundError(f"範本檔案不存在: {template_path}")

        workbook = load_workbook(str(template_path))
        ws = workbook.active

        if 'Print_Area' in workbook.defined_names:
            del workbook.defined_names['Print_Area']

        years = data.get('years', [])
        rows_data = data.get('rows', [])
        start_year = data.get('start_year', 0)
        end_year_val = data.get('end_year', 0)
        N = len(years)
        total_cols = fixed_cols + N * 3

        SAMPLE_YEAR_START_COL = fixed_cols + 1
        HDR1 = 3   # Row 3: 年度合併欄頭 + 固定欄頭（合併 row3:4）
        HDR2 = 4   # Row 4: 指標子欄頭
        DATA_START = 5
        TPL_TOTAL = 6
        TPL_NOTE = 7

        def _grab(cell):
            """擷取儲存格樣式為可複製字典"""
            return {
                'font': copy(cell.font),
                'alignment': copy(cell.alignment),
                'border': copy(cell.border),
                'fill': copy(cell.fill),
                'number_format': cell.number_format,
            }

        def _apply(cell, s):
            """套用樣式字典到儲存格"""
            if s.get('font'):        cell.font = s['font']
            if s.get('alignment'):   cell.alignment = s['alignment']
            if s.get('border'):      cell.border = s['border']
            if s.get('fill'):        cell.fill = s['fill']
            if s.get('number_format'): cell.number_format = s['number_format']

        # ── 0. 前置作業：儲存欄寬 + 解除合併（取得合併格各欄真實邊框）────
        col_widths_by_idx = self._tpl_save_col_widths(ws)

        for mr in list(ws.merged_cells.ranges):
            ws.unmerge_cells(str(mr))

        # 解除合併後各欄恢復為普通格，可正確讀取右邊界欄的真實邊框
        year_hdr_col_borders = self._tpl_capture_row_borders(ws, HDR1, SAMPLE_YEAR_START_COL, 3)

        # ── 1. 擷取樣式 ──────────────────────────────────────────────────
        # 固定欄頭（Row 3 各固定欄）
        fixed_header_values = [ws.cell(HDR1, c).value for c in range(1, fixed_cols + 1)]
        fixed_header_styles = [_grab(ws.cell(HDR1, c)) for c in range(1, fixed_cols + 1)]

        # 年度合併欄頭（Row 3 樣本年度欄）
        year_group_hdr_style = _grab(ws.cell(HDR1, SAMPLE_YEAR_START_COL))

        # 指標子欄頭（Row 4 三個樣本欄）
        sub_hdr_values = [ws.cell(HDR2, SAMPLE_YEAR_START_COL + j).value for j in range(3)]
        sub_hdr_styles  = [_grab(ws.cell(HDR2, SAMPLE_YEAR_START_COL + j)) for j in range(3)]

        # 固定欄資料格（Row 5）
        fixed_data_styles = [_grab(ws.cell(DATA_START, c)) for c in range(1, fixed_cols + 1)]

        # 年度欄資料格（Row 5，三個樣本欄）
        year_data_styles = [_grab(ws.cell(DATA_START, SAMPLE_YEAR_START_COL + j)) for j in range(3)]

        # 合計列（Row 6）
        fixed_total_styles = [_grab(ws.cell(TPL_TOTAL, c)) for c in range(1, fixed_cols + 1)]
        year_total_styles  = [_grab(ws.cell(TPL_TOTAL, SAMPLE_YEAR_START_COL + j)) for j in range(3)]

        # 備註（Row 7）
        note_cell = ws.cell(TPL_NOTE, 1)
        note_rich_text = None
        if hasattr(note_cell, '_value') and hasattr(note_cell._value, '__iter__') and not isinstance(note_cell._value, str):
            note_rich_text = note_cell._value
            note_text = note_cell.value
        else:
            note_text = note_cell.value
        note_font      = copy(note_cell.font)      if note_cell.font      else None
        note_alignment = copy(note_cell.alignment) if note_cell.alignment else None
        note_height = ws.row_dimensions[TPL_NOTE].height if TPL_NOTE in ws.row_dimensions else 96.0

        # 列高（用於重建後套用）
        hdr1_height  = ws.row_dimensions[HDR1].height      if HDR1      in ws.row_dimensions else 25.0
        hdr2_height  = ws.row_dimensions[HDR2].height      if HDR2      in ws.row_dimensions else 45.0
        data_height  = ws.row_dimensions[DATA_START].height if DATA_START in ws.row_dimensions else 21.0
        total_height = ws.row_dimensions[TPL_TOTAL].height  if TPL_TOTAL  in ws.row_dimensions else 21.0

        # Row 2 日期儲存格的字型與對齊
        date_font = date_align = None
        for col in range(1, ws.max_column + 1):
            c = ws.cell(2, col)
            if c.value and '製表日期' in str(c.value):
                date_font  = copy(c.font)      if c.font      else None
                date_align = copy(c.alignment) if c.alignment else None
                break

        # 外框底線（取自 TPL_TOTAL 列，用於最末資料列或合計列的底部粗線）
        frame_bottom_sides = {}
        for c in range(1, fixed_cols + 1):
            cell = ws.cell(TPL_TOTAL, c)
            if cell.border and cell.border.bottom and getattr(cell.border.bottom, 'style', None):
                frame_bottom_sides[c] = copy(cell.border.bottom)
        for j in range(3):
            cell = ws.cell(TPL_TOTAL, SAMPLE_YEAR_START_COL + j)
            if cell.border and cell.border.bottom and getattr(cell.border.bottom, 'style', None):
                frame_bottom_sides[SAMPLE_YEAR_START_COL + j] = copy(cell.border.bottom)

        # 固定欄頭 HDR2 列邊框（垂直合併底端格）
        # 範本 XML 通常不為垂直合併底端格儲存明確樣式，故以 HDR1 邊框 + 外框底線重建：
        # left/right 取自 HDR1（外框左線與內分隔右線），bottom 取自 frame_bottom_sides（外框底線）
        fixed_hdr_hdr2_borders = []
        for c in range(1, fixed_cols + 1):
            b1 = fixed_header_styles[c - 1].get('border')
            fixed_hdr_hdr2_borders.append(Border(
                left=b1.left   if b1 else None,
                right=b1.right if b1 else None,
                bottom=frame_bottom_sides.get(c),
            ))

        fixed_data_styles_inner = [self._tpl_inner_style(s) for s in fixed_data_styles]
        year_data_styles_inner  = [self._tpl_inner_style(s) for s in year_data_styles]

        # ── 2. 更新標題文字（替換佔位符）──────────────────────────────────
        title_text = re.sub(
            r'OOO年度～OOO年度',
            f'{start_year}年度～{end_year_val}年度',
            str(ws.cell(1, 1).value or ''),
        )

        # ── 3. 清除 Row 2 日期區域 + 清除 Row 3+ ─────────────────────────
        # （unmerge 已於步驟 0 前置完成）
        # 清除 Row 2 中除表號欄(A2)以外的儲存格（移除舊日期佔位符）
        for col in range(2, ws.max_column + 1):
            ws.cell(2, col).value = None
        # 清除 Row 3+ 所有儲存格
        clear_cols = max(ws.max_column, total_cols)
        for row in range(HDR1, ws.max_row + 1):
            for col in range(1, clear_cols + 1):
                cell = ws.cell(row, col)
                if not isinstance(cell, MergedCell):
                    cell.value  = None
                    cell.border = Border()
            if row in ws.row_dimensions:
                del ws.row_dimensions[row]

        # 範本原始總欄數（固定欄 + 1 個樣本年度組）；Row 1 與製表日期的合併範圍固定於此，
        # 不隨動態年度數量延伸，與範本位置保持一致。
        TPL_TOTAL_COLS = fixed_cols + 3

        # ── 4. Row 1 標題：更新文字 + 合併至範本原始欄界（不延伸至動態年度欄）──
        self._set_cell_value_safe_by_position(ws, 1, 1, title_text)
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=TPL_TOTAL_COLS)

        # ── 5. Row 2 日期：位置與範本一致（範本最後兩欄合併）──────────────
        today = datetime.now()
        new_date = f"製表日期：{today.year - 1911}年{today.month:02d}月{today.day:02d}日"
        date_start_col = TPL_TOTAL_COLS - 1
        ws.merge_cells(start_row=2, start_column=date_start_col, end_row=2, end_column=TPL_TOTAL_COLS)
        date_cell = ws.cell(2, date_start_col)
        date_cell.value = new_date
        if date_font:  date_cell.font      = date_font
        if date_align: date_cell.alignment = date_align

        # ── 6. Row 3：固定欄頭（合併 row3:row4）+ N 年度合併欄頭 ────────
        ws.row_dimensions[HDR1].height = hdr1_height
        for i in range(fixed_cols):
            col = i + 1
            ws.merge_cells(start_row=HDR1, start_column=col, end_row=HDR2, end_column=col)
            cell = ws.cell(HDR1, col)
            cell.value = fixed_header_values[i]
            _apply(cell, fixed_header_styles[i])
            # merge_cells 會刪除底端格（HDR2）；用 _tpl_force_interior_border 注入邊框，
            # 確保 A4 行高區域的左外框與下外框在 XML 中有明確樣式。
            self._tpl_force_interior_border(ws, HDR2, col, fixed_hdr_hdr2_borders[i])

        for i, year in enumerate(years):
            sc = fixed_cols + i * 3 + 1
            # 先逐欄設定邊框再合併（保留右邊界欄右外框），由 _tpl_merge_horizontal 封裝
            self._tpl_merge_horizontal(ws, HDR1, sc, 3, year_hdr_col_borders)
            cell = ws.cell(HDR1, sc)
            cell.value = f"{year}年度"
            # 套用非邊框樣式（邊框已在合併前設定，不用 _apply 以免覆蓋）
            cell.font          = year_group_hdr_style['font']
            cell.alignment     = year_group_hdr_style['alignment']
            cell.fill          = year_group_hdr_style['fill']
            cell.number_format = year_group_hdr_style['number_format']

        # ── 7. Row 4：N × 3 指標子欄頭 ──────────────────────────────────
        ws.row_dimensions[HDR2].height = hdr2_height
        for i in range(N):
            for j in range(3):
                col = fixed_cols + i * 3 + j + 1
                cell = ws.cell(HDR2, col)
                cell.value = sub_hdr_values[j]
                _apply(cell, sub_hdr_styles[j])

        # ── 8. 資料列 ────────────────────────────────────────────────────
        year_totals = {y: {'cases': 0, 'area': _Decimal('0'), 'subsidy': 0} for y in years}

        for idx, row_item in enumerate(rows_data):
            row_num = DATA_START + idx
            ws.row_dimensions[row_num].height = data_height

            # 固定識別欄
            if fixed_cols == 2:
                fixed_vals = [row_item.get('county_name', ''), row_item.get('town_name', '')]
            else:
                fixed_vals = [row_item.get('office_name', '')]

            for ci, (val, s) in enumerate(zip(fixed_vals, fixed_data_styles_inner)):
                cell = ws.cell(row_num, ci + 1)
                cell.value = val
                _apply(cell, s)

            # 年度指標欄
            for i, ym in enumerate(row_item.get('year_metrics', [])):
                y      = ym.get('year', 0)
                cases  = int(ym.get('completed_cases', 0) or 0)
                area   = float(ym.get('total_area', 0) or 0)
                subsidy = int(ym.get('total_subsidy', 0) or 0)
                sc = fixed_cols + i * 3 + 1

                for j, (val, s) in enumerate(zip([cases, area, subsidy], year_data_styles_inner)):
                    cell = ws.cell(row_num, sc + j)
                    cell.value = val
                    _apply(cell, s)

                if y in year_totals:
                    year_totals[y]['cases']   += cases
                    year_totals[y]['area']    += _Decimal(str(area))
                    year_totals[y]['subsidy'] += subsidy

        # ── 9. 合計列（僅 show_total=True 時生成）────────────────────────
        if show_total:
            total_row = DATA_START + len(rows_data)
            ws.row_dimensions[total_row].height = total_height

            if fixed_cols == 2:
                ws.merge_cells(start_row=total_row, start_column=1, end_row=total_row, end_column=2)
            cell = ws.cell(total_row, 1)
            cell.value = '合  計'
            _apply(cell, fixed_total_styles[0])

            for i, year in enumerate(years):
                sc = fixed_cols + i * 3 + 1
                yt = year_totals[year]
                for j, (val, s) in enumerate(zip(
                    [yt['cases'], float(yt['area']), yt['subsidy']],
                    year_total_styles,
                )):
                    cell = ws.cell(total_row, sc + j)
                    cell.value = val
                    _apply(cell, s)

            note_start_row = total_row + 1
        else:
            note_start_row = DATA_START + len(rows_data)

        # ── 10. 最末列套用外框底線 ────────────────────────────────────────
        last_table_row = (total_row if show_total else DATA_START + len(rows_data) - 1)
        if rows_data and frame_bottom_sides:
            for col in range(1, total_cols + 1):
                cell = ws.cell(last_table_row, col)
                src_key = col if col <= fixed_cols else SAMPLE_YEAR_START_COL + (col - fixed_cols - 1) % 3
                bottom = frame_bottom_sides.get(src_key)
                if bottom and cell.border:
                    cell.border = Border(
                        left=cell.border.left,
                        right=cell.border.right,
                        top=cell.border.top,
                        bottom=bottom,
                    )

        # ── 11. 新增年度欄的欄寬（僅設定超出範本原始欄的新增欄）────────────
        for i in range(1, N):
            self._tpl_apply_col_widths(
                ws, col_widths_by_idx,
                src_col_start=SAMPLE_YEAR_START_COL, src_count=3,
                dst_col_start=fixed_cols + i * 3 + 1,
            )

        # ── 12. 備註列 ───────────────────────────────────────────────────
        if note_text:
            note_row = note_start_row
            last_col_letter = get_column_letter(total_cols)
            ws.merge_cells(f"A{note_row}:{last_col_letter}{note_row}")
            note_c = ws.cell(note_row, 1)
            if note_rich_text:
                note_c._value    = note_rich_text
                note_c.data_type = 's'
            else:
                note_c.value = note_text
            if note_font:      note_c.font      = note_font
            if note_alignment: note_c.alignment = note_alignment
            ws.row_dimensions[note_row].height = note_height

        # ── 13. 儲存 ─────────────────────────────────────────────────────
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename  = f"{filename_prefix}_{timestamp}.xlsx"
        file_path = self.temp_dir / filename
        workbook.save(str(file_path))
        return str(file_path)

    # ==================== A03 管理處經費統計報表 ====================

    async def generate_a03_budget_analysis_report(
        self,
        data: Dict[str, Any],
        year: int
    ) -> str:
        """
        生成 A03 各管理處經費統計報表 Excel 檔案

        範本驅動 + 動態增長架構（同 A01/A02 模式）：
        - 範本 A03.xlsx 提供：標題格式、欄寬、資料列樣式參考（Row 4）、備註文字
        - 程式碼負責：清除範例資料 → 動態寫入實際資料（12欄位）→ 合計列 → 備註跟隨尾端

        Args:
            data: BudgetAnalysisResponse 資料（包含 offices、total_* 等欄位）
            year: 統計年度（民國年）

        Returns:
            str: 生成的 Excel 檔案路徑
        """
        from openpyxl import load_workbook
        from openpyxl.styles import Border, Font
        from decimal import Decimal

        template_path = settings.get_template_path("A03.xlsx")
        if not template_path.exists():
            raise FileNotFoundError(f"範本檔案不存在: {template_path}")

        workbook = load_workbook(str(template_path))
        worksheet = workbook.active

        DATA_START_ROW = 4  # 範本中資料區塊起始列（同時作為樣式參考列）
        HEADER_ROW = 3
        COL_COUNT = 12  # A03 報表共 12 個欄位

        # 1. 從範本擷取樣式參考（Row 4 的每欄格式 + 表頭外框粗細）
        col_styles = {}
        frame_bottom_sides = {}
        for col in range(1, COL_COUNT + 1):
            ref_cell = worksheet.cell(row=DATA_START_ROW, column=col)
            col_styles[col] = {
                'font': copy(ref_cell.font) if ref_cell.font else None,
                'alignment': copy(ref_cell.alignment) if ref_cell.alignment else None,
                'border': copy(ref_cell.border) if ref_cell.border else None,
                'fill': copy(ref_cell.fill) if ref_cell.fill else None,
                'number_format': ref_cell.number_format,
            }
            # 表頭底部邊框 = 表格外框粗細（用於最後一列資料的底線）
            header_cell = worksheet.cell(row=HEADER_ROW, column=col)
            if header_cell.border and header_cell.border.bottom:
                frame_bottom_sides[col] = header_cell.border.bottom

        # 2. 擷取備註（解除 Row 4 以下的所有合併儲存格）
        footnote_text = None
        footnote_font = None
        footnote_alignment = None
        footnote_row_height = None
        footnote_rich_text = None  # 保存 Rich Text 數據
        for merge in list(worksheet.merged_cells.ranges):
            if merge.min_row >= DATA_START_ROW:
                cell = worksheet.cell(row=merge.min_row, column=1)
                # 檢查是否為 Rich Text（部分文字有不同格式）
                if hasattr(cell, '_value') and hasattr(cell._value, '__iter__') and not isinstance(cell._value, str):
                    # 保存 Rich Text 數據（包含所有格式信息）
                    footnote_rich_text = cell._value
                    footnote_text = cell.value  # 保存純文字作為後備
                else:
                    footnote_text = cell.value
                footnote_font = copy(cell.font) if cell.font else None
                footnote_alignment = copy(cell.alignment) if cell.alignment else None
                footnote_row_height = worksheet.row_dimensions[merge.min_row].height
                worksheet.unmerge_cells(str(merge))

        # 3. 清除範本的範例資料（Row 4 到最後一行：內容、邊框、行高）
        max_row = worksheet.max_row
        for row in range(DATA_START_ROW, max_row + 1):
            for col in range(1, COL_COUNT + 1):
                cell = worksheet.cell(row=row, column=col)
                cell.value = None
                cell.border = Border()
            # 重置行高（移除範本殘留的自訂行高）
            if row in worksheet.row_dimensions:
                del worksheet.row_dimensions[row]

        # 4. 更新標題和製表日期
        worksheet['A1'].value = (
            f"農業部農田水利署\n推廣管路灌溉設施計畫\n{year}年度各管理處經費統計表"
        )
        today = datetime.now()
        date_str = f"製表日期：{today.year - 1911}年{today.month:02d}月{today.day:02d}日"
        self._set_cell_value_safe(worksheet, 'L2', date_str)

        # 5. 動態寫入資料列（套用範本樣式）
        offices = data.get('offices', [])
        for idx, office in enumerate(offices):
            row = DATA_START_ROW + idx
            row_values = [
                office.get('office_name', ''),
                float(office.get('planned_area', 0) or 0),
                office.get('planned_budget', 0) or 0,
                office.get('budgeted_cases', 0) or 0,
                float(office.get('budgeted_area', 0) or 0),
                office.get('budgeted_subsidy', 0) or 0,
                office.get('unbudgeted_subsidy', 0) or 0,
                office.get('verified_cases', 0) or 0,
                float(office.get('verified_area', 0) or 0),
                office.get('verified_amount', 0) or 0,
                float(office.get('area_execution_rate', 0) or 0),
                float(office.get('budget_execution_rate', 0) or 0),
            ]
            for col, value in enumerate(row_values, start=1):
                cell = worksheet.cell(row=row, column=col, value=value)
                style = col_styles[col]
                if style['font']:
                    cell.font = style['font']
                if style['alignment']:
                    cell.alignment = style['alignment']
                if style['border']:
                    cell.border = style['border']
                if style['fill']:
                    cell.fill = style['fill']
                if style['number_format']:
                    cell.number_format = style['number_format']

        # 6. 新增合計列（使用粗體字）
        if offices:
            total_row = DATA_START_ROW + len(offices)
            total_values = [
                '合計',
                float(data.get('total_planned_area', 0) or 0),
                data.get('total_planned_budget', 0) or 0,
                sum(o.get('budgeted_cases', 0) or 0 for o in offices),
                sum(float(o.get('budgeted_area', 0) or 0) for o in offices),
                data.get('total_budgeted_subsidy', 0) or 0,
                data.get('total_unbudgeted_subsidy', 0) or 0,
                sum(o.get('verified_cases', 0) or 0 for o in offices),
                sum(float(o.get('verified_area', 0) or 0) for o in offices),
                data.get('total_verified_amount', 0) or 0,
                float(data.get('overall_area_execution_rate', 0) or 0),
                float(data.get('overall_budget_execution_rate', 0) or 0),
            ]
            for col, value in enumerate(total_values, start=1):
                cell = worksheet.cell(row=total_row, column=col, value=value)
                style = col_styles[col]
                # 套用樣式並將字體設為粗體
                if style['font']:
                    bold_font = copy(style['font'])
                    bold_font.bold = True
                    cell.font = bold_font
                else:
                    cell.font = Font(bold=True)
                if style['alignment']:
                    cell.alignment = style['alignment']
                if style['border']:
                    cell.border = style['border']
                if style['fill']:
                    cell.fill = style['fill']
                if style['number_format']:
                    cell.number_format = style['number_format']

            # 6.1 合計列套用表格外框底線（與表頭粗細一致）
            for col in range(1, COL_COUNT + 1):
                cell = worksheet.cell(row=total_row, column=col)
                if col in frame_bottom_sides and cell.border:
                    cell.border = Border(
                        left=cell.border.left,
                        right=cell.border.right,
                        top=cell.border.top,
                        bottom=frame_bottom_sides[col],
                    )

        # 7. 動態定位備註（緊跟合計列，空一行）
        if footnote_text:
            footnote_row = DATA_START_ROW + len(offices) + 2  # 資料列 + 合計列 + 空行
            worksheet.merge_cells(f"A{footnote_row}:L{footnote_row}")
            cell = worksheet.cell(row=footnote_row, column=1)
            
            # 優先使用 Rich Text（保留底線等格式），否則使用純文字
            if footnote_rich_text:
                cell._value = footnote_rich_text
                cell.data_type = 's'  # 設定為字串類型
            else:
                cell.value = footnote_text
                
            if footnote_font:
                cell.font = footnote_font
            if footnote_alignment:
                cell.alignment = footnote_alignment
            if footnote_row_height:
                worksheet.row_dimensions[footnote_row].height = footnote_row_height

        # 8. 生成檔案
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"A03_budget_analysis_{year}_{timestamp}.xlsx"
        file_path = self.temp_dir / filename

        try:
            workbook.save(str(file_path))
            return str(file_path)
        except Exception as e:
            print(f"Excel save error: {e}")
            print(f"File path: {file_path}")
            raise

    # ==================== A04 原民區域統計報表 ====================

    async def generate_a04_aboriginal_report(
        self,
        data: Dict[str, Any],
        year: int
    ) -> str:
        """
        生成 A04 原民區域統計報表 Excel 檔案

        範本驅動 + 動態增長架構（同 A01/A02/A03 模式）：
        - 範本 A04.xlsx 提供：標題格式、欄寬、資料列樣式參考（Row 4）、備註文字
        - 程式碼負責：清除範例資料 → 動態寫入實際資料（4 欄位）→ 備註跟隨尾端
        - 無合計列；無資料的欄位以空白呈現

        Args:
            data: 原民區域統計資料（包含 stats、total_* 等欄位）
            year: 統計年度（民國年）

        Returns:
            str: 生成的 Excel 檔案路徑
        """
        from openpyxl import load_workbook
        from openpyxl.styles import Border

        template_path = settings.get_template_path("A04.xlsx")
        if not template_path.exists():
            raise FileNotFoundError(f"範本檔案不存在: {template_path}")

        workbook = load_workbook(str(template_path))
        worksheet = workbook.active

        DATA_START_ROW = 4
        HEADER_ROW = 3
        COL_COUNT = 5  # A04 共 5 欄（縣市、鄉鎮區、案件數、面積、金額）

        # 1. 從範本擷取樣式參考（Row 4 的每欄格式 + 表頭外框粗細）
        col_styles = {}
        frame_bottom_sides = {}
        for col in range(1, COL_COUNT + 1):
            ref_cell = worksheet.cell(row=DATA_START_ROW, column=col)
            col_styles[col] = {
                'font': copy(ref_cell.font) if ref_cell.font else None,
                'alignment': copy(ref_cell.alignment) if ref_cell.alignment else None,
                'border': copy(ref_cell.border) if ref_cell.border else None,
                'fill': copy(ref_cell.fill) if ref_cell.fill else None,
                'number_format': ref_cell.number_format,
            }
            header_cell = worksheet.cell(row=HEADER_ROW, column=col)
            if header_cell.border and header_cell.border.bottom:
                frame_bottom_sides[col] = header_cell.border.bottom

        # 2. 擷取備註（解除 Row 4 以下的所有合併儲存格）
        footnote_text = None
        footnote_font = None
        footnote_alignment = None
        footnote_row_height = None
        footnote_rich_text = None
        last_col_letter = get_column_letter(COL_COUNT)

        for merge in list(worksheet.merged_cells.ranges):
            if merge.min_row >= DATA_START_ROW:
                cell = worksheet.cell(row=merge.min_row, column=1)
                if hasattr(cell, '_value') and hasattr(cell._value, '__iter__') and not isinstance(cell._value, str):
                    footnote_rich_text = cell._value
                    footnote_text = cell.value
                else:
                    footnote_text = cell.value
                footnote_font = copy(cell.font) if cell.font else None
                footnote_alignment = copy(cell.alignment) if cell.alignment else None
                footnote_row_height = worksheet.row_dimensions[merge.min_row].height
                worksheet.unmerge_cells(str(merge))

        # 3. 清除範本的範例資料（Row 4 到最後一行：內容、邊框、行高）
        max_row = worksheet.max_row
        for row in range(DATA_START_ROW, max_row + 1):
            for col in range(1, COL_COUNT + 1):
                cell = worksheet.cell(row=row, column=col)
                cell.value = None
                cell.border = Border()
            if row in worksheet.row_dimensions:
                del worksheet.row_dimensions[row]

        # 4. 更新標題和製表日期
        worksheet['A1'].value = (
            f"農業部農田水利署\n推廣管路灌溉設施計畫\n{year}年度原住民地區推動成果統計表"
        )
        today = datetime.now()
        date_str = f"製表日期：{today.year - 1911}年{today.month:02d}月{today.day:02d}日"
        self._set_cell_value_safe(worksheet, f'{last_col_letter}2', date_str)

        # 5. 動態寫入資料列（套用範本樣式；無資料欄位以空白呈現）
        stats = data.get('stats', [])
        for idx, stat in enumerate(stats):
            row = DATA_START_ROW + idx
            county = stat.get('county') or None
            town = stat.get('town') or None
            grant_count = stat['grant_count'] if stat.get('grant_count') else None
            subsidy_area = stat['subsidy_area'] if stat.get('subsidy_area') else None
            subsidy_amount = stat['subsidy_amount'] if stat.get('subsidy_amount') else None
            row_values = [county, town, grant_count, subsidy_area, subsidy_amount]
            for col, value in enumerate(row_values, start=1):
                cell = worksheet.cell(row=row, column=col, value=value)
                style = col_styles[col]
                if style['font']:
                    cell.font = style['font']
                if style['alignment']:
                    cell.alignment = style['alignment']
                if style['border']:
                    cell.border = style['border']
                if style['fill']:
                    cell.fill = style['fill']
                if style['number_format']:
                    cell.number_format = style['number_format']

        # 6. 最末資料列套用表格外框底線（與表頭粗細一致）
        if stats:
            last_data_row = DATA_START_ROW + len(stats) - 1
            for col in range(1, COL_COUNT + 1):
                cell = worksheet.cell(row=last_data_row, column=col)
                if col in frame_bottom_sides and cell.border:
                    cell.border = Border(
                        left=cell.border.left,
                        right=cell.border.right,
                        top=cell.border.top,
                        bottom=frame_bottom_sides[col],
                    )

        # 7. 動態定位備註（緊跟資料列，空一行）
        if footnote_text:
            footnote_row = DATA_START_ROW + len(stats) + 1  # 資料列 + 空行
            worksheet.merge_cells(f"A{footnote_row}:{last_col_letter}{footnote_row}")
            cell = worksheet.cell(row=footnote_row, column=1)

            if footnote_rich_text:
                cell._value = footnote_rich_text
                cell.data_type = 's'
            else:
                cell.value = footnote_text

            if footnote_font:
                cell.font = footnote_font
            if footnote_alignment:
                cell.alignment = footnote_alignment
            if footnote_row_height:
                worksheet.row_dimensions[footnote_row].height = footnote_row_height

        # 8. 生成檔案
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"A04_aboriginal_{year}_{timestamp}.xlsx"
        file_path = self.temp_dir / filename

        try:
            workbook.save(str(file_path))
            return str(file_path)
        except Exception as e:
            print(f"Excel save error: {e}")
            print(f"File path: {file_path}")
            raise

    # ==================== B01 系列推動成果統計報表（管理區內外分組） ====================

    def _generate_b01_report(
        self,
        template_name: str,
        col_count: int,
        title_text: str,
        date_text: str,
        rows: List[List[Any]],
        filename_prefix: str,
    ) -> str:
        """
        B01 報表通用生成邏輯（範本驅動 + 動態增長）

        架構與 A02 完全一致，但欄位數量不同：
        - B01-1/B01-3: 7欄（縣市 + 管理區內3指標 + 管理區外3指標）
        - B01-2/B01-4: 7欄（管理處 + 管理區內3指標 + 管理區外3指標）
        """
        from openpyxl import load_workbook
        from openpyxl.styles import Border
        from openpyxl.cell.cell import MergedCell

        template_path = settings.get_template_path(template_name)
        if not template_path.exists():
            raise FileNotFoundError(f"範本檔案不存在: {template_path}")

        workbook = load_workbook(str(template_path))
        worksheet = workbook.active

        # 移除 Print Area 定義以避免警告
        if 'Print_Area' in workbook.defined_names:
            del workbook.defined_names['Print_Area']

        DATA_START_ROW = 4
        HEADER_ROW = 3

        # 1. 從範本擷取樣式參考（Row 4）
        col_styles = {}
        frame_bottom_sides = {}
        for col in range(1, col_count + 1):
            ref_cell = worksheet.cell(row=DATA_START_ROW, column=col)
            col_styles[col] = {
                'font': copy(ref_cell.font) if ref_cell.font else None,
                'alignment': copy(ref_cell.alignment) if ref_cell.alignment else None,
                'border': copy(ref_cell.border) if ref_cell.border else None,
                'fill': copy(ref_cell.fill) if ref_cell.fill else None,
                'number_format': ref_cell.number_format,
            }
            # 表頭底部邊框
            header_cell = worksheet.cell(row=HEADER_ROW, column=col)
            if (header_cell.border and header_cell.border.bottom
                    and getattr(header_cell.border.bottom, 'style', None)):
                frame_bottom_sides[col] = header_cell.border.bottom

        # 2. 標題與日期（第1列與第2列）
        worksheet['A1'] = title_text
        last_col_letter = get_column_letter(col_count)
        self._set_cell_value_safe(worksheet, f'{last_col_letter}2', date_text)

        # 3. 清除範例資料（保留 Row 3 表頭和 Row 4 樣式參考）
        max_row = worksheet.max_row
        for row in range(DATA_START_ROW, max_row + 1):
            for col in range(1, col_count + 1):
                cell = worksheet.cell(row=row, column=col)
                # 跳過合併單元格（MergedCell 的 value 是唯讀的）
                if not isinstance(cell, MergedCell):
                    cell.value = None
                    cell.border = Border()
            if row in worksheet.row_dimensions:
                del worksheet.row_dimensions[row]

        # 4. 動態新增資料列 + 應用範本樣式
        for row_idx, row_data in enumerate(rows, start=DATA_START_ROW):
            for col_idx, value in enumerate(row_data, start=1):
                if col_idx > col_count:
                    continue
                cell = worksheet.cell(row=row_idx, column=col_idx, value=value)
                # 應用範本樣式
                style = col_styles.get(col_idx, {})
                if style.get('font'):
                    cell.font = copy(style['font'])
                if style.get('alignment'):
                    cell.alignment = copy(style['alignment'])
                if style.get('border'):
                    cell.border = copy(style['border'])
                if style.get('fill'):
                    cell.fill = copy(style['fill'])
                if style.get('number_format'):
                    cell.number_format = style['number_format']

        # 5. 小計列
        last_data_row = DATA_START_ROW + len(rows) - 1
        subtotal_row = last_data_row + 1
        self._set_cell_value_safe_by_position(worksheet, subtotal_row, 1, "小計")

        # 應用小計列樣式並計算總和公式
        for col in range(1, col_count + 1):
            cell = worksheet.cell(row=subtotal_row, column=col)
            style = col_styles.get(col, {})
            if style.get('font'):
                cell.font = copy(style['font'])
            if style.get('alignment'):
                cell.alignment = copy(style['alignment'])
            if style.get('fill'):
                cell.fill = copy(style['fill'])

            # 數字欄位加總公式（第2欄起為數字）
            if col > 1:
                col_letter = get_column_letter(col)
                sum_formula = f"=SUM({col_letter}{DATA_START_ROW}:{col_letter}{last_data_row})"
                self._set_cell_value_safe_by_position(worksheet, subtotal_row, col, sum_formula)
                if style.get('number_format'):
                    cell.number_format = style['number_format']

            # 底部邊框（表格外框）
            if col in frame_bottom_sides:
                current_border = copy(cell.border) if cell.border else Border()
                cell.border = Border(
                    left=current_border.left,
                    right=current_border.right,
                    top=current_border.top,
                    bottom=frame_bottom_sides[col]
                )

        # 6. 備註（緊跟小計列之後）
        note_row = subtotal_row + 1
        self._set_cell_value_safe_by_position(worksheet, note_row, 1, "註：案件數為有效之有案號案件數")

        # 儲存檔案
        output_filename = f"{filename_prefix}.xlsx"
        output_path = self.temp_dir / output_filename
        workbook.save(str(output_path))
        return str(output_path)

    async def generate_b01_1_report(self, data: Dict[str, Any], year: int) -> str:
        """生成 B01-1 各縣市管理區內外統計報表（單年度）"""
        today = datetime.now()
        rows = []
        for s in data.get('stats', []):
            rows.append([
                s.get('county_name', ''),
                # 管理區內
                s.get('inside_cases', 0) or 0,
                float(s.get('inside_area', 0) or 0),
                s.get('inside_subsidy', 0) or 0,
                # 管理區外
                s.get('outside_cases', 0) or 0,
                float(s.get('outside_area', 0) or 0),
                s.get('outside_subsidy', 0) or 0,
            ])
        return self._generate_b01_report(
            template_name="B01-1.xlsx",
            col_count=7,
            title_text=f"農業部農田水利署\n推廣管路灌溉設施計畫\n{year}年度各縣市推動成果統計表",
            date_text=f"製表日期：{today.year - 1911}年{today.month:02d}月{today.day:02d}日",
            rows=rows,
            filename_prefix=f"B01-1_{year}",
        )

    async def generate_b01_2_report(self, data: Dict[str, Any], year: int) -> str:
        """生成 B01-2 各管理處管理區內外統計報表（單年度）"""
        today = datetime.now()
        rows = []
        for s in data.get('stats', []):
            rows.append([
                s.get('office_name', ''),
                # 管理區內
                s.get('inside_cases', 0) or 0,
                float(s.get('inside_area', 0) or 0),
                s.get('inside_subsidy', 0) or 0,
                # 管理區外
                s.get('outside_cases', 0) or 0,
                float(s.get('outside_area', 0) or 0),
                s.get('outside_subsidy', 0) or 0,
            ])
        return self._generate_b01_report(
            template_name="B01-2.xlsx",
            col_count=7,
            title_text=f"農業部農田水利署\n推廣管路灌溉設施計畫\n{year}年度各管理處推動成果統計表",
            date_text=f"製表日期：{today.year - 1911}年{today.month:02d}月{today.day:02d}日",
            rows=rows,
            filename_prefix=f"B01-2_{year}",
        )

    async def generate_b01_3_report(self, data: Dict[str, Any], start_year: int, end_year: int) -> str:
        """生成 B01-3 歷年各縣市管理區內外統計報表"""
        today = datetime.now()
        rows = []
        for s in data.get('stats', []):
            rows.append([
                s.get('county_name', ''),
                # 管理區內
                s.get('inside_cases', 0) or 0,
                float(s.get('inside_area', 0) or 0),
                s.get('inside_subsidy', 0) or 0,
                # 管理區外
                s.get('outside_cases', 0) or 0,
                float(s.get('outside_area', 0) or 0),
                s.get('outside_subsidy', 0) or 0,
            ])
        return self._generate_b01_report(
            template_name="B01-3.xlsx",
            col_count=7,
            title_text=f"農業部農田水利署\n推廣管路灌溉設施計畫\n{start_year}年度～{end_year}年度各縣市推動成果統計表",
            date_text=f"製表日期：{today.year - 1911}年{today.month:02d}月{today.day:02d}日",
            rows=rows,
            filename_prefix=f"B01-3_{start_year}-{end_year}",
        )

    async def generate_b01_4_report(self, data: Dict[str, Any], start_year: int, end_year: int) -> str:
        """生成 B01-4 歷年各管理處管理區內外統計報表"""
        today = datetime.now()
        rows = []
        for s in data.get('stats', []):
            rows.append([
                s.get('office_name', ''),
                # 管理區內
                s.get('inside_cases', 0) or 0,
                float(s.get('inside_area', 0) or 0),
                s.get('inside_subsidy', 0) or 0,
                # 管理區外
                s.get('outside_cases', 0) or 0,
                float(s.get('outside_area', 0) or 0),
                s.get('outside_subsidy', 0) or 0,
            ])
        return self._generate_b01_report(
            template_name="B01-4.xlsx",
            col_count=7,
            title_text=f"農業部農田水利署\n推廣管路灌溉設施計畫\n{start_year}年度～{end_year}年度各管理處推動成果統計表",
            date_text=f"製表日期：{today.year - 1911}年{today.month:02d}月{today.day:02d}日",
            rows=rows,
            filename_prefix=f"B01-4_{start_year}-{end_year}",
        )

    def cleanup_temp_files(self, max_age_hours: int = 24):
        """清理超過指定時間的臨時檔案"""
        import time

        current_time = time.time()
        max_age_seconds = max_age_hours * 3600

        for file_path in self.temp_dir.glob("*.xls*"):
            if current_time - file_path.stat().st_mtime > max_age_seconds:
                try:
                    file_path.unlink()
                except OSError:
                    pass  # 忽略刪除失敗的檔案