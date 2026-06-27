import logging
from typing import Optional

from src.database.audit_models import AuditAction, AuditEventType, AuditResult, SecurityAuditLog

logger = logging.getLogger(__name__)


def mask_id_number(id_number: str) -> str:
    if len(id_number) < 5:
        return id_number
    return id_number[:3] + "****" + id_number[-3:]


def mask_name(name: str) -> str:
    if not name:
        return name
    if len(name) == 1:
        return name + "*"
    if len(name) == 2:
        return name[0] + "*"
    return name[0] + "*" + name[-1]


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
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        endpoint: Optional[str] = None,
        changed_fields: Optional[dict] = None,
        failure_reason: Optional[str] = None,
    ) -> None:
        try:
            await SecurityAuditLog.create(
                event_type=event_type.value,
                action=action.value,
                result=result.value,
                actor_id=actor_id,
                actor_username=actor_username,
                actor_role=actor_role,
                resource_type=resource_type,
                resource_id=resource_id,
                ip_address=ip_address,
                user_agent=user_agent,
                endpoint=endpoint,
                changed_fields=changed_fields,
                failure_reason=failure_reason,
            )
        except Exception:
            logger.error("稽核記錄寫入失敗", exc_info=True)
            return


audit_service = AuditService()
