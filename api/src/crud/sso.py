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
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from src.database.audit_models import AuditAction, AuditEventType, AuditResult
from src.database.geo_models import OfficeBoundaries
from src.database.models import (
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


async def _attribute_identity_integrity_error(
    account: str, user_id: Optional[int], exc: IntegrityError
) -> str:
    """`sso_identities` 有兩個 unique 約束，必須**逐一實際查詢驗證**。

    禁止用刪除法猜測最後一個候選（AERC-0417 的教訓：`users` 表的 IntegrityError 被
    刪除法誤判為「此電子郵件已被使用」，真因是 PK 序列落後，與 email 完全無關）。
    兩個候選都不衝突時誠實回報未知，並把原始例外寫進日誌供追查。
    """
    if await SsoIdentity.filter(external_id=account).exists():
        return "此入口帳號識別已綁定其他 AERC 帳號"
    if user_id is not None and await SsoIdentity.filter(user_id=user_id).exists():
        return "此 AERC 帳號已被其他入口身分綁定"
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

    # users 全表僅數百筆，正規化比對的全表掃描成本可忽略；不為此建函數索引。
    candidates = [
        user for user in await Users.all().only("id", "username", "email", "is_active")
        if normalize_email(user.email) == email
    ]

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
