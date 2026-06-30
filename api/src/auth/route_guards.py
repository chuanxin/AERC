"""
Declarative FastAPI route guards for AERC permission enforcement.

Usage in route decorators:
    @router.put(
        "/case/{case_number}/step/{step}",
        dependencies=[
            Depends(require_grant_scope_by_case_number),
            Depends(require_permission(ModuleName.GRANTS, PermissionAction.EDIT)),
        ],
    )
    async def update_grant_step_api(...):
        ...  # no permission logic inside

Two guard types:
  - require_permission(module, action): action-level check (role matrix)
  - require_grant_scope_by_case_number / require_grant_scope_by_id: per-grant scope check
"""

import os
from fastapi import Depends, Path

from src.auth.guard import require_full_auth
from src.schemas.users import UserInfoSchema
from src.schemas.permissions import ModuleName, PermissionAction
from src.services.permission_service import permission_service
from src.exceptions import AppError
from src.database.models import Grants

# Controlled via environment variable; default open to preserve backward compatibility.
# Set ALLOW_USER_LEGACY_GRANT_ACCESS=false to block user role from legacy grants.
_ALLOW_USER_LEGACY_GRANT_ACCESS = (
    os.getenv("ALLOW_USER_LEGACY_GRANT_ACCESS", "true").lower() == "true"
)


# ── Action-level guard ──────────────────────────────────────────────────────

def require_permission(module: ModuleName, action: PermissionAction):
    """Factory: returns a FastAPI dependency that enforces role-matrix permission.

    Raises AppError(403) with a fixed message on failure — never silently passes.
    """
    async def _guard(
        current_user: UserInfoSchema = Depends(require_full_auth),
    ) -> None:
        allowed, _ = permission_service.check_permission(
            current_user.role, current_user.permissions, module, action
        )
        if not allowed:
            raise AppError(403, "無此操作權限")

    return _guard


# ── Scope-level guards ──────────────────────────────────────────────────────

def _enforce_grant_scope(
    *,
    grant_office_id: int | None,
    created_by_id: int | None,
    current_user: UserInfoSchema,
) -> None:
    """Enforce per-grant scope. All branches either return or raise — no silent pass.

    Called exclusively by require_grant_scope_by_* functions below.
    """
    role = current_user.role  # UserInfoSchema guarantees this field exists

    if role == "admin":
        return

    if role in ("manager", "staff"):
        office = current_user.office
        if office is None:
            raise AppError(403, "帳號尚未指派管理處，請聯繫系統管理員完成設定")
        if grant_office_id != office.id:
            raise AppError(403, "無此操作權限")
        return

    if role == "user":
        office = current_user.office
        if office is None:
            raise AppError(403, "帳號尚未指派管理處，請聯繫系統管理員完成設定")
        if grant_office_id != office.id:
            raise AppError(403, "無此操作權限")
        if created_by_id is not None:
            # Normal grant: must also be the creator
            if created_by_id != current_user.id:
                raise AppError(403, "無此操作權限")
        else:
            # Legacy grant (created_by=None): behaviour controlled by env flag
            if not _ALLOW_USER_LEGACY_GRANT_ACCESS:
                raise AppError(403, "無此操作權限")
        return

    # Unknown role: explicit rejection, not silent
    raise AppError(403, "無此操作權限")


async def require_grant_scope_by_case_number(
    case_number: str = Path(...),
    current_user: UserInfoSchema = Depends(require_full_auth),
) -> None:
    """Scope guard for routes with path parameter {case_number}."""
    grant = (
        await Grants.filter(case_number=case_number)
        .prefetch_related("created_by")
        .first()
    )
    if grant is None:
        raise AppError(404, "案件不存在")
    _enforce_grant_scope(
        grant_office_id=grant.office_id,
        created_by_id=grant.created_by.id if grant.created_by else None,
        current_user=current_user,
    )


async def require_grant_scope_by_id(
    grant_id: int = Path(...),
    current_user: UserInfoSchema = Depends(require_full_auth),
) -> None:
    """Scope guard for routes with path parameter {grant_id}."""
    grant = (
        await Grants.filter(id=grant_id)
        .prefetch_related("created_by")
        .first()
    )
    if grant is None:
        raise AppError(404, "案件不存在")
    _enforce_grant_scope(
        grant_office_id=grant.office_id,
        created_by_id=grant.created_by.id if grant.created_by else None,
        current_user=current_user,
    )
