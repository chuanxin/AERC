from typing import Optional

from pydantic import BaseModel, Field


class MfaSendRequest(BaseModel):
    mfa_token: str = Field(..., max_length=128, description="AuthToken.token（MFA_VERIFICATION 類型）")


class MfaSendResponse(BaseModel):
    message: str
    masked_email: str
    retry_after_seconds: int


class MfaVerifyRequest(BaseModel):
    mfa_token: str = Field(..., max_length=128, description="AuthToken.token（MFA_VERIFICATION 類型）")
    otp: str = Field(..., min_length=6, max_length=6, description="6位數字驗證碼")


class MfaVerifyFailedResponse(BaseModel):
    detail: str
    attempts_remaining: Optional[int] = None
