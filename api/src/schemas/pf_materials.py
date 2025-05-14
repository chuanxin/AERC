from typing import Optional, List
from pydantic import BaseModel, Field

class PFMaterialsBase(BaseModel):
    name: str = Field(..., max_length=255, description="管件材質名稱")
    # description: Optional[str] = Field(None, description="模組描述") # 可選，如果您的模型有此字段

class PFMaterialsCreate(PFMaterialsBase):
    pass

class PFMaterialsUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255, description="管件材質名稱")
    # description: Optional[str] = Field(None, description="模組描述") # 可選

class PFMaterialsResponse(BaseModel):
    id: int = Field(..., description="管件材質ID")
    name: str = Field(..., max_length=255, description="管件材質名稱")

    class Config:
        from_attributes = True

class PFMaterialsListResponse(BaseModel):
    items: List[PFMaterialsResponse]
    total: int