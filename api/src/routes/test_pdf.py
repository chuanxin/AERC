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
    """生成示例 PDF 文件"""
    try:
        from src.utils.chinese_pdf import create_chinese_pdf
        import datetime
        
        content = [
            "AERC 農業工程系統",
            "PDF 生成測試",
            "=" * 30,
            "✅ ReportLab 正常工作",
            f"✅ 系統時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "✅ 中文字體測試"
        ]
        
        pdf_data = create_chinese_pdf("PDF 測試文件", content)
        
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=chinese_test.pdf"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 生成失敗: {str(e)}")

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
