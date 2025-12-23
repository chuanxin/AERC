"""
推廣管路灌溉設施補助計畫工程預算書 PDF 生成服務

基於範例 PDF 格式，動態生成符合格式的工程預算書文件（共 11 頁）
"""
import io
import os
from typing import Dict, Any, List
from datetime import datetime

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

from src.utils.chinese_pdf import setup_kaiu_font, setup_chinese_font


class BudgetStatementPDFGenerator:
    """工程預算書 PDF 生成器（11 頁完整版本）"""

    def __init__(self):
        self.font_name = 'Helvetica'
        self.font_available = False
        self._setup_fonts()
        self.revision_date = self._get_file_revision_date()

    def _setup_fonts(self) -> None:
        """設置中文字體"""
        try:
            # 優先使用標楷體
            font_available, font_name = setup_kaiu_font()
            if font_available and font_name == 'KaiU':
                self.font_name = font_name
                self.font_available = True
            else:
                # 回退到其他中文字體
                font_available, font_name = setup_chinese_font()
                if font_available:
                    self.font_name = font_name
                    self.font_available = True
        except Exception as e:
            print(f"字體設置失敗: {e}")

    def _get_file_revision_date(self) -> str:
        """取得本檔案的最後修改時間，轉換為民國年格式"""
        try:
            file_path = os.path.abspath(__file__)
            mtime = os.path.getmtime(file_path)
            mod_datetime = datetime.fromtimestamp(mtime)
            roc_year = mod_datetime.year - 1911
            return f"民國{roc_year}年{mod_datetime.month}月{mod_datetime.day}日"
        except Exception:
            return ""

    def _draw_justified_text(
        self,
        c: canvas.Canvas,
        text: str,
        x: float,
        y: float,
        width: float,
        font_name: str = None,
        font_size: float = 12,
        vertical_align: str = None,
        row_height: float = None
    ) -> None:
        """
        繪製分散對齊的文字（每個字符均勻分布在指定寬度內）

        Args:
            c: Canvas 物件
            text: 要繪製的文字
            x: 起始 X 座標
            y: Y 座標（若 vertical_align='middle'，則為欄位頂部）
            width: 目標寬度
            font_name: 字體名稱（None 則使用預設字體）
            font_size: 字體大小
            vertical_align: 垂直對齊方式 ('middle' 為垂直置中，None 為不調整）
            row_height: 欄位高度（垂直置中時必須提供）
        """
        if not text:
            return

        # 移除文字中的空格（因為我們要重新分配間距）
        text = text.replace(' ', '')

        if not text:
            return

        font = font_name or self.font_name
        c.setFont(font, font_size)

        # === 計算垂直置中的 Y 座標 ===
        actual_y = y
        if vertical_align == 'middle' and row_height is not None:
            # 垂直置中：y 是欄位頂部，計算文字基線位置
            # 欄位中心 = y - row_height / 2
            # 微調偏移：向下偏移一點（負值）讓文字視覺上更居中
            actual_y = y - row_height / 2 - font_size * 0.2

        # 如果只有一個字符，直接繪製
        if len(text) == 1:
            c.drawString(x, actual_y, text)
            return

        # 計算每個字符的寬度
        char_widths = [c.stringWidth(char, font, font_size) for char in text]
        total_char_width = sum(char_widths)

        # 計算字符之間需要的總間距
        num_gaps = len(text) - 1  # 字符之間的間隙數量
        total_gap_width = width - total_char_width

        # 如果目標寬度小於字符總寬度，直接正常繪製
        if total_gap_width < 0:
            c.drawString(x, actual_y, text)
            return

        # 計算每個間隙的寬度
        gap_width = total_gap_width / num_gaps if num_gaps > 0 else 0

        # 逐字符繪製
        current_x = x
        for i, char in enumerate(text):
            c.drawString(current_x, actual_y, char)
            current_x += char_widths[i]
            if i < num_gaps:
                current_x += gap_width

    def _draw_centered_text(
        self,
        c: canvas.Canvas,
        text: str,
        x: float,
        y: float,
        width: float,
        font_name: str = None,
        font_size: float = 12
    ) -> None:
        """
        繪製置中對齊的文字

        Args:
            c: Canvas 物件
            text: 要繪製的文字
            x: 起始 X 座標（欄位左邊緣）
            y: Y 座標
            width: 欄位寬度
            font_name: 字體名稱（None 則使用預設字體）
            font_size: 字體大小
        """
        if not text:
            return

        font = font_name or self.font_name
        c.setFont(font, font_size)

        # 計算文字寬度
        text_width = c.stringWidth(text, font, font_size)

        # 計算置中位置
        center_x = x + (width - text_width) / 2

        # 繪製文字
        c.drawString(center_x, y, text)

    def _draw_right_aligned_text(
        self,
        c: canvas.Canvas,
        text: str,
        x: float,
        y: float,
        width: float,
        font_name: str = None,
        font_size: float = 12
    ) -> None:
        """
        繪製靠右對齊的文字

        Args:
            c: Canvas 物件
            text: 要繪製的文字
            x: 起始 X 座標（欄位左邊緣）
            y: Y 座標
            width: 欄位寬度
            font_name: 字體名稱（None 則使用預設字體）
            font_size: 字體大小
        """
        if not text:
            return

        font = font_name or self.font_name
        c.setFont(font, font_size)

        # 計算文字寬度
        text_width = c.stringWidth(text, font, font_size)

        # 計算靠右位置
        right_x = x + width - text_width - 8

        # 繪製文字
        c.drawString(right_x, y, text)

    def _wrap_and_draw_multiline_text(
        self,
        c: canvas.Canvas,
        text: str,
        x: float,
        y: float,
        max_width: float,
        font_name: str = None,
        font_size: float = 12,
        line_spacing: float = 14,
        align: str = 'left',
        vertical_align: str = 'top',
        row_height: float = None
    ) -> int:
        """
        自動換行並繪製多行文字

        Args:
            c: Canvas 物件
            text: 要繪製的文字
            x: 起始 X 座標
            y: 起始 Y 座標（依據 vertical_align 而定）
            max_width: 最大寬度
            font_name: 字體名稱（None 則使用預設字體）
            font_size: 字體大小
            line_spacing: 行距
            align: 水平對齊方式 ('left', 'center', 'right')
            vertical_align: 垂直對齊方式 ('top', 'middle', 'bottom')
            row_height: 欄位高度（垂直置中時必須提供）

        Returns:
            繪製的行數
        """
        if not text:
            return 0

        font = font_name or self.font_name
        c.setFont(font, font_size)

        # 使用現有的 _wrap_text_to_lines 方法將文字分行
        lines = []
        remaining_text = text

        while remaining_text:
            line_chars = self._wrap_text_to_lines(remaining_text, font, font_size, max_width, c)
            if line_chars:
                lines.append(line_chars[0])
                remaining_text = remaining_text[len(line_chars[0]):]
            else:
                break

        num_lines = len(lines)

        # === 計算起始 Y 座標（根據垂直對齊方式） ===
        # 注意：y 是欄位頂部的 Y 座標，欄位底部是 y - row_height
        if vertical_align == 'middle' and row_height is not None:
            # 垂直置中（參考 completion_statement_pdf_generator.py 的實現）
            if num_lines == 1:
                # 單行：文字基線在欄位中心稍微偏上
                # 欄位中心 = y - row_height / 2
                # 微調偏移 = font_size * 0.1（讓視覺中心與 checkbox 等元素對齊）
                start_y = y - row_height / 2 + font_size * 1
            else:
                # 多行：整體內容塊垂直置中
                # 計算所有文字的總高度（包含行距）
                total_text_height = (num_lines - 1) * line_spacing + font_size

                # 計算第一行基線位置
                # 使內容塊整體在欄位中垂直置中
                # 欄位底部 = y - row_height
                # 第一行基線 = 欄位底部 + (欄位高度 + 內容總高度) / 2 - 微調
                start_y = (y - row_height) + (row_height + total_text_height) / 2 - font_size * 0.8
        elif vertical_align == 'bottom' and row_height is not None:
            # 底部對齊：最後一行在欄位底部附近
            total_text_height = (num_lines - 1) * line_spacing
            # 第一行基線 = 欄位底部 + 所有行間距 + 字體大小 + padding
            start_y = y - row_height + total_text_height + font_size + 5
        else:
            # 頂部對齊（預設）：第一行在欄位頂部附近
            start_y = y - 17  # 固定偏移（與表格其他行保持一致）

        # === 繪製每一行 ===
        current_y = start_y
        for line in lines:
            if align == 'center':
                self._draw_centered_text(c, line, x, current_y, max_width, font, font_size)
            elif align == 'right':
                text_width = c.stringWidth(line, font, font_size)
                c.drawString(x + max_width - text_width, current_y, line)
            else:  # left
                c.drawString(x, current_y, line)
            current_y -= line_spacing

        return num_lines

    def _calculate_text_lines(
        self,
        c: canvas.Canvas,
        text: str,
        max_width: float,
        font_name: str = None,
        font_size: float = 12
    ) -> int:
        """
        計算文字換行後的行數

        Args:
            c: Canvas 物件
            text: 要計算的文字
            max_width: 最大寬度
            font_name: 字體名稱（None 則使用預設字體）
            font_size: 字體大小

        Returns:
            行數
        """
        if not text:
            return 0

        font = font_name or self.font_name
        c.setFont(font, font_size)

        lines = []
        remaining_text = text

        while remaining_text:
            line_chars = self._wrap_text_to_lines(remaining_text, font, font_size, max_width, c)
            if line_chars:
                lines.append(line_chars[0])
                remaining_text = remaining_text[len(line_chars[0]):]
            else:
                break

        return len(lines)

    def _wrap_text_to_lines(self, text: str, font_name: str, font_size: float, max_width: float, c: canvas.Canvas) -> List[str]:
        """
        將文字按指定寬度自動換行

        Args:
            text: 要換行的文字
            font_name: 字體名稱
            font_size: 字體大小
            max_width: 最大寬度
            c: Canvas 物件

        Returns:
            換行後的文字列表
        """
        if not text:
            return []

        words = list(text)  # 將文字拆成單字
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word
            test_width = c.stringWidth(test_line, font_name, font_size)

            if test_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines if lines else [""]

    def _draw_paragraph(
        self,
        c: canvas.Canvas,
        text: str,
        x: float,
        y: float,
        max_width: float,
        font_size: float = 12,
        line_spacing: float = 18,
        indent: float = 0,
        hanging_indent: float = 0
    ) -> float:
        """
        繪製段落文字，支援自動換行

        Args:
            c: Canvas 物件
            text: 要繪製的文字
            x: 起始 X 座標
            y: 起始 Y 座標
            max_width: 最大寬度
            font_size: 字體大小
            line_spacing: 行距
            indent: 首行縮排
            hanging_indent: 懸掛縮排（後續行的縮排量，用於項目符號等場景）

        Returns:
            繪製後的 Y 座標（下一行的起始位置）
        """
        if not text:
            return y

        c.setFont(self.font_name, font_size)

        # 如果有懸掛縮排，第一行不縮排，後續行縮排
        # 如果有首行縮排，第一行縮排，後續行不縮排
        # 計算換行時的可用寬度
        if hanging_indent > 0:
            # 懸掛縮排模式：第一行用全寬，後續行減去懸掛縮排
            first_line_width = max_width
            subsequent_width = max_width - hanging_indent
        else:
            # 首行縮排模式：第一行減去縮排，後續行用全寬
            first_line_width = max_width - indent
            subsequent_width = max_width

        # 手動處理換行
        lines = []
        remaining_text = text
        is_first_line = True

        while remaining_text:
            available_width = first_line_width if is_first_line else subsequent_width
            line_chars = self._wrap_text_to_lines(remaining_text, self.font_name, font_size, available_width, c)

            if line_chars:
                lines.append(line_chars[0])
                remaining_text = remaining_text[len(line_chars[0]):]
                is_first_line = False
            else:
                break

        # 繪製所有行
        for i, line in enumerate(lines):
            if hanging_indent > 0:
                # 懸掛縮排：第一行不縮排，後續行縮排
                current_x = x + (hanging_indent if i > 0 else 0)
            else:
                # 首行縮排：第一行縮排，後續行不縮排
                current_x = x + (indent if i == 0 else 0)

            c.drawString(current_x, y, line)
            y -= line_spacing

        return y

    def generate(self, grant_data: Dict[str, Any]) -> bytes:
        """
        生成工程預算書 PDF（11 頁）

        Args:
            grant_data: 補助案件資料

        Returns:
            PDF 檔案的二進位內容
        """
        if not self.font_available:
            raise Exception("中文字體不可用")

        # 創建 PDF 緩衝區
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        # 逐頁生成
        self._generate_cover_page(c, grant_data)           # 第 1 頁：封面頁
        self._generate_budget_table_page(c, grant_data)    # 第 2 頁：預算書主表
        self._generate_land_list_page(c, grant_data)       # 第 3 頁：土地清冊
        self._generate_power_storage_table_page(c, grant_data)  # 第 4 頁：動力與調蓄設施
        self._generate_pipe_materials_table_page(c, grant_data) # 第 5 頁：管路材料表
        self._generate_control_materials_table_page(c, grant_data)  # 第 6 頁：調控設施材料表
        self._generate_design_diagram_page(c, grant_data)  # 第 7 頁：設計圖
        self._generate_photos_page(c, grant_data)          # 第 8 頁：照片頁
        self._generate_receipt_page(c, grant_data)         # 第 9 頁：領款收據
        self._generate_test_report_page(c, grant_data)     # 第 10 頁：功能測試報告
        self._generate_review_checklist_page(c, grant_data)  # 第 11 頁：書面審查表

        # 完成 PDF
        c.save()
        buffer.seek(0)
        return buffer.getvalue()

    # =========================================================================
    # 第 1 頁：封面頁
    # =========================================================================
    def _generate_cover_page(self, c: canvas.Canvas, data: Dict[str, Any]) -> None:
        """生成第 1 頁：封面頁"""
        width, height = A4

        # 設置初始位置
        current_y = height - 75 # 從頂部開始，留出邊距
        left_margin = 60
        right_margin = width - 60
        content_width = right_margin - left_margin

        # === 主標題 ===
        c.setFont(self.font_name, 26)
        title = "推廣管路灌溉設施補助計畫"
        title_width = c.stringWidth(title, self.font_name, 26)
        c.drawString((width - title_width) / 2, current_y, title)
        current_y -= 70

        # === 年度 ===
        c.setFont(self.font_name, 26)
        year = data.get('year', '114')
        year_text = f"{year}年度"
        year_width = c.stringWidth(year_text, self.font_name, 26)
        c.drawString((width - year_width) / 2, current_y, year_text)
        current_y -= 70

        # === 管理處 ===
        c.setFont(self.font_name, 26)
        office_name = data.get('office_name', '石門管理處')
        office_text = f"農業部農田水利署{office_name}"
        office_width = c.stringWidth(office_text, self.font_name, 26)
        c.drawString((width - office_width) / 2, current_y, office_text)
        current_y -= 120

        # === 申請案號 ===
        c.setFont(self.font_name, 20)
        case_number = data.get('case_number', '')
        case_text = f"申請案號:{case_number}"
        c.drawString(left_margin, current_y, case_text)
        current_y -= 60

        # === 申請人 ===
        applicant_name = data.get('applicant_name', '')
        applicant_text = f"申 請 人:{applicant_name}"
        c.drawString(left_margin, current_y, applicant_text)
        current_y -= 60

        # === 通訊住址 ===
        address = data.get('address', '')
        address_text = f"通訊住址:{address}"
        c.drawString(left_margin, current_y, address_text)
        current_y -= 60

        # === 設施地點 ===
        land_location = data.get('land_location', '')
        first_lot_number = data.get('first_lot_number', '')
        land_count = data.get('land_count', 1)

        # 組合顯示文字：桃園市龍潭區-竹龍段,地號:0264-0000,等1筆土地。
        location_text = f"設施地點:{land_location},地號:{first_lot_number},等{land_count}筆土地。"

        # 使用 _draw_paragraph 支援自動換行和懸掛縮排
        # 計算 "設施地點:" 的寬度作為懸掛縮排量
        c.setFont(self.font_name, 20)
        label_width = c.stringWidth("設施地點:", self.font_name, 20)

        # 繪製段落，第二行及後續行會自動縮排對齊到內容開始位置
        current_y = self._draw_paragraph(
            c,
            location_text,
            left_margin,
            current_y,
            content_width,
            font_size=20,
            line_spacing=25,
            hanging_indent=label_width  # 使用懸掛縮排，第二行對齊 "桃園市"
        )
        current_y -= 15  # 額外間距

        # === 申請面積 ===
        facility_area_ha = data.get('facility_area_ha', '0.0000')
        area_text = f"申請面積:{facility_area_ha}公頃"
        c.drawString(left_margin, current_y, area_text)
        current_y -= 60

        # === 設施型式 ===
        facility_type = data.get('facility_type', '')
        type_text = f"設施型式:{facility_type}"
        c.drawString(left_margin, current_y, type_text)

        # 換頁
        c.showPage()

    # =========================================================================
    # 第 2 頁：預算書主表
    # =========================================================================
    def _generate_budget_table_page(self, c: canvas.Canvas, data: Dict[str, Any]) -> None:
        """生成第 2 頁：預算書主表"""
        width, height = A4
        current_y = height - 60

        # === 標題 ===
        c.setFont(self.font_name, 22)
        title = "推廣管路灌溉設施計畫預算書"
        title_width = c.stringWidth(title, self.font_name, 22)
        c.drawString((width - title_width) / 2, current_y, title)
        current_y -= 40

        # === 基本資料表格 ===
        table_font_size = 14
        c.setFont(self.font_name, table_font_size)
        c.setLineWidth(0.5)

        # 第一行：農戶姓名 + 申請案號
        table_x = 120
        table_y = current_y
        col1_width = 80
        col2_width = 100
        col3_width = 80
        col4_width = 100
        row_height = 25

        # === 預先計算第3行的動態高度（用於確定外框總高度） ===
        land_info = f"{data.get('land_location', '')},地號:{data.get('first_lot_number', '')},等{data.get('land_count', 1)}筆土地。"
        content_width = col2_width + col3_width + col4_width - 8
        line_spacing = 14
        num_lines = self._calculate_text_lines(c, land_info, content_width, font_size=table_font_size)
        row3_dynamic_height = max(row_height, (num_lines * line_spacing) + 10)

        # 繪製表格外框（考慮第3行的動態高度）
        total_table_width = col1_width + col2_width + col3_width + col4_width
        total_table_height = row_height * 5 + row3_dynamic_height  # 前2行+後3行用標準高度，第3行用動態高度
        c.rect(table_x, table_y - total_table_height, total_table_width, total_table_height)

        # 第 1 行：農戶姓名 + 申請案號
        c.line(table_x + col1_width, table_y, table_x + col1_width, table_y - row_height)
        c.line(table_x + col1_width + col2_width, table_y, table_x + col1_width + col2_width, table_y - row_height)
        c.line(table_x + col1_width + col2_width + col3_width, table_y, table_x + col1_width + col2_width + col3_width, table_y - row_height)
        c.line(table_x, table_y - row_height, table_x + col1_width + col2_width + col3_width + col4_width, table_y - row_height)

        # 使用分散對齊繪製標籤
        self._draw_justified_text(c, "農戶姓名", table_x + 4, table_y - 17, col1_width - 8, font_size=table_font_size)

        # 內容使用置中對齊
        self._draw_centered_text(
            c,
            data.get('applicant_name', ''),
            table_x + col1_width,                      # 內容欄位左邊緣
            table_y - 17,                              # Y 座標
            col2_width,                                # 內容欄位寬度
            font_size=table_font_size
        )

        self._draw_justified_text(c, "申請案號", table_x + col1_width + col2_width + 4, table_y - 17, col3_width - 8, font_size=table_font_size)
        self._draw_centered_text(
            c,
            data.get('case_number', ''),
            table_x + col1_width + col2_width + col3_width,                      # 內容欄位左邊緣
            table_y - 17,                              # Y 座標
            col2_width,                                # 內容欄位寬度
            font_size=table_font_size
        )

        # 第 2 行：住址
        table_y -= row_height
        c.line(table_x + col1_width, table_y, table_x + col1_width, table_y - row_height)
        c.line(table_x, table_y - row_height, table_x + col1_width + col2_width + col3_width + col4_width, table_y - row_height)
        self._draw_justified_text(c, "住址", table_x + 4, table_y - 17, col1_width - 8, font_size=table_font_size)
        c.drawString(table_x + col1_width + 4, table_y - 17, data.get('address', ''))

        # 第 3 行：設施地段（支援自動換行和動態欄高）
        table_y -= row_height

        # 使用預先計算的動態行高
        dynamic_row_height = row3_dynamic_height

        # 繪製垂直線（根據動態高度）
        c.line(table_x + col1_width, table_y, table_x + col1_width, table_y - dynamic_row_height)
        c.line(table_x, table_y - dynamic_row_height, table_x + col1_width + col2_width + col3_width + col4_width, table_y - dynamic_row_height)

        # 繪製標籤（使用內建的垂直置中功能）
        self._draw_justified_text(
            c, "設施地段",
            table_x + 4,
            table_y,  # 欄位頂部
            col1_width - 8,
            font_size=table_font_size,
            vertical_align='middle',      # 垂直置中
            row_height=dynamic_row_height  # 動態行高
        )

        # 繪製自動換行的內容（垂直置中）
        self._wrap_and_draw_multiline_text(
            c, land_info,
            table_x + col1_width + 4,   # X 座標
            table_y,                     # Y 座標（欄位頂部）
            content_width,               # 最大寬度
            font_size=table_font_size,
            line_spacing=line_spacing,
            align='left',                # 水平對齊：'left', 'center', 'right'
            vertical_align='middle',     # 垂直置中
            row_height=dynamic_row_height  # 欄位高度
        )

        # 更新 table_y 位置（移動到下一行）
        table_y -= dynamic_row_height

        # 第 4 行：設施面積
        c.line(table_x + col1_width, table_y, table_x + col1_width, table_y - row_height)
        c.line(table_x, table_y - row_height, table_x + col1_width + col2_width + col3_width + col4_width, table_y - row_height)
        self._draw_justified_text(c, "設施面積", table_x + 4, table_y - 17, col1_width - 8, font_size=table_font_size)
        c.drawString(table_x + col1_width + 4, table_y - 17, f"{data.get('facility_area_ha', '0.0000')} 公頃")

        # 第 5 行：設施型式
        table_y -= row_height
        c.line(table_x + col1_width, table_y, table_x + col1_width, table_y - row_height)
        c.line(table_x, table_y - row_height, table_x + col1_width + col2_width + col3_width + col4_width, table_y - row_height)
        self._draw_justified_text(c, "設施型式", table_x + 4, table_y - 17, col1_width - 8, font_size=table_font_size)
        c.drawString(table_x + col1_width + 4, table_y - 17, data.get('facility_type', ''))

        # 第 6 行：補助標準
        table_y -= row_height
        c.line(table_x + col1_width, table_y, table_x + col1_width, table_y - row_height)
        self._draw_justified_text(c, "補助標準", table_x + 4, table_y - 17, col1_width - 8, font_size=table_font_size)
        c.drawString(table_x + col1_width + 4, table_y - 17, data.get('subsidy_standard', '一般標準'))

        current_y = table_y - 60

        # === 預算明細表 ===
        table_x = 40
        current_y = self._draw_budget_detail_table(c, data, table_x, current_y)
        current_y -= 20

        # === 簽核欄位 ===
        self._draw_signature_section(c, table_x, current_y)

        # 換頁
        c.showPage()

    # =========================================================================
    # 第 3 頁
    # =========================================================================
    def _generate_land_list_page(self, c: canvas.Canvas, data: Dict[str, Any]) -> None:
        """生成第 3 頁：設施土地清冊"""
        width, height = A4
        current_y = height - 60

        # 標題
        c.setFont(self.font_name, 22)
        title = "設施土地清冊"
        title_width = c.stringWidth(title, self.font_name, 22)
        c.drawString((width - title_width) / 2, current_y, title)
        current_y -= 40

        # 基本資訊
        left_margin = 40
        right_margin = width - 40
        content_width = right_margin - left_margin
        c.setFont(self.font_name, 14)
        c.drawString(left_margin, current_y, f"申請案號:{data.get('case_number', '')}")
        current_y -= 25
        c.drawString(left_margin, current_y, f"申 請 人:{data.get('applicant_name', '')}")
        current_y -= 25

        land_count = data.get('land_count', 0)
        c.drawString(left_margin, current_y, f"共{land_count}筆土地資料,詳列如下")
        current_y -= 40

        # 土地清冊表格
        lands = data.get('lands', [])
        if lands:
            # 表格設定
            table_x = left_margin
            # 寬度:516
            col_widths = [200, 76, 120, 120]
            row_height = 22
            table_font_size = 12

            # 計算表格總高度
            total_width = sum(col_widths)
            table_height = row_height * (len(lands) + 2)  # 標題行 + 資料行 + 合計行
            table_start_y = current_y

            headers = ["地段", "地號", "土地面積(m²)", "施設面積(m²)"]
            c.setFont(self.font_name, table_font_size)
            c.setLineWidth(0.5)

            # === 繪製表格外框 ===
            c.rect(table_x, table_start_y - table_height, total_width, table_height)

            # === 繪製垂直分隔線 ===
            vertical_positions = [0]
            for width_val in col_widths:
                vertical_positions.append(vertical_positions[-1] + width_val)

            # 繪製內部垂直線（除了最左和最右的邊框）
            for i in range(1, len(vertical_positions) - 1):
                line_x = table_x + vertical_positions[i]
                c.line(line_x, table_start_y, line_x, table_start_y - table_height)

            # === 繪製標題行 ===
            for i, header in enumerate(headers):
                col_x = table_x + vertical_positions[i]
                col_width = col_widths[i]
                # 使用置中對齊繪製標題
                self._draw_centered_text(
                    c, header,
                    col_x, table_start_y - row_height / 2 - table_font_size * 0.2,
                    col_width,
                    font_size=table_font_size
                )

            # 標題行底線
            c.line(table_x, table_start_y - row_height, table_x + total_width, table_start_y - row_height)
            current_y = table_start_y - row_height

            # === 繪製土地資料 ===
            total_land_area = 0.0
            total_facility_area = 0.0

            for land in lands:
                # 縣市、鄉鎮、地段資訊
                land_county = land.get('land_county', '')
                land_town = land.get('land_town', '')
                section = land.get('section', '')
                lot_number = land.get('lot_number', '')

                # 組合完整地段資訊：縣市 + 鄉鎮 + 地段
                full_section = f"{land_county}{land_town}-{section}"

                # 安全轉換為 float
                try:
                    land_area = float(land.get('land_area', 0) or 0)
                except (ValueError, TypeError):
                    land_area = 0.0

                try:
                    facility_area = float(land.get('facility_area', 0) or 0)
                except (ValueError, TypeError):
                    facility_area = 0.0

                # 繪製資料（使用垂直置中）
                row_y = current_y - row_height / 2 - table_font_size * 0.3

                # 地段（左對齊，包含縣市鄉鎮資訊）
                c.drawString(table_x + 10, row_y, full_section)

                # 地號（左對齊）
                c.drawString(table_x + col_widths[0] + 10, row_y, lot_number)

                # 土地面積（置中對齊）
                self._draw_centered_text(
                    c, f"{int(land_area):,}" if land_area else "0",
                    table_x + sum(col_widths[:2]), row_y,
                    col_widths[2],
                    font_size=table_font_size
                )

                # 施設面積（置中對齊）
                self._draw_centered_text(
                    c, f"{int(facility_area):,}" if facility_area else "0",
                    table_x + sum(col_widths[:3]), row_y,
                    col_widths[3],
                    font_size=table_font_size
                )

                total_land_area += land_area
                total_facility_area += facility_area

                # 資料行底線
                current_y -= row_height
                c.line(table_x, current_y, table_x + total_width, current_y)

            # === 合計行 ===
            row_y = current_y - row_height / 2 - table_font_size * 0.2

            # "合計"文字（置中對齊，跨前兩欄）
            self._draw_centered_text(
                c, "合計",
                table_x, row_y,
                sum(col_widths[:2]),
                font_size=table_font_size
            )

            # 土地面積合計（置中對齊）
            self._draw_centered_text(
                c, f"{int(total_land_area):,}",
                table_x + sum(col_widths[:2]), row_y,
                col_widths[2],
                font_size=table_font_size
            )

            # 施設面積合計（置中對齊）
            self._draw_centered_text(
                c, f"{int(total_facility_area):,}",
                table_x + sum(col_widths[:3]), row_y,
                col_widths[3],
                font_size=table_font_size
            )

            current_y -= row_height

        current_y -= 20
        # "以下空白"分隔線
        c.setFont(self.font_name, 10)
        separator = "--------------------以下空白--------------------"
        sep_width = c.stringWidth(separator, self.font_name, 10)
        c.drawString((width - sep_width) / 2, current_y, separator)

        c.showPage()

    def _generate_power_storage_table_page(self, c: canvas.Canvas, data: Dict[str, Any]) -> None:
        """生成第 4 頁：動力設施與調蓄設施數量表"""
        width, height = A4
        current_y = height - 80

        # 標題
        c.setFont(self.font_name, 18)
        title = "動力設施與調蓄設施數量表"
        title_width = c.stringWidth(title, self.font_name, 18)
        c.drawString((width - title_width) / 2, current_y, title)
        current_y -= 50

        # 基本資訊
        c.setFont(self.font_name, 12)
        c.drawString(60, current_y, f"申請案號:{data.get('case_number', '')}")
        current_y -= 25
        c.drawString(60, current_y, f"設施型式:{data.get('facility_type', '')}")
        current_y -= 25
        c.drawString(60, current_y, f"坵塊形狀:{data.get('block_shape', '135m ×33m')}")
        current_y -= 25
        c.drawString(60, current_y, f"噴頭配置間距(SSxSL):{data.get('nozzle_spacing', '1 x 5.8')}")
        current_y -= 50

        # === 動力設施數量表 ===
        c.setFont(self.font_name, 14)
        subtitle = "動力設施數量表"
        subtitle_width = c.stringWidth(subtitle, self.font_name, 14)
        c.drawString((width - subtitle_width) / 2, current_y, subtitle)
        current_y -= 35

        # 動力設施表格
        power_items = data.get('power_items', [{'name': '馬達+抽水機', 'quantity': 1, 'amount': 4000}])
        table_x = 100
        col_widths = [200, 100, 100]
        row_height = 25
        table_font_size = 11

        # 計算表格高度
        total_width = sum(col_widths)
        table_height = row_height * (len(power_items) + 2)  # 標題行 + 資料行 + 小計行
        table_start_y = current_y

        # === 繪製表格外框 ===
        c.rect(table_x, table_start_y - table_height, total_width, table_height)

        # === 繪製垂直分隔線 ===
        vertical_positions = [0]
        for width_val in col_widths:
            vertical_positions.append(vertical_positions[-1] + width_val)

        for i in range(1, len(vertical_positions) - 1):
            line_x = table_x + vertical_positions[i]
            c.line(line_x, table_start_y, line_x, table_start_y - table_height)

        # === 繪製標題行 ===
        headers = ["動力設備", "數量", "金額"]
        c.setFont(self.font_name, table_font_size)

        for i, header in enumerate(headers):
            col_x = table_x + vertical_positions[i]
            col_width = col_widths[i]
            self._draw_centered_text(
                c, header,
                col_x, table_start_y - row_height / 2 - table_font_size * 0.2,
                col_width,
                font_size=table_font_size
            )

        # 標題行底線
        c.line(table_x, table_start_y - row_height, table_x + total_width, table_start_y - row_height)
        current_y = table_start_y - row_height

        # === 繪製資料行 ===
        power_total = 0
        for item in power_items:
            row_y = current_y - row_height / 2 - table_font_size * 0.2

            # 動力設備名稱（左對齊）
            c.drawString(table_x + 10, row_y, item.get('name', ''))

            # 數量（置中對齊）
            self._draw_centered_text(
                c, str(item.get('quantity', '')),
                table_x + col_widths[0], row_y,
                col_widths[1],
                font_size=table_font_size
            )

            # 金額（置中對齊）
            self._draw_centered_text(
                c, f"{item.get('amount', 0):,}",
                table_x + sum(col_widths[:2]), row_y,
                col_widths[2],
                font_size=table_font_size
            )

            power_total += item.get('amount', 0)
            current_y -= row_height
            c.line(table_x, current_y, table_x + total_width, current_y)

        # === 小計行 ===
        row_y = current_y - row_height / 2 - table_font_size * 0.2

        # "小計"文字（置中對齊，跨前兩欄）
        self._draw_centered_text(
            c, "小計",
            table_x, row_y,
            sum(col_widths[:2]),
            font_size=table_font_size
        )

        # 金額小計（置中對齊）
        self._draw_centered_text(
            c, f"{power_total:,}",
            table_x + sum(col_widths[:2]), row_y,
            col_widths[2],
            font_size=table_font_size
        )

        current_y -= row_height + 50

        # === 調蓄設施數量表 ===
        c.setFont(self.font_name, 14)
        subtitle = "調蓄設施數量表"
        subtitle_width = c.stringWidth(subtitle, self.font_name, 14)
        c.drawString((width - subtitle_width) / 2, current_y, subtitle)
        current_y -= 35

        # 調蓄設施表格
        storage_items = data.get('storage_items', [
            {'material': '不鏽鋼', 'tonnage': 10, 'quantity': 1, 'amount': 40000},
            {'material': '不鏽鋼', 'tonnage': 10, 'quantity': 1, 'amount': 40000}
        ])
        col_widths = [100, 100, 100, 100]

        # 計算表格高度
        total_width = sum(col_widths)
        table_height = row_height * (len(storage_items) + 2)  # 標題行 + 資料行 + 小計行
        table_start_y = current_y

        # === 繪製表格外框 ===
        c.rect(table_x, table_start_y - table_height, total_width, table_height)

        # === 繪製垂直分隔線 ===
        vertical_positions = [0]
        for width_val in col_widths:
            vertical_positions.append(vertical_positions[-1] + width_val)

        for i in range(1, len(vertical_positions) - 1):
            line_x = table_x + vertical_positions[i]
            c.line(line_x, table_start_y, line_x, table_start_y - table_height)

        # === 繪製標題行 ===
        headers = ["材質", "噸數", "數量", "金額"]
        c.setFont(self.font_name, table_font_size)

        for i, header in enumerate(headers):
            col_x = table_x + vertical_positions[i]
            col_width = col_widths[i]
            self._draw_centered_text(
                c, header,
                col_x, table_start_y - row_height / 2 - table_font_size * 0.2,
                col_width,
                font_size=table_font_size
            )

        # 標題行底線
        c.line(table_x, table_start_y - row_height, table_x + total_width, table_start_y - row_height)
        current_y = table_start_y - row_height

        # === 繪製資料行 ===
        storage_total = 0
        for item in storage_items:
            row_y = current_y - row_height / 2 - table_font_size * 0.2

            # 材質（置中對齊）
            self._draw_centered_text(
                c, item.get('material', ''),
                table_x, row_y,
                col_widths[0],
                font_size=table_font_size
            )

            # 噸數（置中對齊）
            self._draw_centered_text(
                c, str(item.get('tonnage', '')),
                table_x + col_widths[0], row_y,
                col_widths[1],
                font_size=table_font_size
            )

            # 數量（置中對齊）
            self._draw_centered_text(
                c, str(item.get('quantity', '')),
                table_x + sum(col_widths[:2]), row_y,
                col_widths[2],
                font_size=table_font_size
            )

            # 金額（置中對齊）
            self._draw_centered_text(
                c, f"{item.get('amount', 0):,}",
                table_x + sum(col_widths[:3]), row_y,
                col_widths[3],
                font_size=table_font_size
            )

            storage_total += item.get('amount', 0)
            current_y -= row_height
            c.line(table_x, current_y, table_x + total_width, current_y)

        # === 小計行 ===
        row_y = current_y - row_height / 2 - table_font_size * 0.2

        # "小計"文字（置中對齊，跨前三欄）
        self._draw_centered_text(
            c, "小計",
            table_x, row_y,
            sum(col_widths[:3]),
            font_size=table_font_size
        )

        # 金額小計（置中對齊）
        self._draw_centered_text(
            c, f"{storage_total:,}",
            table_x + sum(col_widths[:3]), row_y,
            col_widths[3],
            font_size=table_font_size
        )

        current_y -= row_height + 40

        # "以下空白"分隔線
        c.setFont(self.font_name, 10)
        separator = "--------------------以下空白--------------------"
        sep_width = c.stringWidth(separator, self.font_name, 10)
        c.drawString((width - sep_width) / 2, current_y, separator)

        c.showPage()

    def _generate_pipe_materials_table_page(self, c: canvas.Canvas, data: Dict[str, Any]) -> None:
        """生成第 5 頁：管路灌溉系統材料數量表"""
        width, height = A4
        current_y = height - 80

        # 標題
        c.setFont(self.font_name, 18)
        title = "管路灌溉系統材料數量表"
        title_width = c.stringWidth(title, self.font_name, 18)
        c.drawString((width - title_width) / 2, current_y, title)
        current_y -= 50

        # 基本資訊
        c.setFont(self.font_name, 12)
        c.drawString(60, current_y, f"申請案號:{data.get('case_number', '')}")
        current_y -= 25
        c.drawString(60, current_y, f"設施型式:{data.get('facility_type', '')}")
        current_y -= 25
        c.drawString(60, current_y, f"坵塊形狀:{data.get('block_shape', '135m ×33m')}")
        current_y -= 25
        c.drawString(60, current_y, f"噴頭配置間距(SSxSL):{data.get('nozzle_spacing', '1 x 5.8')}")
        current_y -= 50

        # === 材料數量表 ===
        pipe_materials = data.get('pipe_materials', [])
        table_x = 40
        col_widths = [40, 100, 80, 50, 60, 60, 70]
        row_height = 20
        table_font_size = 10

        # 計算表格高度
        total_width = sum(col_widths)
        table_height = row_height * (len(pipe_materials) + 2)  # 標題行 + 資料行 + 總價行
        table_start_y = current_y

        # === 繪製表格外框 ===
        c.rect(table_x, table_start_y - table_height, total_width, table_height)

        # === 繪製垂直分隔線 ===
        vertical_positions = [0]
        for width_val in col_widths:
            vertical_positions.append(vertical_positions[-1] + width_val)

        for i in range(1, len(vertical_positions) - 1):
            line_x = table_x + vertical_positions[i]
            c.line(line_x, table_start_y, line_x, table_start_y - table_height)

        # === 繪製標題行 ===
        headers = ["項目", "材料名稱", "規格", "單位", "單價", "數量", "總價"]
        c.setFont(self.font_name, table_font_size)

        for i, header in enumerate(headers):
            col_x = table_x + vertical_positions[i]
            col_width = col_widths[i]
            self._draw_centered_text(
                c, header,
                col_x, table_start_y - row_height / 2 - table_font_size * 0.2,
                col_width,
                font_size=table_font_size
            )

        # 標題行底線
        c.line(table_x, table_start_y - row_height, table_x + total_width, table_start_y - row_height)
        current_y = table_start_y - row_height

        # === 繪製資料行 ===
        grand_total = 0
        for item in pipe_materials:
            row_y = current_y - row_height / 2 - table_font_size * 0.2

            # 項目（置中對齊）
            self._draw_centered_text(
                c, item.get('category', ''),
                table_x, row_y,
                col_widths[0],
                font_size=table_font_size
            )

            # 材料名稱（左對齊）
            c.drawString(table_x + col_widths[0] + 5, row_y, item.get('name', ''))

            # 規格（左對齊）
            c.drawString(table_x + sum(col_widths[:2]) + 5, row_y, item.get('spec', ''))

            # 單位（置中對齊）
            self._draw_centered_text(
                c, item.get('unit', ''),
                table_x + sum(col_widths[:3]), row_y,
                col_widths[3],
                font_size=table_font_size
            )

            # 單價（置中對齊）
            self._draw_centered_text(
                c, str(item.get('price', '')),
                table_x + sum(col_widths[:4]), row_y,
                col_widths[4],
                font_size=table_font_size
            )

            # 數量（置中對齊）
            self._draw_centered_text(
                c, str(item.get('quantity', '')),
                table_x + sum(col_widths[:5]), row_y,
                col_widths[5],
                font_size=table_font_size
            )

            # 總價（置中對齊）
            self._draw_centered_text(
                c, f"{item.get('total', 0):,}",
                table_x + sum(col_widths[:6]), row_y,
                col_widths[6],
                font_size=table_font_size
            )

            grand_total += item.get('total', 0)
            current_y -= row_height
            c.line(table_x, current_y, table_x + total_width, current_y)

        # === 總價行 ===
        row_y = current_y - row_height / 2 - table_font_size * 0.2

        # "總價"文字（置中對齊，跨前六欄）
        self._draw_centered_text(
            c, "總價",
            table_x, row_y,
            sum(col_widths[:6]),
            font_size=table_font_size
        )

        # 總價金額（置中對齊）
        self._draw_centered_text(
            c, f"{grand_total:,}",
            table_x + sum(col_widths[:6]), row_y,
            col_widths[6],
            font_size=table_font_size
        )

        current_y -= row_height + 40

        # "以下空白"分隔線
        c.setFont(self.font_name, 10)
        separator = "--------------------以下空白--------------------"
        sep_width = c.stringWidth(separator, self.font_name, 10)
        c.drawString((width - sep_width) / 2, current_y, separator)

        c.showPage()

    def _generate_control_materials_table_page(self, c: canvas.Canvas, data: Dict[str, Any]) -> None:
        """生成第 6 頁：調控設施材料數量表"""
        width, height = A4
        current_y = height - 80

        # 標題
        c.setFont(self.font_name, 18)
        title = "調控設施材料數量表"
        title_width = c.stringWidth(title, self.font_name, 18)
        c.drawString((width - title_width) / 2, current_y, title)
        current_y -= 50

        # 基本資訊
        c.setFont(self.font_name, 12)
        c.drawString(60, current_y, f"申請案號:{data.get('case_number', '')}")
        current_y -= 25
        c.drawString(60, current_y, f"設施型式:{data.get('facility_type', '')}")
        current_y -= 25
        c.drawString(60, current_y, f"坵塊形狀:{data.get('block_shape', '135m ×33m')}")
        current_y -= 25
        c.drawString(60, current_y, f"噴頭配置間距(SSxSL):{data.get('nozzle_spacing', '1 x 5.8')}")
        current_y -= 50

        # === 調控設施材料表 ===
        control_materials = data.get('control_materials', [
            {'category': '1. 微氣象調節', 'name': '微噴霧降溫設施', 'spec': '', 'unit': '', 'price': 473340, 'quantity': 1, 'total': 473340}
        ])
        table_x = 40
        col_widths = [40, 100, 80, 50, 60, 60, 70]
        row_height = 20
        table_font_size = 10

        # 計算表格高度（每個 item 佔兩行：category行 + 資料行）
        total_width = sum(col_widths)
        table_height = row_height * (len(control_materials) * 2 + 2)  # 標題行 + (category行+資料行)*N + 總價行
        table_start_y = current_y

        # === 繪製表格外框 ===
        c.rect(table_x, table_start_y - table_height, total_width, table_height)

        # === 繪製垂直分隔線 ===
        vertical_positions = [0]
        for width_val in col_widths:
            vertical_positions.append(vertical_positions[-1] + width_val)

        for i in range(1, len(vertical_positions) - 1):
            line_x = table_x + vertical_positions[i]
            c.line(line_x, table_start_y, line_x, table_start_y - table_height)

        # === 繪製標題行 ===
        headers = ["項目", "材料名稱", "規格", "單位", "單價", "數量", "總價"]
        c.setFont(self.font_name, table_font_size)

        for i, header in enumerate(headers):
            col_x = table_x + vertical_positions[i]
            col_width = col_widths[i]
            self._draw_centered_text(
                c, header,
                col_x, table_start_y - row_height / 2 - table_font_size * 0.2,
                col_width,
                font_size=table_font_size
            )

        # 標題行底線
        c.line(table_x, table_start_y - row_height, table_x + total_width, table_start_y - row_height)
        current_y = table_start_y - row_height

        # === 繪製資料行（每個 item 佔兩行） ===
        grand_total = 0
        for item in control_materials:
            # 第一行：項目類別（category）
            row_y = current_y - row_height / 2 - table_font_size * 0.2
            c.drawString(table_x + 5, row_y, item.get('category', ''))
            current_y -= row_height
            c.line(table_x, current_y, table_x + total_width, current_y)

            # 第二行：材料資料
            row_y = current_y - row_height / 2 - table_font_size * 0.2

            # 材料名稱（左對齊，跨第一、二欄）
            c.drawString(table_x + col_widths[0] + 5, row_y, item.get('name', ''))

            # 單價（置中對齊）
            self._draw_centered_text(
                c, str(item.get('price', '')),
                table_x + sum(col_widths[:4]), row_y,
                col_widths[4],
                font_size=table_font_size
            )

            # 數量（置中對齊）
            self._draw_centered_text(
                c, str(item.get('quantity', '')),
                table_x + sum(col_widths[:5]), row_y,
                col_widths[5],
                font_size=table_font_size
            )

            # 總價（置中對齊）
            self._draw_centered_text(
                c, f"{item.get('total', 0):,}",
                table_x + sum(col_widths[:6]), row_y,
                col_widths[6],
                font_size=table_font_size
            )

            grand_total += item.get('total', 0)
            current_y -= row_height
            c.line(table_x, current_y, table_x + total_width, current_y)

        # === 總價行 ===
        row_y = current_y - row_height / 2 - table_font_size * 0.2

        # "總價"文字（置中對齊，跨前六欄）
        self._draw_centered_text(
            c, "總價",
            table_x, row_y,
            sum(col_widths[:6]),
            font_size=table_font_size
        )

        # 總價金額（置中對齊）
        self._draw_centered_text(
            c, f"{grand_total:,}",
            table_x + sum(col_widths[:6]), row_y,
            col_widths[6],
            font_size=table_font_size
        )

        current_y -= row_height + 40

        # "以下空白"分隔線
        c.setFont(self.font_name, 10)
        separator = "--------------------以下空白--------------------"
        sep_width = c.stringWidth(separator, self.font_name, 10)
        c.drawString((width - sep_width) / 2, current_y, separator)

        c.showPage()

    def _generate_design_diagram_page(self, c: canvas.Canvas, data: Dict[str, Any]) -> None:
        """生成第 7 頁：推廣管路灌溉設施計畫系統設施設計圖"""
        width, height = A4
        current_y = height - 60

        # 標題
        c.setFont(self.font_name, 16)
        title = "推廣管路灌溉設施計畫系統設施設計圖"
        title_width = c.stringWidth(title, self.font_name, 16)
        c.drawString((width - title_width) / 2, current_y, title)
        current_y -= 40

        # 基本資訊
        c.setFont(self.font_name, 11)
        c.drawString(60, current_y, f"申請人：{data.get('applicant_name', '')}")
        c.drawString(250, current_y, f"施設型式：{data.get('facility_type', '')}")
        c.drawString(450, current_y, f"申請案號：{data.get('case_number', '')}")
        current_y -= 25

        land_location = data.get('land_location', '')
        c.drawString(60, current_y, f"施設縣市、鄉鎮、地段、地號及面積詳如土地清冊，合計面積{data.get('total_facility_area_m2', 4500)} m²")
        current_y -= 25

        nozzle_spacing = data.get('nozzle_spacing', '1 x 5.8').split(' x ')
        sl = nozzle_spacing[1] if len(nozzle_spacing) > 1 else '5.8'
        ss = nozzle_spacing[0] if len(nozzle_spacing) > 0 else '1'
        l1 = data.get('main_pipe_1_length', 140)

        c.drawString(60, current_y, f"行距(SL)：{sl} m")
        c.drawString(200, current_y, f"間距(SS)：{ss} m")
        c.drawString(350, current_y, f"長度(L1)：{l1} m")
        current_y -= 40

        # 地籍圖區域（大空白區域）
        c.setFont(self.font_name, 12)
        box_x = 60
        box_y = 150
        box_width = width - 120
        box_height = current_y - box_y - 20

        # 繪製邊框
        c.rect(box_x, box_y, box_width, box_height)

        # 標示
        c.drawString(box_x + 10, current_y - 20, "地籍圖：")
        c.drawString(box_x + box_width - 100, current_y - 20, "比例尺：")

        c.showPage()

    def _generate_photos_page(self, c: canvas.Canvas, data: Dict[str, Any]) -> None:
        """生成第 8 頁：照片頁"""
        width, height = A4
        current_y = height - 60

        # 標題資訊
        c.setFont(self.font_name, 12)
        c.drawString(60, current_y, f"申請案號:{data.get('case_number', '')}")
        c.drawString(300, current_y, f"申請人姓名:{data.get('applicant_name', '')}")
        current_y -= 40

        # 照片區域定義
        photo_sections = [
            ("施\n工\n前", "施工前照片"),
            ("施\n工\n後", "施工後照片及系統施噴、滴灌溉情形"),
            ("動\n力\n設\n備", "動力設備照片"),
            ("調\n蓄\n設\n施", "調蓄設施照片"),
            ("調\n節\n控\n制\n設\n施", "調節控制設施照片")
        ]

        c.setFont(self.font_name, 10)
        photo_width = 460
        photo_height = 120
        label_width = 50

        for label, description in photo_sections:
            # 繪製標籤區域
            c.rect(60, current_y - photo_height, label_width, photo_height)
            # 垂直文字（簡化處理）
            label_y = current_y - 20
            for char in label.split('\n'):
                c.drawString(70, label_y, char)
                label_y -= 15

            # 繪製照片區域
            c.rect(60 + label_width, current_y - photo_height, photo_width, photo_height)
            # 照片說明
            c.drawString(60 + label_width + photo_width//2 - 50, current_y - photo_height//2, description)

            current_y -= (photo_height + 10)

        # 備註
        current_y -= 10
        c.setFont(self.font_name, 9)
        c.drawString(60, current_y, "備註：本表之照片可由印表機直接列印出或以沖洗之照片粘貼方式均可，其張數自行調整")

        c.showPage()

    def _generate_receipt_page(self, c: canvas.Canvas, data: Dict[str, Any]) -> None:
        """生成第 9 頁：領款收據"""
        width, height = A4
        current_y = height - 120

        # 標題
        c.setFont(self.font_name, 22)
        title = "領 款 收 據"
        title_width = c.stringWidth(title, self.font_name, 22)
        c.drawString((width - title_width) / 2, current_y, title)
        current_y -= 80

        # 金額（中文大寫）
        c.setFont(self.font_name, 16)
        govt_subsidy = data.get('govt_subsidy_total', 246078)
        amount_chinese = self._amount_to_chinese(govt_subsidy)
        amount_text = f"新臺幣:{amount_chinese}"
        amount_width = c.stringWidth(amount_text, self.font_name, 16)
        c.drawString((width - amount_width) / 2, current_y, amount_text)
        current_y -= 60

        # 說明文字
        c.setFont(self.font_name, 14)
        text = "此係推廣管路灌溉設施補助款，上款如數領訖無訛。"
        text_width = c.stringWidth(text, self.font_name, 14)
        c.drawString((width - text_width) / 2, current_y, text)
        current_y -= 60

        # "此致"
        c.drawString(120, current_y, "此致")
        current_y -= 40

        office_name = data.get('office_name', '石門管理處')
        office_text = f"農業部農田水利署{office_name}"
        office_width = c.stringWidth(office_text, self.font_name, 14)
        c.drawString((width - office_width) / 2, current_y, office_text)
        current_y -= 60

        # 領款人資訊
        c.drawString(80, current_y, f"申請案號:{data.get('case_number', '')}")
        current_y -= 35
        c.drawString(80, current_y, f"領款人(簽名或蓋章):{data.get('applicant_name', '')}")
        current_y -= 35
        c.drawString(80, current_y, f"身分證字號:{data.get('id_number', '')}")
        current_y -= 35
        c.drawString(80, current_y, f"通訊地址:{data.get('address', '')}")
        current_y -= 35
        c.drawString(80, current_y, f"聯絡電話:{data.get('phone', '')}")
        current_y -= 80

        # 日期
        c.setFont(self.font_name, 16)
        date_text = "中    華    民    國          年        月        日"
        date_width = c.stringWidth(date_text, self.font_name, 16)
        c.drawString((width - date_width) / 2, current_y, date_text)

        c.showPage()

    def _generate_test_report_page(self, c: canvas.Canvas, data: Dict[str, Any]) -> None:
        """生成第 10 頁：推廣管路灌溉設施補助功能測試報告書"""
        width, height = A4
        current_y = height - 60

        # 標題
        c.setFont(self.font_name, 18)
        title = "推廣管路灌溉設施補助功能測試報告書"
        title_width = c.stringWidth(title, self.font_name, 18)
        c.drawString((width - title_width) / 2, current_y, title)
        current_y -= 50

        # 基本資訊
        c.setFont(self.font_name, 11)
        c.drawString(60, current_y, f"一、申請人：{data.get('applicant_name', '')}")
        c.drawString(300, current_y, f"申請案號：{data.get('case_number', '')}")
        current_y -= 25

        c.drawString(60, current_y, f"二、設施地點：{data.get('land_location', '')},等{data.get('land_count', 1)}筆(詳如土地清冊)。")
        current_y -= 25

        c.drawString(60, current_y, f"三、申請面積：{data.get('facility_area_ha', '0.45')}公頃")
        current_y -= 25

        c.drawString(60, current_y, f"四、設施型式：{data.get('facility_type', '')}")
        current_y -= 25

        c.drawString(60, current_y, "五、測試日期：     年     月     日")
        current_y -= 25

        c.drawString(60, current_y, "六、功能測試：")
        current_y -= 30

        # === 功能測試表格 ===
        table_x = 80
        col_widths = [120, 350]
        row_height = 25
        table_font_size = 10

        test_items = [
            ("1.設施型式", "與設計圖說 □相符, □不符"),
            ("2.設施規格", "(詳細規格檢查項目)"),
            ("3.功能測試", "經現場運轉功能正常 □相符, □不符")
        ]

        # 計算表格高度
        total_width = sum(col_widths)
        table_height = row_height * len(test_items)
        table_start_y = current_y

        # === 繪製表格外框 ===
        c.rect(table_x, table_start_y - table_height, total_width, table_height)

        # === 繪製垂直分隔線 ===
        c.line(table_x + col_widths[0], table_start_y, table_x + col_widths[0], table_start_y - table_height)

        # === 繪製資料行 ===
        c.setFont(self.font_name, table_font_size)
        current_y = table_start_y

        for item_name, item_content in test_items:
            row_y = current_y - row_height / 2 - table_font_size * 0.2

            # 項目名稱（左對齊）
            c.drawString(table_x + 10, row_y, item_name)

            # 項目內容（左對齊）
            c.drawString(table_x + col_widths[0] + 10, row_y, item_content)

            current_y -= row_height
            if current_y > table_start_y - table_height:  # 不繪製最後一行的底線（已有外框）
                c.line(table_x, current_y, table_x + total_width, current_y)

        current_y -= 40

        c.drawString(60, current_y, "七、辦理結果：")
        current_y -= 25

        c.setFont(self.font_name, 9)
        c.drawString(80, current_y, "測試  1.□合格，依核定補助款發放__________元")
        current_y -= 18
        c.drawString(100, current_y, "2.□合格，依核定補助款減列金額，發放__________元(請說明原因)")
        current_y -= 18
        c.drawString(100, current_y, "3.□不合格，限期改善再行驗收(請註明   年   月   日完成改善)")
        current_y -= 30

        c.drawString(80, current_y, "複查  1.□合格，依核定補助款發放__________元")
        current_y -= 18
        c.drawString(100, current_y, "2.□合格，依核定補助款減列金額，發放__________元(請說明原因)")
        current_y -= 18
        c.drawString(100, current_y, "3.□不合格，取消補助資格")
        current_y -= 40

        c.drawString(60, current_y, "備註:")
        current_y -= 80

        # 簽核欄位
        self._draw_signature_section(c, 60, current_y)

        c.showPage()

    def _generate_review_checklist_page(self, c: canvas.Canvas, data: Dict[str, Any]) -> None:
        """生成第 11 頁：申請案件書面審查表"""
        width, height = A4
        current_y = height - 80

        # 標題
        c.setFont(self.font_name, 18)
        title = "申請案件書面審查表"
        title_width = c.stringWidth(title, self.font_name, 18)
        c.drawString((width - title_width) / 2, current_y, title)
        current_y -= 50

        # 申請案號
        c.setFont(self.font_name, 12)
        c.drawString(200, current_y, f"申請案號")
        c.drawString(350, current_y, data.get('case_number', ''))
        current_y -= 40

        # === 應附文件檢查清單表格 ===
        documents = [
            "1.推廣管路灌溉設施補助申請表",
            "2.國民身分證正反面影本",
            "3.地籍圖謄本及三個月內之土地登記謄本",
            "4.施設需農業用地作農業設施者容許使用文件",
            "5.土地所有權人同意施設證明書或國公有土地租賃契約影本",
            "6.推廣管路灌溉設施補助切結書",
            "7.工程預算書",
            "8.施設完成後之結案申報書",
            "9.施設前、後照片",
            "10.設施性能規格之證明文件",
            "    載明廠牌、品名及型號之統一發票或收據",
            "    出廠證明書",
            "11.領據、相關單據",
            "12.其他指定文件"
        ]

        table_x = 60
        col_widths = [320, 60, 60, 90]
        row_height = 20
        table_font_size = 10

        # 計算表格高度
        total_width = sum(col_widths)
        table_height = row_height * (len(documents) + 1)  # 標題行 + 文件清單
        table_start_y = current_y

        # === 繪製表格外框 ===
        c.rect(table_x, table_start_y - table_height, total_width, table_height)

        # === 繪製垂直分隔線 ===
        vertical_positions = [0]
        for width_val in col_widths:
            vertical_positions.append(vertical_positions[-1] + width_val)

        for i in range(1, len(vertical_positions) - 1):
            line_x = table_x + vertical_positions[i]
            c.line(line_x, table_start_y, line_x, table_start_y - table_height)

        # === 繪製標題行 ===
        headers = ["應附文件", "合格", "不合格", "備註"]
        c.setFont(self.font_name, table_font_size)

        for i, header in enumerate(headers):
            col_x = table_x + vertical_positions[i]
            col_width = col_widths[i]
            self._draw_centered_text(
                c, header,
                col_x, table_start_y - row_height / 2 - table_font_size * 0.2,
                col_width,
                font_size=table_font_size
            )

        # 標題行底線
        c.line(table_x, table_start_y - row_height, table_x + total_width, table_start_y - row_height)
        current_y = table_start_y - row_height

        # === 繪製文件清單 ===
        for doc in documents:
            row_y = current_y - row_height / 2 - table_font_size * 0.2

            # 文件名稱（左對齊）
            c.drawString(table_x + 10, row_y, doc)

            current_y -= row_height
            c.line(table_x, current_y, table_x + total_width, current_y)

        # === 審查結果 ===
        current_y -= 20
        c.setFont(self.font_name, 12)
        c.drawString(60, current_y, "審查結果：□合格        □不合格")
        c.drawString(400, current_y, "審查人：")

        c.showPage()

    # =========================================================================
    # 共用輔助方法
    # =========================================================================
    def _draw_budget_detail_table(self, c: canvas.Canvas, data: Dict[str, Any], x: float, start_y: float) -> float:
        """
        繪製預算明細表（Page 2 的核心表格）

        Args:
            c: Canvas 物件
            data: 補助案件資料
            x: 起始 X 座標
            start_y: 起始 Y 座標

        Returns:
            繪製結束後的 Y 座標
        """
        c.setFont(self.font_name, 10)

        # 表格欄位寬度設定（根據實際繪製座標：0, 150, 200, 230, 280, 330, 400, 455）
        col_widths = [125, 115, 41, 50, 50, 65, 70]  # 施設項目、說明、單位、數量、單價、總價、附註
        total_width = sum(col_widths)
        row_height = 18

        # 預算資料（從 data 中取得）
        budget_data = data.get('budget_items', {})
        a_item_total = budget_data.get('a_item_total', 70665)
        a_materials = budget_data.get('a_materials', 70665)
        main_pipe_1_length = budget_data.get('main_pipe_1_length', 140)
        main_pipe_1_qty = budget_data.get('main_pipe_1_qty', 35)
        main_pipe_1_price = budget_data.get('main_pipe_1_price', 292)
        main_pipe_1_total = budget_data.get('main_pipe_1_total', 10220)
        irrigation_system_total = budget_data.get('irrigation_system_total', 60445)
        b_design_fee = budget_data.get('b_design_fee', 1413)
        c_control_total = budget_data.get('c_control_total', 473340)
        d_power_total = budget_data.get('d_power_total', 4000)
        e_storage_total = budget_data.get('e_storage_total', 80000)

        # 計算金額
        total_amount = a_item_total + b_design_fee + c_control_total + d_power_total + e_storage_total
        farmer_contribution = budget_data.get('farmer_contribution', 383340)
        govt_subsidy_a = budget_data.get('govt_subsidy_a', a_item_total)
        govt_subsidy_c = budget_data.get('govt_subsidy_c', 90000)
        govt_subsidy_d = budget_data.get('govt_subsidy_d', d_power_total)
        govt_subsidy_e = budget_data.get('govt_subsidy_e', e_storage_total)
        govt_subsidy_total = govt_subsidy_a + govt_subsidy_c + govt_subsidy_d + govt_subsidy_e
        subtotal = govt_subsidy_total + b_design_fee

        current_y = start_y

        # 表格標題行
        headers = ["施設項目", "說明", "單位", "數量", "單價", "總價", "附註"]
        table_font_size = 12

        # 先不繪製外框和垂直線，等繪製完內容後再根據實際高度繪製
        table_start_y = current_y

        # 計算欄位位置
        vertical_positions = [0]  # 起始位置
        for i in range(len(col_widths)):
            vertical_positions.append(vertical_positions[-1] + col_widths[i])

        # 繪製標題行
        c.setFont(self.font_name, table_font_size)
        for i, header in enumerate(headers):
            col_x = x + vertical_positions[i]
            col_width = col_widths[i]
            self._draw_justified_text(
                c, header,
                col_x + 8, table_start_y - row_height / 2 - table_font_size * 0.3,
                col_width - 16,
                font_size=table_font_size
            )

        # 標題行底線
        c.line(x, table_start_y - row_height, x + total_width, table_start_y - row_height)

        # 繪製內容
        current_y = table_start_y - row_height
        current_y -= row_height * 0.7

        c.setLineWidth(0.1)
        c.drawString(x + 8, current_y, "A.田間管路設施費")
        self._draw_centered_text(c, "(1)", x + col_widths[0], current_y, col_widths[1], font_size=table_font_size)
        self._draw_centered_text(c, "全", x + col_widths[0] + col_widths[1], current_y, col_widths[2], font_size=table_font_size)
        self._draw_right_aligned_text(c, f"{a_item_total:,}", x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3] + col_widths[4], current_y, col_widths[5], font_size=table_font_size)
        c.line(x, current_y - row_height * 0.3, x + total_width, current_y - row_height * 0.3)

        current_y -= row_height
        c.drawString(x + 20, current_y, "(1)材料費")
        self._draw_right_aligned_text(c, f"{a_materials:,}", x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3] + col_widths[4], current_y, col_widths[5], font_size=table_font_size)
        c.line(x, current_y - row_height * 0.3, x + total_width, current_y - row_height * 0.3)

        current_y -= row_height
        c.drawString(x + 38, current_y, f"田間主管1(L1)")
        self._draw_centered_text(c, "支", x + col_widths[0] + col_widths[1], current_y, col_widths[2], font_size=table_font_size)
        self._draw_centered_text(c, f"{main_pipe_1_qty}", x + col_widths[0] + col_widths[1] + col_widths[2], current_y, col_widths[3], font_size=table_font_size)
        self._draw_centered_text(c, f"{main_pipe_1_price}", x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3], current_y, col_widths[4], font_size=table_font_size)
        self._draw_right_aligned_text(c, f"{main_pipe_1_total:,}", x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3] + col_widths[4], current_y, col_widths[5], font_size=table_font_size)
        self._draw_centered_text(c, f"管長{main_pipe_1_length}公尺", x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3] + col_widths[4] + col_widths[5], current_y, col_widths[6], font_size=table_font_size)
        c.line(x, current_y - row_height * 0.3, x + total_width, current_y - row_height * 0.3)

        current_y -= row_height
        c.drawString(x + 38, current_y, "灌溉系統")
        self._draw_centered_text(c, "式", x + col_widths[0] + col_widths[1], current_y, col_widths[2], font_size=table_font_size)
        self._draw_centered_text(c, "1", x + col_widths[0] + col_widths[1] + col_widths[2], current_y, col_widths[3], font_size=table_font_size)
        self._draw_right_aligned_text(c, f"{irrigation_system_total:,}", x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3] + col_widths[4], current_y, col_widths[5], font_size=table_font_size)
        self._draw_centered_text(c, "詳如數量表", x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3] + col_widths[4] + col_widths[5], current_y, col_widths[6], font_size=table_font_size)
        # A項下方分隔線（保持原樣）
        c.setLineWidth(0.5)
        c.line(x, current_y - row_height * 0.3, x + total_width, current_y - row_height * 0.3)
        

        # B項
        current_y -= row_height
        c.drawString(x + 8, current_y, "B.規劃設計費")
        self._draw_centered_text(c, "A. x 2.0%", x + col_widths[0], current_y, col_widths[1], font_size=table_font_size)
        self._draw_centered_text(c, "式", x + col_widths[0] + col_widths[1], current_y, col_widths[2], font_size=table_font_size)
        self._draw_centered_text(c, "1", x + col_widths[0] + col_widths[1] + col_widths[2], current_y, col_widths[3], font_size=table_font_size)
        self._draw_right_aligned_text(c, f"{b_design_fee:,}", x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3] + col_widths[4], current_y, col_widths[5], font_size=table_font_size)
        # B項下方分隔線
        c.line(x, current_y - row_height * 0.3, x + total_width, current_y - row_height * 0.3)

        # C項
        current_y -= row_height
        c.drawString(x + 8, current_y, "C.調控設施")
        self._draw_centered_text(c, "依計畫補助標準", x + col_widths[0], current_y, col_widths[1], font_size=table_font_size)
        self._draw_centered_text(c, "式", x + col_widths[0] + col_widths[1], current_y, col_widths[2], font_size=table_font_size)
        self._draw_centered_text(c, "1", x + col_widths[0] + col_widths[1] + col_widths[2], current_y, col_widths[3], font_size=table_font_size)
        self._draw_right_aligned_text(c, f"{c_control_total:,}", x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3] + col_widths[4], current_y, col_widths[5], font_size=table_font_size)
        self._draw_centered_text(c, "詳如數量表", x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3] + col_widths[4] + col_widths[5], current_y, col_widths[6], font_size=table_font_size)
        # C項下方分隔線
        c.line(x, current_y - row_height * 0.3, x + total_width, current_y - row_height * 0.3)

        # D項
        current_y -= row_height
        c.drawString(x + 8, current_y, "D.動力設備(1台)")
        self._draw_centered_text(c, "依計畫補助標準", x + col_widths[0], current_y, col_widths[1], font_size=table_font_size)
        self._draw_centered_text(c, "式", x + col_widths[0] + col_widths[1], current_y, col_widths[2], font_size=table_font_size)
        self._draw_centered_text(c, "1", x + col_widths[0] + col_widths[1] + col_widths[2], current_y, col_widths[3], font_size=table_font_size)
        self._draw_right_aligned_text(c, f"{d_power_total:,}", x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3] + col_widths[4], current_y, col_widths[5], font_size=table_font_size)
        self._draw_centered_text(c, "詳如數量表", x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3] + col_widths[4] + col_widths[5], current_y, col_widths[6], font_size=table_font_size)
        # D項下方分隔線
        c.line(x, current_y - row_height * 0.3, x + total_width, current_y - row_height * 0.3)

        # E項
        current_y -= row_height
        c.drawString(x + 8, current_y, "E.調蓄設施(20噸)")
        self._draw_centered_text(c, "依計畫補助標準", x + col_widths[0], current_y, col_widths[1], font_size=table_font_size)
        self._draw_centered_text(c, "式", x + col_widths[0] + col_widths[1], current_y, col_widths[2], font_size=table_font_size)
        self._draw_centered_text(c, "1", x + col_widths[0] + col_widths[1] + col_widths[2], current_y, col_widths[3], font_size=table_font_size)
        self._draw_right_aligned_text(c, f"{e_storage_total:,}", x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3] + col_widths[4], current_y, col_widths[5], font_size=table_font_size)
        self._draw_centered_text(c, "詳如數量表", x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3] + col_widths[4] + col_widths[5], current_y, col_widths[6], font_size=table_font_size)
        # E項下方分隔線
        c.line(x, current_y - row_height * 0.3, x + total_width, current_y - row_height * 0.3)

        # 合計
        current_y -= row_height
        self._draw_justified_text(
            c, "合計",
            x + 30, current_y,
            col_widths[0] - 60,
            font_size=table_font_size
        )
        self._draw_right_aligned_text(c, f"{total_amount:,}", x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3] + col_widths[4], current_y, col_widths[5], font_size=table_font_size)
        # 合計下方分隔線
        c.line(x, current_y - row_height * 0.3, x + total_width, current_y - row_height * 0.3)

        # 農戶配合款
        current_y -= row_height
        self._draw_justified_text(
            c, "農戶配合款",
            x + 30, current_y,
            col_widths[0] - 60,
            font_size=table_font_size
        )
        self._draw_right_aligned_text(c, f"{farmer_contribution:,}", x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3] + col_widths[4], current_y, col_widths[5], font_size=table_font_size)
        # 農戶配合款下方分隔線
        c.line(x, current_y - row_height * 0.3, x + total_width, current_y - row_height * 0.3)

        # === 政府補助款（分割左右兩欄）===
        left_col_width = 55  # 左欄寬度（政府/補助款）
        middle_col_width = 70  # 中欄寬度（農戶請領款等標題）
        govt_section_start_y = current_y - row_height

        # 第一列：政府補助款 | 農戶請領款 | A-E項補助費明細 | 金額
        current_y -= row_height
        first_row_y = current_y  # 記錄第一列的 y 位置，稍後用於計算"政府補助款"的垂直居中位置

        # 計算第一列的垂直居中位置
        first_row_center_y = first_row_y - (row_height / 2) * 4 + table_font_size

        # 農戶請領款（分散對齊，垂直居中）
        self._draw_justified_text(
            c, "農戶請領款",
            x + left_col_width + 4, first_row_center_y,
            middle_col_width - 8,
            font_size=table_font_size
        )

        # 政府補助款總額（靠右對齊，垂直居中）
        self._draw_right_aligned_text(c, f"{govt_subsidy_total:,}", x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3] + col_widths[4], first_row_center_y, col_widths[5], font_size=table_font_size)

        # A-E項補助費（在"農戶請領款"右方的欄位中）
        detail_x = x + left_col_width + middle_col_width + 5
        c.drawString(detail_x, current_y, f"A項補助費:{govt_subsidy_a:,}")
        current_y -= row_height * 0.8
        c.drawString(detail_x, current_y, f"C項補助費:{govt_subsidy_c:,}")
        current_y -= row_height * 0.8
        c.drawString(detail_x, current_y, f"D項補助費:{govt_subsidy_d:,}")
        current_y -= row_height * 0.8
        c.drawString(detail_x, current_y, f"E項補助費:{govt_subsidy_e:,}")

        # 農戶請領款下方分隔線（只畫右欄）
        current_y -= row_height * 0.4
        c.line(x + left_col_width, current_y, x + total_width, current_y)

        # 規劃設計費（第二列右側）
        current_y -= row_height * 0.7
        self._draw_justified_text(
            c, "規劃設計費",
            x + left_col_width + 4, current_y,
            middle_col_width - 8,
            font_size=table_font_size
        )
        self._draw_right_aligned_text(c, f"{b_design_fee:,}", x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3] + col_widths[4], current_y, col_widths[5], font_size=table_font_size)
        c.line(x + left_col_width, current_y - row_height * 0.3, x + total_width, current_y - row_height * 0.3)

        # 小計（第三列右側）
        current_y -= row_height
        self._draw_justified_text(
            c, "小計",
            x + left_col_width + 4, current_y,
            middle_col_width - 8,
            font_size=table_font_size
        )
        self._draw_right_aligned_text(c, f"{subtotal:,}", x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3] + col_widths[4], current_y, col_widths[5], font_size=table_font_size)
        c.line(x, current_y - row_height * 0.3, x + total_width, current_y - row_height * 0.3)

        # 小計下方分隔線
        current_y -= row_height
        small_total_bottom_y = current_y

        # === 繪製"政府補助款"（在左欄垂直居中）===
        left_col_top_y = first_row_y
        left_col_bottom_y = small_total_bottom_y
        left_col_center_y = (left_col_top_y + left_col_bottom_y) / 2 + table_font_size + 2
        self._draw_centered_text(
            c, "政府",
            x, left_col_center_y,
            left_col_width,
            font_size=table_font_size
        )
        self._draw_centered_text(
            c, "補助款",
            x, left_col_center_y - table_font_size - 2,
            left_col_width,
            font_size=table_font_size
        )

        # === 本設施預算總計（表格的一部分，右方欄位合併）===
        total_chinese = self._amount_to_chinese(total_amount)

        # 繪製總計文字
        self._draw_justified_text(
            c, "本設施預算總計",
            x + 14, current_y,
            col_widths[0] - 28,
            font_size=table_font_size
        )
        self._draw_centered_text(c, f"新臺幣 {total_chinese}", x + col_widths[0], current_y, col_widths[1] + col_widths[2] + col_widths[3] + col_widths[4] + col_widths[5] + col_widths[6], font_size=table_font_size)

        # 計算總計行底部位置
        current_y -= row_height * 0.3
        table_bottom_y = current_y

        # === 繪製完整表格外框（包含"本設施預算總計"）===
        table_height = table_start_y - table_bottom_y
        c.rect(x, table_bottom_y, total_width, table_height)

        # === 繪製垂直分隔線（分段）===
        # 1. 從表格頂部到"小計"底部：繪製所有欄位的垂直線
        for i in range(1, len(vertical_positions) - 1):
            line_x = x + vertical_positions[i]
            c.line(line_x, table_start_y, line_x, small_total_bottom_y + row_height * 0.7)

        # 2. 繪製政府補助款區域的垂直分隔線（從農戶配合款到小計）
        c.setLineWidth(0.5)
        c.line(x + left_col_width, govt_section_start_y + row_height * 0.7, x + left_col_width, small_total_bottom_y + row_height * 0.7)

        # 3. 從"小計"底部到表格底部：只繪製"本設施預算總計"左側的垂直線
        c.line(x + col_widths[0], small_total_bottom_y + row_height * 0.7, x + col_widths[0], table_bottom_y)

        # 返回繪製結束後的 Y 座標
        return current_y - row_height  # 留一行間距

    def _amount_to_chinese(self, amount: int) -> str:
        """
        將阿拉伯數字金額轉換為中文大寫

        Args:
            amount: 金額（整數）

        Returns:
            中文大寫金額字串
        """
        # 簡化版本：僅處理常見金額範圍
        digits = ['零', '壹', '貳', '參', '肆', '伍', '陸', '柒', '捌', '玖']
        units = ['', '拾', '佰', '仟', '萬', '拾', '佰', '仟', '億']

        if amount == 0:
            return "零元整"

        # 轉換為字串並反轉
        amount_str = str(amount)
        result = []

        for i, digit in enumerate(reversed(amount_str)):
            digit_val = int(digit)
            if digit_val != 0:
                result.append(digits[digit_val] + units[i])
            elif i > 0 and result and result[-1] != '零':
                result.append('零')

        # 反轉回來並清理多餘的零
        result.reverse()
        chinese_amount = ''.join(result)

        # 簡化處理：直接返回（實際應該有更複雜的規則處理）
        return f"{chinese_amount}元整"

    def _draw_signature_section(self, c: canvas.Canvas, x: float, current_y: float) -> float:
        """
        繪製簽核欄位（多頁共用）

        Args:
            c: Canvas 物件
            x: 起始 X 座標
            current_y: 當前 Y 座標（從上往下繪製的頂部位置）

        Returns:
            繪製結束後的 Y 座標
        """
        c.setFont(self.font_name, 12)

        # 繪製 3x6 簽核表格（職稱欄 + 簽名欄交替）
        title_col_width = 70   # 職稱欄位寬度（1, 3, 5）
        sign_col_width = 102   # 簽名欄位寬度（2, 4, 6）
        row_height = 40

        # 欄位寬度數組（交替排列：職稱-簽名-職稱-簽名-職稱-簽名）
        col_widths = [title_col_width, sign_col_width, title_col_width, sign_col_width, title_col_width, sign_col_width]
        table_width = sum(col_widths)
        table_height = row_height * 3

        # 計算表格底部位置（PDF 座標系統從下往上）
        table_bottom_y = current_y - table_height

        # 外框
        c.rect(x, table_bottom_y, table_width, table_height)

        # 計算每個欄位的起始位置
        col_positions = [0]
        for width in col_widths:
            col_positions.append(col_positions[-1] + width)

        # 垂直線
        for i in range(1, len(col_widths)):
            line_x = x + col_positions[i]
            c.line(line_x, table_bottom_y, line_x, table_bottom_y + table_height)

        # 水平線
        for i in range(1, 3):
            c.line(x, table_bottom_y + row_height * i, x + table_width, table_bottom_y + row_height * i)

        # 填入標籤（1,3,5 欄為標題；2,4,6 欄為簽名空白欄）
        labels = [
            ["設計", "", "股長", "", "主任工程師", ""],
            ["審查", "", "組長", "", "副處長", ""],
            ["主辦", "", "主計單位", "", "處長", ""]
        ]

        for row_idx, row in enumerate(labels):
            for col_idx, label in enumerate(row):
                # 使用對應欄位的起始位置
                text_x = x + col_positions[col_idx]
                text_y = table_bottom_y + row_height * (3 - row_idx - 1) + 15
                self._draw_centered_text(
                    c, label,
                    text_x, text_y,
                    title_col_width,
                    font_size=12
                )

        # 返回繪製結束後的 Y 座標
        return table_bottom_y - 10  # 留一點間距
