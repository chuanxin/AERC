from typing import Optional

from pydantic import BaseModel


class MfaSendRequest(BaseModel):
    mfa_token: str


class MfaSendResponse(BaseModel):
    message: str
    masked_email: str
    retry_after_seconds: int


class MfaVerifyRequest(BaseModel):
    mfa_token: str
    otp: str


class MfaVerifyFailedResponse(BaseModel):
    detail: str
    attempts_remaining: Optional[int] = None
