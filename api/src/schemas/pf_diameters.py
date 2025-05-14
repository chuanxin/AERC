from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class PFDiameterBase(BaseModel):
    value: float = Field(..., description="管徑值")
    name: str = Field(..., max_length=50, description="管徑名稱 (例如 DN50, 2吋)")
    # description: Optional[str] = Field(None, description="管徑描述") # 可選

class PFDiameterCreate(PFDiameterBase):
    pass

class PFDiameterUpdate(BaseModel):
    value: Optional[float] = Field(None, description="管徑值")
    name: Optional[str] = Field(None, max_length=50, description="管徑名稱")
    # description: Optional[str] = Field(None, description="管徑描述") # 可選

class PFDiametersResponse(PFDiameterBase):
    id: int = Field(..., description="管徑ID")
    # 如果您的模型自動管理 created_at 和 modified_at，可以取消註釋
    # created_at: datetime
    # modified_at: datetime

    class Config:
        from_attributes = True # For Pydantic V2

class PFDiametersListResponse(BaseModel):
    items: List[PFDiametersResponse]
    total: int