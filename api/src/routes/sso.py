"""AERC 前端呼叫的 SSO 內部端點（042 US3）

    POST /sso/exchange   交接碼換取正式登入狀態
    POST /sso/bind       完成首次綁定

沿用全站錯誤慣例（AppError + 全域例外處理器）。入口平台呼叫的對外 API 在 routes/portal_sso.py，
錯誤回應格式與此相反，刻意分成兩個檔案。
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

import src.crud.users as crud_users
from src.auth.client_ip import get_client_ip
from src.auth.jwthandler import build_login_response, get_current_user
from src.auth.users import AUTH_SOURCE_SSO, session_password_expired
from src.crud import sso as crud_sso
from src.schemas.sso import SsoBindRequest, SsoExchangeRequest
from src.schemas.users import UserInfoSchema

router = APIRouter(prefix="/sso", tags=["SSO"])


def _request_context(request: Request) -> dict:
    return {
        "request_ip": get_client_ip(request),
        "user_agent": request.headers.get("user-agent", ""),
        "endpoint": str(request.url.path),
    }


@router.post("/exchange")
async def exchange(payload: SsoExchangeRequest, request: Request) -> JSONResponse:
    """交接碼換取登入狀態。無需認證——交接碼本身即為憑據（60 秒、一次性）。

    伺服器端的 302 導向寫不進前端的 localStorage 登入狀態，因此由落地頁主動換取（FR-045）。
    回應與 cookie 形狀完全比照既有登入成功回應；核發的憑證帶 auth_src 宣告。
    """
    user = await crud_sso.exchange_handoff_code(payload.code, **_request_context(request))
    await crud_users.update_last_login(user.id)
    return await build_login_response(
        user, session_password_expired(user, AUTH_SOURCE_SSO), auth_source=AUTH_SOURCE_SSO,
    )


@router.post("/bind")
async def bind(
    payload: SsoBindRequest,
    request: Request,
    current_user: UserInfoSchema = Depends(get_current_user),
) -> dict:
    """持綁定票據完成首次綁定。呼叫者必須剛以帳號密碼完成一次正常登入。

    認證用 get_current_user 而**非** require_full_auth：密碼逾期者會被後者 403 擋下，而綁定
    正是他日後取得 SSO 豁免的途徑，擋在這裡就形成無法脫離的循環。get_current_user 仍檢查
    帳號啟用與憑證有效，足以證明「他是這個帳號的持有人」。

    ⚠️ 綁定成功後**不重新核發**帶 auth_src 的憑證。使用者本次是以帳號密碼登入的，補發等於
    讓一次本地登入取得 SSO 專屬的密碼政策豁免，且毫無痕跡。下次自入口進入才會取得。
    """
    await crud_sso.bind_identity(payload.ticket, current_user, **_request_context(request))
    return {"success": True, "message": "已完成綁定"}
