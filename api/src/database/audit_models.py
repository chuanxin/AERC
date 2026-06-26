from enum import Enum
from tortoise import fields
from tortoise.models import Model


class AuditEventType(str, Enum):
    AUTH = "AUTH"
    ACCOUNT = "ACCOUNT"
    REGISTRATION = "REGISTRATION"
    DATA_ACCESS = "DATA_ACCESS"
    GRANT_OPS = "GRANT_OPS"
    CONFIG = "CONFIG"


class AuditAction(str, Enum):
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    LOGIN_FAILED = "LOGIN_FAILED"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DISABLE = "DISABLE"
    ENABLE = "ENABLE"
    UNLOCK = "UNLOCK"
    VIEW = "VIEW"
    EXPORT = "EXPORT"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"
    ROLE_CHANGE = "ROLE_CHANGE"


class AuditResult(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"


class SecurityAuditLog(Model):
    id = fields.BigIntField(pk=True)
    occurred_at = fields.DatetimeField(use_tz=True, auto_now_add=True)
    actor_id = fields.IntField(null=True)
    actor_username = fields.CharField(max_length=20, null=True)
    actor_role = fields.CharField(max_length=50, null=True)
    event_type = fields.CharField(max_length=20)
    action = fields.CharField(max_length=30)
    resource_type = fields.CharField(max_length=50, null=True)
    resource_id = fields.CharField(max_length=100, null=True)
    ip_address = fields.CharField(max_length=45, null=True)
    user_agent = fields.CharField(max_length=500, null=True)
    endpoint = fields.CharField(max_length=200, null=True)
    changed_fields = fields.JSONField(null=True)
    result = fields.CharField(max_length=10)
    failure_reason = fields.CharField(max_length=500, null=True)

    class Meta:
        table = "security_audit_logs"
