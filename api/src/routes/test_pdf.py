"""
PDF 處理功能測試 API 端點
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
import io

router = APIRouter(prefix="/test", tags=["測試"])

@router.get("/pdf-packages")
async def test_pdf_packages():
    """測試所有 PDF 處理套件是否正常工作"""
    results = {}
    
    # 測試 ReportLab
    try:
        from reportlab.pdfgen import canvas
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 750, "ReportLab Test")
        p.save()
        results["reportlab"] = {
            "status": "success",
            "pdf_size": len(buffer.getvalue())
        }
    except Exception as e:
        results["reportlab"] = {"status": "failed", "error": str(e)}
    
    # 測試 PyPDF
    try:
        import pypdf
        results["pypdf"] = {
            "status": "success", 
            "version": pypdf.__version__
        }
    except Exception as e:
        results["pypdf"] = {"status": "failed", "error": str(e)}
    
    # 測試 PyMuPDF
    try:
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((100, 100), "PyMuPDF Test")
        pdf_data = doc.write()
        doc.close()
        results["pymupdf"] = {
            "status": "success",
            "version": fitz.__version__,
            "pdf_size": len(pdf_data)
        }
    except Exception as e:
        results["pymupdf"] = {"status": "failed", "error": str(e)}
    
    # 測試 Pillow
    try:
        from PIL import Image
        import PIL
        img = Image.new('RGB', (100, 100), color='red')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        results["pillow"] = {
            "status": "success",
            "version": PIL.__version__,
            "image_size": len(buffer.getvalue())
        }
    except Exception as e:
        results["pillow"] = {"status": "failed", "error": str(e)}
    
    return {
        "message": "PDF 套件測試完成",
        "results": results,
        "all_passed": all(r.get("status") == "success" for r in results.values())
    }

@router.get("/generate-sample-pdf")
async def generate_sample_pdf():
    """生成示例 PDF 文件（使用標楷體）"""
    try:
        from src.utils.chinese_pdf import create_kaiu_pdf
        import datetime
        
        content = [
            "AERC 農業工程系統",
            "標楷體 PDF 生成測試",
            "=" * 35,
            "✅ ReportLab 正常工作",
            f"✅ 系統時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "✅ 標楷體字體測試",
            "繁體中文內容展示：",
            "農業工程研究、系統開發、資料庫管理",
            "標楷體特色：楷書風格、端正典雅"
        ]
        
        pdf_data = create_kaiu_pdf("標楷體 PDF 測試文件", content)
        
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=kaiu_test.pdf"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"標楷體 PDF 生成失敗: {str(e)}")

@router.get("/check-fonts")
async def check_available_fonts():
    """檢查系統可用字體"""
    try:
        from src.utils.chinese_pdf import list_available_fonts, setup_chinese_font
        
        fonts = list_available_fonts()
        font_available, font_name = setup_chinese_font()
        
        return {
            "chinese_font_available": font_available,
            "active_font": font_name,
            "total_fonts_found": len(fonts),
            "font_list": fonts[:10],  # 只顯示前10個字體
            "chinese_fonts": [f for f in fonts if any(keyword in f.lower() for keyword in ['chinese', 'cjk', 'han', 'wqy', 'source', 'noto'])]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"字體檢查失敗: {str(e)}")

@router.get("/generate-kaiu-pdf")
async def generate_kaiu_pdf():
    """生成標楷體 PDF 文件"""
    try:
        from src.utils.chinese_pdf import create_kaiu_pdf, setup_kaiu_font
        import datetime
        
        # 檢查標楷體是否可用
        font_available, font_name = setup_kaiu_font()
        
        content = [
            "標楷體字體展示文件",
            "AERC 農業工程研究中心",
            "=" * 40,
            f"字體狀態: {'✅ 標楷體可用' if font_name == 'KaiU' else '⚠️ 使用備用字體'}",
            f"使用字體: {font_name}",
            f"生成時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "標楷體特色展示：",
            "端正典雅的楷書字體",
            "適合正式文件與報告",
            "繁體中文完整支援",
            "",
            "農業工程相關詞彙：",
            "灌溉系統、土壤管理、作物栽培",
            "機械操作、環境監測、產量分析",
            "",
            "數字與符號測試：",
            "0123456789",
            "※◎★☆▲▼◆◇○●□■"
        ]
        
        pdf_data = create_kaiu_pdf("標楷體展示文件", content)
        
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=kaiu_showcase.pdf"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"標楷體 PDF 生成失敗: {str(e)}")

@router.get("/check-kaiu-font")
async def check_kaiu_font():
    """檢查標楷體字體狀態"""
    try:
        from src.utils.chinese_pdf import setup_kaiu_font
        import os
        
        kaiu_path = '/usr/share/fonts/truetype/kaiu/kaiu.ttf'
        font_available, font_name = setup_kaiu_font()
        
        return {
            "kaiu_file_exists": os.path.exists(kaiu_path),
            "kaiu_file_path": kaiu_path,
            "font_registered": font_available,
            "active_font_name": font_name,
            "is_kaiu_active": font_name == 'KaiU',
            "file_size": os.path.getsize(kaiu_path) if os.path.exists(kaiu_path) else 0,
            "recommendations": {
                "use_kaiu": font_name == 'KaiU',
                "message": "標楷體可用，推薦用於正式文件" if font_name == 'KaiU' else "標楷體不可用，使用備用字體"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"標楷體檢查失敗: {str(e)}")
