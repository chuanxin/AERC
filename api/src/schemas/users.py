from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, NewType
from datetime import datetime

from src.database.models import Users
from src.services.password_policy import validate_password_strength
from src.schemas.permissions import UserPermissionsSchema


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
    permissions: Optional[UserPermissionsSchema] = None
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
    permissions: Optional[UserPermissionsSchema]
    # last_login: Optional[datetime]
    office: Optional[SimpleOfficeSchema] = None
    department: Optional[dict] = None
    password_expired: bool = False  # 密碼是否已過期（計算欄位，由 check_password_expired 填入）

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
# 加密密碼請求 Schemas（Hybrid Encryption）
# ============================================

class EncryptedPasswordMixin(BaseModel):
    """加密密碼欄位組（AES-GCM + RSA-OAEP Hybrid Encryption）"""
    encrypted_password: str = Field(..., description="AES-GCM 加密後的密碼密文 + auth tag，base64url 編碼")
    encrypted_key: str = Field(..., description="RSA-OAEP-SHA256 加密後的 AES-256 金鑰，base64url 編碼")
    iv: str = Field(..., description="AES-GCM 初始化向量（12 bytes），base64url 編碼")
    kid: str = Field(..., description="伺服器公鑰識別碼")
    timestamp: int = Field(..., description="請求產生時間，Unix 毫秒時間戳")
    nonce: str = Field(..., min_length=32, max_length=128, description="隨機唯一字串，每次請求不重複，用於防重放")


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


class PasswordResetConfirm(EncryptedPasswordMixin):
    """確認密碼重設（密碼以 AES-GCM + RSA-OAEP hybrid encryption 傳輸）"""
    token: str = Field(..., min_length=36, max_length=36, description="重設 Token (UUID)")

    class Config:
        json_schema_extra = {
            "example": {
                "token": "550e8400-e29b-41d4-a716-446655440000",
                "encrypted_password": "<base64url ciphertext>",
                "encrypted_key": "<base64url wrapped AES key>",
                "iv": "<base64url 12-byte IV>",
                "kid": "<public key id>",
                "timestamp": 1700000000000,
                "nonce": "<32-char random string>"
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



# ============================================
# 帳號註冊相關 Schemas
# ============================================

class UserRegistrationRequest(EncryptedPasswordMixin):
    """帳號註冊請求（密碼以 AES-GCM + RSA-OAEP hybrid encryption 傳輸）"""
    username: str = Field(..., min_length=3, max_length=20, description="使用者帳號")
    email: EmailStr = Field(..., description="電子郵件地址")
    full_name: str = Field(..., min_length=1, max_length=50, description="使用者姓名")
    office_id: int = Field(..., description="所屬單位/管理處 ID")
    department: str = Field(..., min_length=1, max_length=100, description="所屬部門/工作站")

    # 聯絡資訊
    job_title: Optional[str] = Field(None, max_length=50, description="職稱")
    phone: str = Field(..., min_length=1, max_length=20, description="聯絡電話")
    phone_ext: Optional[str] = Field(None, max_length=10, description="分機")
    mobile: Optional[str] = Field(None, max_length=20, description="手機")

    # 申請原因
    application_reason: str = Field(..., min_length=1, max_length=1000, description="申請原因說明")

    # Email 驗證 Token（由 verify-registration-otp 返回）
    verified_token: str = Field(..., description="Email 驗證成功後的 Token")

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
                "job_title": "技術員",
                "phone": "02-12345678",
                "phone_ext": "123",
                "mobile": "0912345678",
                "application_reason": "因業務需要，申請系統帳號以便查詢補助案件資料。",
                "verified_token": "dXNlckBleGFtcGxlLmNvbTp2ZXJpZmllZDoxNzMxODU2MDAwOmFiY2RlZjEyMzQ1Ng==",
                "encrypted_password": "<base64url-encoded AES-GCM ciphertext>",
                "encrypted_key": "<base64url-encoded RSA-OAEP wrapped AES key>",
                "iv": "<base64url-encoded 12-byte IV>",
                "kid": "<public key id>",
                "timestamp": 1700000000000,
                "nonce": "<32-char random string>"
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


# ============================================
# 帳號轉移相關 Schemas（舊系統使用者啟用）
# ============================================

class AccountMigrationOTPVerifyRequest(BaseModel):
    """帳號轉移 OTP 驗證請求"""
    token: str = Field(..., description="帳號轉移 Token (從 Email 連結取得)")
    otp: str = Field(..., min_length=6, max_length=6, description="6位數字驗證碼")

    class Config:
        json_schema_extra = {
            "example": {
                "token": "abc123def456",
                "otp": "123456"
            }
        }


class AccountMigrationOTPVerifyResponse(BaseModel):
    """帳號轉移 OTP 驗證回應"""
    message: str
    success: bool
    user_info: Optional[dict] = Field(None, description="使用者基本資訊（驗證成功時返回）")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "驗證成功，請設定您的帳號資訊",
                "success": True,
                "user_info": {
                    "username": "user001",
                    "full_name": "王小明",
                    "email": "user@example.com",
                    "office_id": 11,
                    "office_name": "嘉南管理處",
                    "department": {
                        "branch": {"code": "1", "name": "新化分處"},
                        "station": {"code": "01", "name": "歸仁站"}
                    },
                    "job_title": "專員",
                    "phone": "02-12345678",
                    "phone_ext": "123",
                    "mobile": "0912345678"
                }
            }
        }


class AccountMigrationCompleteRequest(EncryptedPasswordMixin):
    """完成帳號轉移請求（密碼以 AES-GCM + RSA-OAEP hybrid encryption 傳輸）"""
    token: str = Field(..., description="帳號轉移 Token")
    otp: str = Field(..., min_length=6, max_length=6, description="6位數字驗證碼")

    # 使用者資訊（可選更新）
    full_name: Optional[str] = Field(None, min_length=2, max_length=50, description="姓名")
    job_title: Optional[str] = Field(None, max_length=50, description="職稱")
    office_id: Optional[int] = Field(None, description="所屬單位 ID")
    department: Optional[str] = Field(None, description="部門詳細資訊 JSON 字串")
    phone: Optional[str] = Field(None, max_length=20, description="聯絡電話")
    phone_ext: Optional[str] = Field(None, max_length=10, description="分機")
    mobile: Optional[str] = Field(None, max_length=20, description="手機")

    class Config:
        json_schema_extra = {
            "example": {
                "token": "abc123def456",
                "otp": "123456",
                "full_name": "王小明",
                "phone": "02-12345678",
                "phone_ext": "123",
                "mobile": "0912345678",
                "encrypted_password": "<base64url ciphertext>",
                "encrypted_key": "<base64url wrapped AES key>",
                "iv": "<base64url 12-byte IV>",
                "kid": "<public key id>",
                "timestamp": 1700000000000,
                "nonce": "<32-char random string>"
            }
        }


class EncryptedSecureLoginRequest(EncryptedPasswordMixin):
    """含驗證碼的安全登入請求（加密格式）"""
    username: str = Field(..., min_length=1, max_length=20, description="使用者帳號")
    captcha_token: str = Field(..., min_length=1, max_length=512, description="HMAC 簽名的驗證碼 token")
    captcha_code: str = Field(..., min_length=4, max_length=4, description="使用者輸入的驗證碼")

    @field_validator('captcha_code')
    @classmethod
    def validate_captcha_code(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError('驗證碼必須是 4 位數字')
        return v


class EncryptedChangePasswordRequest(EncryptedPasswordMixin):
    """密碼更換請求（加密格式）；不含舊密碼，JWT 已驗身"""
    pass


class AccountMigrationCompleteResponse(BaseModel):
    """完成帳號轉移回應"""
    message: str
    success: bool
    username: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "message": "帳號啟用成功，請使用新密碼登入",
                "success": True,
                "username": "user001"
            }
        }


# ============================================
# 密碼規則 API 相關 Schemas
# ============================================

class PasswordPolicyLabels(BaseModel):
    """密碼格式規則的中文說明"""
    min_length: str
    required_types: str
    has_digit: str
    has_upper: str
    has_lower: str
    has_special: str

    class Config:
        from_attributes = True


class CharTypePatterns(BaseModel):
    """各字元類型的 regex pattern（前端本地驗證使用）"""
    digit: str
    upper: str
    lower: str
    special: str

    class Config:
        from_attributes = True


class PasswordPolicyResponse(BaseModel):
    """密碼格式規則回應（GET /password-policy 端點使用）"""
    min_length: int
    required_types_count: int
    total_types_count: int
    special_chars_pattern: str
    char_type_patterns: CharTypePatterns
    labels: PasswordPolicyLabels

    class Config:
        from_attributes = True


class RejectUserRequest(BaseModel):
    """駁回帳號申請請求（POST /{user_id}/reject 使用）"""
    reason: str = Field(..., min_length=1, max_length=500, description="駁回原因")