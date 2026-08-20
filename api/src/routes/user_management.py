"""
使用者帳號管理 API 端點

提供帳號管理功能：
- 使用者列表查詢（支援篩選、分頁、搜尋）
- 使用者詳細資訊
- 批次啟用/停用帳號
- 帳號審核功能（030-account-approval-flow）

Created: 2025-12-08
Updated: 2026-06-26 (030-account-approval-flow: role check, approval logic, audit)
"""

import logging
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request, Query, status
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import in_transaction

from src.auth.guard import require_full_auth
from src.auth.route_guards import require_permission
from src.database.audit_models import AuditAction, AuditEventType, AuditResult
from src.database.models import (
    UserRegistration,
    RegistrationStatus,
    Users,
    AuthToken,
    AuthTokenType,
    AuthTokenStatus,
)
from src.exceptions import AppError
from src.services.data_encryption import data_encryption_service
from src.schemas.permissions import (
    ModuleName,
    PermissionAction,
    UpdateUserPermissionsRequest,
    UserPermissionsResponse,
    UserPermissionsSchema
)
from src.schemas.users import (
    RejectUserRequest,
    UserInfoSchema,
    UserRoleUpdateRequest,
    EmailVerificationResponse,
    AccountAssignmentUpdateRequest,
)
from src.services.audit_service import audit_service
from src.services.email_service import EmailConfig, EmailService
from src.services.permission_service import permission_service

RESEND_VERIFICATION_COOLDOWN_SECONDS = 60


router = APIRouter()
logger = logging.getLogger(__name__)


# ============================================================================
# 使用者列表與查詢
# ============================================================================

@router.get(
    "",
    response_model=dict,
    summary="取得使用者列表",
    description="支援篩選、分頁、搜尋功能"
)
async def list_users(
    request: Request,
    page: int = Query(1, ge=1, description="頁碼"),
    page_size: int = Query(20, ge=1, le=100, description="每頁筆數"),
    is_active: Optional[bool] = Query(None, description="帳號狀態篩選"),
    role: Optional[str] = Query(None, description="角色篩選"),
    office_id: Optional[int] = Query(None, description="管理處 ID 篩選"),
    search: Optional[str] = Query(None, description="搜尋關鍵字（帳號、姓名、Email）"),
    email_verified: Optional[bool] = Query(None, description="email 驗證狀態篩選"),
    current_user: Users = Depends(require_full_auth)
):
    """取得使用者列表（分頁）"""
    can_view_all, _ = permission_service.check_permission(
        user_role=current_user.role,
        user_permissions=current_user.permissions,
        module=ModuleName.USERS,
        action=PermissionAction.VIEW_ALL,
    )
    if not can_view_all:
        actor_office = current_user.office
        if not actor_office:
            raise AppError(403, "帳號尚未指派管理處，請聯繫系統管理員完成設定")
        # manager 只能查看同管理處帳號，忽略 office_id query param
        office_id = actor_office.id

    query = Users.all().prefetch_related('office')

    if is_active is not None:
        query = query.filter(is_active=is_active)
    if role:
        query = query.filter(role=role)
    if office_id:
        query = query.filter(office_id=office_id)
    if email_verified is not None:
        query = query.filter(email_verified=email_verified)
    if search:
        # full_name 已加密，無法用 DB __icontains；改為讀取所有後 Python 層篩選
        # 先以非 PII 條件縮小結果集，再 Python 篩選 username/email/full_name
        all_users = await query.all()
        search_lower = search.lower()
        users = [
            u for u in all_users
            if search_lower in (u.username or "").lower()
            or search_lower in (u.email or "").lower()
            or search_lower in (data_encryption_service.decrypt(u.full_name) or "").lower()
        ]
        total = len(users)
        offset = (page - 1) * page_size
        users = users[offset: offset + page_size]
    else:
        total = await query.count()
        offset = (page - 1) * page_size
        users = await query.offset(offset).limit(page_size).all()

    users_data = [
        {
            "id": user.id,
            "username": user.username,
            "full_name": data_encryption_service.decrypt(user.full_name),
            "email": user.email,
            "job_title": user.job_title,
            "is_active": user.is_active,
            "email_verified": user.email_verified,
            "role": user.role,
            "permissions": user.permissions,
            "office": {
                "id": user.office.id,
                "name": user.office.name,
                "short_name": user.office.short_name,
                "code": user.office.code,
                "classification": user.office.classification,
                "is_funding_source": user.office.is_funding_source
            } if user.office else None,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
        }
        for user in users
    ]

    await audit_service.log(
        event_type=AuditEventType.DATA_ACCESS,
        action=AuditAction.VIEW,
        result=AuditResult.SUCCESS,
        actor_id=current_user.id,
        actor_username=current_user.username,
        actor_role=current_user.role,
        resource_type="user",
        resource_id="list",
        ip_address=request.headers.get("X-Real-IP", ""),
        user_agent=request.headers.get("user-agent", ""),
        endpoint=str(request.url.path),
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "users": users_data
    }


# 注意：/pending-approval 必須在 /{user_id} 之前定義，否則 FastAPI 會將靜態段當成 user_id 做 int 轉換 → 422
@router.get(
    "/pending-approval",
    summary="取得待審核帳號列表",
    description="列出所有待審核的帳號申請（admin 全部，manager 限同管理處）"
)
async def get_pending_approval_users(
    request: Request,
    page: int = Query(1, ge=1, description="頁碼"),
    page_size: int = Query(20, ge=1, le=100, description="每頁筆數"),
    current_user: Users = Depends(require_full_auth)
):
    """取得待審核帳號清單"""
    if current_user.role not in ["admin", "manager"]:
        raise AppError(403, "無審核帳號權限")

    query = UserRegistration.filter(
        status=RegistrationStatus.PENDING
    ).prefetch_related("user", "user__office")

    if current_user.role == "manager":
        if current_user.office is None:
            raise AppError(403, "帳號尚未指派管理處，請聯繫系統管理員完成設定")
        query = query.filter(user__office_id=current_user.office.id)

    total = await query.count()
    offset = (page - 1) * page_size
    registrations = await query.offset(offset).limit(page_size).order_by("-created_at")

    users_data = [
        {
            "user_id": reg.user.id,
            "registration_id": reg.id,
            "username": reg.user.username,
            "full_name": data_encryption_service.decrypt(reg.user.full_name),
            "email": reg.user.email,
            "office_name": reg.user.office.name if reg.user.office else None,
            "application_reason": data_encryption_service.decrypt(reg.application_reason),
            "applied_at": reg.created_at.isoformat() if reg.created_at else None,
        }
        for reg in registrations
    ]

    await audit_service.log(
        event_type=AuditEventType.DATA_ACCESS,
        action=AuditAction.VIEW,
        result=AuditResult.SUCCESS,
        actor_id=current_user.id,
        actor_username=current_user.username,
        actor_role=current_user.role,
        resource_type="registration",
        resource_id="pending-list",
        ip_address=request.headers.get("X-Real-IP", ""),
        user_agent=request.headers.get("user-agent", ""),
        endpoint=str(request.url.path),
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "users": users_data
    }


@router.get(
    "/{user_id}",
    summary="取得單一使用者詳細資訊",
    description="根據使用者 ID 取得詳細資訊"
)
async def get_user(
    request: Request,
    user_id: int,
    current_user: Users = Depends(require_full_auth)
):
    """取得單一使用者詳細資訊"""
    if current_user.role not in ["admin", "manager"]:
        raise AppError(403, "無帳號管理權限")

    try:
        user = await Users.get(id=user_id).prefetch_related('office')
        user.full_name = data_encryption_service.decrypt(user.full_name)
        await audit_service.log(
            event_type=AuditEventType.DATA_ACCESS,
            action=AuditAction.VIEW,
            result=AuditResult.SUCCESS,
            actor_id=current_user.id,
            actor_username=current_user.username,
            actor_role=current_user.role,
            resource_type="user",
            resource_id=str(user_id),
            ip_address=request.headers.get("X-Real-IP", ""),
            user_agent=request.headers.get("user-agent", ""),
            endpoint=str(request.url.path),
        )
        return UserInfoSchema.model_validate(user)
    except DoesNotExist:
        raise AppError(404, f"使用者 ID {user_id} 不存在")


# ============================================================================
# 權限管理
# ============================================================================

@router.patch(
    "/{user_id}/permissions",
    response_model=UserPermissionsResponse,
    summary="更新使用者權限",
    description="更新指定使用者的權限設定（需 admin 角色）",
    dependencies=[Depends(require_permission(ModuleName.USERS, PermissionAction.EDIT))],
)
async def update_user_permissions(
    user_id: int,
    request: UpdateUserPermissionsRequest,
    current_user: UserInfoSchema = Depends(require_full_auth)
):

    valid, error_msg = permission_service.validate_permissions_structure(request.permissions)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"權限設定不合法: {error_msg}"
        )

    try:
        user = await Users.get(id=user_id)
        user.permissions = request.permissions.model_dump(exclude_none=True)
        await user.save()

        return UserPermissionsResponse(
            user_id=user.id,
            username=user.username,
            full_name=data_encryption_service.decrypt(user.full_name),
            role=user.role,
            permissions=UserPermissionsSchema(**user.permissions) if user.permissions else None,
            updated_at=datetime.now(timezone.utc).isoformat()
        )
    except DoesNotExist:
        raise AppError(404, f"使用者 ID {user_id} 不存在")


@router.patch(
    "/{user_id}/role",
    summary="變更使用者群組",
    description="變更指定使用者的角色群組（需 admin 且具 users.edit 權限）",
    dependencies=[Depends(require_permission(ModuleName.USERS, PermissionAction.EDIT))],
)
async def update_user_role(
    user_id: int,
    request: UserRoleUpdateRequest,
    current_user: UserInfoSchema = Depends(require_full_auth)
):
    try:
        user = await Users.get(id=user_id)
    except DoesNotExist:
        raise AppError(404, f"使用者 ID {user_id} 不存在")

    old_role = user.role
    if old_role == request.role:
        raise AppError(400, "新角色與目前角色相同")

    if current_user.role == "manager":
        if old_role == "admin":
            raise AppError(403, "無法變更管理員帳號的群組")
        if request.role == "admin":
            raise AppError(403, "無法將帳號提升為管理員群組")

    user.role = request.role
    await user.save()

    await audit_service.log(
        event_type=AuditEventType.ACCOUNT,
        action=AuditAction.ROLE_CHANGE,
        result=AuditResult.SUCCESS,
        actor_id=current_user.id,
        actor_username=current_user.username,
        actor_role=current_user.role,
        endpoint=f"/user-management/{user_id}/role",
        changed_fields={"role": {"before": old_role, "after": request.role}},
    )

    return {"user_id": user.id, "username": user.username, "role": user.role}


# ============================================================================
# 批次操作
# ============================================================================

@router.post(
    "/batch-activate",
    summary="批次啟用帳號",
    description="批次啟用多個使用者帳號（需 admin 角色）",
    dependencies=[Depends(require_permission(ModuleName.USERS, PermissionAction.EDIT))],
)
async def batch_activate_users(
    user_ids: List[int],
    current_user: UserInfoSchema = Depends(require_full_auth)
):

    results = []
    success_count = 0
    failed_count = 0

    for user_id in user_ids:
        try:
            user = await Users.get(id=user_id)
            if current_user.role == "manager" and user.role == "admin":
                results.append({"user_id": user_id, "username": user.username, "success": False, "message": "無法操作管理員帳號"})
                failed_count += 1
                continue
            user.is_active = True
            await user.save()
            results.append({"user_id": user_id, "username": user.username, "success": True, "message": "啟用成功"})
            success_count += 1
        except DoesNotExist:
            results.append({"user_id": user_id, "success": False, "message": "使用者不存在"})
            failed_count += 1
        except Exception:
            results.append({"user_id": user_id, "success": False, "message": "系統錯誤，請稍後再試"})
            failed_count += 1

    return {"success": success_count, "failed": failed_count, "details": results}


@router.post(
    "/batch-deactivate",
    summary="批次停用帳號",
    description="批次停用多個使用者帳號（需 admin 角色）",
    dependencies=[Depends(require_permission(ModuleName.USERS, PermissionAction.EDIT))],
)
async def batch_deactivate_users(
    user_ids: List[int],
    current_user: UserInfoSchema = Depends(require_full_auth)
):

    results = []
    success_count = 0
    failed_count = 0

    for user_id in user_ids:
        try:
            user = await Users.get(id=user_id)
            if user.id == current_user.id:
                results.append({"user_id": user_id, "username": user.username, "success": False, "message": "不能停用自己的帳號"})
                failed_count += 1
                continue
            if current_user.role == "manager" and user.role == "admin":
                results.append({"user_id": user_id, "username": user.username, "success": False, "message": "無法操作管理員帳號"})
                failed_count += 1
                continue
            user.is_active = False
            await user.save()
            results.append({"user_id": user_id, "username": user.username, "success": True, "message": "停用成功"})
            success_count += 1
        except DoesNotExist:
            results.append({"user_id": user_id, "success": False, "message": "使用者不存在"})
            failed_count += 1
        except Exception:
            results.append({"user_id": user_id, "success": False, "message": "系統錯誤，請稍後再試"})
            failed_count += 1

    return {"success": success_count, "failed": failed_count, "details": results}


# ============================================================================
# 帳號驗證重啟（039-account-verification-profile）
# ============================================================================

@router.post(
    "/{user_id}/resend-verification",
    response_model=EmailVerificationResponse,
    summary="重寄驗證信",
    description="針對未啟用且 email 未驗證的帳號重新發送驗證信（admin 全部，manager 限同管理處）",
)
async def resend_verification(
    user_id: int,
    request: Request,
    current_user: UserInfoSchema = Depends(require_full_auth),
):
    if current_user.role not in ["admin", "manager"]:
        raise AppError(403, "無帳號管理權限")

    try:
        target = await Users.get(id=user_id)
    except DoesNotExist:
        raise AppError(404, f"使用者 ID {user_id} 不存在")

    if current_user.role == "manager":
        if current_user.office is None:
            raise AppError(403, "帳號尚未指派管理處，請聯繫系統管理員完成設定")
        if target.office_id is None:
            raise AppError(403, "此帳號尚無管理處歸屬，請由系統管理員處理")
        if target.office_id != current_user.office.id:
            raise AppError(403, "無法對其他管理處的帳號執行此操作")

    if target.is_active:
        raise AppError(409, "此帳號已啟用，無須重寄驗證信")
    if target.email_verified:
        raise AppError(409, "此帳號已完成 email 驗證")
    if not target.email:
        raise AppError(422, "此帳號未登記 email，無法寄送驗證信")

    # 節流查詢刻意不篩 status：撤銷動作只改 status、不改 created_at，
    # 節流基準才不會因為下方的撤銷動作而消失（見 research.md R2c）
    latest_token = await AuthToken.filter(
        user_id=target.id,
        token_type=AuthTokenType.EMAIL_VERIFICATION,
    ).order_by("-created_at").first()
    if latest_token is not None:
        elapsed_seconds = (datetime.now(timezone.utc) - latest_token.created_at).total_seconds()
        if elapsed_seconds < RESEND_VERIFICATION_COOLDOWN_SECONDS:
            retry_after = int(RESEND_VERIFICATION_COOLDOWN_SECONDS - elapsed_seconds)
            raise HTTPException(
                status_code=429,
                detail={"message": "請稍候再重新發送", "retry_after_seconds": retry_after},
            )

    # 撤銷既有 PENDING token，確保使用者只有最新一封信可用（見 research.md R2b）
    await AuthToken.filter(
        user_id=target.id,
        token_type=AuthTokenType.EMAIL_VERIFICATION,
        status=AuthTokenStatus.PENDING,
    ).update(status=AuthTokenStatus.REVOKED)

    email_service = EmailService()
    sent = await email_service.send_verification_email(
        user=target,
        ip_address=request.headers.get("X-Real-IP", ""),
        user_agent=request.headers.get("user-agent", ""),
    )
    if not sent:
        raise AppError(500, "驗證信發送失敗，請稍後再試")

    await audit_service.log(
        event_type=AuditEventType.ACCOUNT,
        action=AuditAction.CREATE,
        result=AuditResult.SUCCESS,
        actor_id=current_user.id,
        actor_username=current_user.username,
        actor_role=current_user.role,
        resource_type="user",
        resource_id=str(target.id),
        ip_address=request.headers.get("X-Real-IP", ""),
        user_agent=request.headers.get("user-agent", ""),
        endpoint=str(request.url.path),
    )

    return EmailVerificationResponse(
        message="驗證信已重新發送",
        success=True,
        email=target.email,
    )


# ============================================================================
# 帳號審核 — 私有輔助函數
# ============================================================================

async def _check_manager_office_restriction(actor: UserInfoSchema, target_user_id: int) -> None:
    """若 actor 是 manager，強制驗證 target_user 與 actor 同管理處"""
    if actor.role != "manager":
        return
    target_user = await Users.get(id=target_user_id)
    actor_office_id = actor.office.id if actor.office else None
    if target_user.office_id != actor_office_id:
        raise AppError(403, "無法審核其他管理處的帳號申請")


async def _execute_approval(user_id: int, actor: UserInfoSchema) -> UserRegistration:
    """在 transaction 內核准帳號申請（select_for_update 防 race condition）"""
    async with in_transaction():
        registration = await UserRegistration.select_for_update().filter(
            user_id=user_id, status=RegistrationStatus.PENDING
        ).get_or_none()
        if not registration:
            raise AppError(409, "申請不存在或已審核")
        await _check_manager_office_restriction(actor, user_id)
        registration.status = RegistrationStatus.APPROVED
        registration.reviewed_by_id = actor.id
        registration.reviewed_at = datetime.now(timezone.utc)
        await registration.save()
        await Users.filter(id=user_id).update(is_active=True)
    return registration


async def _execute_rejection(user_id: int, actor: UserInfoSchema, reason: str) -> UserRegistration:
    """在 transaction 內駁回帳號申請（select_for_update 防 race condition）"""
    async with in_transaction():
        registration = await UserRegistration.select_for_update().filter(
            user_id=user_id, status=RegistrationStatus.PENDING
        ).get_or_none()
        if not registration:
            raise AppError(409, "申請不存在或已審核")
        await _check_manager_office_restriction(actor, user_id)
        registration.status = RegistrationStatus.REJECTED
        registration.reviewed_by_id = actor.id
        registration.reviewed_at = datetime.now(timezone.utc)
        registration.review_comment = reason
        await registration.save()
    return registration


# ============================================================================
# 帳號審核 — 路由端點
# ============================================================================

@router.post(
    "/{user_id}/approve",
    summary="審核通過帳號",
    description="核准帳號申請並啟用帳號（admin 全部，manager 限同管理處）",
    dependencies=[Depends(require_permission(ModuleName.USERS, PermissionAction.APPROVE))],
)
async def approve_user(
    user_id: int,
    request: Request,
    current_user: UserInfoSchema = Depends(require_full_auth)
):

    try:
        user = await Users.get(id=user_id)
    except DoesNotExist:
        raise AppError(404, "使用者不存在")

    registration = await _execute_approval(user_id, current_user)

    # 核准（is_active=True）已在 _execute_approval() 的 transaction 內 commit；以下兩封信
    # 的寄送各自獨立處理失敗，不得因信件寄送問題讓已完成的核准結果對外顯示 500
    # （039-account-verification-profile 一併修正既存問題，見 research.md R11）
    login_url = f"{EmailConfig.FRONTEND_URL}/login"
    email_svc = EmailService()

    try:
        approval_notification_sent = await email_svc.send_approval_notification(
            user.email, user.username, login_url
        )
    except Exception as e:
        approval_notification_sent = False
        logger.error(
            "核准通知信寄送失敗 user_id=%s username=%s error=%s",
            user_id, user.username, str(e),
        )
    if not approval_notification_sent:
        logger.error(
            "核准通知信寄送未成功 user_id=%s username=%s", user_id, user.username,
        )

    password_setup_email_sent = True
    if user.password is None:
        try:
            password_setup_email_sent = await email_svc.send_password_reset_email(user=user)
        except Exception as e:
            password_setup_email_sent = False
            logger.error(
                "密碼設定信寄送失敗 user_id=%s username=%s error=%s",
                user_id, user.username, str(e),
            )

    await audit_service.log(
        event_type=AuditEventType.REGISTRATION,
        action=AuditAction.APPROVE,
        result=AuditResult.SUCCESS,
        actor_id=current_user.id,
        actor_username=current_user.username,
        actor_role=current_user.role,
        ip_address=request.headers.get("X-Real-IP", ""),
        endpoint=str(request.url.path),
        resource_type="user_registration",
        resource_id=str(registration.id),
        changed_fields={
            "status": {"before": "pending", "after": "approved"},
            "approval_notification_sent": approval_notification_sent,
            "password_setup_email_sent": password_setup_email_sent,
        }
    )

    return {
        "success": True,
        "message": f"帳號 {user.username} 已核准",
        "user_id": user.id,
        "username": user.username,
        "approval_notification_sent": approval_notification_sent,
        "password_setup_email_sent": password_setup_email_sent,
    }


@router.post(
    "/{user_id}/reject",
    summary="駁回帳號申請",
    description="駁回帳號申請（admin 全部，manager 限同管理處），需提供駁回原因",
    dependencies=[Depends(require_permission(ModuleName.USERS, PermissionAction.APPROVE))],
)
async def reject_user(
    user_id: int,
    request: Request,
    body: RejectUserRequest,
    current_user: UserInfoSchema = Depends(require_full_auth)
):

    try:
        user = await Users.get(id=user_id)
    except DoesNotExist:
        raise AppError(404, "使用者不存在")

    registration = await _execute_rejection(user_id, current_user, body.reason)

    email_svc = EmailService()
    await email_svc.send_rejection_notification(user.email, user.username, body.reason)

    await audit_service.log(
        event_type=AuditEventType.REGISTRATION,
        action=AuditAction.REJECT,
        result=AuditResult.SUCCESS,
        actor_id=current_user.id,
        actor_username=current_user.username,
        actor_role=current_user.role,
        ip_address=request.headers.get("X-Real-IP", ""),
        endpoint=str(request.url.path),
        resource_type="user_registration",
        resource_id=str(registration.id),
        changed_fields={"status": {"before": "pending", "after": "rejected"}}
    )

    return {
        "success": True,
        "message": f"帳號 {user.username} 申請已駁回",
        "user_id": user.id,
        "username": user.username
    }


# ============================================================================
# 管理處/工作站變更（039-account-verification-profile）
# ============================================================================

@router.patch(
    "/{user_id}/assignment",
    summary="變更帳號所屬管理處與工作站",
    description="admin 可變更任一帳號的管理處與工作站；manager 僅能變更自己管理處內帳號的工作站",
)
async def update_account_assignment(
    user_id: int,
    payload: AccountAssignmentUpdateRequest,
    current_user: UserInfoSchema = Depends(require_full_auth),
):
    if current_user.role not in ["admin", "manager"]:
        raise AppError(403, "無帳號管理權限")

    if payload.office_id is None and payload.station is None:
        raise AppError(422, "office_id 與 station 至少須提供一個")

    try:
        target = await Users.get(id=user_id)
    except DoesNotExist:
        raise AppError(404, f"使用者 ID {user_id} 不存在")

    if current_user.role == "manager":
        if payload.office_id is not None:
            raise AppError(403, "manager 不可變更帳號的管理處歸屬")
        if current_user.office is None:
            raise AppError(403, "帳號尚未指派管理處，請聯繫系統管理員完成設定")
        if target.office_id != current_user.office.id:
            raise AppError(403, "無法變更其他管理處的帳號")

    before_office_id = target.office_id
    before_department = target.department

    if payload.office_id is not None:
        target.office_id = payload.office_id

    if payload.station is not None:
        # department 為既有結構化格式時僅更新 station 子鍵；若為 legacy_text 舊格式（無 station
        # 子鍵），直接覆寫為結構化格式，不保留 legacy_text 內容，不產生混合格式（見 research.md R12）
        current_department = target.department if isinstance(target.department, dict) else {}
        if "station" in current_department or "branch" in current_department:
            new_department = dict(current_department)
            new_department["station"] = payload.station
        else:
            # 只放有值的鍵，不放空的 branch：既有寫入端（signup.vue::buildDepartmentPayload）
            # 與 DB 現況（94 筆僅有 station 鍵、無任何一筆為 branch:{}）都是這個慣例，
            # 寫入 {"branch": {}} 會產生全表唯一的第四種形態
            new_department = {"station": payload.station}
        target.department = new_department

    await target.save()

    await audit_service.log(
        event_type=AuditEventType.ACCOUNT,
        action=AuditAction.UPDATE,
        result=AuditResult.SUCCESS,
        actor_id=current_user.id,
        actor_username=current_user.username,
        actor_role=current_user.role,
        resource_type="user",
        resource_id=str(target.id),
        endpoint=str(f"/user-management/{user_id}/assignment"),
        changed_fields={
            "office_id": {"before": before_office_id, "after": target.office_id},
            "department": {"before": before_department, "after": target.department},
        },
    )

    return {
        "user_id": target.id,
        "username": target.username,
        "office_id": target.office_id,
        "department": target.department,
    }
