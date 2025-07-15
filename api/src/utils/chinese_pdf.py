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
        
        # Alpine Linux 中的字體路徑（按優先順序排列）
        font_paths = [
            '/usr/share/fonts/truetype/kaiu/kaiu.ttf',  # 標楷體（優先使用）
            '/usr/share/fonts/wqy-zenhei/wqy-zenhei.ttc',  # 文泉驛正黑
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
            '/usr/share/fonts/TTF/wqy-zenhei.ttc',
            '/usr/share/fonts/dejavu/DejaVuSans.ttf',  # 支援部分中文
        ]
        
        font_names = [
            'KaiU',  # 標楷體
            'WenQuanYi',  # 文泉驛正黑
            'WenQuanYi',
            'WenQuanYi', 
            'DejaVu'
        ]

        for i, font_path in enumerate(font_paths):
            if os.path.exists(font_path):
                try:
                    font_name = font_names[i]
                    # 特殊處理 TTC 文件 (TrueType Collection)
                    if font_path.endswith('.ttc'):
                        # 對於 TTC 文件，我們需要指定字體索引
                        # wqy-zenhei.ttc 通常包含多個字體，使用索引 0
                        pdfmetrics.registerFont(TTFont(font_name, font_path, subfontIndex=0))
                    else:
                        pdfmetrics.registerFont(TTFont(font_name, font_path))
                    
                    print(f"Successfully registered font: {font_name} from {font_path}")
                    return True, font_name
                except Exception as e:
                    print(f"Failed to register font {font_path}: {e}")
                    continue
        
        return False, 'Helvetica'
    except ImportError:
        return False, 'Helvetica'

def setup_kaiu_font():
    """優先設置標楷體字體"""
    try:
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfbase import pdfmetrics
        
        kaiu_path = '/usr/share/fonts/truetype/kaiu/kaiu.ttf'
        if os.path.exists(kaiu_path):
            try:
                pdfmetrics.registerFont(TTFont('KaiU', kaiu_path))
                print(f"Successfully registered KaiU font from {kaiu_path}")
                return True, 'KaiU'
            except Exception as e:
                print(f"Failed to register KaiU font: {e}")
        
        # 回退到其他中文字體
        return setup_chinese_font()
    except ImportError:
        return False, 'Helvetica'

def create_chinese_pdf(title: str = "測試文件", content: list = None) -> bytes:
    """創建支援中文的 PDF"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    if content is None:
        content = [
            "標楷體中文字體測試",
            "AERC 農業工程研究中心",
            "繁體中文測試內容：",
            "農業工程、資料庫管理、系統開發",
            "標楷體特色：楷書風格、清晰易讀",
            "適合正式文件、報告書製作",
            "特殊符號：①②③④⑤ ✓✗☆★♦♣",
            "數字測試：0123456789",
            "英文測試：ABCDEFGHIJKLMNOPQRSTUVWXYZ"
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

def create_kaiu_pdf(title: str = "標楷體測試文件", content: list = None) -> bytes:
    """創建使用標楷體的 PDF"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    if content is None:
        content = [
            "標楷體字體展示",
            "AERC 農業工程研究中心",
            "繁體中文楷書測試",
            "農業技術、工程管理、系統整合",
            "標楷體特色：端正典雅、適合正式文件",
            "數字：0123456789",
            "英文：Agriculture Engineering Research Center",
            "符號：※◎★☆▲▼◆◇○●□■"
        ]
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # 優先使用標楷體
    font_available, font_name = setup_kaiu_font()
    
    if font_available and font_name == 'KaiU':
        # 使用標楷體
        p.setFont(font_name, 20)
        p.drawString(100, 750, title)
        
        # 添加副標題
        p.setFont(font_name, 16)
        p.drawString(100, 720, "標楷體字體展示文件")
        
        p.setFont(font_name, 12)
        y_position = 690
        
        for line in content:
            p.drawString(100, y_position, line)
            y_position -= 25
            
        # 添加字體狀態信息
        p.setFont(font_name, 10)
        p.drawString(100, y_position - 30, f"✅ 使用字體: {font_name} (標楷體)")
        p.drawString(100, y_position - 45, "✅ 繁體中文標楷體支援正常")
        p.drawString(100, y_position - 60, "✅ 字體檔案: /usr/share/fonts/truetype/kaiu/kaiu.ttf")
    else:
        # 回退到其他中文字體
        if font_available:
            p.setFont(font_name, 16)
            p.drawString(100, 750, title + " (回退字體)")
            
            p.setFont(font_name, 12)
            y_position = 720
            
            for line in content:
                p.drawString(100, y_position, line)
                y_position -= 20
                
            p.setFont(font_name, 10)
            p.drawString(100, y_position - 20, f"⚠️  標楷體不可用，使用 {font_name}")
        else:
            # 最終回退到英文
            p.setFont('Helvetica', 16)
            p.drawString(100, 750, "KaiU Font Test (Fallback)")
            
            p.setFont('Helvetica', 12)
            p.drawString(100, 720, "KaiU font not available")
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
