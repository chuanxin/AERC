import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Request
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
from tortoise.exceptions import DoesNotExist

from src.schemas.token import TokenData
from src.schemas.users import UserInfoSchema, SimpleOfficeSchema
from src.database.models import Users, Offices
from src.services.data_encryption import data_encryption_service


SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class OAuth2PasswordBearerCookie(OAuth2):
    def __init__(
        self,
        token_url: str,
        scheme_name: str = None,
        scopes: dict = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": token_url, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        # 優先從 Authorization Header 獲取 Token
        authorization_header = request.headers.get("Authorization")
        
        if authorization_header:
            scheme, param = get_authorization_scheme_param(authorization_header)
            if authorization_header and scheme.lower() == "bearer":
                return param
        
        # 回退到 Cookie 方式（向後相容）
        authorization_cookie = request.cookies.get("Authorization")
        if authorization_cookie:
            scheme, param = get_authorization_scheme_param(authorization_cookie)
            if authorization_cookie and scheme.lower() == "bearer":
                return param

        # 如果兩種方式都沒有找到 Token
        if self.auto_error:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            return None


security = OAuth2PasswordBearerCookie(token_url="/login")


async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    # 查詢 pwd_iat（必須在裸 except 的 try 區塊之外，避免靜默缺失導致所有 token 立即失效）
    try:
        _u = await Users.get(username=data.get("sub"))
        pwd_iat = int(_u.password_changed_at.timestamp()) if _u.password_changed_at else 0
    except DoesNotExist:
        raise HTTPException(
            status_code=500,
            detail={"error_code": "TOKEN_CREATION_FAILED", "message": "無法建立憑證，使用者不存在"},
        )
    to_encode["pwd_iat"] = pwd_iat

    # 取得使用者資料以獲取角色和部門資訊
    try:
        user = await Users.get(username=data.get("sub"))
        to_encode.update({
            "is_active": user.is_active,
            "role": user.role,
            "department": user.department,
            "permissions": user.permissions
        })
    except:
        pass
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_current_user(token: str = Depends(security)):
    credentials_exception = HTTPException(
        status_code=401,
        detail={"error_code": "TOKEN_INVALIDATED", "message": "憑證已失效，請重新登入"},
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    try:
        user = await Users.filter(username=token_data.username).only(
            'id', 'username', 'full_name', 'email', 'office_id',
            'job_title', 'is_active', 'role', 'permissions', 'last_login',
            'department', 'password_changed_at'
        ).first()

        if user is None:
            raise credentials_exception

        if not user.is_active:
            raise HTTPException(
                status_code=401,
                detail={"error_code": "ACCOUNT_DISABLED", "message": "您的帳號已停用，請聯繫系統管理員"},
            )

        # pwd_iat 比對（缺少 claim 視為 token 無效）
        jwt_pwd_iat = payload.get("pwd_iat")
        if jwt_pwd_iat is None:
            raise HTTPException(
                status_code=401,
                detail={"error_code": "TOKEN_INVALIDATED", "message": "憑證已失效，請重新登入"},
            )
        if user.password_changed_at is not None:
            db_pwd_iat = int(user.password_changed_at.timestamp())
            if db_pwd_iat != jwt_pwd_iat:
                raise HTTPException(
                    status_code=401,
                    detail={"error_code": "TOKEN_INVALIDATED", "message": "憑證已失效，請重新登入"},
                )

        office_data = None
        if user.office_id:
            office = await Offices.filter(id=user.office_id).only(
                'id', 'name', 'short_name', 'code', 'classification', 'is_funding_source'
            ).first()

            if office:
                office_data = SimpleOfficeSchema(
                    id=office.id,
                    name=office.name,
                    short_name=office.short_name,
                    code=office.code,
                    classification=office.classification,
                    is_funding_source=office.is_funding_source
                )

        return UserInfoSchema(
            id=user.id,
            username=user.username,
            full_name=data_encryption_service.decrypt(user.full_name),
            email=user.email,
            job_title=user.job_title,
            is_active=user.is_active,
            role=user.role,
            permissions=user.permissions,
            last_login=user.last_login,
            office=office_data,
            department=user.department
        )

    except DoesNotExist:
        raise credentials_exception
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_current_user: {e}")
        raise credentials_exception
    
    # return user