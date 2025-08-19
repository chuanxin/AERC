"""
PDF 處理功能測試 API 端點
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
import io
import datetime
import os

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

@router.post("/generate-kaiu-pdf")
async def generate_kaiu_pdf(data: dict = None):
    """使用 ReportLab 處理帶有自訂資料的 PDF 範本（解決中文黑點問題）"""
    try:
        from src.utils.chinese_pdf import create_template_with_reportlab
        
        # 使用 ReportLab 創建 PDF，確保中文正確顯示
        pdf_data = create_template_with_reportlab(data)
        
        # 生成檔名
        current_time = datetime.datetime.now()
        case_id = data.get("CASE_ID", "11400888") if data else "11400888"
        timestamp = current_time.strftime('%Y%m%d_%H%M%S')
        output_filename = f"{case_id}_KaiU_ReportLab_{timestamp}.pdf"
        
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={output_filename}",
                "X-Method": "reportlab-with-kaiu",
                "X-Font-Support": "chinese-kaiu-font",
                "X-Generation-Time": current_time.strftime('%Y-%m-%d %H:%M:%S'),
                "X-Encoding-Solution": "reportlab-native-chinese"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ReportLab 標楷體 PDF 處理失敗: {str(e)}")

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

@router.get("/debug-pymupdf-fonts")
async def debug_pymupdf_fonts():
    """診斷 PyMuPDF 字體支援"""
    try:
        import fitz
        import os
        
        results = {}
        
        # 檢查標楷體檔案
        kaiu_path = '/usr/share/fonts/truetype/kaiu/kaiu.ttf'
        results["kaiu_file_exists"] = os.path.exists(kaiu_path)
        if os.path.exists(kaiu_path):
            results["kaiu_file_size"] = os.path.getsize(kaiu_path)
        
        # 測試 PyMuPDF 字體載入
        doc = fitz.open()
        page = doc.new_page()
        
        # 測試 1: 使用 fontfile 參數
        try:
            page.insert_text(
                (50, 100), 
                "測試中文字體 - fontfile", 
                fontfile=kaiu_path,
                fontsize=16
            )
            results["fontfile_test"] = "success"
        except Exception as e:
            results["fontfile_test"] = f"failed: {str(e)}"
        
        # 測試 2: 使用內建字體
        try:
            page.insert_text(
                (50, 130), 
                "測試中文字體 - built-in", 
                fontname="helv",
                fontsize=16
            )
            results["builtin_test"] = "success"
        except Exception as e:
            results["builtin_test"] = f"failed: {str(e)}"
        
        # 測試 3: 檢查可用字體名稱
        try:
            font_list = fitz.get_font_list()
            results["available_fonts"] = font_list[:10]  # 只顯示前10個
            results["total_fonts"] = len(font_list)
        except Exception as e:
            results["font_list_error"] = str(e)
        
        # 測試 4: 創建測試 PDF
        try:
            test_pdf = doc.write()
            results["pdf_creation"] = "success"
            results["pdf_size"] = len(test_pdf)
        except Exception as e:
            results["pdf_creation"] = f"failed: {str(e)}"
        
        doc.close()
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PyMuPDF 診斷失敗: {str(e)}")

@router.post("/generate-kaiu-pdf-alternative")
async def generate_kaiu_pdf_alternative(data: dict = None):
    """使用替代方法處理中文 PDF（解決黑點問題）"""
    try:
        import fitz
        import datetime
        import os
        
        # 嘗試使用 CJK 字體或 Unicode 編碼
        placeholder_template_path = "src/utils/placeholder_template.pdf"
        original_template_path = "src/utils/114-11400001-工程預算書範本P1.pdf"
        
        # 確保有範本
        if not os.path.exists(placeholder_template_path):
            if not os.path.exists(original_template_path):
                raise HTTPException(status_code=404, detail="找不到 PDF 範本檔案")
        
        # 開啟範本
        template_path = placeholder_template_path if os.path.exists(placeholder_template_path) else original_template_path
        doc = fitz.open(template_path)
        page = doc[0]
        
        # 預設資料
        current_time = datetime.datetime.now()
        default_data = {
            "11400001": "11400888",
            "測試1": "王小明",
            "桃園市中壢區合江路18號": "台北市信義區忠孝東路五段123號",
            "桃園市復興區-高遶段": "台北市信義區-信義段",
            "0052-0000": "8888-9999", 
            "0.1000": "0.3500",
            "地表定置式滴嘴滴灌系統": "地表定置式噴灌系統",
            "114": "114"
        }
        
        # 合併用戶資料
        user_mapping = {}
        if data:
            # 將英文 key 對應回中文
            key_mapping = {
                "CASE_ID": "11400001",
                "APPLICANT": "測試1", 
                "ADDRESS": "桃園市中壢區合江路18號",
                "LOCATION": "桃園市復興區-高遶段",
                "LAND_ID": "0052-0000",
                "AREA_NUMBER": "0.1000", 
                "FACILITY_TYPE": "地表定置式滴嘴滴灌系統",
                "YEAR": "114"
            }
            
            for eng_key, value in data.items():
                if eng_key in key_mapping:
                    chinese_key = key_mapping[eng_key]
                    user_mapping[chinese_key] = value
        
        final_data = {**default_data, **user_mapping}
        
        replacements_made = 0
        font_methods = [
            {"type": "cjk", "encoding": "utf-8"},
            {"type": "unicode", "encoding": "utf-16"},
            {"type": "basic", "encoding": "latin-1"}
        ]
        
        # 嘗試不同的文字插入方法
        for search_text, replacement in final_data.items():
            rects = page.search_for(search_text)
            for rect in rects:
                success = False
                
                # 方法 1: 直接替換 (最簡單)
                try:
                    page.add_redact_annot(rect)
                    page.apply_redactions()
                    
                    # 嘗試不同的字體和編碼
                    for method in font_methods:
                        try:
                            if method["type"] == "cjk":
                                # 使用 CJK 字體
                                page.insert_text(
                                    (rect.x0, rect.y0 + 15),
                                    str(replacement),
                                    fontname="cjk",
                                    fontsize=16,
                                    color=(0, 0, 0)
                                )
                            elif method["type"] == "unicode":
                                # 使用 Unicode 編碼
                                text_unicode = str(replacement).encode('utf-8').decode('utf-8')
                                page.insert_text(
                                    (rect.x0, rect.y0 + 15),
                                    text_unicode,
                                    fontsize=16,
                                    color=(0, 0, 0)
                                )
                            else:
                                # 基本方法
                                page.insert_text(
                                    (rect.x0, rect.y0 + 15),
                                    str(replacement),
                                    fontsize=16,
                                    color=(0, 0, 0)
                                )
                            
                            success = True
                            replacements_made += 1
                            print(f"成功替換 '{search_text}' -> '{replacement}' (方法: {method['type']})")
                            break
                            
                        except Exception as e:
                            print(f"方法 {method['type']} 失敗: {e}")
                            continue
                
                except Exception as e:
                    print(f"替換失敗 '{search_text}': {e}")
                
                if success:
                    break
        
        # 添加替代方法標記
        try:
            info_text = f"替代方法生成 | {current_time.strftime('%Y-%m-%d %H:%M:%S')} | 替換: {replacements_made}"
            page.insert_text(
                (50, 750),
                info_text,
                fontsize=10,
                color=(1, 0, 0)  # 紅色
            )
        except:
            pass
        
        pdf_bytes = doc.write(garbage=4, deflate=True)
        doc.close()
        
        # 生成檔名
        timestamp = current_time.strftime('%Y%m%d_%H%M%S')
        output_filename = f"alternative_method_{timestamp}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={output_filename}",
                "X-Data-Filled": str(replacements_made),
                "X-Method": "alternative-cjk-unicode",
                "X-Template-Source": template_path.split('/')[-1]
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"替代方法 PDF 處理失敗: {str(e)}")

@router.post("/generate-kaiu-pdf-direct")
async def generate_kaiu_pdf_direct(data: dict = None):
    """直接在原始範本上替換，避免佔位符問題"""
    try:
        import fitz
        import datetime
        import os
        
        # 直接使用原始範本
        original_template_path = "src/utils/114-11400001-工程預算書範本P1.pdf"
        if not os.path.exists(original_template_path):
            raise HTTPException(status_code=404, detail="找不到原始 PDF 範本檔案")
        
        # 開啟原始範本
        doc = fitz.open(original_template_path)
        page = doc[0]
        
        # 預設資料對應表
        current_time = datetime.datetime.now()
        
        # 直接的文字對應關係
        replacement_map = {
            "11400001": data.get("CASE_ID", "11400888"),
            "測試1": data.get("APPLICANT", "王小明"),
            "桃園市中壢區合江路18號": data.get("ADDRESS", "台北市信義區忠孝東路五段123號"),
            "桃園市復興區-高遶段": data.get("LOCATION", "台北市信義區-信義段"),
            "0052-0000": data.get("LAND_ID", "8888-9999"),
            "0.1000": data.get("AREA_NUMBER", "0.3500"),
            "地表定置式滴嘴滴灌系統": data.get("FACILITY_TYPE", "地表定置式噴灌系統"),
            "114": data.get("YEAR", "114")
        }
        
        replacements_made = 0
        
        # 直接替換每個項目
        for original_text, new_text in replacement_map.items():
            rects = page.search_for(original_text)
            for rect in rects:
                try:
                    # 方法 1: 使用白色矩形覆蓋
                    page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                    
                    # 方法 2: 插入新文字 - 使用最簡單的方式
                    page.insert_text(
                        (rect.x0, rect.y1 - 2),
                        str(new_text),
                        fontsize=12,
                        color=(0, 0, 0)
                    )
                    
                    replacements_made += 1
                    print(f"成功替換: '{original_text}' -> '{new_text}'")
                    
                except Exception as e:
                    print(f"替換失敗 '{original_text}': {e}")
                    # 備用方法 - 使用更大的覆蓋區域
                    try:
                        # 擴大覆蓋區域
                        expanded_rect = fitz.Rect(rect.x0-5, rect.y0-2, rect.x1+50, rect.y1+2)
                        page.draw_rect(expanded_rect, color=(1, 1, 1), fill=(1, 1, 1))
                        
                        page.insert_text(
                            (rect.x0, rect.y1 - 2),
                            str(new_text),
                            fontsize=12,
                            color=(0, 0, 0)
                        )
                        replacements_made += 1
                        print(f"備用方法成功: '{original_text}' -> '{new_text}'")
                    except:
                        print(f"備用方法也失敗: '{original_text}'")
        
        # 添加處理標記
        try:
            info_text = f"直接替換法 | {current_time.strftime('%Y-%m-%d %H:%M:%S')} | 成功: {replacements_made}"
            page.insert_text(
                (50, 50),
                info_text,
                fontsize=8,
                color=(0, 0, 1)
            )
        except:
            pass
        
        pdf_bytes = doc.write(garbage=4, deflate=True)
        doc.close()
        
        # 生成檔名
        case_id = replacement_map.get("11400001", "unknown")
        timestamp = current_time.strftime('%Y%m%d_%H%M%S')
        output_filename = f"{case_id}_direct_method_{timestamp}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={output_filename}",
                "X-Data-Filled": str(replacements_made),
                "X-Method": "direct-replacement-no-placeholder",
                "X-Template-Source": "original-template"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"直接替換法失敗: {str(e)}")

@router.get("/debug-template-content")
async def debug_template_content():
    """調試 PDF 範本內容"""
    try:
        import fitz
        import os
        
        results = {}
        
        # 檢查檔案
        placeholder_template_path = "src/utils/placeholder_template.pdf"
        original_template_path = "src/utils/114-11400001-工程預算書範本P1.pdf"
        
        results["placeholder_exists"] = os.path.exists(placeholder_template_path)
        results["original_exists"] = os.path.exists(original_template_path)
        
        # 檢查原始範本內容
        if os.path.exists(original_template_path):
            doc = fitz.open(original_template_path)
            page = doc[0]
            
            # 提取所有文字
            text_dict = page.get_text("dict")
            all_text = page.get_text()
            
            results["original_template"] = {
                "total_text_length": len(all_text),
                "text_preview": all_text[:500] + "..." if len(all_text) > 500 else all_text,
                "text_blocks": len(text_dict.get("blocks", [])),
            }
            
            # 搜尋特定文字
            search_terms = ["11400001", "測試1", "桃園市", "地表定置式"]
            search_results = {}
            for term in search_terms:
                rects = page.search_for(term)
                search_results[term] = len(rects)
            
            results["search_results_original"] = search_results
            doc.close()
        
        # 檢查佔位符範本內容
        if os.path.exists(placeholder_template_path):
            doc = fitz.open(placeholder_template_path)
            page = doc[0]
            
            all_text = page.get_text()
            results["placeholder_template"] = {
                "total_text_length": len(all_text),
                "text_preview": all_text[:500] + "..." if len(all_text) > 500 else all_text,
            }
            
            # 搜尋佔位符
            placeholders = ["{{CASE_ID}}", "{{APPLICANT}}", "{{ADDRESS}}", "{{LOCATION}}"]
            placeholder_results = {}
            for placeholder in placeholders:
                rects = page.search_for(placeholder)
                placeholder_results[placeholder] = len(rects)
            
            results["search_results_placeholder"] = placeholder_results
            doc.close()
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"範本內容調試失敗: {str(e)}")

@router.post("/generate-kaiu-pdf-reportlab")
async def generate_kaiu_pdf_reportlab(data: dict = None):
    """使用 ReportLab 重新創建範本，確保中文正確顯示"""
    try:
        from src.utils.chinese_pdf import create_template_with_reportlab
        import datetime
        
        # 使用 ReportLab 創建 PDF
        pdf_data = create_template_with_reportlab(data)
        
        # 生成檔名
        current_time = datetime.datetime.now()
        case_id = data.get("CASE_ID", "11400888") if data else "11400888"
        timestamp = current_time.strftime('%Y%m%d_%H%M%S')
        output_filename = f"{case_id}_ReportLab_{timestamp}.pdf"
        
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={output_filename}",
                "X-Method": "reportlab-recreation",
                "X-Font-Support": "kaiu-chinese",
                "X-Generation-Time": current_time.strftime('%Y-%m-%d %H:%M:%S')
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ReportLab PDF generation failed: {str(e)}")

@router.get("/analyze-original-template")
async def analyze_original_template():
    """詳細分析原始範本的字體和座標資訊"""
    try:
        import fitz
        import os
        
        original_template_path = "src/utils/114-11400001-工程預算書範本P1.pdf"
        if not os.path.exists(original_template_path):
            raise HTTPException(status_code=404, detail="原始範本不存在")
        
        doc = fitz.open(original_template_path)
        page = doc[0]
        
        # 獲取頁面尺寸
        page_rect = page.rect
        
        # 獲取詳細的文字資訊
        text_dict = page.get_text("dict")
        
        analysis = {
            "page_size": {
                "width": page_rect.width,
                "height": page_rect.height
            },
            "text_elements": []
        }
        
        # 分析每個文字區塊
        for block in text_dict["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text:  # 只處理非空文字
                            bbox = span["bbox"]
                            element = {
                                "text": text,
                                "font": span["font"],
                                "size": span["size"],
                                "flags": span["flags"],
                                "color": span["color"],
                                "position": {
                                    "x": bbox[0],
                                    "y": bbox[1],
                                    "width": bbox[2] - bbox[0],
                                    "height": bbox[3] - bbox[1]
                                },
                                "is_bold": bool(span["flags"] & 2**4),
                                "is_italic": bool(span["flags"] & 2**1)
                            }
                            analysis["text_elements"].append(element)
        
        # 按 Y 座標排序（從上到下）
        analysis["text_elements"].sort(key=lambda x: -x["position"]["y"])
        
        doc.close()
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"範本分析失敗: {str(e)}")
