"""
中文 PDF 生成工具
"""
import os
import io
from typing import Optional

def format_case_number(case_number: str | None) -> str:
     """
     格式化案號顯示：移除 _ 及其後面的後綴（用於歷史案件的唯一性標識）

     例如: "113-01-0001_2legacy" -> "113-01-0001"

     Args:
         case_number: 完整案號（可能包含後綴）

     Returns:
         顯示用的案號（移除後綴）
     """
     if not case_number:
         return ''

     underscore_index = case_number.find('_')
     if underscore_index != -1:
         return case_number[:underscore_index]

     return case_number


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
        import platform
        
        # 根據作業系統選擇字體路徑
        system = platform.system()
        kaiu_paths = []
        
        if system == "Linux":
            kaiu_paths = [
                '/usr/share/fonts/truetype/kaiu/kaiu.ttf',
                '/usr/local/share/fonts/kaiu.ttf'
            ]
        elif system == "Windows":
            kaiu_paths = [
                'C:/Windows/Fonts/kaiu.ttf',
                'C:/Windows/Fonts/kaiu.TTF',
                'fonts/kaiu.ttf',
                './fonts/kaiu.ttf'
            ]
        elif system == "Darwin":  # macOS
            kaiu_paths = [
                '/System/Library/Fonts/kaiu.ttf',
                '/Library/Fonts/kaiu.ttf'
            ]
        
        # 嘗試找到並註冊標楷體字體
        for kaiu_path in kaiu_paths:
            if os.path.exists(kaiu_path):
                try:
                    pdfmetrics.registerFont(TTFont('KaiU', kaiu_path))
                    print(f"Successfully registered KaiU font from {kaiu_path}")
                    return True, 'KaiU'
                except Exception as e:
                    print(f"Failed to register KaiU font from {kaiu_path}: {e}")
                    continue
        
        print("KaiU font not found in standard locations")
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

def create_template_with_reportlab(data: dict = None) -> bytes:
    """使用 ReportLab 精確重現原始範本佈局，確保中文正確顯示"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import cm
    import datetime
    
    # 預設資料
    current_time = datetime.datetime.now()
    default_data = {
        "CASE_ID": "",
        "APPLICANT": "",
        "ADDRESS": "",
        "LOCATION": "",
        "LAND_ID": "",
        "AREA_NUMBER": "",
        "FACILITY_TYPE": "",
        "YEAR": ""
    }
    
    # 合併用戶資料
    final_data = {**default_data, **(data or {})}
    
    buffer = io.BytesIO()
    
    # 使用原始範本的頁面尺寸 (595 x 842 pt)
    page_size = (595, 842)
    p = canvas.Canvas(buffer, pagesize=page_size)
    
    # 設置標楷體字體
    font_available, font_name = setup_kaiu_font()
    
    if not font_available:
        raise Exception("Kaiu font not available")
    
    # 頁面尺寸
    width, height = page_size
    
    # 根據原始範本的座標和字體大小精確重現
    # 注意：ReportLab 的座標系統 Y 軸是從底部開始，需要轉換
    
    # 1. 標題：推廣管路灌溉設施補助計畫 (原座標 y: 54, 字體大小: 26)
    p.setFont(font_name, 26)
    p.drawString(141.5, height - 54 - 26, "推廣管路灌溉設施補助計畫")
    
    # 2. 年度：114年度 (原座標 y: 124, 字體大小: 24/26)
    p.setFont(font_name, 24)
    p.drawString(252, height - 124 - 24, final_data['YEAR'])
    p.setFont(font_name, 26)
    p.drawString(288, height - 124 - 26, "年度")
    
    # 3. 機構名稱：財團法人農業工程研究中心 (原座標 y: 192, 字體大小: 26)
    p.setFont(font_name, 26)
    p.drawString(141.5, height - 192 - 26, "財團法人農業工程研究中心")
    
    # 4. 申請案號 (原座標 y: 257, 字體大小: 20)
    p.setFont(font_name, 20)
    p.drawString(56, height - 257 - 20, f"申請案號:{final_data['CASE_ID']}")
    
    # 5. 申請人 (原座標 y: 317, 字體大小: 20)
    p.setFont(font_name, 20)
    p.drawString(56, height - 317 - 20, f"申 請 人:{final_data['APPLICANT']}")
    
    # 6. 通訊住址 (原座標 y: 377, 字體大小: 20)
    p.setFont(font_name, 20)
    p.drawString(56, height - 377 - 20, f"通訊住址:{final_data['ADDRESS']}")
    
    # 7. 設施地點 (原座標 y: 437, 字體大小: 20)
    p.setFont(font_name, 20)
    p.drawString(56, height - 437 - 20, f"設施地點:{final_data['LOCATION']},地號:{final_data['LAND_ID']},等1筆")
    
    # 8. 土地 (原座標 y: 467, 字體大小: 20)
    p.setFont(font_name, 20)
    p.drawString(146, height - 467 - 20, "土地。")
    
    # 9. 申請面積 (原座標 y: 527, 字體大小: 20)
    p.setFont(font_name, 20)
    p.drawString(56, height - 527 - 20, f"申請面積:{final_data['AREA_NUMBER']}公頃")
    
    # 10. 設施型式 (原座標 y: 587, 字體大小: 20)
    p.setFont(font_name, 20)
    p.drawString(56, height - 587 - 20, f"設施型式:{final_data['FACILITY_TYPE']}")
    
    # 頁尾資訊（較小字體，不影響原版面）
    p.setFont(font_name, 8)
    footer_text = f"ReportLab 標楷體版本 | {current_time.strftime('%Y年%m月%d日 %H:%M:%S')}"
    p.drawString(50, 30, footer_text)
    
    # 右下角標記（確認中文顯示正常）
    p.setFont(font_name, 10)
    p.setFillColor((0, 0, 1))  # 藍色
    signature_text = "✅ 中文字體正常"
    p.drawString(width - 150, 50, signature_text)
    
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
