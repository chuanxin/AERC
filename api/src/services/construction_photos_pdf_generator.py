"""
施工前後照片 PDF 生成服務

生成施工前後照片記錄表 PDF 範本（A4 直向，5 個照片區塊，空白佔位框）
PDF 不嵌入實際照片，僅提供列印用的空白版面，實際照片另以原始格式附於 ZIP 中
"""
from io import BytesIO
from typing import Dict, Any

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from src.utils.chinese_pdf import setup_kaiu_font, setup_chinese_font, format_case_number


class ConstructionPhotosPDFGenerator:
    """施工前後照片記錄表 PDF 生成器（空白佔位版本）"""

    def __init__(self):
        self.font_name = 'Helvetica'
        self.font_available = False
        self._setup_fonts()

    def _setup_fonts(self) -> None:
        """設置中文字體"""
        try:
            font_available, font_name = setup_kaiu_font()
            if font_available and font_name == 'KaiU':
                self.font_name = font_name
                self.font_available = True
            else:
                font_available, font_name = setup_chinese_font()
                if font_available:
                    self.font_name = font_name
                    self.font_available = True
        except Exception as e:
            print(f"字體設置失敗: {e}")

    def generate(self, grant_data: Dict[str, Any]) -> bytes:
        """
        生成施工前後照片記錄表 PDF

        Args:
            grant_data: 包含 case_number 與 applicant_name 的字典

        Returns:
            PDF 內容的 bytes
        """
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        self._generate_photos_page(c, grant_data)
        c.save()
        return buffer.getvalue()

    def _draw_centered_text(
        self,
        c: canvas.Canvas,
        text: str,
        x: float,
        y: float,
        width: float,
        font_size: float = 12
    ) -> None:
        """繪製置中對齊的文字"""
        if not text:
            return
        c.setFont(self.font_name, font_size)
        text_width = c.stringWidth(text, self.font_name, font_size)
        center_x = x + (width - text_width) / 2
        c.drawString(center_x, y, text)

    def _generate_photos_page(self, c: canvas.Canvas, data: Dict[str, Any]) -> None:
        """生成施工前後照片記錄表頁面"""
        width, height = A4
        current_y = height - 60
        left_margin = 40

        # 標題資訊
        c.setFont(self.font_name, 12)
        c.drawString(left_margin, current_y, f"申請案號：{format_case_number(data.get('case_number', ''))}")
        c.drawString(left_margin + 240, current_y, f"申請人姓名：{data.get('applicant_name', '')}")
        current_y -= 20

        # 照片區域定義
        photo_sections = [
            ("施工前", "施工前照片"),
            ("施工後", "施工後照片及系統施噴、滴灌溉情形"),
            ("動力設備", "動力設備照片"),
            ("調蓄設施", "調蓄設施照片"),
            ("調節控制設施", "調節控制設施照片")
        ]

        c.setFont(self.font_name, 12)
        c.setLineWidth(0.5)
        photo_width = width - left_margin * 2
        photo_height = 120
        label_width = 30

        for label, description in photo_sections:
            # 繪製標籤區域
            c.rect(left_margin, current_y - photo_height, label_width, photo_height)

            # 垂直文字（垂直和水平置中）
            char_spacing = 15
            label_font_size = 12

            center_y = current_y - photo_height / 2
            n = len(label)
            text_span = (n - 1) * char_spacing
            start_y = center_y + text_span / 2 - label_font_size * 0.3
            label_x = left_margin + label_width / 2 - label_font_size * 0.4

            label_y = start_y
            for char in label:
                c.drawString(label_x, label_y, char)
                label_y -= char_spacing

            # 繪製照片區域
            c.rect(left_margin, current_y - photo_height, photo_width, photo_height)

            # 照片說明（置中對齊）
            photo_area_x = left_margin + label_width
            photo_area_width = photo_width - label_width
            description_y = current_y - photo_height / 2 - 12 * 0.2
            self._draw_centered_text(c, description, photo_area_x, description_y, photo_area_width, font_size=12)

            current_y -= photo_height

        # 備註
        current_y -= 20
        c.setFont(self.font_name, 12)
        c.drawString(left_margin, current_y, "備註：本表之照片可由印表機直接列印出或以沖洗之照片粘貼方式均可，其張數自行調整")

        c.showPage()
