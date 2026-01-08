"""
推廣管路灌溉設施規劃委託書 PDF 生成服務

基於範例 PDF 格式，動態生成符合格式的規劃委託書文件
"""
import io
import os
from typing import Dict, Any
from datetime import datetime

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm

from src.utils.chinese_pdf import setup_kaiu_font, setup_chinese_font, format_case_number


class AuthorizationPDFGenerator:
    """規劃委託書 PDF 生成器"""

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

    def _wrap_text_to_lines(self, text: str, font_name: str, font_size: float, max_width: float, c: canvas.Canvas) -> list:
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
        indent: float = 0
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

        Returns:
            繪製後的 Y 座標（下一行的起始位置）
        """
        if not text:
            return y

        c.setFont(self.font_name, font_size)

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
            # 首行縮排：第一行縮排，後續行不縮排
            current_x = x + (indent if i == 0 else 0)
            c.drawString(current_x, y, line)
            y -= line_spacing

        return y

    def generate(self, grant_data: Dict[str, Any]) -> bytes:
        """
        生成規劃委託書 PDF

        Args:
            grant_data: 補助案件資料

        Returns:
            PDF 檔案的二進位內容
        """
        if not self.font_available:
            raise Exception("中文字體不可用")

        # 創建 PDF 緩衝區
        buffer = io.BytesIO()

        # 創建 Canvas
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # 設置初始位置
        current_y = height - 80  # 從頂部開始，留出邊距
        left_margin = 60
        right_margin = width - 60
        content_width = right_margin - left_margin

        # 繪製修訂日期（右上角，淡灰色）
        if self.revision_date:
            c.setFont(self.font_name, 8)
            c.setFillColorRGB(0.6, 0.6, 0.6)  # 淡灰色
            revision_text = f"{self.revision_date}修訂"
            revision_text_width = c.stringWidth(revision_text, self.font_name, 8)
            c.drawString(width - revision_text_width - 20, height - 30, revision_text)
            c.setFillColorRGB(0, 0, 0)  # 恢復黑色

        # === 標題 ===
        c.setFont(self.font_name, 22)
        title = "推廣管路灌溉設施規劃委託書"
        title_width = c.stringWidth(title, self.font_name, 22)
        c.drawString((width - title_width) / 2, current_y, title)
        current_y -= 60

        # === 開頭段落 ===
        year = grant_data.get('year', '114')

        # 合併為完整段落，依照欄寬自動換行，首行縮排兩個字
        opening_paragraph = f"本人申請農業部農田水利署{year}年度推廣管路灌溉設施補助，擬委託____________________君（管理處）有關人員代辦系統規劃佈置，恐口說無憑，特立此委託書。"
        current_y = self._draw_paragraph(c, opening_paragraph, left_margin, current_y, content_width, font_size=16, line_spacing=28, indent=32)
        current_y -= 60  # 額外間距

        # === 委託人資訊 ===
        c.setFont(self.font_name, 14)

        # 申請案號
        case_number = grant_data.get('case_number', '')
        c.drawString(left_margin, current_y, f"申請案號：{format_case_number(case_number)}")
        current_y -= 40

        # 委託人
        applicant_name = grant_data.get('applicant_name', '')
        c.drawString(left_margin, current_y, f"委託人(簽名或蓋章)：{applicant_name}")
        current_y -= 40

        # 身分證字號
        id_number = grant_data.get('id_number', '')
        c.drawString(left_margin, current_y, f"身分證字號：{id_number}")
        current_y -= 40

        # 通訊地址
        address = grant_data.get('address', '')
        c.drawString(left_margin, current_y, f"通訊地址：{address}")
        current_y -= 40

        # 聯絡電話
        phone = grant_data.get('phone', '')
        c.drawString(left_margin, current_y, f"聯絡電話：{phone}")
        current_y -= 60

        # === 受託人資訊（空白，由手填） ===
        c.drawString(left_margin, current_y, "受託人(簽名或蓋章)：")
        current_y -= 40

        c.drawString(left_margin, current_y, "身分證字號：")
        current_y -= 40

        c.drawString(left_margin, current_y, "通訊地址：")
        current_y -= 40

        c.drawString(left_margin, current_y, "聯絡電話：")
        current_y -= 40

        c.drawString(left_margin, current_y, "*研習字號或證照編號：")
        current_y -= 80

        # === 日期 ===
        c.setFont(self.font_name, 16)
        date_text = (f"中華民國            年          月          日")
        date_text_width = c.stringWidth(date_text, self.font_name, 16)
        c.drawString((width - date_text_width) / 2, current_y, date_text)

        # 完成 PDF
        c.save()

        # 返回 PDF 內容
        buffer.seek(0)
        return buffer.getvalue()
