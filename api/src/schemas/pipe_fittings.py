from typing import Optional, List, Any
from pydantic import BaseModel, Field
from datetime import datetime

# Basic response schemas for related models (ideally, these would be in their own files)
class PFMaterialResponseMin(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class PFModuleResponseMin(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class PFDiameterResponseMin(BaseModel):
    id: int
    value: float
    name: str

    class Config:
        from_attributes = True

class OfficeResponseMin(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class UserResponseMin(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

# Base schema for PipeFitting
class PipeFittingBase(BaseModel):
    name: str = Field(..., max_length=50, description="管件名稱或料號")
    material_id: int = Field(..., description="所屬管件材質ID")
    module_id: int = Field(..., description="所屬管件功能類型ID")
    diameter1_id: Optional[int] = Field(None, description="所屬管徑1 ID")
    diameter2_id: Optional[int] = Field(None, description="所屬管徑2 ID")
    diameter3_id: Optional[int] = Field(None, description="所屬管徑3 ID")
    unit: Optional[str] = Field(None, max_length=10, description="管件計量單位")
    description: Optional[str] = Field(None, max_length=255, description="管件描述")
    office_id: Optional[int] = Field(None, description="所屬單位/管理處ID")
    length: Optional[float] = Field(None, description="管件長度")
    compatibility_group: Optional[List[Any]] = Field(None, description="相容性分組 (JSON)") # Or dict, depending on structure
    typical_location: Optional[str] = Field(None, max_length=255, description="典型使用位置")
    is_active: bool = Field(True, description="是否啟用")
    is_terminal: bool = Field(False, description="是否為末端設備")
    year: Optional[int] = Field(None, description="管件年份")

# Schema for creating a PipeFitting
class PipeFittingCreate(PipeFittingBase):
    created_by_id: Optional[int] = Field(None, description="建立人帳號ID")

# Schema for updating a PipeFitting
class PipeFittingUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50, description="管件名稱或料號")
    material_id: Optional[int] = Field(None, description="所屬管件材質ID")
    module_id: Optional[int] = Field(None, description="所屬管件功能類型ID")
    diameter1_id: Optional[int] = Field(None, description="所屬管徑1 ID")
    diameter2_id: Optional[int] = Field(None, description="所屬管徑2 ID")
    diameter3_id: Optional[int] = Field(None, description="所屬管徑3 ID")
    unit: Optional[str] = Field(None, max_length=10, description="管件計量單位")
    description: Optional[str] = Field(None, max_length=255, description="管件描述")
    office_id: Optional[int] = Field(None, description="所屬單位/管理處ID")
    length: Optional[float] = Field(None, description="管件長度")
    compatibility_group: Optional[List[Any]] = Field(None, description="相容性分組 (JSON)")
    typical_location: Optional[str] = Field(None, max_length=255, description="典型使用位置")
    is_active: Optional[bool] = Field(None, description="是否啟用")
    is_terminal: Optional[bool] = Field(None, description="是否為末端設備")
    year: Optional[int] = Field(None, description="管件年份")
    modified_by_id: Optional[int] = Field(None, description="修改人帳號ID")

class PriceHistoryResponse(BaseModel):
    id: int = Field(..., description="價格記錄ID")
    year: int = Field(..., description="年度")
    price: float = Field(..., description="價格")
    is_active: bool = Field(..., description="是否啟用")
    # pipe_fitting_id: int = Field(..., description="所屬管件ID")
    # office_id: Optional[int] = Field(None, description="所屬單位/管理處ID")
    # created_at: datetime
    # modified_at: datetime

    class Config:
        from_attributes = True

# Schema for responding with PipeFitting data
class PipeFittingResponse(PipeFittingBase):
    pomno: int = Field(..., description="管件代碼")
    material: Optional[PFMaterialResponseMin] = None
    module: Optional[PFModuleResponseMin] = None
    diameter1: Optional[PFDiameterResponseMin] = None
    diameter2: Optional[PFDiameterResponseMin] = None
    diameter3: Optional[PFDiameterResponseMin] = None
    office: Optional[OfficeResponseMin] = None
    created_at: datetime
    modified_at: datetime
    created_by: Optional[UserResponseMin] = None
    modified_by: Optional[UserResponseMin] = None

    current_price: Optional[float] = Field(None, description="當前價格")
    price_history: List[PriceHistoryResponse] = Field(default_factory=list, description="價格歷史記錄")

    class Config:
        from_attributes = True

class PipeFittingListResponse(BaseModel):
    items: List[PipeFittingResponse]
    total: int