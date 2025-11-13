from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, NewType
from datetime import datetime

from src.database.models import Users


UserInSchema = pydantic_model_creator(
    Users, name="UserIn", exclude_readonly=True
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

class UserDatabaseSchema(BaseSchema):
    id: int
    username: str
    password: str
    is_active: bool
    role: Optional[str] = None
    permissions: Optional[list] = None
    last_login: Optional[datetime] = None

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


# ============================================
# Email 驗證相關 Schemas
# ============================================

class EmailVerificationRequest(BaseModel):
    """請求發送 Email 驗證信"""
    email: EmailStr = Field(..., description="電子郵件地址")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }


class EmailVerificationConfirm(BaseModel):
    """確認 Email 驗證"""
    token: str = Field(..., min_length=36, max_length=36, description="驗證 Token (UUID)")

    class Config:
        json_schema_extra = {
            "example": {
                "token": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class EmailVerificationResponse(BaseModel):
    """Email 驗證回應"""
    message: str
    success: bool
    email: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "message": "驗證信已發送至您的電子郵件",
                "success": True,
                "email": "user@example.com"
            }
        }


# ============================================
# 密碼重設相關 Schemas
# ============================================

class PasswordResetRequest(BaseModel):
    """請求密碼重設"""
    email: EmailStr = Field(..., description="電子郵件地址")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }


class PasswordResetConfirm(BaseModel):
    """確認密碼重設"""
    token: str = Field(..., min_length=36, max_length=36, description="重設 Token (UUID)")
    new_password: str = Field(..., min_length=8, max_length=128, description="新密碼")

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """驗證密碼強度"""
        if len(v) < 8:
            raise ValueError('密碼長度至少需要 8 個字元')
        if not any(c.isupper() for c in v):
            raise ValueError('密碼需包含至少一個大寫字母')
        if not any(c.islower() for c in v):
            raise ValueError('密碼需包含至少一個小寫字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密碼需包含至少一個數字')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "token": "550e8400-e29b-41d4-a716-446655440000",
                "new_password": "NewPassword123"
            }
        }


class PasswordResetResponse(BaseModel):
    """密碼重設回應"""
    message: str
    success: bool

    class Config:
        json_schema_extra = {
            "example": {
                "message": "密碼重設成功",
                "success": True
            }
        }