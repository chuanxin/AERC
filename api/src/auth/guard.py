from datetime import datetime, timezone

from fastapi import Depends, HTTPException

from src.auth.jwthandler import get_current_user
from src.auth.users import check_password_expired
from src.database.models import Users
from src.schemas.users import UserInfoSchema


def auth_error_response(error_code: str, message: str) -> dict:
    return {"error_code": error_code, "message": message}


async def require_full_auth(
    current_user: UserInfoSchema = Depends(get_current_user),
) -> UserInfoSchema:
    """Tier C 完整授權依賴：繼承 get_current_user 全部檢查，加入帳號鎖定與密碼過期。
    拒絕優先順序：帳號鎖定 > 密碼過期。
    FR-001(6) 的權限驗證由各路由端點個別負責，不納入此集中層。
    """
    user = await Users.get(id=current_user.id)

    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        raise HTTPException(
            status_code=401,
            detail=auth_error_response("ACCOUNT_LOCKED", "帳號已暫時鎖定，請稍後再試"),
        )

    if check_password_expired(user):
        raise HTTPException(
            status_code=403,
            detail=auth_error_response("PASSWORD_EXPIRED", "您的密碼已過期，請先完成密碼更換"),
        )

    return current_user
