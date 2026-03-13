from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import List, Optional
from pydantic import BaseModel
from src.database.models import GrantAttachments, Grants, Users
from src.services.file_storage import FileStorageService
from src.auth.jwthandler import get_current_user
import os

router = APIRouter(prefix="/attachments", tags=["Grant Attachments"])
storage = FileStorageService()

class BatchOperationRequest(BaseModel):
    operation: str
    attachment_ids: List[int]
    parameters: Optional[dict] = None

@router.post("/upload/{grant_id}/{step}")
async def upload_attachment(
    grant_id: int,
    step: int,
    file: UploadFile = File(...),
    category: Optional[str] = Form(None),
    categories: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    current_user: Users = Depends(get_current_user)
):
    """
    上傳補助申請案件附件

    支援兩種模式：
    1. 單一類別：使用 category 參數
    2. 多個類別：使用 categories 參數（JSON 陣列字串，如 '["cat1","cat2"]'）

    當指定多個類別時：
    - 實體檔案只儲存一次（透過 checksum 去重）
    - 為每個類別創建獨立的資料庫記錄
    - 所有記錄共用同一個實體檔案（相同 internal_filename 和 checksum）
    """
    try:
        import json

        grant = await Grants.get_or_none(id=grant_id)
        if not grant:
            raise HTTPException(status_code=404, detail="補助申請案件不存在")

        if step not in [3, 7, 8]:
            raise HTTPException(status_code=400, detail="非法的步驟編號")

        # 解析類別列表
        category_list = []
        if categories:
            try:
                category_list = json.loads(categories)
                if not isinstance(category_list, list) or len(category_list) == 0:
                    raise ValueError("categories 必須是非空的 JSON 陣列")
            except (json.JSONDecodeError, ValueError) as e:
                raise HTTPException(status_code=400, detail=f"categories 格式錯誤: {str(e)}")
        elif category:
            category_list = [category]
        else:
            category_list = ["general"]

        # 讀取檔案內容並計算 checksum
        file_content = await file.read()
        storage.validate_file_size(len(file_content))

        import hashlib
        checksum = hashlib.sha256(file_content).hexdigest()

        # 檢查是否已存在相同檔案（透過 checksum 去重）
        existing_attachment = await GrantAttachments.filter(
            grant_id=grant_id,
            step=step,
            checksum=checksum,
            status="active"
        ).first()

        # 決定檔案儲存策略
        if existing_attachment:
            # 重用已存在的實體檔案
            internal_filename = existing_attachment.internal_filename
            relative_path = existing_attachment.filepath
            file_reused = True
            print(f"[Upload] 重用已存在檔案: {internal_filename} (checksum: {checksum[:8]}...)")
        else:
            # 儲存新的實體檔案
            absolute_path, internal_filename, relative_path = storage.generate_file_info(grant_id, file.filename)
            await storage.save_file(file_content, absolute_path)
            file_reused = False
            print(f"[Upload] 儲存新檔案: {internal_filename} (checksum: {checksum[:8]}...)")

        # 為每個類別創建資料庫記錄
        created_attachments = []
        for cat in category_list:
            # 檢查是否已存在相同類別的記錄
            existing_category_record = await GrantAttachments.filter(
                grant_id=grant_id,
                step=step,
                category=cat,
                checksum=checksum,
                status="active"
            ).first()

            if existing_category_record:
                print(f"[Upload] 類別 '{cat}' 已存在相同檔案記錄，跳過")
                created_attachments.append({
                    "id": existing_category_record.id,
                    "category": cat,
                    "existed": True
                })
                continue

            attachment = await GrantAttachments.create(
                grant_id=grant_id,
                step=step,
                category=cat,
                original_filename=file.filename,
                internal_filename=internal_filename,
                filepath=relative_path,
                filesize=len(file_content),
                mime_type=storage.get_mime_type(file.filename),
                checksum=checksum,
                description=description,
                uploaded_by_id=current_user.id
            )
            created_attachments.append({
                "id": attachment.id,
                "category": cat,
                "existed": False
            })
            print(f"[Upload] 為類別 '{cat}' 創建記錄 (ID: {attachment.id})")

        return {
            "success": True,
            "attachments": created_attachments,
            "filename": file.filename,
            "internal_filename": internal_filename,
            "filesize": len(file_content),
            "checksum": checksum,
            "file_reused": file_reused,
            "categories_count": len(category_list)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上傳失敗: {str(e)}")

@router.get("/list/{grant_id}/{step}")
async def list_attachments(
    grant_id: int,
    step: int,
    category: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """取得指定案件和步驟的附件列表"""
    try:
        query = GrantAttachments.filter(grant_id=grant_id, step=step, status="active")
        
        if category:
            query = query.filter(category=category)
        
        total_count = await query.count()
        attachments = await query.select_related("uploaded_by").offset(offset).limit(limit).all()
        
        attachment_list = []
        for att in attachments:
            attachment_list.append({
                "id": att.id,
                "original_filename": att.original_filename,
                "filesize": att.filesize,
                "mime_type": att.mime_type,
                "category": att.category,
                "description": att.description,
                "uploaded_at": att.uploaded_at,
                "uploaded_by": att.uploaded_by.full_name or att.uploaded_by.username
            })
        
        return {
            "attachments": attachment_list,
            "total_count": total_count,
            "has_more": offset + limit < total_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢失敗: {str(e)}")

@router.get("/download/{attachment_id}")
async def download_attachment(attachment_id: int, current_user: Users = Depends(get_current_user)):
    """下載附件"""
    try:
        attachment = await GrantAttachments.get_or_none(id=attachment_id, status="active")
        if not attachment:
            raise HTTPException(status_code=404, detail="附件不存在")
        
        absolute_path = storage.settings.get_absolute_path(attachment.filepath)
        
        if not os.path.exists(absolute_path):
            raise HTTPException(status_code=404, detail="檔案不存在")
        
        return FileResponse(
            path=str(absolute_path),
            filename=attachment.original_filename,
            media_type=attachment.mime_type
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下載失敗: {str(e)}")

@router.get("/info/{attachment_id}")
async def get_attachment_info(attachment_id: int, current_user: Users = Depends(get_current_user)):
    """取得附件詳細資訊"""
    try:
        attachment = await GrantAttachments.select_related("uploaded_by", "grant").get_or_none(id=attachment_id, status="active")
        if not attachment:
            raise HTTPException(status_code=404, detail="附件不存在")
        
        return {
            "id": attachment.id,
            "grant_id": attachment.grant.id,
            "step": attachment.step,
            "original_filename": attachment.original_filename,
            "internal_filename": attachment.internal_filename,
            "filesize": attachment.filesize,
            "mime_type": attachment.mime_type,
            "category": attachment.category,
            "description": attachment.description,
            "uploaded_at": attachment.uploaded_at,
            "uploaded_by": attachment.uploaded_by.full_name or attachment.uploaded_by.username,
            "is_active": attachment.status == "active"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢失敗: {str(e)}")

@router.delete("/{attachment_id}")
async def delete_attachment(attachment_id: int, current_user: Users = Depends(get_current_user)):
    """刪除附件"""
    try:
        attachment = await GrantAttachments.get_or_none(id=attachment_id, status="active")
        if not attachment:
            raise HTTPException(status_code=404, detail="附件不存在")
        
        absolute_path = storage.settings.get_absolute_path(attachment.filepath)
        await storage.delete_file(str(absolute_path))
        
        attachment.status = "deleted"
        await attachment.save()
        
        return {
            "success": True,
            "message": "附件已成功刪除",
            "deleted_attachment_id": attachment_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刪除失敗: {str(e)}")

@router.post("/batch-operation")
async def batch_operation(
    request: BatchOperationRequest,
    current_user: Users = Depends(get_current_user)
):
    """批量操作附件"""
    try:
        if request.operation == "delete":
            deleted_count = 0
            for attachment_id in request.attachment_ids:
                attachment = await GrantAttachments.get_or_none(id=attachment_id, status="active")
                if attachment:
                    absolute_path = storage.settings.get_absolute_path(attachment.filepath)
                    await storage.delete_file(str(absolute_path))
                    attachment.status = "deleted"
                    await attachment.save()
                    deleted_count += 1
            
            return {
                "success": True,
                "message": f"成功刪除 {deleted_count} 個附件",
                "processed_count": deleted_count
            }
        else:
            raise HTTPException(status_code=400, detail="不支援的操作類型")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量操作失敗: {str(e)}")