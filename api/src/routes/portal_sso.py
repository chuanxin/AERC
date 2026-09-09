"""智慧灌溉入口平台呼叫的三支對外 API（042）

    GET/POST /TokenLogin    登入落地
    POST     /Register      帳號建立
    POST     /QueryStatus   狀態查詢

⚠️ **本檔案是 AERC 錯誤處理慣例的局部例外，這是刻意的，不要「順手統一風格」。**

全站的錯誤回應是 `{"detail": ..., "error_code": ...}`（main.py 的四個全域例外處理器），
但入口平台只認得 `{code, success, err_msg, results}`。任何例外只要冒到全域處理器，
對方收到的就是它無法解析的格式——功能等同失效。

因此本檔案的 router 掛了自訂的 `route_class`，在單一位置攔截**請求解析階段與端點執行
階段的所有例外**。特別注意 `RequestValidationError` 發生在進入端點函數**之前**
（FastAPI 解析請求體時），端點內的 try/except 攔不到它——這是必須用 route_class
而非逐端點 try/except 的直接原因。

供 AERC 前端呼叫的內部端點在 `routes/sso.py`，那一支沿用全站慣例。兩者刻意分成兩個
檔案，因為它們的錯誤處理規則相反，放在一起必然會有人套錯。
"""

import logging

from fastapi import APIRouter, Depends, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from src.auth.client_ip import get_client_ip
from src.config.portal_sso import portal_sso_settings
from src.crud import sso as crud_sso
from src.schemas.sso import QueryStatusRequest, RegisterRequest, envelope

logger = logging.getLogger(__name__)


class PortalAuthError(Exception):
    """來源驗證未通過（FR-037）。由 route_class 轉為 401 信封。"""


class PortalBadRequestError(Exception):
    """請求層級錯誤（非逐筆業務失敗）。由 route_class 轉為 400 信封。"""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class PortalEnvelopeRoute(APIRoute):
    """把本 router 底下所有回應（含例外）統一為對外契約的信封格式。"""

    def get_route_handler(self):
        original_route_handler = super().get_route_handler()

        async def envelope_route_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)

            except PortalAuthError:
                # 不記錄呈交的密鑰內容（FR-040）
                logger.warning(
                    "入口平台 API 來源驗證失敗 endpoint=%s ip=%s",
                    request.url.path, get_client_ip(request),
                )
                return JSONResponse(
                    status_code=401,
                    content=envelope(401, False, err_msg="未經授權"),
                )

            except PortalBadRequestError as exc:
                return JSONResponse(
                    status_code=400,
                    content=envelope(400, False, err_msg=exc.message),
                )

            except RequestValidationError:
                # 發生在進入端點函數之前，端點內的 try/except 攔不到——這正是必須用
                # route_class 的原因。不回傳 Pydantic 的錯誤明細（CWE-209）。
                return JSONResponse(
                    status_code=400,
                    content=envelope(400, False, err_msg="請求格式錯誤"),
                )

            except Exception as exc:
                # 未預期的內部錯誤。
                #
                # 客戶契約只列出 200／400／401 三種狀態，但把內部錯誤回報為 200 等於
                # 對呼叫端宣稱「請求已被處理」——我們並不知道處理結果。誠實回報 500，
                # 並維持信封格式（FR-003），讓對方至少能分辨「業務結果」與「我方壞了」。
                logger.exception(
                    "入口平台 API 未預期例外 endpoint=%s", request.url.path
                )
                return JSONResponse(
                    status_code=500,
                    content=envelope(500, False, err_msg="系統錯誤，請稍後再試"),
                )

        return envelope_route_handler


async def verify_portal_source(request: Request) -> None:
    """來源驗證（FR-037）：共享密鑰 + 來源 IP 允許清單，**兩者皆須成立**。

    客戶契約提供的驗證方式只有一個固定的共享密鑰標頭，不含簽章、時間戳或防重放機制，
    而 /Register 具有建立帳號的寫入副作用。因此加上來源 IP 限制作為第二道條件。

    密鑰以逗號分隔支援新舊兩把並存，使雙方不必同時切換。
    """
    if not portal_sso_settings.webhook_secrets:
        # 未設定即拒絕所有請求（fail-closed）。這是本整合尚未啟用時的正確行為。
        raise PortalAuthError()

    presented = request.headers.get("X-Webhook-Secret", "")
    if presented not in portal_sso_settings.webhook_secrets:
        raise PortalAuthError()

    if not portal_sso_settings.allowed_ips:
        raise PortalAuthError()

    if get_client_ip(request) not in portal_sso_settings.allowed_ips:
        raise PortalAuthError()


router = APIRouter(route_class=PortalEnvelopeRoute)


@router.post("/Register", dependencies=[Depends(verify_portal_source)])
async def register(payload: RegisterRequest, request: Request) -> JSONResponse:
    """入口平台代為建立帳號（US1）。

    「部分成功」與「全部失敗」都回 HTTP 200——逐筆結果由 `results[]` 承載，
    頂層 `success` 表達的是**請求層級**是否成功。這使「部分成功」不需要第三種狀態。
    """
    if not payload.data:
        raise PortalBadRequestError("請求的 data 陣列為空")

    results = await crud_sso.register_accounts(
        payload.data,
        request_ip=get_client_ip(request),
        user_agent=request.headers.get("user-agent", ""),
        endpoint=str(request.url.path),
    )
    return JSONResponse(status_code=200, content=envelope(200, True, results))


@router.post("/QueryStatus", dependencies=[Depends(verify_portal_source)])
async def query_status(payload: QueryStatusRequest, request: Request) -> JSONResponse:
    """入口平台查詢帳號狀態（US2）。"""
    if not payload.data:
        raise PortalBadRequestError("請求的 data 陣列為空")

    results = await crud_sso.query_account_status(
        payload.data,
        request_ip=get_client_ip(request),
        user_agent=request.headers.get("user-agent", ""),
        endpoint=str(request.url.path),
    )
    return JSONResponse(status_code=200, content=envelope(200, True, results))
