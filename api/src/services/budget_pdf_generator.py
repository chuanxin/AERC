"""
工程預算書 PDF 生成服務

基於範例PDF格式，動態生成符合格式的工程預算書文件
"""
import os
import io
import tempfile
from typing import List, Dict, Optional, Any
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from src.utils.chinese_pdf import setup_kaiu_font, setup_chinese_font


class BudgetPDFGenerator:
    """工程預算書PDF生成器"""

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

    def _format_currency(self, amount: float) -> str:
        """格式化金額為中文大寫"""
        if amount == 0:
            return "零元整"

        # 簡化版中文數字轉換
        digits = ["零", "壹", "貳", "參", "肆", "伍", "陸", "柒", "捌", "玖"]
        units = ["", "拾", "佰", "仟", "萬"]

        amount_str = str(int(amount))
        if len(amount_str) > 5:
            return f"{amount:,.0f}元整"  # 超過萬元用數字表示

        result = ""
        for i, digit in enumerate(reversed(amount_str)):
            if digit != "0":
                result = digits[int(digit)] + units[i] + result

        return result + "元整" if result else "零元整"

    def _get_subsidy_standard(self, facility_type: str, region_type: str = "一般標準") -> str:
        """根據設施型式和地區類型獲取補助標準"""
        if "原民" in region_type:
            return "原民鄉"
        return "一般標準"

    def generate_cover_page(self, grant_data: Dict[str, Any]) -> bytes:
        """生成封面頁"""
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        if not self.font_available:
            raise Exception("中文字體不可用")

        # 標題：推廣管路灌溉設施補助計畫
        p.setFont(self.font_name, 26)
        title_text = "推廣管路灌溉設施補助計畫"
        title_width = p.stringWidth(title_text, self.font_name, 26)
        p.drawString((width - title_width) / 2, height - 80, title_text)

        # 年度
        p.setFont(self.font_name, 24)
        year_text = f"{grant_data.get('year', '114')}年度"
        year_width = p.stringWidth(year_text, self.font_name, 24)
        p.drawString((width - year_width) / 2, height - 140, year_text)

        # 機構名稱
        p.setFont(self.font_name, 26)
        org_text = "財團法人農業工程研究中心"
        org_width = p.stringWidth(org_text, self.font_name, 26)
        p.drawString((width - org_width) / 2, height - 200, org_text)

        # 案件資訊
        p.setFont(self.font_name, 20)
        y_pos = height - 280

        info_lines = [
            f"申請案號:{grant_data.get('case_number', '')}",
            f"申 請 人:{grant_data.get('applicant_name', '')}",
            f"通訊住址:{grant_data.get('address', '')}",
            f"設施地點:{grant_data.get('location', '')},地號:{grant_data.get('land_number', '')},等{grant_data.get('land_count', 1)}筆",
            "土地。",
            f"申請面積:{grant_data.get('area', '0.0000')}公頃",
            f"設施型式:{grant_data.get('facility_type', '')}"
        ]

        for line in info_lines:
            p.drawString(60, y_pos, line)
            y_pos -= 40

        p.save()
        return buffer.getvalue()

    def generate_budget_table(self, grant_data: Dict[str, Any], items: List[Dict[str, Any]]) -> bytes:
        """生成預算表頁面"""
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        if not self.font_available:
            raise Exception("中文字體不可用")

        # 標題
        p.setFont(self.font_name, 18)
        title_text = "推廣管路灌溉設施計畫預算書"
        title_width = p.stringWidth(title_text, self.font_name, 18)
        p.drawString((width - title_width) / 2, height - 40, title_text)

        # 基本資訊表格
        p.setFont(self.font_name, 10)
        y_start = height - 80

        # 農戶資訊
        info_data = [
            ["農戶姓名", grant_data.get('applicant_name', ''), "申請案號", grant_data.get('case_number', '')],
            ["住    址", grant_data.get('address', ''), "", ""],
            ["設施地段", f"{grant_data.get('location', '')}, 地號: {grant_data.get('land_number', '')} ,等", "", ""],
            ["", f"{grant_data.get('land_count', 1)}筆土地。", "", ""],
            ["設施面積", f"{grant_data.get('area', '0.0000')} 公頃", "", ""],
            ["設施型式", grant_data.get('facility_type', ''), "", ""],
            ["補助標準", self._get_subsidy_standard(grant_data.get('facility_type', ''), grant_data.get('region_type', '')), "", ""]
        ]

        # 繪製基本資訊表格
        self._draw_info_table(p, info_data, 50, y_start - 100, width - 100)

        # 預算項目表格
        y_budget_start = y_start - 250
        self._draw_budget_table(p, items, grant_data, 50, y_budget_start, width - 100)

        # 簽名欄
        self._draw_signature_section(p, 50, 100, width - 100)

        p.save()
        return buffer.getvalue()

    def _draw_info_table(self, canvas_obj, data: List[List[str]], x: float, y: float, table_width: float):
        """繪製基本資訊表格"""
        row_height = 20
        col_widths = [80, 200, 80, 150]  # 調整欄位寬度

        for i, row in enumerate(data):
            y_pos = y - (i * row_height)
            x_pos = x

            for j, cell in enumerate(row):
                if j < len(col_widths):
                    # 繪製邊框
                    canvas_obj.rect(x_pos, y_pos - row_height, col_widths[j], row_height)

                    # 填寫內容
                    if cell:
                        canvas_obj.drawString(x_pos + 5, y_pos - 15, cell)

                    x_pos += col_widths[j]

    def _draw_budget_table(self, canvas_obj, items: List[Dict], grant_data: Dict, x: float, y: float, table_width: float):
        """繪製預算項目表格"""
        headers = ["施設項目", "說明", "單位", "數量", "單價", "總價", "附註"]
        col_widths = [80, 80, 40, 40, 60, 80, 60]
        row_height = 20

        # 繪製表頭
        canvas_obj.setFont(self.font_name, 10)
        y_pos = y
        x_pos = x

        for i, header in enumerate(headers):
            canvas_obj.rect(x_pos, y_pos - row_height, col_widths[i], row_height)
            canvas_obj.drawString(x_pos + 5, y_pos - 15, header)
            x_pos += col_widths[i]

        # 繪製項目列
        total_amount = 0
        design_fee = 0

        y_pos -= row_height

        # A.田間管路設施費
        main_total = sum(float(item.get('total_price', 0)) for item in items if item.get('category') == 'materials')
        total_amount += main_total

        self._draw_budget_row(canvas_obj, x, y_pos, col_widths,
                             ["A.田間管路設施費", "(1)", "全", "", "", f"{main_total:,.0f}", ""])
        y_pos -= row_height

        # 材料費明細
        material_rows = [item for item in items if item.get('category') == 'materials']
        for item in material_rows:
            self._draw_budget_row(canvas_obj, x, y_pos, col_widths, [
                f"  {item.get('name', '')}",
                item.get('description', ''),
                item.get('unit', ''),
                item.get('quantity', ''),
                item.get('unit_price', ''),
                item.get('total_price', ''),
                item.get('note', '')
            ])
            y_pos -= row_height

        # B.規劃設計費
        design_fee = main_total * 0.02
        total_amount += design_fee
        self._draw_budget_row(canvas_obj, x, y_pos, col_widths,
                             ["B.規劃設計費", "A. x 2.0%", "式", "1", "", f"{design_fee:,.0f}", ""])
        y_pos -= row_height

        # C.調控設施
        self._draw_budget_row(canvas_obj, x, y_pos, col_widths,
                             ["C.調控設施", "依計畫補助標準", "式", "", "", "", ""])
        y_pos -= row_height

        # D.動力設備
        self._draw_budget_row(canvas_obj, x, y_pos, col_widths,
                             ["D.動力設備(0台)", "依計畫補助標準", "式", "", "", "", ""])
        y_pos -= row_height

        # E.調蓄設施
        self._draw_budget_row(canvas_obj, x, y_pos, col_widths,
                             ["E.調蓄設施(0噸)", "依計畫補助標準", "式", "", "", "", ""])
        y_pos -= row_height

        # 合計
        self._draw_budget_row(canvas_obj, x, y_pos, col_widths,
                             ["合    計", "", "", "", "", f"{total_amount:,.0f}", ""])
        y_pos -= row_height

        # 補助金額計算
        subsidy_amount = min(total_amount * 0.9, 18000)  # 90%補助，最高18000
        farmer_payment = total_amount - subsidy_amount

        self._draw_budget_row(canvas_obj, x, y_pos, col_widths,
                             ["農戶配合款", "", "", "", "", f"{farmer_payment:,.0f}", ""])
        y_pos -= row_height

        # 政府補助款
        canvas_obj.setFont(self.font_name, 8)
        canvas_obj.drawString(x, y_pos + 5, "政府")
        canvas_obj.drawString(x, y_pos - 10, "補助款")

        self._draw_budget_row(canvas_obj, x + 30, y_pos, [col_widths[0]-30] + col_widths[1:],
                             ["農戶請領款", f"A項補助費:{subsidy_amount:,.0f}", "", "", "", f"{subsidy_amount:,.0f}", ""])
        y_pos -= row_height

        self._draw_budget_row(canvas_obj, x + 30, y_pos, [col_widths[0]-30] + col_widths[1:],
                             ["規劃設計費", "B", "", "", "", f"{design_fee:,.0f}", ""])
        y_pos -= row_height

        self._draw_budget_row(canvas_obj, x + 30, y_pos, [col_widths[0]-30] + col_widths[1:],
                             ["小    計", "", "", "", "", f"{subsidy_amount + design_fee:,.0f}", ""])
        y_pos -= row_height

        # 總計
        canvas_obj.setFont(self.font_name, 12)
        canvas_obj.drawString(x, y_pos - 10, f"本設施預算總計    新台幣 {self._format_currency(total_amount)}")

    def _draw_budget_row(self, canvas_obj, x: float, y: float, col_widths: List[float], row_data: List[str]):
        """繪製預算表格的一行"""
        row_height = 20
        x_pos = x

        for i, cell in enumerate(row_data):
            if i < len(col_widths):
                # 繪製邊框
                canvas_obj.rect(x_pos, y - row_height, col_widths[i], row_height)

                # 填寫內容
                if cell:
                    canvas_obj.drawString(x_pos + 3, y - 15, str(cell))

                x_pos += col_widths[i]

    def _draw_signature_section(self, canvas_obj, x: float, y: float, table_width: float):
        """繪製簽名欄"""
        canvas_obj.setFont(self.font_name, 10)

        # 簽名表格
        sig_data = [
            ["設計", "股長", "主任工程師"],
            ["審查", "組長", "副處長"],
            ["主辦", "主計單位", "處長"]
        ]

        col_width = table_width / 3
        row_height = 30

        for i, row in enumerate(sig_data):
            y_pos = y - (i * row_height)
            for j, cell in enumerate(row):
                x_pos = x + (j * col_width)
                canvas_obj.rect(x_pos, y_pos - row_height, col_width, row_height)
                canvas_obj.drawString(x_pos + 10, y_pos - 20, cell)

    def generate_land_list(self, grant_data: Dict[str, Any], land_data: List[Dict[str, Any]]) -> bytes:
        """生成設施土地清冊"""
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        if not self.font_available:
            raise Exception("中文字體不可用")

        # 標題
        p.setFont(self.font_name, 18)
        title_text = "設施土地清冊"
        title_width = p.stringWidth(title_text, self.font_name, 18)
        p.drawString((width - title_width) / 2, height - 40, title_text)

        # 基本資訊
        p.setFont(self.font_name, 12)
        y_pos = height - 80

        p.drawString(60, y_pos, f"申請案號:{grant_data.get('case_number', '')}")
        y_pos -= 25
        p.drawString(60, y_pos, f"申 請 人:{grant_data.get('applicant_name', '')}")
        y_pos -= 25
        p.drawString(60, y_pos, f"共{len(land_data)}筆土地資料,詳列如下")
        y_pos -= 40

        # 分隔線
        p.drawString(60, y_pos, "--------------------以下空白--------------------")
        y_pos -= 40

        # 土地清冊表格
        headers = ["地段", "地號", "土地面積(m²)", "施設面積(m²)"]
        col_widths = [150, 100, 120, 120]
        row_height = 25

        # 表頭
        x_pos = 60
        for i, header in enumerate(headers):
            p.rect(x_pos, y_pos - row_height, col_widths[i], row_height)
            p.drawString(x_pos + 5, y_pos - 18, header)
            x_pos += col_widths[i]

        y_pos -= row_height

        # 土地資料
        total_land_area = 0
        total_facility_area = 0

        for land in land_data:
            x_pos = 60
            land_area = float(land.get('land_area', 0))
            facility_area = float(land.get('facility_area', 0))

            total_land_area += land_area
            total_facility_area += facility_area

            row_data = [
                land.get('location', ''),
                land.get('land_number', ''),
                f"{land_area:,.0f}",
                f"{facility_area:,.0f}"
            ]

            for i, cell in enumerate(row_data):
                p.rect(x_pos, y_pos - row_height, col_widths[i], row_height)
                p.drawString(x_pos + 5, y_pos - 18, cell)
                x_pos += col_widths[i]

            y_pos -= row_height

        # 合計
        x_pos = 60
        p.rect(x_pos, y_pos - row_height, col_widths[0], row_height)
        p.drawString(x_pos + 5, y_pos - 18, "合計")
        x_pos += col_widths[0]

        p.rect(x_pos, y_pos - row_height, col_widths[1], row_height)
        x_pos += col_widths[1]

        p.rect(x_pos, y_pos - row_height, col_widths[2], row_height)
        p.drawString(x_pos + 5, y_pos - 18, f"{total_land_area:,.0f}")
        x_pos += col_widths[2]

        p.rect(x_pos, y_pos - row_height, col_widths[3], row_height)
        p.drawString(x_pos + 5, y_pos - 18, f"{total_facility_area:,.0f}")

        p.save()
        return buffer.getvalue()

    def generate_complete_budget_book(self, grant_data: Dict[str, Any],
                                    budget_items: List[Dict[str, Any]],
                                    land_data: List[Dict[str, Any]]) -> str:
        """生成完整的工程預算書PDF檔案"""

        # 創建臨時檔案
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file.close()

        try:
            from reportlab.pdfgen import canvas
            from pypdf import PdfWriter, PdfReader

            # 生成各個頁面
            cover_pdf = self.generate_cover_page(grant_data)
            budget_pdf = self.generate_budget_table(grant_data, budget_items)
            land_pdf = self.generate_land_list(grant_data, land_data)

            # 合併PDF
            writer = PdfWriter()

            # 添加封面頁
            cover_reader = PdfReader(io.BytesIO(cover_pdf))
            for page in cover_reader.pages:
                writer.add_page(page)

            # 添加預算表頁
            budget_reader = PdfReader(io.BytesIO(budget_pdf))
            for page in budget_reader.pages:
                writer.add_page(page)

            # 添加土地清冊頁
            land_reader = PdfReader(io.BytesIO(land_pdf))
            for page in land_reader.pages:
                writer.add_page(page)

            # 寫入檔案
            with open(temp_file.name, 'wb') as output_file:
                writer.write(output_file)

            return temp_file.name

        except Exception as e:
            # 清理臨時檔案
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
            raise Exception(f"PDF生成失敗: {str(e)}")


def extract_grant_budget_data(grant, version_data: Dict[str, Any]) -> tuple:
    """從Grant資料中提取預算書所需資料"""

    # 基本資料
    grant_data = {
        'case_number': str(grant.case_number) if grant.case_number else "",
        'applicant_name': str(grant.applicant_name) if grant.applicant_name else "",
        'address': str(grant.address) if grant.address else "",
        'year': str(grant.year) if grant.year else "114",
        'facility_type': version_data.get('step3', {}).get('irrigation_type', '其它'),
        'location': "",  # 需要從step2土地資料中取得
        'land_number': "",
        'land_count': 1,
        'area': "0.0000",
        'region_type': "一般標準"
    }

    # 從step2取得土地資料
    step2_data = version_data.get('step2', {})
    land_list = step2_data.get('land_list', [])

    if land_list:
        first_land = land_list[0]
        grant_data['location'] = first_land.get('section_name', '')
        grant_data['land_number'] = first_land.get('land_number', '')
        grant_data['land_count'] = len(land_list)

        # 計算總面積（轉換為公頃）
        total_area = sum(float(land.get('facility_area', 0)) for land in land_list)
        grant_data['area'] = f"{total_area / 10000:.4f}"  # m²轉公頃

    # 預算項目（從step3和step4取得）
    budget_items = []

    # 從step4取得管路材料
    step4_data = version_data.get('step4', {})
    material_list = step4_data.get('material_list', [])

    for material in material_list:
        budget_items.append({
            'category': 'materials',
            'name': material.get('name', ''),
            'description': material.get('specification', ''),
            'unit': material.get('unit', ''),
            'quantity': material.get('quantity', ''),
            'unit_price': material.get('unit_price', ''),
            'total_price': material.get('total_price', ''),
            'note': ''
        })

    # 土地清冊資料
    land_data = []
    for land in land_list:
        land_data.append({
            'location': land.get('section_name', ''),
            'land_number': land.get('land_number', ''),
            'land_area': land.get('land_area', 0),  # m²
            'facility_area': land.get('facility_area', 0)  # m²
        })

    return grant_data, budget_items, land_data