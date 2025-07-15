"""
中文 PDF 生成工具
"""
import os
import io
from typing import Optional

def setup_chinese_font():
    """設置中文字體支援"""
    try:
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfbase import pdfmetrics
        
        # Alpine Linux 中的字體路徑 (修正後的路徑)
        font_paths = [
            '/usr/share/fonts/wqy-zenhei/wqy-zenhei.ttc',  # 正確的 Alpine Linux 路徑
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
            '/usr/share/fonts/TTF/wqy-zenhei.ttc',
            '/usr/share/fonts/dejavu/DejaVuSans.ttf',  # 支援部分中文
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    # 特殊處理 TTC 文件 (TrueType Collection)
                    if font_path.endswith('.ttc'):
                        # 對於 TTC 文件，我們需要指定字體索引
                        # wqy-zenhei.ttc 通常包含多個字體，使用索引 0
                        pdfmetrics.registerFont(TTFont('ChineseFont', font_path, subfontIndex=0))
                    else:
                        pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                    
                    print(f"Successfully registered font: {font_path}")
                    return True, 'ChineseFont'
                except Exception as e:
                    print(f"Failed to register font {font_path}: {e}")
                    continue
        
        return False, 'Helvetica'
    except ImportError:
        return False, 'Helvetica'

def create_chinese_pdf(title: str = "測試文件", content: list = None) -> bytes:
    """創建支援中文的 PDF"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    if content is None:
        content = [
            "這是中文字體測試",
            "AERC 農業工程研究中心",
            "測試各種中文字符：",
            "繁體中文：資料庫、農業工程、系統開發",
            "簡體中文：数据库、农业工程、系统开发",
            "特殊符號：①②③④⑤ ✓✗☆★♦♣"
        ]
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # 設置字體
    font_available, font_name = setup_chinese_font()
    
    if font_available:
        p.setFont(font_name, 18)
        p.drawString(100, 750, title)
        
        # 添加副標題
        p.setFont(font_name, 14)
        p.drawString(100, 720, "中文字體測試報告")
        
        p.setFont(font_name, 12)
        y_position = 690
        
        for line in content:
            p.drawString(100, y_position, line)
            y_position -= 25
            
        # 添加字體狀態信息
        p.setFont(font_name, 10)
        p.drawString(100, y_position - 30, f"✅ 使用字體: {font_name}")
        p.drawString(100, y_position - 45, "✅ 中文字體支援正常")
        p.drawString(100, y_position - 60, "✅ TTC 字體檔案載入成功")
    else:
        # 回退到英文
        p.setFont('Helvetica', 16)
        p.drawString(100, 750, "Chinese Font Test (Fallback)")
        
        p.setFont('Helvetica', 12)
        p.drawString(100, 720, "Chinese font not available")
        p.drawString(100, 700, "Using fallback font")
    
    p.save()
    return buffer.getvalue()

def list_available_fonts():
    """列出系統可用字體"""
    font_dirs = [
        '/usr/share/fonts/',
        '/usr/local/share/fonts/',
        '/System/Library/Fonts/',  # macOS
        '/Windows/Fonts/'  # Windows
    ]
    
    fonts = []
    for font_dir in font_dirs:
        if os.path.exists(font_dir):
            for root, dirs, files in os.walk(font_dir):
                for file in files:
                    if file.endswith(('.ttf', '.ttc', '.otf')):
                        fonts.append(os.path.join(root, file))
    
    return fonts
