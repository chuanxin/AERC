from typing import Optional

from pydantic import BaseModel


# schema-max-length: skip（伺服器解碼已驗證 JWT payload 後內部組裝，非使用者輸入路徑）
class TokenData(BaseModel):
    username: Optional[str] = None


# schema-max-length: skip（通用回應包裝型別，做為 response_model 使用，非使用者輸入路徑）
class Status(BaseModel):
    message: str