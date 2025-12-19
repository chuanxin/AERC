"""
推廣管路灌溉設施補助切結書 PDF 生成服務

基於範例 PDF 格式，動態生成符合格式的切結書文件
"""
import io
import os
import re
from typing import Dict, Any, List
from datetime import datetime

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm

from src.utils.chinese_pdf import setup_kaiu_font, setup_chinese_font


class DeclarationPDFGenerator:
    """補助切結書 PDF 生成器"""

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

            # 轉換為民國年
            roc_year = mod_datetime.year - 1911
            return f"民國{roc_year}年{mod_datetime.month}月{mod_datetime.day}日"
        except Exception:
            return ""

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
        hanging_indent: float = 0,
        bold: bool = False,
        underline: bool = False
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
            bold: 是否粗體顯示（通過偏移繪製模擬）
            underline: 是否添加底線

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

            # 繪製文字
            if bold:
                # 模擬粗體：通過微小偏移多次繪製
                c.drawString(current_x, y, line)
                c.drawString(current_x + 0.3, y, line)  # 水平偏移
                c.drawString(current_x, y + 0.3, line)  # 垂直偏移
            else:
                c.drawString(current_x, y, line)

            # 繪製底線
            if underline:
                line_width = c.stringWidth(line, self.font_name, font_size)
                underline_y = y - 3  # 底線位置在文字下方 2 點
                c.line(current_x, underline_y, current_x + line_width, underline_y)

            y -= line_spacing

        return y

    def generate(self, grant_data: Dict[str, Any]) -> bytes:
        """
        生成補助切結書 PDF

        Args:
            grant_data: 補助案件資料

        Returns:
            PDF 檔案的二進位內容
        """
        # 創建 PDF 緩衝區
        buffer = io.BytesIO()

        # 創建 Canvas
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # 設置初始位置
        current_y = height - 80  # 從頂部開始，留出邊距
        left_margin = 50
        right_margin = width - 50
        content_width = right_margin - left_margin

        # 繪製修訂日期（右上角，淡灰色）
        if self.revision_date:
            c.setFont(self.font_name, 8)
            c.setFillColorRGB(0.6, 0.6, 0.6)  # 淡灰色
            revision_text = f"{self.revision_date}修訂"
            revision_text_width = c.stringWidth(revision_text, self.font_name, 8)
            c.drawString(width - revision_text_width - 20, height - 30, revision_text)
            c.setFillColorRGB(0, 0, 0)  # 恢復黑色

        # 繪製「附件二」標籤（左上角）
        # c.setFont(self.font_name, 10)
        # c.rect(left_margin, current_y - 2, 40, 20, stroke=1, fill=0)
        # c.drawString(left_margin + 5, current_y + 5, "附件二")
        # current_y -= 40

        # 繪製標題：推廣管路灌溉設施補助切結書
        c.setFont(self.font_name, 22)
        title = "推廣管路灌溉設施補助切結書"
        title_width = c.stringWidth(title, self.font_name, 20)
        c.drawString((width - title_width) / 2, current_y, title)
        current_y -= 60

        # 提取資料
        applicant_name = grant_data.get('applicant_name', '')
        county = grant_data.get('county', '')
        town = grant_data.get('town', '')
        land_section = grant_data.get('land_section', '')
        # land_subsection = grant_data.get('land_subsection', '')
        land_number = grant_data.get('land_number', '')
        land_count = grant_data.get('land_count', 0)
        year = grant_data.get('year', '')
        completion_date = grant_data.get('completion_date', '')  # 格式: YYYY年MM月DD日
        office_name = grant_data.get('office_name', '○○管理處')

        # ID card and contact info
        id_number = grant_data.get('id_number', '')
        address = grant_data.get('address', '')
        phone = grant_data.get('phone', '')

        # 繪製開頭段落（合併為一個連續段落）
        c.setFont(self.font_name, 12)

        # 組合完整段落：具切結書人資訊 + 申請資訊
        para_parts = [
            f"具切結書人(同申請人)於",
            f"{county}{town}",
            f"-",
            f"{land_section}",
            # f"{land_subsection}小段" if land_subsection else "",
            f"{land_number}地號",
            f"合計{land_count}筆(詳如申請書所列土地)，",
            f"申請農業部農田水利署{year}年度推廣管路灌溉設施補助，",
            f"除遵守貴單位有關規定辦理，同意具切結書如下："
        ]
        full_paragraph = "".join([p for p in para_parts if p])
        current_y = self._draw_paragraph(c, full_paragraph, left_margin, current_y, content_width, font_size=12, indent=24)
        current_y -= 10  # 額外間距

        # 七項切結內容
        pledges = [
            ("一", "補助金額依補助基準計算，並依排定優先順序辦理，如無法列入補助對象時，絕無異議。"),
            ("二", f"本設施同意於民國_____年_____月_____日前完成結案申報。"),
            ("三", "具切結書人如有下列情形之一者，同意放棄經費補助，並放棄追訴權："),
            ("", "    1.經系統測試不合格，且未依指定改善日期辦理完成。"),
            ("", "    2.經發現曾接受農業部農村發展及水土保持署補助調蓄設施者(符合再次申請補助之條件者，不在此限)。"),
            ("四", "所灌溉土地非以休閒農場或露營區之方式經營者。"),
            ("五", "所檢附任何相關證明文件、施設前後照片以及單據憑證等資料，若有偽造、變造、隱匿或虛偽等情事，同意自負一切法律責任，並繳回全部補助款。"),
            ("六", "本設施完成後，同意將設施運轉成果資料提供貴單位，供作研究發展計畫之參考。"),
            ("七", "若為配合農時而需提前施設，同意遵照規定程序辦理，所申請補助金額俟計畫核定後再撥款，倘因計畫變更或調整經費支用項目無法補助時，一切設施費用同意自行承擔，絕無異議。"),
        ]

        for number, content in pledges:
            if number:
                # 有編號的項目（如 "一"、"五"、"七"）
                # 計算項目符號寬度，用於懸掛縮排
                bullet = f"{number}、"
                bullet_width = c.stringWidth(bullet, self.font_name, 12)
                pledge_text = f"{bullet}{content}"

                # 項目四、五、七使用粗體和底線
                use_bold = number in ["四", "五", "七"]
                use_underline = number in ["四", "五", "七"]

                # 使用懸掛縮排，使換行後的內容對齊到項目符號之後
                current_y = self._draw_paragraph(c, pledge_text, left_margin, current_y, content_width,
                                                 font_size=12, hanging_indent=bullet_width,
                                                 bold=use_bold, underline=use_underline)
            else:
                # 縮排的子項目（如 "    1.內容..." 或 "    2.內容..."）
                # 計算項目符號的寬度，用於懸掛縮排
                match = re.match(r'^(\s+\d+\.)', content)
                if match:
                    # 提取項目符號部分（如 "    1."）
                    bullet = match.group(1)
                    bullet_width = c.stringWidth(bullet, self.font_name, 12)
                    # 使用懸掛縮排繪製，後續行對齊到項目符號之後
                    current_y = self._draw_paragraph(c, content, left_margin, current_y, content_width, font_size=12, hanging_indent=bullet_width)
                else:
                    # 沒有項目符號，正常繪製
                    current_y = self._draw_paragraph(c, content, left_margin, current_y, content_width, font_size=12)
            current_y -= 5  # 項目間距

        current_y -= 30  # 額外間距

        # === 此致 ===
        c.setFont(self.font_name, 16)
        c.drawString(left_margin + 40, current_y, "此致")
        current_y -= 40

        # c.setFillColorRGB(0.5, 0.5, 0.5)
        office_text = f"農業部農田水利署{office_name}"
        office_text_width = c.stringWidth(office_text, self.font_name, 16)
        c.drawString((width - office_text_width) / 2, current_y, office_text)
        # c.setFillColorRGB(0, 0, 0)  # 恢復黑色
        current_y -= 50

        # 檢查是否需要換頁
        if current_y < 200:
            c.showPage()
            current_y = height - 60
            c.setFont(self.font_name, 12)

        # 繪製簽名區
        c.setFont(self.font_name, 14)
        c.drawString(left_margin, current_y, f"具切結書人(簽名或蓋章)：{applicant_name}")
        current_y -= 40

        c.drawString(left_margin, current_y, f"身分證字號：{id_number}")
        current_y -= 40

        c.drawString(left_margin, current_y, f"通訊地址：{address}")
        current_y -= 40

        c.drawString(left_margin, current_y, f"聯絡電話：{phone}")
        current_y -= 60

        # 繪製日期
        # today = datetime.now()
        # roc_year = today.year - 1911
        c.setFont(self.font_name, 16)
        date_text = (f"中華民國            年          月          日")
        date_text_width = c.stringWidth(date_text, self.font_name, 16)
        c.drawString((width - date_text_width) / 2, current_y, date_text)
        
        # 完成 PDF
        c.save()

        # 返回 PDF 內容
        buffer.seek(0)
        return buffer.getvalue()
