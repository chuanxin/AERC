from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel
from typing import Optional

from src.database.models import Users


UserInSchema = pydantic_model_creator(
    Users, name="UserIn", exclude_readonly=True
)
UserOutSchema = pydantic_model_creator(
    Users, name="UserOut", exclude=["password", "created_at", "modified_at"]
)
UserDatabaseSchema = pydantic_model_creator(
    Users, name="User", exclude=["created_at", "modified_at"]
)

class SimpleOfficeSchema(BaseModel):
    id: int
    name: str
    short_name: str
    code: str
    classification: int
    is_funding_source: bool
    
    class Config:
        from_attributes = True

class UserInfoSchema(BaseModel):
    id: int
    username: str
    full_name: Optional[str]
    email: Optional[str]
    job_title: Optional[str]
    is_active: bool
    role: Optional[str]
    permissions: Optional[list]
    # last_login: Optional[datetime]
    office: Optional[SimpleOfficeSchema] = None
    
    class Config:
        from_attributes = True