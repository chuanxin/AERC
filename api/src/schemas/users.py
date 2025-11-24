from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, NewType
from datetime import datetime

from src.database.models import Users
from src.services.password_policy import validate_password_strength


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
    password_expired: bool = False  # 密碼是否已過期

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
        """使用統一的密碼強度驗證"""
        return validate_password_strength(v)

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
    captcha_token: str = Field(..., description="HMAC 簽名的驗證碼 token")
    captcha_code: str = Field(..., description="4位數字驗證碼")

    class Config:
        json_schema_extra = {
            "example": {
                "captcha_token": "MTczMTg1NjAwMDoxYTJiM2M0ZDVlNmY3ZzhoOWkwag==",
                "captcha_code": "1234"
            }
        }


class RegistrationOTPResponse(BaseModel):
    """註冊 OTP 發送回應"""
    message: str = Field(..., description="回應訊息")
    token: str = Field(..., description="HMAC 簽名的驗證 token")
    expires_in: int = Field(..., description="過期時間（秒）")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "驗證碼已發送至您的電子郵件",
                "token": "eyJhbGc...",
                "expires_in": 900
            }
        }


class RegistrationOTPVerificationResponse(BaseModel):
    """註冊 OTP 驗證回應"""
    message: str = Field(..., description="回應訊息")
    success: bool = Field(..., description="驗證是否成功")
    email: str = Field(..., description="已驗證的 Email")
    verified_token: str = Field(..., description="Email 已驗證的 token，用於最終註冊")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Email 驗證成功",
                "success": True,
                "email": "user@example.com",
                "verified_token": "eyJhbGc..."
            }
        }


class LoginWithCaptchaRequest(BaseModel):
    """含驗證碼的登入請求"""
    username: str = Field(..., min_length=1, description="使用者帳號")
    password: str = Field(..., min_length=1, description="使用者密碼")
    captcha_token: str = Field(..., min_length=1, description="HMAC 簽名的驗證碼 token")
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


# ============================================
# 帳號註冊相關 Schemas
# ============================================

class UserRegistrationRequest(BaseModel):
    """帳號註冊請求"""
    username: str = Field(..., min_length=3, max_length=20, description="使用者帳號")
    email: EmailStr = Field(..., description="電子郵件地址")
    full_name: str = Field(..., min_length=1, max_length=50, description="使用者姓名")
    office_id: int = Field(..., description="所屬單位/管理處 ID")
    department: str = Field(..., min_length=1, max_length=100, description="所屬部門/工作站")
    password: str = Field(..., min_length=8, max_length=128, description="密碼")

    # 聯絡資訊
    job_title: Optional[str] = Field(None, max_length=50, description="職稱")
    phone: str = Field(..., min_length=1, max_length=20, description="聯絡電話")
    phone_ext: Optional[str] = Field(None, max_length=10, description="分機")
    mobile: Optional[str] = Field(None, max_length=20, description="手機")

    # 申請原因
    application_reason: str = Field(..., min_length=1, max_length=1000, description="申請原因說明")

    # Email 驗證 Token（由 verify-registration-otp 返回）
    verified_token: str = Field(..., description="Email 驗證成功後的 Token")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """使用統一的密碼強度驗證"""
        return validate_password_strength(v)

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """驗證使用者帳號格式"""
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('帳號只能包含英文字母、數字和底線')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "full_name": "王小明",
                "office_id": 1,
                "department": "北區工作站",
                "password": "SecurePass123!",
                "job_title": "技術員",
                "phone": "02-12345678",
                "phone_ext": "123",
                "mobile": "0912345678",
                "application_reason": "因業務需要，申請系統帳號以便查詢補助案件資料。",
                "verified_token": "dXNlckBleGFtcGxlLmNvbTp2ZXJpZmllZDoxNzMxODU2MDAwOmFiY2RlZjEyMzQ1Ng=="
            }
        }


class UserRegistrationResponse(BaseModel):
    """帳號註冊回應"""
    message: str
    success: bool
    user_id: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "message": "帳號申請已送出，請等待管理員審核",
                "success": True,
                "user_id": 123
            }
        }