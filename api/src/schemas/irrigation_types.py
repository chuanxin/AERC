from typing import List, Optional
from pydantic import BaseModel

class IrrigationTypeBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool = True
    parent_id: Optional[int] = None

class IrrigationTypeCreate(IrrigationTypeBase): # Though only read-only for now, define for consistency
    pass

class IrrigationTypeUpdate(BaseModel): # Define for consistency, even if not used for read-only
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    parent_id: Optional[int] = None

class IrrigationType(IrrigationTypeBase):
    id: int

    # Pydantic V2 uses from_attributes instead of orm_mode
    # Assuming Pydantic V1 for now based on common FastAPI project structures
    # If Pydantic V2, this should be: model_config = {"from_attributes": True}
    class Config:
        from_attributes = True

class IrrigationTypeOptions(IrrigationType):
    option: Optional[List['IrrigationTypeOptions']] = None

    class Config:
        from_attributes = True
# Schema for a list response, if you plan to include pagination details from Tortoise
# For now, FastAPI will automatically return a list of IrrigationType
# class IrrigationTypeList(BaseModel):
#     items: list[IrrigationType]
#     total: int
# 修正 forward reference
IrrigationTypeOptions.model_rebuild()