from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel
from typing import Optional, NewType

from src.database.models import Users


UserInSchema = pydantic_model_creator(
    Users, name="UserIn", exclude_readonly=True
)
UserDatabaseSchema = pydantic_model_creator(
    Users, name="User", include=["id", "username", "is_active", "role", "permissions", "password", "last_login"]
)

class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class SimpleOfficeSchema(BaseSchema):
    id: int
    name: str
    short_name: str
    code: str
    classification: int
    is_funding_source: bool

class UserInfoSchema(BaseSchema):
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

UserOutSchema = UserInfoSchema

UserId = NewType("UserId", int)