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
        """
        驗證密碼強度

        規則：
        1. 至少 8 個字元
        2. 以下 4 項至少符合 3 項：
           - 包含數字
           - 包含英文大寫
           - 包含英文小寫
           - 包含特殊符號
        """
        import re

        if len(v) < 8:
            raise ValueError('密碼長度至少需要 8 個字元')

        # 檢查各項條件
        has_digit = any(c.isdigit() for c in v)
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', v))

        # 計算符合的項目數
        conditions_met = sum([has_digit, has_upper, has_lower, has_special])

        if conditions_met < 3:
            raise ValueError(
                '密碼需符合以下 4 項中的至少 3 項：包含數字、包含英文大寫、包含英文小寫、包含特殊符號'
            )

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


class OTPVerificationRequest(BaseModel):
    """OTP 驗證請求"""
    token: str = Field(..., min_length=36, max_length=36, description="重設 Token (UUID)")
    otp: str = Field(..., min_length=6, max_length=6, description="6位數字 OTP")

    @field_validator('otp')
    @classmethod
    def validate_otp(cls, v: str) -> str:
        """驗證 OTP 格式"""
        if not v.isdigit():
            raise ValueError('OTP 必須是 6 位數字')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "token": "550e8400-e29b-41d4-a716-446655440000",
                "otp": "123456"
            }
        }


class OTPVerificationResponse(BaseModel):
    """OTP 驗證回應"""
    message: str
    success: bool

    class Config:
        json_schema_extra = {
            "example": {
                "message": "OTP 驗證成功",
                "success": True
            }
        }


class CaptchaResponse(BaseModel):
    """驗證碼生成回應"""
    captcha_id: str = Field(..., description="驗證碼 session ID")
    captcha_code: str = Field(..., description="4位數字驗證碼")

    class Config:
        json_schema_extra = {
            "example": {
                "captcha_id": "550e8400-e29b-41d4-a716-446655440000",
                "captcha_code": "1234"
            }
        }


class LoginWithCaptchaRequest(BaseModel):
    """含驗證碼的登入請求"""
    username: str = Field(..., min_length=1, description="使用者帳號")
    password: str = Field(..., min_length=1, description="使用者密碼")
    captcha_id: str = Field(..., min_length=36, max_length=36, description="驗證碼 session ID")
    captcha_code: str = Field(..., min_length=4, max_length=4, description="使用者輸入的驗證碼")

    @field_validator('captcha_code')
    @classmethod
    def validate_captcha_code(cls, v: str) -> str:
        """驗證驗證碼格式"""
        if not v.isdigit():
            raise ValueError('驗證碼必須是 4 位數字')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "username": "user123",
                "password": "password123",
                "captcha_id": "550e8400-e29b-41d4-a716-446655440000",
                "captcha_code": "1234"
            }
        }