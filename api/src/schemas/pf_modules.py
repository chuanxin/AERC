from typing import Optional, List
from pydantic import BaseModel, Field

class PFModulesBase(BaseModel):
    name: str = Field(..., max_length=255, description="管件功能類型名稱")
    # description: Optional[str] = Field(None, description="模組描述") # 可選，如果您的模型有此字段

class PFModulesCreate(PFModulesBase):
    pass

class PFModulesUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255, description="管件功能類型名稱")
    # description: Optional[str] = Field(None, description="模組描述") # 可選

class PFModulesResponse(BaseModel):
    id: int = Field(..., description="管件功能類型ID")
    name: str = Field(..., max_length=255, description="管件功能類型名稱")

    class Config:
        from_attributes = True

class PFModulesListResponse(BaseModel):
    items: List[PFModulesResponse]
    total: int