from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request

from src.auth.client_ip import get_client_ip
from src.auth.jwthandler import get_current_user
from src.database.audit_models import AuditAction, AuditEventType, AuditResult
from src.database.models import AuthToken, AuthTokenStatus, AuthTokenType, IPWhitelistEntry, Users
from src.exceptions import AppError
from src.schemas.permissions import ModuleName, PermissionAction
from src.schemas.security import (
    IPWhitelistCreateRequest,
    IPWhitelistEntryResponse,
    IPWhitelistUpdateRequest,
    PendingOtpResponse,
)
from src.schemas.users import UserInfoSchema
from src.services.audit_service import audit_service
from src.services.permission_service import permission_service

router = APIRouter(prefix="/security", tags=["Security"])


def _check_security_permission(current_user: UserInfoSchema, action: PermissionAction) -> None:
    allowed, reason = permission_service.check_permission(
        user_role=current_user.role,
        user_permissions=current_user.permissions,
        module=ModuleName.SECURITY,
        action=action,
    )
    if not allowed:
        raise AppError(403, reason or "僅限管理員操作")


@router.get("/ip-whitelist", response_model=list[IPWhitelistEntryResponse])
async def list_ip_whitelist(
    include_archived: bool = False,
    current_user: UserInfoSchema = Depends(get_current_user),
):
    _check_security_permission(current_user, PermissionAction.VIEW)

    query = IPWhitelistEntry.all()
    if not include_archived:
        query = query.filter(is_archived=False)
    entries = await query.prefetch_related("created_by").order_by("-created_at")
    return [
        IPWhitelistEntryResponse(
            id=entry.id,
            cidr=entry.cidr,
            name=entry.name,
            is_active=entry.is_active,
            is_archived=entry.is_archived,
            created_by=entry.created_by.username if entry.created_by else None,
            created_at=entry.created_at,
        )
        for entry in entries
    ]


@router.post("/ip-whitelist", response_model=IPWhitelistEntryResponse)
async def create_ip_whitelist_entry(
    payload: IPWhitelistCreateRequest,
    request: Request,
    current_user: UserInfoSchema = Depends(get_current_user),
):
    _check_security_permission(current_user, PermissionAction.CREATE)

    user = await Users.get(id=current_user.id)
    entry = await IPWhitelistEntry.create(
        cidr=payload.cidr,
        name=payload.name,
        is_active=True,
        created_by=user,
    )

    await audit_service.log(
        event_type=AuditEventType.CONFIG,
        action=AuditAction.CREATE,
        result=AuditResult.SUCCESS,
        actor_id=current_user.id,
        actor_username=current_user.username,
        actor_role=current_user.role,
        resource_type="ip_whitelist_entry",
        resource_id=str(entry.id),
        ip_address=get_client_ip(request),
        endpoint=str(request.url.path),
        changed_fields={"cidr": payload.cidr, "name": payload.name},
    )

    return IPWhitelistEntryResponse(
        id=entry.id,
        cidr=entry.cidr,
        name=entry.name,
        is_active=entry.is_active,
        is_archived=entry.is_archived,
        created_by=current_user.username,
        created_at=entry.created_at,
    )


@router.patch("/ip-whitelist/{entry_id}", response_model=IPWhitelistEntryResponse)
async def update_ip_whitelist_entry(
    entry_id: int,
    payload: IPWhitelistUpdateRequest,
    request: Request,
    current_user: UserInfoSchema = Depends(get_current_user),
):
    _check_security_permission(current_user, PermissionAction.EDIT)

    entry = await IPWhitelistEntry.filter(id=entry_id).prefetch_related("created_by").first()
    if entry is None:
        raise AppError(404, "白名單網段不存在")

    if payload.is_archived is not None:
        if payload.is_archived and entry.is_active:
            raise AppError(409, "僅能封存已停用的網段，請先停用")
        field_name = "is_archived"
        before_value = entry.is_archived
        entry.is_archived = payload.is_archived
        after_value = entry.is_archived
    else:
        field_name = "is_active"
        before_value = entry.is_active
        entry.is_active = payload.is_active
        after_value = entry.is_active

    await entry.save()

    await audit_service.log(
        event_type=AuditEventType.CONFIG,
        action=AuditAction.UPDATE,
        result=AuditResult.SUCCESS,
        actor_id=current_user.id,
        actor_username=current_user.username,
        actor_role=current_user.role,
        resource_type="ip_whitelist_entry",
        resource_id=str(entry.id),
        ip_address=get_client_ip(request),
        endpoint=str(request.url.path),
        changed_fields={field_name: {"before": before_value, "after": after_value}},
    )

    return IPWhitelistEntryResponse(
        id=entry.id,
        cidr=entry.cidr,
        name=entry.name,
        is_active=entry.is_active,
        is_archived=entry.is_archived,
        created_by=entry.created_by.username if entry.created_by else None,
        created_at=entry.created_at,
    )


@router.get("/mfa/pending-otp/{user_id}", response_model=PendingOtpResponse)
async def get_pending_mfa_otp(
    user_id: int,
    request: Request,
    current_user: UserInfoSchema = Depends(get_current_user),
):
    """供 Email 服務中斷時人工協助轉告 OTP（User Story 5），必須稽核（FR-017）"""
    _check_security_permission(current_user, PermissionAction.VIEW)

    auth_token = await AuthToken.filter(
        user_id=user_id,
        token_type=AuthTokenType.MFA_VERIFICATION,
        status=AuthTokenStatus.PENDING,
    ).order_by("-created_at").first()

    if auth_token is None or auth_token.otp is None:
        raise AppError(404, "查無待驗證的驗證碼")

    now = datetime.now(timezone.utc)
    if auth_token.expires_at < now:
        raise AppError(404, "查無待驗證的驗證碼")

    expires_in_seconds = int((auth_token.expires_at - now).total_seconds())

    await audit_service.log(
        event_type=AuditEventType.DATA_ACCESS,
        action=AuditAction.VIEW,
        result=AuditResult.SUCCESS,
        actor_id=current_user.id,
        actor_username=current_user.username,
        actor_role=current_user.role,
        resource_type="mfa_pending_otp",
        resource_id=str(user_id),
        ip_address=get_client_ip(request),
        endpoint=str(request.url.path),
    )

    return PendingOtpResponse(otp=auth_token.otp, expires_in_seconds=expires_in_seconds)
