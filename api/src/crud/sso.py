"""智慧灌溉入口平台 SSO 整合的資料存取層（042）

三層架構的 CRUD 層。採三層而非兩層的一句話理由：**批次帳號建立須在單一交易內跨四個
實體（帳號、申請記錄、身分對應、管理處查表）完成，且逐筆容錯互不影響**。

## 這一層承擔的兩件事，遺漏任一都會壞

1. **逐筆驗證**：`schemas/sso.py` 的輸入欄位刻意寬鬆（單筆不合法不得讓整批 422），
   所以必填、長度、格式的檢查全在這裡。**特別是長度**——ORM 的 `CharField` 會在
   `create()` 時驗證 `max_length`，漏檢會拋 `ValidationError` 冒成 500。
2. **逐筆容錯**：任何一筆的失敗都不得影響其他筆（FR-022），且結果筆數與順序必須與
   請求一致（FR-004）。
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from src.database.audit_models import AuditAction, AuditEventType, AuditResult
from src.database.geo_models import OfficeBoundaries
from src.database.models import (
    AuthToken,
    AuthTokenStatus,
    AuthTokenType,
    Offices,
    RegistrationStatus,
    SsoBindMethod,
    SsoIdentity,
    UserRegistration,
    Users,
)
from src.exceptions import AppError
from src.schemas.sso import AccountStatus, ApplyStatus
from src.services.audit_service import audit_service
from src.services.data_encryption import data_encryption_service
from src.services.email_service import EmailService
from src.services.portal_token import PortalClaims

logger = logging.getLogger(__name__)

# 入口代建帳號的固定申請原因，使管理員在待審核清單上一眼可辨識來源（FR-028）。
# 此欄位在 user_management.py:211 會被解密後顯示。
PORTAL_APPLICATION_REASON = "由智慧灌溉入口平台代為申請（SSO）"

# 新帳號一律以最小權限建立，實際角色由管理員於審核時指派（FR-027）
PORTAL_DEFAULT_ROLE = "user"

# ORM CharField 的長度上限。schemas 層刻意不設 max_length（否則單筆超長會讓整批 422），
# 因此這裡是唯一的防線——漏檢會在 create() 時拋 ValidationError 冒成 500。
_MAX_LENGTHS: Dict[str, int] = {
    "account": 20,        # Users.username
    "email": 255,         # Users.email
    "title": 50,          # Users.job_title
    "name": 100,          # Users.full_name 為 TextField，此為防禦性上限
    "wtn": 50,            # Offices.name
    "branch": 50,
    "stn": 50,
    "phone_number": 20,
    "extension": 20,
}

_REQUIRED_FIELDS: Tuple[str, ...] = ("account", "name", "email", "wtn", "phone_number")


# ---------------------------------------------------------------------------
# 共用小工具
# ---------------------------------------------------------------------------

def normalize_email(value: Optional[str]) -> str:
    """電子郵件正規化：去前後空白、轉小寫（FR-031）。

    ⚠️ 僅供本功能的比對路徑使用。既有端點的比對行為不得因此改變（憲法 I）。
    """
    return (value or "").strip().lower()


def _clean(value: Optional[str]) -> str:
    return (value or "").strip()


async def log_portal_event(
    *,
    event_type: AuditEventType,
    action: AuditAction,
    result: AuditResult,
    request_ip: str,
    user_agent: str,
    endpoint: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    external_id: Optional[str] = None,
    failure_reason: Optional[str] = None,
    extra_fields: Optional[dict] = None,
    actor: Optional[Any] = None,
    target_username: Optional[str] = None,
) -> None:
    """入口平台相關事件的稽核寫入（FR-039、FR-040）。

    `audit_service.log()` 的所有參數都有預設值，漏傳不報錯、型別檢查也抓不到，
    只會靜默寫出一筆殘缺記錄（TD-012c）。此處統一填齊，呼叫端不必逐一記得。

    `external_id` 一律寫進 `changed_fields`：帳號被硬刪除後（DELETE /users/{id}），
    稽核只剩數字 id 無法還原身分（TD-012b），保留入口識別至少讓 SSO 事件可回溯。

    **不得記錄**憑證原文、共享密鑰、任何密碼。
    """
    changed_fields = dict(extra_fields or {})
    if external_id:
        changed_fields["external_id"] = external_id

    await audit_service.log(
        event_type=event_type,
        action=action,
        result=result,
        # actor 可為 Users 或 UserInfoSchema，兩者皆有 id／username／role
        actor_id=actor.id if actor else None,
        actor_username=actor.username if actor else None,
        actor_role=actor.role if actor else None,
        target_username=target_username,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=request_ip,
        user_agent=user_agent,
        endpoint=endpoint,
        changed_fields=changed_fields or None,
        failure_reason=failure_reason,
    )


# ---------------------------------------------------------------------------
# 狀態對照（data-model.md 第八節）
# ---------------------------------------------------------------------------

def account_status_code(is_active: bool, has_pending_registration: bool) -> int:
    """帳號建立回應的 status（0 接受註冊請求 / 1 已啟用 / 2 停用中）"""
    if is_active:
        return AccountStatus.ACTIVE
    if has_pending_registration:
        return AccountStatus.PENDING
    return AccountStatus.DISABLED


def apply_status_code(registration_status: Optional[str]) -> int:
    """審核維度（apply_status）。

    **無申請記錄的既有帳號一律判「受理中(0)」**（FR-035）——早期由舊系統匯入的帳號
    沒有走過 AERC 的審核流程，但它們是合法且使用中的帳號。判 3（無此使用者）會謊稱
    查無此人，判 1（已啟用）會謊稱通過了一個從未發生的審核。
    """
    if registration_status == RegistrationStatus.APPROVED.value:
        return ApplyStatus.ACTIVE
    if registration_status == RegistrationStatus.REJECTED.value:
        return ApplyStatus.DISABLED
    return ApplyStatus.PENDING


# ---------------------------------------------------------------------------
# 逐筆驗證
# ---------------------------------------------------------------------------

def validate_register_item(item) -> Optional[str]:
    """回傳錯誤訊息，通過則回傳 None。"""
    for field in _REQUIRED_FIELDS:
        if not _clean(getattr(item, field, None)):
            return f"缺少必填欄位「{field}」"

    for field, limit in _MAX_LENGTHS.items():
        value = _clean(getattr(item, field, None))
        if len(value) > limit:
            return f"欄位「{field}」長度為 {len(value)}，超過上限 {limit}"

    email = normalize_email(item.email)
    if "@" not in email or email.startswith("@") or email.endswith("@"):
        return "電子郵件格式不正確"

    return None


# ---------------------------------------------------------------------------
# 管理處 / 分處 / 工作站解析
# ---------------------------------------------------------------------------

async def resolve_offices(names: Set[str]) -> Dict[str, int]:
    """整批一次查出管理處名稱 → id。

    以整批的集合一次查詢，不在逐筆迴圈內各查一次（N 筆請求 N 次往返）。
    比對為精確相等（去前後空白後）——管理處是受控的 25 筆固定資料，客戶端送出的
    就是同一套官方名稱，模糊比對只會引入「比對到錯的管理處」這種比失敗更糟的結果。
    """
    cleaned = {name for name in names if name}
    if not cleaned:
        return {}
    rows = await Offices.filter(name__in=list(cleaned)).values("id", "name")
    return {row["name"]: row["id"] for row in rows}


async def resolve_department(
    office_id: int, branch: str, station: str
) -> Tuple[Optional[dict], List[str]]:
    """解析分處與工作站，回傳 (department, 告警訊息清單)。

    分處與工作站在客戶契約中為**選填**，對應不到時**不阻擋帳號建立**（FR-026），
    該子欄位留空並記錄告警供管理員後續補正。這與管理處相反——管理處對應不到必須
    讓該筆失敗（FR-025），因為權限守衛在管理處為空時會拒絕存取，那種帳號建了不能用。
    """
    warnings: List[str] = []
    if not branch and not station:
        return None, warnings

    ia_code = str(office_id).zfill(2)
    rows = await OfficeBoundaries.filter(ia_code=ia_code).values(
        "mng_code", "mng_name", "stn_code", "stn_name"
    )

    department: dict = {}
    if branch:
        matched = next((r for r in rows if r["mng_name"] == branch), None)
        if matched:
            department["branch"] = {"code": matched["mng_code"], "name": matched["mng_name"]}
        else:
            warnings.append(f"分處「{branch}」在管理處 {office_id} 查無對應，已留空")

    if station:
        matched = next((r for r in rows if r["stn_name"] == station), None)
        if matched:
            department["station"] = {"code": matched["stn_code"], "name": matched["stn_name"]}
        else:
            warnings.append(f"工作站「{station}」在管理處 {office_id} 查無對應，已留空")

    return (department or None), warnings


# ---------------------------------------------------------------------------
# 帳號建立
# ---------------------------------------------------------------------------

async def _create_account_with_identity(item, office_id: int, department: Optional[dict]) -> Users:
    """於**同一交易**內建立帳號、申請記錄、身分對應（FR-029）。

    三者必須同進同退——只有其中之一的中間狀態會讓後續流程無法歸因：有帳號無對應
    關係，使用者從入口進來會被當成「未綁定」而進入綁定流程；有對應關係無帳號則
    直接指向不存在的帳號。
    """
    account = _clean(item.account)
    async with in_transaction():
        user = await Users.create(
            username=account,
            email=_clean(item.email),
            email_verified=False,
            full_name=data_encryption_service.encrypt(_clean(item.name)),
            office_id=office_id,
            department=department,
            job_title=_clean(item.title) or None,
            phone=data_encryption_service.encrypt(_clean(item.phone_number)),
            phone_ext=data_encryption_service.encrypt(_clean(item.extension)),
            password=None,
            is_active=False,
            role=PORTAL_DEFAULT_ROLE,
        )
        await UserRegistration.create(
            user_id=user.id,
            application_reason=data_encryption_service.encrypt(PORTAL_APPLICATION_REASON),
        )
        await SsoIdentity.create(
            external_id=account,
            user_id=user.id,
            bound_method=SsoBindMethod.REGISTERED,
            bound_at=datetime.now(timezone.utc),
        )
    return user


async def _identity_conflict(account: Optional[str], user_id: Optional[int]) -> Optional[str]:
    """`sso_identities` 兩個 unique 約束的**逐一實際查詢**，回傳衝突說明或 None。

    帳號建立的 IntegrityError 歸因、首次綁定的預檢與 IntegrityError 歸因共用此判準，
    使同一種衝突在所有路徑上都是同一句話。
    """
    if account and await SsoIdentity.filter(external_id=account).exists():
        return "此入口帳號識別已綁定其他 AERC 帳號"
    if user_id is not None and await SsoIdentity.filter(user_id=user_id).exists():
        return "此 AERC 帳號已被其他入口身分綁定"
    return None


async def _attribute_identity_integrity_error(
    account: str, user_id: Optional[int], exc: IntegrityError
) -> str:
    """`sso_identities` 有兩個 unique 約束，必須**逐一實際查詢驗證**。

    禁止用刪除法猜測最後一個候選（AERC-0417 的教訓：`users` 表的 IntegrityError 被
    刪除法誤判為「此電子郵件已被使用」，真因是 PK 序列落後，與 email 完全無關）。
    兩個候選都不衝突時誠實回報未知，並把原始例外寫進日誌供追查。
    """
    message = await _identity_conflict(account, user_id)
    if message:
        return message
    logger.error("sso_identities 寫入 IntegrityError 無法歸因 account=%s: %s", account, exc)
    raise AppError(500, "系統錯誤，請稍後再試", diagnostic=str(exc))


def _result(index: int, item, *, success: bool, status: Optional[int] = None,
            err_msg: Optional[str] = None) -> dict:
    """逐筆結果。

    `account` 與 `email` **原樣回填請求帶入的值**，不回傳 AERC 端的登入帳號——在入口
    代建情境下兩者相同，但冪等命中一個既有帳號時會不同（該帳號的 AERC 登入帳號是它
    當初建立時決定的，與入口識別無關）。回傳 AERC 端帳號會讓呼叫端收到一個它不認得的
    識別，也無謂洩漏內部登入帳號。
    """
    payload: dict = {
        "index": index,
        "account": _clean(item.account),
        "email": _clean(item.email),
        "success": success,
    }
    if success:
        payload["status"] = status
    else:
        payload["err_msg"] = err_msg
    return payload


async def _idempotent_result(index: int, item, identity: SsoIdentity) -> dict:
    """入口帳號識別已存在時的處理（FR-023 / FR-024）。

    冪等的判準是「帳號識別**與**電子郵件皆相符」。對應關係是怎麼建立的
    （入口代建、本人綁定、管理員改綁）完全不影響判定——因為本 API **從不更新**任何
    既有資料，「這個帳號能不能由入口更新」這個問題在此沒有意義。
    """
    user = await Users.filter(id=identity.user_id).first()
    if user is None:
        # CASCADE 保證帳號刪除時對應關係一併消滅，理論上不可達；真的發生代表資料異常
        logger.error("sso_identities 指向不存在的帳號 external_id=%s", identity.external_id)
        return _result(index, item, success=False, err_msg="系統錯誤，請稍後再試")

    if normalize_email(user.email) != normalize_email(item.email):
        return _result(
            index, item, success=False,
            err_msg="此入口帳號識別已存在，但電子郵件與系統紀錄不符",
        )

    has_pending = await UserRegistration.filter(
        user_id=user.id, status=RegistrationStatus.PENDING
    ).exists()
    return _result(
        index, item, success=True,
        status=account_status_code(user.is_active, has_pending),
    )


async def _process_register_item(
    index: int, item, offices: Dict[str, int], seen_accounts: Set[str]
) -> dict:
    """單筆處理。任何失敗都只影響這一筆（FR-022）。"""
    error = validate_register_item(item)
    if error:
        return _result(index, item, success=False, err_msg=error)

    account = _clean(item.account)

    # 同一批次內重複：第二筆起一律失敗（FR-023b）。
    # 不能讓第二筆因第一筆剛建立的資料而被判為冪等成功——那會把一筆明顯有問題的
    # 輸入回報為正常受理。
    if account in seen_accounts:
        return _result(index, item, success=False, err_msg="同一批次內出現重複的帳號識別")
    seen_accounts.add(account)

    identity = await SsoIdentity.filter(external_id=account).first()
    if identity is not None:
        return await _idempotent_result(index, item, identity)

    if await Users.filter(username=account).exists():
        return _result(
            index, item, success=False,
            err_msg="此帳號識別已被系統中的既有帳號使用，請由管理員確認後改綁",
        )

    office_id = offices.get(_clean(item.wtn))
    if office_id is None:
        return _result(
            index, item, success=False,
            err_msg=f"所屬管理處「{_clean(item.wtn)}」在系統中查無對應",
        )

    department, warnings = await resolve_department(
        office_id, _clean(item.branch), _clean(item.stn)
    )
    for warning in warnings:
        logger.warning("入口代建帳號 %s：%s", account, warning)

    try:
        user = await _create_account_with_identity(item, office_id, department)
    except IntegrityError as exc:
        message = await _attribute_identity_integrity_error(account, None, exc)
        return _result(index, item, success=False, err_msg=message)

    return _result(index, item, success=True, status=account_status_code(user.is_active, True))


async def register_accounts(
    items: List[Any], *, request_ip: str, user_agent: str, endpoint: str
) -> List[dict]:
    """批次建立帳號。回傳的筆數與順序與請求一致（FR-004）。"""
    wtn_names = {_clean(getattr(item, "wtn", None)) for item in items}
    offices = await resolve_offices(wtn_names)

    seen_accounts: Set[str] = set()
    results: List[dict] = []

    for position, item in enumerate(items):
        index = item.index if item.index is not None else position
        result = await _process_register_item(index, item, offices, seen_accounts)
        results.append(result)
        await _log_register_result(
            result, request_ip=request_ip, user_agent=user_agent, endpoint=endpoint
        )

    return results


async def _log_register_result(
    result: dict, *, request_ip: str, user_agent: str, endpoint: str
) -> None:
    """成功與失敗路徑皆記錄（FR-039）。"""
    succeeded = result.get("success", False)
    await log_portal_event(
        event_type=AuditEventType.REGISTRATION,
        action=AuditAction.CREATE,
        result=AuditResult.SUCCESS if succeeded else AuditResult.FAILURE,
        request_ip=request_ip,
        user_agent=user_agent,
        endpoint=endpoint,
        resource_type="user",
        resource_id=result.get("account") or None,
        external_id=result.get("account") or None,
        failure_reason=None if succeeded else result.get("err_msg"),
    )


# ---------------------------------------------------------------------------
# 狀態查詢
# ---------------------------------------------------------------------------

async def find_users_by_email(normalized_email: str) -> List[Users]:
    """以正規化後的電子郵件比對帳號（FR-031）。狀態查詢與登入落地共用同一判準。

    users 全表僅數百筆，正規化比對的全表掃描成本可忽略；不為此建函數索引。
    """
    if not normalized_email:
        return []
    return [
        user for user in await Users.all().only("id", "username", "email", "is_active", "password", "role")
        if normalize_email(user.email) == normalized_email
    ]


async def _query_single_status(index: int, item) -> Tuple[dict, Optional[str]]:
    """回傳 (逐筆結果, 告警訊息)。

    以電子郵件為**唯一比對鍵**，姓名完全不參與比對（FR-030）；回應中的姓名原樣回填
    請求帶入的值（FR-032），不從 AERC 端讀取。
    """
    email = normalize_email(item.email)
    base = {
        "index": index,
        "email": _clean(item.email),
        "name": _clean(item.name),
    }
    not_found = {
        **base, "account": None,
        "apply_status": ApplyStatus.NOT_FOUND, "status": AccountStatus.NOT_FOUND,
    }

    if not email:
        return not_found, None

    candidates = await find_users_by_email(email)

    if not candidates:
        return not_found, None

    if len(candidates) > 1:
        # 命中多筆視為無法唯一辨識，回報無此使用者並留下告警。
        # **不得任意挑選其中一筆回報**——那會對呼叫端宣稱一個未經確認的對象。
        return not_found, f"電子郵件 {email} 在系統中命中 {len(candidates)} 筆帳號，無法唯一辨識"

    user = candidates[0]
    registration = await UserRegistration.filter(user_id=user.id).order_by("-created_at").first()
    return {
        **base,
        "account": user.username,
        "apply_status": apply_status_code(registration.status.value if registration else None),
        "status": AccountStatus.ACTIVE if user.is_active else AccountStatus.DISABLED,
    }, None


async def query_account_status(
    items: List[Any], *, request_ip: str, user_agent: str, endpoint: str
) -> List[dict]:
    """批次查詢帳號狀態。

    稽核：**僅記錄失敗路徑**（資料品質告警）。成功查詢為唯讀且不改變任何狀態，
    逐筆記錄會讓稽核表被例行輪詢灌滿而淹沒真正需要調查的事件。
    """
    results: List[dict] = []
    for position, item in enumerate(items):
        index = item.index if item.index is not None else position
        result, warning = await _query_single_status(index, item)
        results.append(result)
        if warning:
            logger.warning("狀態查詢資料品質告警：%s", warning)
            await log_portal_event(
                event_type=AuditEventType.DATA_ACCESS,
                action=AuditAction.VIEW,
                result=AuditResult.FAILURE,
                request_ip=request_ip,
                user_agent=user_agent,
                endpoint=endpoint,
                resource_type="user",
                failure_reason=warning,
            )
    return results


# ---------------------------------------------------------------------------
# 登入落地、交接碼交換、首次綁定（US3）
#
# 稽核一律寫在交易之外：audit_service 在交易內寫入時會加入同一個交易，拒絕路徑一旦
# raise，稽核紀錄會跟著被回滾——「有人嘗試但被擋下」正是最不能遺失的紀錄（FR-039）。
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class _LandingOutcome:
    """登入落地的分流結果，對應 contracts/external-portal-api.md 1.3 第 1–7 列。"""
    query: Dict[str, str]                  # 導向前端落地頁 /sso 的查詢參數
    failure_reason: Optional[str] = None   # None 即分流 1（發出交接碼，可進入）
    user: Optional[Users] = None


async def _issue_token(
    user: Users, token_type: AuthTokenType, request_ip: str, user_agent: str,
    external_id: Optional[str] = None,
) -> str:
    # auth_tokens.ip_address／user_agent 為 CharField(45)／(255)，超長會在 ORM 層冒成 500
    auth_token = await EmailService().create_auth_token(
        user=user,
        token_type=token_type,
        ip_address=(request_ip or "")[:45] or None,
        user_agent=(user_agent or "")[:255] or None,
        external_id=external_id,
    )
    return auth_token.token


async def _land_unbound_candidate(
    user: Users, claims: PortalClaims, request_ip: str, user_agent: str
) -> _LandingOutcome:
    """查無對應關係、電子郵件唯一命中時的分流（第 5–7 列）。

    ⚠️ 核發綁定票據的條件是三項缺一不可：唯一命中（呼叫端已保證）+ 啟用 + 已設定密碼。
    綁定的下一步是「本人以帳號密碼登入」，未啟用或無密碼的帳號都做不到——只檢查其中一項，
    使用者會拿到一張兌現不了的票據，卡在「請以原帳密登入」這個他做不到的指示上（FR-017）。
    """
    if not user.is_active:
        return _LandingOutcome({"reason": "account_inactive"}, "候選帳號未啟用，未核發票據", user)
    if not user.password:
        return _LandingOutcome({"reason": "password_setup_required"}, "候選帳號未設定密碼，未核發票據", user)
    ticket = await _issue_token(user, AuthTokenType.SSO_BINDING, request_ip, user_agent, claims.external_id)
    return _LandingOutcome({"bind": ticket}, "尚未綁定，已核發綁定票據", user)


async def _resolve_landing(claims: PortalClaims, request_ip: str, user_agent: str) -> _LandingOutcome:
    """先查對應關係，查得到者進入啟用狀態閘門，查不到者走首次綁定（FR-015）。

    「查得到」**不等於**放行：入口代建的帳號在審核前就有對應關係，但尚未啟用（FR-012）。
    """
    identity = await SsoIdentity.filter(external_id=claims.external_id).prefetch_related("user").first()
    if identity is not None:
        if not identity.user.is_active:
            return _LandingOutcome({"reason": "account_inactive"}, "帳號未啟用", identity.user)
        code = await _issue_token(identity.user, AuthTokenType.SSO_HANDOFF, request_ip, user_agent)
        return _LandingOutcome({"code": code}, None, identity.user)

    candidates = await find_users_by_email(normalize_email(claims.email))
    if not candidates:
        return _LandingOutcome({"reason": "no_account"}, "電子郵件查無帳號")
    if len(candidates) > 1:
        # 不得與 no_account 合併：使用者確實有帳號，導去申請會造成重複帳號
        logger.warning(
            "登入落地資料品質告警：電子郵件命中 %d 筆帳號 external_id=%s",
            len(candidates), claims.external_id,
        )
        return _LandingOutcome({"reason": "ambiguous_account"}, "電子郵件命中多筆，無法唯一辨識")
    return await _land_unbound_candidate(candidates[0], claims, request_ip, user_agent)


async def resolve_token_login(
    claims: PortalClaims, *, request_ip: str, user_agent: str, endpoint: str
) -> Dict[str, str]:
    """憑證驗證通過後的分流與稽核。回傳導向落地頁的查詢參數。"""
    outcome = await _resolve_landing(claims, request_ip, user_agent)
    succeeded = outcome.failure_reason is None
    await log_portal_event(
        event_type=AuditEventType.AUTH,
        action=AuditAction.LOGIN if succeeded else AuditAction.LOGIN_FAILED,
        result=AuditResult.SUCCESS if succeeded else AuditResult.FAILURE,
        request_ip=request_ip,
        user_agent=user_agent,
        endpoint=endpoint,
        resource_type="sso_identity",
        resource_id=str(outcome.user.id) if outcome.user else None,
        target_username=outcome.user.username if outcome.user else None,
        actor=outcome.user if succeeded else None,
        external_id=claims.external_id,
        failure_reason=outcome.failure_reason,
    )
    return outcome.query


async def log_token_login_rejection(
    token_ref: str, *, request_ip: str, user_agent: str, endpoint: str
) -> None:
    """憑證未通過驗證（第 8 列）。失敗原因不細分步驟，與對外回應的不透露原則一致；
    細分步驟只進診斷日誌。只記錄憑證雜湊前綴供關聯，不記錄原文（FR-040）。"""
    await log_portal_event(
        event_type=AuditEventType.AUTH,
        action=AuditAction.LOGIN_FAILED,
        result=AuditResult.FAILURE,
        request_ip=request_ip,
        user_agent=user_agent,
        endpoint=endpoint,
        resource_type="sso_identity",
        failure_reason="憑證驗證未通過",
        extra_fields={"token_ref": token_ref},
    )


async def _lock_pending_token(value: str, token_type: AuthTokenType) -> Optional[AuthToken]:
    """鎖定一筆仍在效期內的 pending token。須在交易內呼叫。

    逾期者**不在此標記** expired：這使所有拒絕路徑都不寫入任何資料，呼叫端可在交易內直接
    拒絕而不必擔心回滾掉狀態變更。逾期而仍為 pending 的列無害——此查詢已排除它，同一使用者
    下次核發同類 token 時也會一併撤銷。
    """
    return await AuthToken.filter(
        token=value,
        token_type=token_type,
        status=AuthTokenStatus.PENDING,
        expires_at__gt=datetime.now(timezone.utc),
    ).select_for_update().first()


async def _mark_used(token: AuthToken) -> None:
    token.status = AuthTokenStatus.USED
    token.used_at = datetime.now(timezone.utc)
    await token.save(update_fields=["status", "used_at"])


async def _redeem_handoff_code(code: str) -> Optional[Users]:
    """回傳交接碼所屬帳號；帳號仍為啟用狀態時才消耗交接碼。查無有效交接碼時回傳 None。"""
    async with in_transaction():
        token = await _lock_pending_token(code, AuthTokenType.SSO_HANDOFF)
        if token is None:
            return None
        user = await Users.get(id=token.user_id)
        if user.is_active:
            await _mark_used(token)
        return user


async def _bound_external_id(user_id: int) -> Optional[str]:
    identity = await SsoIdentity.filter(user_id=user_id).first()
    return identity.external_id if identity else None


async def exchange_handoff_code(
    code: str, *, request_ip: str, user_agent: str, endpoint: str
) -> Users:
    """交接碼換取登入狀態前的驗證（contracts/internal-sso-api.md 第一節）。

    400 不是防禦性分支：交接碼一次性，使用者按上一頁、重新整理、多分頁開同一連結都會走到。
    """
    user = await _redeem_handoff_code(code)
    common = dict(
        event_type=AuditEventType.AUTH,
        request_ip=request_ip,
        user_agent=user_agent,
        endpoint=endpoint,
        resource_type="sso_handoff",
        resource_id=str(user.id) if user else None,
        target_username=user.username if user else None,
        external_id=await _bound_external_id(user.id) if user else None,
    )
    if user is None:
        await log_portal_event(
            **common, action=AuditAction.LOGIN_FAILED, result=AuditResult.FAILURE,
            failure_reason="交接碼無效、已使用或已逾期",
        )
        raise AppError(400, "登入連結已失效，請自智慧灌溉入口平台重新進入")
    if not user.is_active:
        # 交接碼發出到交換之間的空窗期，管理員可能已停用帳號
        await log_portal_event(
            **common, action=AuditAction.LOGIN_FAILED, result=AuditResult.FAILURE,
            failure_reason="交接碼有效但帳號已停用",
        )
        raise AppError(403, "您的帳號已停用，請聯繫系統管理員")

    await log_portal_event(**common, action=AuditAction.LOGIN, result=AuditResult.SUCCESS, actor=user)
    return user


class _BindRejection(Exception):
    """綁定的業務拒絕。在交易內拋出（未寫入任何資料），於交易外寫稽核後轉為 AppError。"""

    def __init__(self, status_code: int, message: str, failure_reason: str) -> None:
        super().__init__(failure_reason)
        self.status_code = status_code
        self.message = message
        self.failure_reason = failure_reason


async def _redeem_binding_ticket(ticket: str, user_id: int) -> str:
    """驗證票據並建立對應關係，與票據標記 used 於**同一交易**（FR-018）。回傳入口身分。"""
    async with in_transaction():
        token = await _lock_pending_token(ticket, AuthTokenType.SSO_BINDING)
        if token is None:
            raise _BindRejection(400, "綁定連結已失效，請自智慧灌溉入口平台重新進入", "綁定票據無效、已使用或已逾期")
        if token.user_id != user_id:
            # 關鍵檢查：否則拿到別人的票據，就能把別人的入口身分綁到自己登入的帳號
            raise _BindRejection(403, "此綁定連結不屬於目前登入的帳號，請改以正確的帳號登入", "票據候選帳號與登入者不一致")
        if not token.external_id:
            raise AppError(500, "系統錯誤，請稍後再試", diagnostic=f"sso_binding token id={token.id} 缺少 external_id")

        # 應用層預檢只為友善訊息；並發下會漏，資料庫 unique 約束才是最終防線（FR-019）
        conflict = await _identity_conflict(token.external_id, user_id)
        if conflict:
            raise _BindRejection(409, conflict, conflict)

        await SsoIdentity.create(
            external_id=token.external_id,
            user_id=user_id,
            bound_method=SsoBindMethod.SELF_BOUND,
            bound_at=datetime.now(timezone.utc),
        )
        await _mark_used(token)
        return token.external_id


async def _ticket_external_id(ticket: str) -> Optional[str]:
    """供失敗路徑稽核回溯票據所載入口身分（不論票據狀態）。"""
    token = await AuthToken.filter(token=ticket, token_type=AuthTokenType.SSO_BINDING).first()
    return token.external_id if token else None


async def bind_identity(
    ticket: str, current_user: Any, *, request_ip: str, user_agent: str, endpoint: str
) -> str:
    """完成首次綁定（contracts/internal-sso-api.md 第二節）。`current_user` 為剛以帳號密碼登入的使用者。"""
    common = dict(
        event_type=AuditEventType.AUTH,
        action=AuditAction.BIND,
        request_ip=request_ip,
        user_agent=user_agent,
        endpoint=endpoint,
        resource_type="sso_identity",
        resource_id=str(current_user.id),
        target_username=current_user.username,
        actor=current_user,
    )
    try:
        external_id = await _redeem_binding_ticket(ticket, current_user.id)
    except _BindRejection as rejection:
        await log_portal_event(
            **common, result=AuditResult.FAILURE,
            external_id=await _ticket_external_id(ticket), failure_reason=rejection.failure_reason,
        )
        raise AppError(rejection.status_code, rejection.message)
    except IntegrityError as exc:
        # 預檢與寫入之間的並發競態。兩個 unique 約束逐一實際驗證，驗不出來誠實回報（AERC-0417）
        external_id = await _ticket_external_id(ticket)
        conflict = await _identity_conflict(external_id, current_user.id)
        await log_portal_event(
            **common, result=AuditResult.FAILURE, external_id=external_id,
            failure_reason=conflict or "寫入對應關係時發生無法歸因的 IntegrityError",
        )
        if conflict is None:
            logger.error("sso_identities 綁定寫入 IntegrityError 無法歸因 external_id=%s: %s", external_id, exc)
            raise AppError(500, "系統錯誤，請稍後再試", diagnostic=str(exc))
        raise AppError(409, conflict)

    await log_portal_event(**common, result=AuditResult.SUCCESS, external_id=external_id)
    return external_id
