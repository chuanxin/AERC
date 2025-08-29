from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from tortoise.contrib.pydantic import pydantic_model_creator
from src.database.models import GrantAttachments

class GrantAttachmentCreateSchema(BaseModel):
    """建立附件時使用的資料模型"""
    grant_id: int = Field(..., description="所屬補助申請案件ID")
    version_id: Optional[int] = Field(None, description="所屬案件版本ID")
    step: int = Field(..., description="申請步驟編號 (5:現場勘查, 6:補助申請, 7:結案申報, 8:測試合格)")
    category: str = Field(..., description="附件分類 (如:施工前照片、施工後照片、收據等)")
    description: Optional[str] = Field(None, description="附件說明或備註")
    related_attachment_id: Optional[int] = Field(None, description="關聯附件ID (用於前後對比)")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "grant_id": 1,
                "version_id": 1,
                "step": 7,
                "category": "施工前照片",
                "description": "管路鋪設前現況照片",
                "related_attachment_id": None
            }
        }

class GrantAttachmentUpdateSchema(BaseModel):
    """更新附件時使用的資料模型"""
    category: Optional[str] = Field(None, description="附件分類")
    description: Optional[str] = Field(None, description="附件說明或備註")
    status: Optional[str] = Field(None, description="附件狀態 (active:有效, deleted:已刪除)")
    related_attachment_id: Optional[int] = Field(None, description="關聯附件ID")
    
    class Config:
        from_attributes = True

class GrantAttachmentResponseSchema(BaseModel):
    """附件回應資料模型"""
    id: int = Field(..., description="附件ID")
    grant_id: int = Field(..., description="所屬補助申請案件ID")
    version_id: Optional[int] = Field(None, description="所屬案件版本ID")
    step: int = Field(..., description="申請步驟編號")
    category: str = Field(..., description="附件分類")
    
    # 檔案資訊
    original_filename: str = Field(..., description="使用者上傳的原始檔名")
    internal_filename: str = Field(..., description="系統內部儲存檔名")
    filepath: str = Field(..., description="檔案儲存相對路徑")
    filesize: int = Field(..., description="檔案大小 (位元組)")
    mime_type: str = Field(..., description="檔案MIME類型")
    checksum: str = Field(..., description="檔案SHA-256校驗和")
    
    # 業務資訊
    description: Optional[str] = Field(None, description="附件說明或備註")
    status: str = Field(..., description="附件狀態")
    related_attachment_id: Optional[int] = Field(None, description="關聯附件ID")
    
    # 審計資訊
    uploaded_at: datetime = Field(..., description="上傳時間")
    uploaded_by_id: int = Field(..., description="上傳人員ID")
    
    class Config:
        from_attributes = True

class GrantAttachmentListSchema(BaseModel):
    """附件列表資料模型"""
    id: int = Field(..., description="附件ID")
    original_filename: str = Field(..., description="原始檔名")
    category: str = Field(..., description="附件分類")
    filesize: int = Field(..., description="檔案大小")
    uploaded_at: datetime = Field(..., description="上傳時間")
    status: str = Field(..., description="附件狀態")
    
    class Config:
        from_attributes = True

# 使用 Tortoise 自動生成的 Schema (用於複雜查詢)
GrantAttachmentTortoiseSchema = pydantic_model_creator(
    GrantAttachments, 
    name="GrantAttachmentTortoise",
    exclude=("uploaded_by.password",)
)