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
    description: Optional[str] = Form(None),
    current_user: Users = Depends(get_current_user)
):
    """上傳補助申請案件附件"""
    try:
        grant = await Grants.get_or_none(id=grant_id)
        if not grant:
            raise HTTPException(status_code=404, detail="補助申請案件不存在")
        
        if step not in [5, 6, 7, 8]:
            raise HTTPException(status_code=400, detail="步驟編號必須在5-8之間")
        
        file_content = await file.read()
        storage.validate_file_size(len(file_content))
        
        absolute_path, internal_filename, relative_path = storage.generate_file_info(grant_id, file.filename)
        checksum = await storage.save_file(file_content, absolute_path)
        
        attachment = await GrantAttachments.create(
            grant_id=grant_id,
            step=step,
            category=category or "general",
            original_filename=file.filename,
            internal_filename=internal_filename,
            filepath=relative_path,
            filesize=len(file_content),
            mime_type=storage.get_mime_type(file.filename),
            checksum=checksum,
            description=description,
            uploaded_by_id=current_user.id
        )
        
        return {
            "success": True,
            "attachment_id": attachment.id,
            "filename": file.filename,
            "internal_filename": internal_filename,
            "filesize": len(file_content),
            "upload_time": attachment.uploaded_at
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