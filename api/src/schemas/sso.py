"""智慧灌溉入口平台 SSO 整合的請求／回應模型（042）

## 為何逐筆欄位一律寬鬆、不在 Pydantic 層做驗證

客戶契約要求「**批次中單筆失敗不得影響其他筆**」（FR-022），且 `results[]` 的筆數與
順序必須與請求一致、**任何情況下都不得省略某一筆**（FR-004）——呼叫端以索引對齊，
少一筆就整串錯位。

Pydantic 的驗證是**整包**的：`data[]` 裡任何一筆缺必填欄位、或某個字串超長，
`RequestValidationError` 會讓**整批請求**變成 422，其餘正常的筆數一起陪葬。這與上述
兩條需求直接牴觸。

因此逐筆欄位在此一律為 `Optional[str]` 且不設 `max_length`，必填與長度檢查改在
`crud/sso.py` 逐筆執行，失敗的那一筆回報 `success: false` 與原因，其餘照常處理。

⚠️ 這表示 **ORM 層的長度保護在此不適用**——`crud/sso.py` 必須在寫入前自行檢查長度，
漏檢會在 ORM 層拋 `ValidationError` 冒成 500。相關檢查集中在
`crud/sso.py::_validate_register_item()`，改動時兩處要一起看。

## 為何回應模型可以是嚴格的

回應由我方建構，不存在「使用者輸入不合法」的情形，故照常使用型別約束。
"""

from typing import Any, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# 對外契約的共通回應信封
# ---------------------------------------------------------------------------

# 回應模型，由我方建構，不是使用者輸入路徑。
# schema-max-length: skip
class PortalEnvelope(BaseModel):
    """三支對外 API 的統一回應結構（FR-001）。

    `/Register` 與 `/QueryStatus` 的**每一個** JSON 回應都必須是這個形狀，
    包含未預期的例外——那由 routes/portal_sso.py 的自訂 route_class 統一包覆。
    """

    code: int
    success: bool
    err_msg: Optional[str] = None
    results: List[Any] = Field(default_factory=list)


def envelope(
    code: int,
    success: bool,
    results: Optional[List[Any]] = None,
    err_msg: Optional[str] = None,
) -> dict:
    """建構回應信封。

    `err_msg` 僅在 `success` 為 false 時提供（契約要求），故成功時一律不輸出該鍵。
    """
    body: dict = {"code": code, "success": success, "results": results or []}
    if not success and err_msg:
        body["err_msg"] = err_msg
    return body


# ---------------------------------------------------------------------------
# Register（帳號建立）
# ---------------------------------------------------------------------------

# **這不是「本 schema 不是使用者輸入路徑」的豁免，而是刻意的取捨，理由必須讀懂再改：**
# 在此設 max_length 會讓「批次中單筆超長」變成整批 422，其餘正常筆數一起陪葬，
# 直接違反 FR-022（單筆失敗不得影響其他筆）與 FR-004（results 不得少一筆）。
# 長度檢查改在 crud/sso.py::validate_register_item() 逐筆執行，且**那裡是唯一的防線**
# ——漏檢會在 ORM create() 時拋 ValidationError 冒成 500。兩處改動要一起看。
# schema-max-length: skip
class RegisterItem(BaseModel):
    """單筆帳號建立資料。欄位一律寬鬆，驗證在 CRUD 層逐筆執行（見模組 docstring）。"""

    index: Optional[int] = None
    account: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    wtn: Optional[str] = None
    branch: Optional[str] = None
    stn: Optional[str] = None
    phone_number: Optional[str] = None
    title: Optional[str] = None
    extension: Optional[str] = None


class RegisterRequest(BaseModel):
    data: List[RegisterItem] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# QueryStatus（狀態查詢）
# ---------------------------------------------------------------------------

# 同 RegisterItem：逐筆容錯要求長度檢查在 CRUD 層執行。此外本 schema 為唯讀查詢，
# 不寫入任何 ORM CharField，不存在 Schema Drift 導致 500 的路徑。
# schema-max-length: skip
class QueryStatusItem(BaseModel):
    """單筆查詢條件。

    `name` 接受但**不參與比對**（FR-030）——姓名有同名與改名問題而不具唯一性，
    且以姓名比對會使此端點成為試探 AERC 端真實資料的管道。它只被原樣回填至回應。
    """

    index: Optional[int] = None
    name: Optional[str] = None
    email: Optional[str] = None


class QueryStatusRequest(BaseModel):
    data: List[QueryStatusItem] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# 對外契約的狀態值（客戶制定，不得改名或改值）
# ---------------------------------------------------------------------------

class ApplyStatus:
    """審核維度（apply_status）"""

    PENDING = 0       # 受理中
    ACTIVE = 1        # 已啟用
    DISABLED = 2      # 停用中
    NOT_FOUND = 3     # 無此使用者資訊


class AccountStatus:
    """啟用維度（status）。

    帳號建立的回應沿用同一組數值：0 代表「接受註冊請求」，語意等同受理中。
    """

    PENDING = 0       # 接受註冊請求 / 受理中
    ACTIVE = 1        # 已啟用
    DISABLED = 2      # 停用中
    NOT_FOUND = 3     # 無此使用者資訊


# ---------------------------------------------------------------------------
# 管理端：入口身分改綁（US4，僅系統管理員）
# ---------------------------------------------------------------------------

class SsoRebindRequest(BaseModel):
    """改綁請求。僅一個整數欄位，不涉及字串長度對齊。"""

    user_id: int = Field(..., ge=1, description="要綁定的 AERC 帳號 id")


class SsoExchangeRequest(BaseModel):
    """交接碼換取登入狀態（POST /sso/exchange）。長度對齊 AuthToken.token 的 CharField(128)。"""
    code: str = Field(..., min_length=1, max_length=128)


class SsoBindRequest(BaseModel):
    """完成首次綁定（POST /sso/bind）。長度對齊 AuthToken.token 的 CharField(128)。"""
    ticket: str = Field(..., min_length=1, max_length=128)
