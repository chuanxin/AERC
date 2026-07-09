import ipaddress
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class IPWhitelistCreateRequest(BaseModel):
    cidr: str = Field(..., max_length=50, description="IPv4 CIDR 網段，如 192.168.1.0/24")
    name: str = Field(..., max_length=100, description="說明名稱")

    @field_validator("cidr")
    @classmethod
    def validate_cidr(cls, v: str) -> str:
        # ipaddress.ip_network() 不會自動 trim 前後空白，需顯式 strip（見 research.md 決策七）
        stripped = v.strip()
        try:
            network = ipaddress.ip_network(stripped, strict=True)
        except ValueError as e:
            raise ValueError(f"無效的 CIDR 網段：{e}")
        if network.version != 4:
            raise ValueError("僅支援 IPv4 CIDR 網段")
        return stripped


class IPWhitelistUpdateRequest(BaseModel):
    """僅能二選一：切換啟用狀態，或封存（封存前必須已停用，見 route 層驗證）"""
    is_active: Optional[bool] = None
    is_archived: Optional[bool] = None

    @model_validator(mode="after")
    def validate_exactly_one_field(self):
        if (self.is_active is None) == (self.is_archived is None):
            raise ValueError("必須且只能提供 is_active 或 is_archived 其中一項")
        return self


class IPWhitelistEntryResponse(BaseModel):
    id: int
    cidr: str
    name: str
    is_active: bool
    is_archived: bool
    created_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PendingOtpResponse(BaseModel):
    otp: str
    expires_in_seconds: int
