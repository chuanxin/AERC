from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from tortoise.contrib.pydantic import pydantic_model_creator
from src.database.models import GrantVersions

# 基本模型
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class GrantVersionCreateSchema(BaseSchema):
    """建立補助申請案件版本時使用的資料模型"""
    grant_id: int = Field(..., description="補助申請案件ID")
    all_steps_data: Dict[str, Any] = Field(..., description="所有步驟的資料(JSON格式)")
    comment: Optional[str] = Field(None, description="版本說明", max_length=255)

class GrantVersionUpdateSchema(BaseSchema):
    """更新補助申請案件版本時使用的資料模型"""
    all_steps_data: Optional[Dict[str, Any]] = Field(None, description="所有步驟的資料(JSON格式)")
    comment: Optional[str] = Field(None, description="版本說明", max_length=255)

class GrantVersionListSchema(BaseSchema):
    """補助申請案件版本列表資料模型"""
    id: int = Field(..., description="版本ID")
    grant_id: int = Field(..., description="補助申請案件ID")
    version: int = Field(..., description="版本號")
    comment: Optional[str] = Field(None, description="版本說明")
    created_at: datetime = Field(..., description="建立時間")
    created_by_name: Optional[str] = Field(None, description="建立人姓名")

class GrantVersionDetailSchema(BaseSchema):
    """補助申請案件版本詳細資料模型"""
    id: int = Field(..., description="版本ID")
    grant_id: int = Field(..., description="補助申請案件ID")
    version: int = Field(..., description="版本號")
    all_steps_data: Dict[str, Any] = Field(..., description="所有步驟的資料(JSON格式)")
    all_steps_data_hash: Optional[str] = Field(None, description="資料雜湊值")
    data_schema_version: Optional[str] = Field(None, description="資料結構版本")
    comment: Optional[str] = Field(None, description="版本說明")
    created_at: datetime = Field(..., description="建立時間")
    modified_at: datetime = Field(..., description="修改時間")
    created_by: Optional[Dict[str, Any]] = Field(None, description="建立人資訊")

class GrantVersionCompareSchema(BaseSchema):
    """補助申請案件版本比較資料模型"""
    version_a_id: int = Field(..., description="版本A的ID")
    version_b_id: int = Field(..., description="版本B的ID")
    
class GrantVersionCompareResultSchema(BaseSchema):
    """補助申請案件版本比較結果資料模型"""
    version_a: GrantVersionDetailSchema = Field(..., description="版本A")
    version_b: GrantVersionDetailSchema = Field(..., description="版本B")
    differences: Dict[str, Any] = Field(..., description="差異資訊")

class GrantVersionResponseSchema(BaseSchema):
    """建立版本後的回應資料模型"""
    id: int = Field(..., description="版本ID")
    grant_id: int = Field(..., description="補助申請案件ID")
    version: int = Field(..., description="版本號")
    comment: Optional[str] = Field(None, description="版本說明")
    created_at: datetime = Field(..., description="建立時間")
    case_number: Optional[str] = Field(None, description="案件編號")

# 使用 Tortoise ORM 自動生成的 Schema
GrantVersionOutSchema = pydantic_model_creator(
    GrantVersions, name="GrantVersionOut", exclude=("created_by.password",)
)
