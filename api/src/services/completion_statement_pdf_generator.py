"""
結案申報書 PDF 生成服務

基於範例 PDF 格式，動態生成符合格式的結案申報書文件
"""
import io
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle

from src.utils.chinese_pdf import setup_kaiu_font, setup_chinese_font


class CompletionStatementPDFGenerator:
    """結案申報書 PDF 生成器"""

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

    def _draw_checkbox(self, c: canvas.Canvas, x: float, y: float, checked: bool = False, size: float = 12):
        """繪製核取方塊"""
        if checked:
            # 選中時：繪製實心方塊
            c.rect(x, y, size, size, stroke=1, fill=1)
        else:
            # 未選中：繪製空心方框
            c.rect(x, y, size, size, stroke=1, fill=0)

    def _wrap_text(self, text: str, font_name: str, font_size: float, max_width: float, c: canvas.Canvas) -> List[str]:
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

    def _draw_text_with_wrapping(
        self,
        c: canvas.Canvas,
        text: str,
        x: float,
        y: float,
        row_height: float,
        max_width: float,
        font_size: float = 12,
        line_spacing: float = 16,
        padding: float = 5
    ) -> None:
        """
        繪製支援自動換行的文字，並垂直置中

        Args:
            c: Canvas 物件
            text: 要繪製的文字
            x: 起始 X 座標
            y: 起始 Y 座標（欄位底部）
            row_height: 欄位高度
            max_width: 最大寬度
            font_size: 字體大小
            line_spacing: 行距
            padding: 上下內邊距
        """
        if not text:
            return

        # 換行處理
        lines = self._wrap_text(text, self.font_name, font_size, max_width, c)
        num_lines = len(lines)

        if num_lines == 1:
            # 單行：簡單垂直置中，基線位置在行高的中間偏下一點
            # 調整係數讓文字視覺中心與 checkbox 中心對齊
            line_y = y + row_height / 2 + font_size * 0.1
            c.drawString(x, line_y, lines[0])
        else:
            # 多行：計算整體內容塊的高度並垂直置中
            total_text_height = (num_lines - 1) * line_spacing + font_size

            # 第一行基線位置
            start_y = y + (row_height + total_text_height) / 2 - font_size * 0.3

            # 繪製每一行
            for i, line in enumerate(lines):
                line_y = start_y - i * line_spacing
                c.drawString(x, line_y, line)

    def _calculate_row_height(
        self,
        text: str,
        max_width: float,
        font_size: float,
        line_spacing: float,
        min_height: float,
        padding: float,
        c: canvas.Canvas
    ) -> float:
        """
        根據文字內容計算需要的行高

        Args:
            text: 要計算的文字
            max_width: 最大寬度
            font_size: 字體大小
            line_spacing: 行距
            min_height: 最小行高
            padding: 上下內邊距
            c: Canvas 物件

        Returns:
            計算後的行高
        """
        if not text:
            return min_height

        lines = self._wrap_text(text, self.font_name, font_size, max_width, c)
        num_lines = len(lines)

        # 計算需要的高度：行數 * 行距 + 上下內邊距
        required_height = num_lines * line_spacing + padding * 2

        # 返回最小行高和計算高度的較大值
        return max(min_height, required_height)

    def _format_land_info(self, land_data: List[Dict[str, Any]]) -> tuple:
        """
        格式化土地資訊
        返回：(縣市, 鄉鎮, 地段字串, 地號字串, 筆數, 總面積m²)
        """
        if not land_data:
            return ("", "", "", "", 0, 0)

        # 取第一筆土地的地點資訊
        first_land = land_data[0]
        land_county = first_land.get('land_county', '')
        land_town = first_land.get('land_town', '')
        land_section = first_land.get('land_section', '')

        # 收集所有地號
        land_numbers = []
        total_area = 0

        for land in land_data:
            land_no = land.get('land_number', '')
            if land_no:
                land_numbers.append(land_no)

            # 累加面積（單位：m²）
            area = land.get('facility_area_m2', 0) or 0
            total_area += float(area)

        # 格式化地號（只顯示第一個地號）
        land_no_str = land_numbers[0] if land_numbers else ""
        count = len(land_numbers)

        return (land_county, land_town, land_section, land_no_str, count, int(total_area))

    def _get_irrigation_system_info(self, step_data: Dict[str, Any]) -> Dict[str, bool]:
        """
        從 step5 資料提取灌溉系統資訊
        返回各類型灌溉系統是否存在的標記
        """
        irrigation_type = step_data.get('irrigationType', '')

        return {
            'perforated_pipe': '穿孔管' in irrigation_type,
            'sprinkler': '噴頭' in irrigation_type,
            'micro_sprinkler': '微噴' in irrigation_type,
            'drip': '滴灌' in irrigation_type,
            'not_applied': not irrigation_type
        }

    def _get_power_facility_info(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        從 step4 資料提取動力設施資訊
        """
        facilities = step_data.get('facilities', [])

        motor_count = 0
        plunger_pump_count = 0
        gasoline_engine_count = 0
        diesel_engine_count = 0

        for facility in facilities:
            facility_type = facility.get('type', '')
            if facility_type == 'power':
                name = facility.get('name', '').lower()
                quantity = facility.get('quantity', 0)
                # 確保 quantity 是整數
                quantity = int(quantity) if quantity else 0

                if '馬達' in name or 'motor' in name:
                    motor_count += quantity
                elif '柱塞' in name or 'plunger' in name:
                    plunger_pump_count += quantity
                elif '汽油' in name or 'gasoline' in name:
                    gasoline_engine_count += quantity
                elif '柴油' in name or 'diesel' in name:
                    diesel_engine_count += quantity

        return {
            'motor': motor_count,
            'plunger_pump': plunger_pump_count,
            'gasoline_engine': gasoline_engine_count,
            'diesel_engine': diesel_engine_count,
            'not_applied': motor_count + plunger_pump_count + gasoline_engine_count + diesel_engine_count == 0
        }

    def _get_storage_facility_info(self, step_data: Dict[str, Any]) -> str:
        """
        從 step4 資料提取調蓄設施資訊
        返回設施描述字串，如 "不鏽鋼10噸2座"
        """
        facilities = step_data.get('facilities', [])

        storage_items = []
        for facility in facilities:
            if facility.get('type') == 'storage':
                name = facility.get('name', '')
                quantity = facility.get('quantity', 0)
                # 確保 quantity 是整數
                quantity = int(quantity) if quantity else 0

                # 簡化描述
                if name and quantity > 0:
                    storage_items.append(f"{name}{quantity}座")

        return '、'.join(storage_items) if storage_items else ""

    def _get_control_facility_info(self, step_data: Dict[str, Any]) -> str:
        """
        從 step4 資料提取調控設施資訊
        """
        facilities = step_data.get('facilities', [])

        control_items = []
        for facility in facilities:
            facility_type = facility.get('type', '')
            # 排除動力和調蓄設施
            if facility_type not in ['power', 'storage']:
                name = facility.get('name', '')
                if name:
                    control_items.append(name)

        return '、'.join(control_items) if control_items else ""

    def _get_file_revision_date(self) -> str:
        """
        取得本檔案的最後修改時間

        Returns:
            民國紀年格式的修訂日期字串（格式：民國XXX年XX月XX日）
        """
        try:
            # 取得本檔案的路徑
            file_path = os.path.abspath(__file__)
            # 取得最後修改時間
            mtime = os.path.getmtime(file_path)
            # 轉換為 datetime
            mod_datetime = datetime.fromtimestamp(mtime)
            # 轉換為民國紀年
            roc_year = mod_datetime.year - 1911
            return f"民國{roc_year}年{mod_datetime.month}月{mod_datetime.day}日"
        except Exception:
            return ""

    def generate_completion_statement(
        self,
        grant_data: Dict[str, Any],
        land_data: List[Dict[str, Any]],
        step4_data: Dict[str, Any],
        step5_data: Dict[str, Any]
    ) -> bytes:
        """
        生成結案申報書 PDF

        Args:
            grant_data: 補助案件基本資料
            land_data: 土地清冊資料
            step4_data: 步驟4資料（灌溉調控設施）
            step5_data: 步驟5資料（田間管路）

        Returns:
            PDF 檔案的二進位資料

        Note:
            修訂日期會自動使用本檔案的最後修改時間，以淡灰色字體顯示在 PDF 右上角
        """
        if not self.font_available:
            raise Exception("中文字體不可用")

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # === 修訂日期（右上角）===
        if self.revision_date:
            c.setFont(self.font_name, 8)
            c.setFillColorRGB(0.6, 0.6, 0.6)  # 淡灰色
            revision_text = f"{self.revision_date}修訂"
            revision_text_width = c.stringWidth(revision_text, self.font_name, 8)
            # 右上角位置：右邊距 20pt，上邊距 30pt
            c.drawString(width - revision_text_width - 20, height - 30, revision_text)
            # 重設顏色為黑色
            c.setFillColorRGB(0, 0, 0)

        # === 標題 ===
        c.setFont(self.font_name, 22)
        title = "結案申報書"
        title_width = c.stringWidth(title, self.font_name, 22)
        c.drawString((width - title_width - 10) / 2, height - 80, title)

        # === 主要內容段落 ===
        # 提取資料
        year = grant_data.get('year', '')
        land_county, land_town, land_section, land_no, land_count, total_area_m2 = self._format_land_info(land_data)

        # 建立段落樣式
        paragraph_style = ParagraphStyle(
            name='MainText',
            fontName=self.font_name,
            fontSize=16,
            leading=28,  # 行距（行高）
            alignment=TA_JUSTIFY,  # 左右對齊
            leftIndent=0,
            rightIndent=0,
            firstLineIndent=32  # 首行縮排（兩個全形字）
        )

        # 格式化面積，添加千分位逗號
        formatted_area = f"{total_area_m2:,}"

        # 組合主要文字（單一段落，自動換行）
        main_text = (
            f"茲申請農業部農田水利署{year}年度推廣管路灌溉設施補助，"
            f"設置地點：{land_county}{land_town}{land_section}{land_no}地號等{land_count}筆（詳如土地清冊），"
            f"合計面積{formatted_area}m²，已於民國_____年_____月_____日全部完成，請貴單位辦理結案審查。"
        )

        # 建立並繪製段落
        para = Paragraph(main_text, paragraph_style)
        para_width = width - 120  # 左右各留 60 點邊距
        para_height = 150  # 預估最大高度
        para.wrapOn(c, para_width, para_height)

        y_pos = height - 120
        para.drawOn(c, 60, y_pos - para.height)

        # 更新 y_pos 為段落後的位置
        y_pos = y_pos - para.height - 20

        # 表格資料
        irrigation_info = self._get_irrigation_system_info(step5_data)
        power_info = self._get_power_facility_info(step4_data)
        storage_info = self._get_storage_facility_info(step4_data)
        control_info = self._get_control_facility_info(step4_data)

        # 繪製表格邊框和內容
        table_x = 60
        table_y = y_pos - 200
        table_width = width - 120
        c.setLineWidth(0.5)

        # 表格標題行
        row_height = 30
        c.setFont(self.font_name, 12)

        # 第一欄：申請項目（置中）
        c.rect(table_x, y_pos - 30, table_width * 0.2, row_height)
        col1_text = "申請項目"
        col1_width = c.stringWidth(col1_text, self.font_name, 12)
        col1_center_x = table_x + (table_width * 0.2 - col1_width) / 2
        c.drawString(col1_center_x, y_pos - 18, col1_text)

        # 第二欄：內容（置中）
        c.rect(table_x + table_width * 0.2, y_pos - 30, table_width * 0.55, 30)
        col2_text = "內容"
        col2_width = c.stringWidth(col2_text, self.font_name, 12)
        col2_center_x = table_x + table_width * 0.2 + (table_width * 0.55 - col2_width) / 2
        c.drawString(col2_center_x, y_pos - 18, col2_text)

        # 第三欄：結案自主審查（置中，兩行文字）
        c.setLineWidth(2)
        c.rect(table_x + table_width * 0.75, y_pos - 30, table_width * 0.25, 30)
        col3_text1 = "結案自主審查"
        col3_text2 = "(申請人自行填寫)"
        col3_width1 = c.stringWidth(col3_text1, self.font_name, 12)
        col3_width2 = c.stringWidth(col3_text2, self.font_name, 12)
        col3_center_x1 = table_x + table_width * 0.75 + (table_width * 0.25 - col3_width1) / 2
        col3_center_x2 = table_x + table_width * 0.75 + (table_width * 0.25 - col3_width2) / 2
        c.drawString(col3_center_x1, y_pos - 14, col3_text1)
        c.drawString(col3_center_x2, y_pos - 26, col3_text2)

        # 第1行：灌溉系統
        row_height = 68
        y_pos -= 30 + row_height
        c.setLineWidth(0.5)
        c.rect(table_x, y_pos, table_width * 0.2, row_height)
        review_y = y_pos + row_height / 2
        c.drawString(table_x + 10, review_y, "1.灌溉系統")

        c.rect(table_x + table_width * 0.2, y_pos, table_width * 0.55, row_height)
        content_x = table_x + table_width * 0.2 + 10
        content_y = y_pos + row_height - 15
        # 繪製灌溉系統選項
        self._draw_checkbox(c, content_x, content_y - 3, irrigation_info['perforated_pipe'])
        c.drawString(content_x + 13, content_y, "穿孔管系統")
        self._draw_checkbox(c, content_x + 110, content_y - 3, irrigation_info['sprinkler'])
        c.drawString(content_x + 123, content_y, "噴頭系統")
        content_y -= 20
        self._draw_checkbox(c, content_x, content_y - 3, irrigation_info['micro_sprinkler'])
        c.drawString(content_x + 13, content_y, "微噴系統")
        self._draw_checkbox(c, content_x + 110, content_y - 3, irrigation_info['drip'])
        c.drawString(content_x + 123, content_y, "滴灌系統")
        content_y -= 20
        self._draw_checkbox(c, content_x, content_y - 3, irrigation_info['not_applied'])
        c.drawString(content_x + 13, content_y, "未申請")

        c.setLineWidth(2)
        c.rect(table_x + table_width * 0.75, y_pos, table_width * 0.25, row_height)
        review_x = table_x + table_width * 0.75 + 10
        review_y = y_pos + row_height / 2
        c.setLineWidth(0.5)
        self._draw_checkbox(c, review_x, review_y - 3)
        c.drawString(review_x + 13, review_y, "相符")
        self._draw_checkbox(c, review_x + 65, review_y - 3)
        c.drawString(review_x + 78, review_y, "不符")

        # 第2行：動力設施
        y_pos -= row_height
        c.rect(table_x, y_pos, table_width * 0.2, row_height)
        review_y = y_pos + row_height / 2
        c.drawString(table_x + 10, review_y, "2.動力設施")

        c.rect(table_x + table_width * 0.2, y_pos, table_width * 0.55, row_height)
        content_y = y_pos + row_height - 15
        motor_text = f"馬達{power_info['motor']}台" if power_info['motor'] > 0 else "馬達___台"
        self._draw_checkbox(c, content_x, content_y - 3, power_info['motor'] > 0)
        c.drawString(content_x + 13, content_y, motor_text)
        plunger_text = f"柱塞式泵浦{power_info['plunger_pump']}台" if power_info['plunger_pump'] > 0 else "柱塞式泵浦___台"
        self._draw_checkbox(c, content_x + 110, content_y - 3, power_info['plunger_pump'] > 0)
        c.drawString(content_x + 123, content_y, plunger_text)
        content_y -= 20
        gasoline_text = f"汽油引擎{power_info['gasoline_engine']}台" if power_info['gasoline_engine'] > 0 else "汽油引擎___台"
        self._draw_checkbox(c, content_x, content_y - 3, power_info['gasoline_engine'] > 0)
        c.drawString(content_x + 13, content_y, gasoline_text)
        diesel_text = f"柴油引擎{power_info['diesel_engine']}台" if power_info['diesel_engine'] > 0 else "柴油引擎___台"
        self._draw_checkbox(c, content_x + 110, content_y - 3, power_info['diesel_engine'] > 0)
        c.drawString(content_x + 123, content_y, diesel_text)
        content_y -= 20
        self._draw_checkbox(c, content_x, content_y - 3, power_info['not_applied'])
        c.drawString(content_x + 13, content_y, "未申請")

        c.setLineWidth(2)
        c.rect(table_x + table_width * 0.75, y_pos, table_width * 0.25, row_height)
        review_y = y_pos + row_height / 2
        c.setLineWidth(0.5)
        self._draw_checkbox(c, review_x, review_y - 3)
        c.drawString(review_x + 13, review_y, "相符")
        self._draw_checkbox(c, review_x + 65, review_y - 3)
        c.drawString(review_x + 78, review_y, "不符")

        # 第3行：調蓄設施
        # 計算內容區域的可用寬度（扣除 checkbox 和 padding）
        content_available_width = table_width * 0.55 - 30  # 扣除 checkbox(12) + 間距(13) + 左右 padding(5)

        # 動態計算行高
        row_height_3 = self._calculate_row_height(
            text=storage_info,
            max_width=content_available_width,
            font_size=12,
            line_spacing=16,
            min_height=40,
            padding=8,
            c=c
        )

        y_pos -= row_height_3
        c.rect(table_x, y_pos, table_width * 0.2, row_height_3)
        review_y = y_pos + row_height_3 / 2
        c.drawString(table_x + 10, review_y, "3.調蓄設施")

        c.rect(table_x + table_width * 0.2, y_pos, table_width * 0.55, row_height_3)
        if storage_info:
            self._draw_checkbox(c, content_x, y_pos + row_height_3 / 2 - 3, True)
            # 使用自動換行繪製文字
            self._draw_text_with_wrapping(
                c=c,
                text=storage_info,
                x=content_x + 13,
                y=y_pos - 2,
                row_height=row_height_3,
                max_width=content_available_width,
                font_size=12,
                line_spacing=16
            )

        c.setLineWidth(2)
        c.rect(table_x + table_width * 0.75, y_pos, table_width * 0.25, row_height_3)
        review_y = y_pos + row_height_3 / 2
        c.setLineWidth(0.5)
        self._draw_checkbox(c, review_x, review_y - 3)
        c.drawString(review_x + 13, review_y, "相符")
        self._draw_checkbox(c, review_x + 65, review_y - 3)
        c.drawString(review_x + 78, review_y, "不符")

        # 第4行：調控設施
        # 動態計算行高
        row_height_4 = self._calculate_row_height(
            text=control_info,
            max_width=content_available_width,
            font_size=12,
            line_spacing=16,
            min_height=40,
            padding=8,
            c=c
        )

        y_pos -= row_height_4
        c.rect(table_x, y_pos, table_width * 0.2, row_height_4)
        review_y = y_pos + row_height_4 / 2
        c.drawString(table_x + 10, review_y, "4.調控設施")

        c.rect(table_x + table_width * 0.2, y_pos, table_width * 0.55, row_height_4)
        if control_info:
            self._draw_checkbox(c, content_x, y_pos + row_height_4 / 2 - 3, True)
            # 使用自動換行繪製文字
            self._draw_text_with_wrapping(
                c=c,
                text=control_info,
                x=content_x + 13,
                y=y_pos - 2,
                row_height=row_height_4,
                max_width=content_available_width,
                font_size=12,
                line_spacing=16
            )

        c.setLineWidth(2)
        c.rect(table_x + table_width * 0.75, y_pos, table_width * 0.25, row_height_4)
        review_y = y_pos + row_height_4 / 2
        c.setLineWidth(0.5)
        self._draw_checkbox(c, review_x, review_y - 3)
        c.drawString(review_x + 13, review_y, "相符")
        self._draw_checkbox(c, review_x + 65, review_y - 3)
        c.drawString(review_x + 78, review_y, "不符")

        # === 此致 ===
        y_pos -= 30
        c.setFont(self.font_name, 16)
        c.drawString(90, y_pos, "此致")

        y_pos -= 40
        office_name = grant_data.get('office_name', '')
        office_text = f"農業部農田水利署{office_name}" if '管理處' not in office_name else f"農業部農田水利署{office_name}"

        # 計算置中位置
        office_text_width = c.stringWidth(office_text, self.font_name, 16)
        office_x = (width - office_text_width) / 2
        c.drawString(office_x, y_pos, office_text)

        # === 申請人資訊 ===
        c.setFont(self.font_name, 14)

        y_pos -= 50
        case_number = grant_data.get('case_number', '')
        c.drawString(60, y_pos, f"申請案號：{case_number}")

        y_pos -= 40
        applicant_name = grant_data.get('applicant_name', '')
        c.drawString(60, y_pos, f"申請人（簽名或蓋章）：{applicant_name}")

        y_pos -= 40
        address = grant_data.get('address', '')
        c.drawString(60, y_pos, f"通訊地址：{address}")

        y_pos -= 40
        phone = grant_data.get('phone', '')
        c.drawString(60, y_pos, f"聯絡電話：{phone}")

        # === 日期 ===
        c.setFont(self.font_name, 16)
        
        y_pos -= 60

        # 計算置中位置
        date_text = (f"中華民國            年          月          日")
        date_text_width = c.stringWidth(date_text, self.font_name, 16)
        date_x = (width - date_text_width) / 2
        c.drawString(date_x, y_pos, date_text)

        # 完成 PDF
        c.save()

        buffer.seek(0)
        return buffer.getvalue()
