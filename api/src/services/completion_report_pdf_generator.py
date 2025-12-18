"""
結案申報書 PDF 生成服務

基於範例 PDF 格式，動態生成符合格式的結案申報書文件
"""
import io
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


class CompletionReportPDFGenerator:
    """結案申報書 PDF 生成器"""

    def __init__(self):
        self.font_name = 'Helvetica'
        self.font_available = False
        self._setup_fonts()

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

    def _format_land_info(self, land_data: List[Dict[str, Any]]) -> tuple:
        """
        格式化土地資訊
        返回：(地段字串, 地號字串, 筆數, 總面積m²)
        """
        if not land_data:
            return ("", "", 0, 0)

        # 取第一筆土地的地段資訊
        first_land = land_data[0]
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

        return (land_section, land_no_str, count, int(total_area))

    def _get_irrigation_system_info(self, step_data: Dict[str, Any]) -> Dict[str, bool]:
        """
        從 step4 資料提取灌溉系統資訊
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
        從 step3 資料提取動力設施資訊
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
        從 step3 資料提取調蓄設施資訊
        返回設施描述字串，如 "不鏽鋼10噸2座"
        """
        facilities = step_data.get('facilities', [])

        storage_items = []
        for facility in facilities:
            if facility.get('type') == 'storage':
                name = facility.get('name', '')
                quantity = facility.get('quantity', 0)

                # 簡化描述
                if name and quantity > 0:
                    storage_items.append(f"{name}{quantity}座")

        return '、'.join(storage_items) if storage_items else ""

    def _get_control_facility_info(self, step_data: Dict[str, Any]) -> str:
        """
        從 step3 資料提取調控設施資訊
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

    def generate_completion_report(
        self,
        grant_data: Dict[str, Any],
        land_data: List[Dict[str, Any]],
        step3_data: Dict[str, Any],
        step4_data: Dict[str, Any]
    ) -> bytes:
        """
        生成結案申報書 PDF

        Args:
            grant_data: 補助案件基本資料
            land_data: 土地清冊資料
            step3_data: 步驟3資料（灌溉調控設施）
            step4_data: 步驟4資料（田間管路）

        Returns:
            PDF 檔案的二進位資料
        """
        if not self.font_available:
            raise Exception("中文字體不可用")

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # === 標題 ===
        c.setFont(self.font_name, 22)
        title = "結案申報書"
        title_width = c.stringWidth(title, self.font_name, 20)
        c.drawString((width - title_width - 10) / 2, height - 80, title)

        # === 主要內容段落 ===
        # 提取資料
        year = grant_data.get('year', '')
        county = grant_data.get('county', '')
        town = grant_data.get('town', '')
        land_section, land_no, land_count, total_area_m2 = self._format_land_info(land_data)

        # 建立段落樣式
        paragraph_style = ParagraphStyle(
            name='MainText',
            fontName=self.font_name,
            fontSize=16,
            leading=22,  # 行距（行高）
            alignment=TA_JUSTIFY,  # 左右對齊
            leftIndent=0,
            rightIndent=0,
            firstLineIndent=28  # 首行縮排（兩個全形字）
        )

        # 組合主要文字（單一段落，自動換行）
        main_text = (
            f"茲申請農業部農田水利署{year}年度推廣管路灌溉設施補助，"
            f"設置地點：{county}{town}{land_section}{land_no}地號等{land_count}筆（詳如土地清冊），"
            f"合計面積{total_area_m2}m²，已於民國_____年_____月_____日全部完成，請貴單位辦理結案審查。"
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

        # === 申請項目表格 ===
        y_pos -= 10

        # 表格資料
        irrigation_info = self._get_irrigation_system_info(step4_data)
        power_info = self._get_power_facility_info(step3_data)
        storage_info = self._get_storage_facility_info(step3_data)
        control_info = self._get_control_facility_info(step3_data)

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
        c.drawString(col3_center_x2, y_pos - 27, col3_text2)

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
        row_height = 40
        y_pos -= row_height
        c.rect(table_x, y_pos, table_width * 0.2, row_height)
        review_y = y_pos + row_height / 2
        c.drawString(table_x + 10, review_y, "3.調蓄設施")

        c.rect(table_x + table_width * 0.2, y_pos, table_width * 0.55, row_height)
        if storage_info:
            self._draw_checkbox(c, content_x, y_pos + row_height / 2 - 5, True)
            c.drawString(content_x + 18, y_pos + row_height / 2, storage_info)
        
        c.setLineWidth(2)
        c.rect(table_x + table_width * 0.75, y_pos, table_width * 0.25, row_height)
        review_y = y_pos + row_height / 2
        c.setLineWidth(0.5)
        self._draw_checkbox(c, review_x, review_y - 3)
        c.drawString(review_x + 13, review_y, "相符")
        self._draw_checkbox(c, review_x + 65, review_y - 3)
        c.drawString(review_x + 78, review_y, "不符")

        # 第4行：調控設施
        y_pos -= row_height
        c.rect(table_x, y_pos, table_width * 0.2, row_height)
        review_y = y_pos + row_height / 2
        c.drawString(table_x + 10, review_y, "4.調控設施")

        c.rect(table_x + table_width * 0.2, y_pos, table_width * 0.55, row_height)
        if control_info:
            self._draw_checkbox(c, content_x, y_pos + row_height / 2 - 5, True)
            c.drawString(content_x + 18, y_pos + row_height / 2, control_info)

        c.setLineWidth(2)
        c.rect(table_x + table_width * 0.75, y_pos, table_width * 0.25, row_height)
        review_y = y_pos + row_height / 2
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

        y_pos -= 40
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
