import logging
from typing import Optional

from src.database.audit_models import AuditAction, AuditEventType, AuditResult, SecurityAuditLog

logger = logging.getLogger(__name__)


def mask_id_number(id_number: str) -> str:
    if len(id_number) < 5:
        return id_number
    return id_number[:3] + "****" + id_number[-3:]


def mask_phone(phone: str) -> str:
    """遮罩電話類欄位（電話/分機/手機）供稽核 changed_fields 使用，比照 mask_id_number 規則"""
    if not phone or len(phone) < 5:
        return phone
    return phone[:3] + "****" + phone[-3:]


def mask_name(name: str) -> str:
    if not name:
        return name
    if len(name) == 1:
        return name + "*"
    if len(name) == 2:
        return name[0] + "*"
    return name[0] + "*" + name[-1]


def _truncate_to_field_limits(values: dict) -> dict:
    """把字串值截到 SecurityAuditLog 對應欄位的長度上限。

    為什麼需要：`ip_address`（上限 45）取自外部可控的 X-Real-IP 標頭，
    `user_agent`（500）取自 user-agent 標頭。Tortoise 的 CharField 在
    `create()` 時驗證長度，超長即拋 ValidationError → 被 log() 的
    `except Exception` 吞掉 → **整筆稽核紀錄消失，業務照常回 2xx**。
    也就是越權者只要塞一個長標頭，被擋下這件事就不留紀錄。

    上限一律動態讀自 ORM 欄位定義，不寫死數字——寫死的數字會與欄位定義
    漂移，而漂移的後果不是「截多了」，是回到整筆遺失，且以完全相同的
    沉默方式復發。

    對全部字串值一體適用，不維護「哪些欄位需要保護」的清單：新增欄位
    自動涵蓋，沒有同步點需要記得。
    """
    fields_map = SecurityAuditLog._meta.fields_map
    out = {}
    for name, value in values.items():
        max_length = getattr(fields_map.get(name), "max_length", None)
        if isinstance(value, str) and max_length and len(value) > max_length:
            logger.warning(
                "稽核欄位 %s 超出長度上限，已截斷（原長度 %d > %d）",
                name, len(value), max_length,
            )
            value = value[:max_length]
        out[name] = value
    return out


class AuditService:
    async def log(
        self,
        event_type: AuditEventType,
        action: AuditAction,
        result: AuditResult,
        *,
        actor_id: Optional[int] = None,
        actor_username: Optional[str] = None,
        actor_role: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        target_username: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        endpoint: Optional[str] = None,
        changed_fields: Optional[dict] = None,
        failure_reason: Optional[str] = None,
    ) -> None:
        try:
            # changed_fields 為 JSONField，無長度上限，不進截斷
            fields = _truncate_to_field_limits({
                "event_type": event_type.value,
                "action": action.value,
                "result": result.value,
                "actor_id": actor_id,
                "actor_username": actor_username,
                "actor_role": actor_role,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "target_username": target_username,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "endpoint": endpoint,
                "failure_reason": failure_reason,
            })
            await SecurityAuditLog.create(changed_fields=changed_fields, **fields)
        except Exception:
            logger.error("稽核記錄寫入失敗", exc_info=True)
            return


audit_service = AuditService()
