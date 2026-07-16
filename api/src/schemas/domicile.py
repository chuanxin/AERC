from tortoise.contrib.pydantic import pydantic_model_creator
from src.database.models import Counties, Towns, Villages

from pydantic import BaseModel
from typing import Optional

# Base schema creators
CountySchema = pydantic_model_creator(
    Counties,
    name="County",
    exclude=("town",)
)

# schema-max-length: skip（唯讀參照資料，回應用，非使用者輸入路徑）
class TownSchema(BaseModel):
    id: int
    name: str
    code: str
    land_code: Optional[str] = None
    is_indigenous: bool
    indigenous_type: Optional[str] = None
    county_id: int  # We'll include just the ID

    # Optional fields from County that we want to include
    county_name: Optional[str] = None
    
    class Config:
        from_attributes = True

# schema-max-length: skip（唯讀參照資料，回應用，非使用者輸入路徑）
class VillageSchema(BaseModel):
    id: int
    name: str
    code: str
    town_id: int  # Just the ID
    
    # Optional fields from Town that we want to include
    town_name: Optional[str] = None
    county_id: Optional[int] = None
    county_name: Optional[str] = None
    
    class Config:
        from_attributes = True

# Input schemas (for creation/updates)
CountyCreateSchema = pydantic_model_creator(
    Counties, name="CountyCreate", exclude_readonly=True
)
TownCreateSchema = pydantic_model_creator(
    Towns, name="TownCreate", exclude_readonly=True
)
VillageCreateSchema = pydantic_model_creator(
    Villages, name="VillageCreate", exclude_readonly=True
)

# For nested responses (simplified for frontend use)
# schema-max-length: skip（唯讀參照資料，回應用，非使用者輸入路徑）
class TownNestedSchema(BaseModel):
    id: int
    name: str
    code: str
    
    class Config:
        from_attributes = True

# schema-max-length: skip（唯讀參照資料，回應用，非使用者輸入路徑）
class VillageNestedSchema(BaseModel):
    id: int
    name: str
    code: str
    
    class Config:
        from_attributes = True