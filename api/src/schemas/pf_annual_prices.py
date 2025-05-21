from pydantic import BaseModel, Field
from typing import Optional, List
import datetime

class PFAnnualPriceBase(BaseModel):
    """
    Base schema for pipe fitting annual price.
    """
    pipe_fitting_id: int = Field(..., description="所屬管件ID")
    office_id: Optional[int] = Field(None, description="所屬單位/管理處ID")
    year: int = Field(..., description="年度")
    price: float = Field(..., description="價格")
    is_active: bool = Field(True, description="是否啟用")

class PFAnnualPriceCreate(PFAnnualPriceBase):
    """
    Schema for creating a new annual price.
    Used as request body, pipe_fitting_id will be from path.
    """
    created_by_id: Optional[int] = Field(None, description="建立人帳號ID")

class PFAnnualPriceUpdate(BaseModel):
    """
    Schema for updating an existing annual price.
    All fields are optional.
    """
    pipe_fitting_id: Optional[int] = Field(None, description="所屬管件ID")
    office_id: Optional[int] = Field(None, description="所屬單位/管理處ID")
    year: Optional[int] = Field(None, description="年度")
    price: Optional[float] = Field(None, description="價格")
    is_active: Optional[bool] = Field(None, description="是否啟用")
    modified_by_id: Optional[int] = Field(None, description="修改人帳號ID")

# class PfAnnualPriceInDBBase(PfAnnualPriceBase):
#     """
#     Base schema for annual price data as stored in the database.
#     Includes ID and relationship ID.
#     """
#     id: int
#     pipe_fitting_id: int
#     created_at: datetime.datetime
#     updated_at: datetime.datetime

#     # Pydantic V2 uses model_config instead of class Config
#     # and from_attributes instead of orm_mode
#     model_config = ConfigDict(from_attributes=True)


class PFAnnualPricesResponse(PFAnnualPriceBase):
    """
    Schema for representing an annual price in API responses.
    This can be used directly or inherited if more fields are needed for response.
    """
    id: int = Field(..., description="年度價格ID")
    # created_at: datetime
    # modified_at: datetime
    
    class Config:
        from_attributes = True

class PFAnnualPricesListResponse(BaseModel):
    """
    Response schema for a list of annual prices.
    """
    items: List[PFAnnualPricesResponse]
    total: int

# class PfAnnualPriceCreatePayload(BaseModel):
#     """
#     Payload for creating/updating an annual price via API.
#     Explicitly defines what the API expects in the body.
#     """
#     year: int
#     unit_price: float

