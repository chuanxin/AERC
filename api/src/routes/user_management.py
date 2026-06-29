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

from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request, Query, status
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import in_transaction

from src.auth.guard import require_full_auth
from src.database.audit_models import AuditAction, AuditEventType, AuditResult
from src.database.models import UserRegistration, RegistrationStatus, Users
from src.exceptions import AppError
from src.services.data_encryption import data_encryption_service
from src.schemas.permissions import (
    UpdateUserPermissionsRequest,
    UserPermissionsResponse,
    UserPermissionsSchema
)
from src.schemas.users import RejectUserRequest, UserInfoSchema
from src.services.audit_service import audit_service
from src.services.email_service import EmailConfig, EmailService
from src.services.permission_service import permission_service


router = APIRouter()


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
    current_user: Users = Depends(require_full_auth)
):
    """取得使用者列表（分頁）"""
    if current_user.role not in ["admin", "manager"]:
        raise AppError(403, "無帳號管理權限")

    query = Users.all().prefetch_related('office')

    if is_active is not None:
        query = query.filter(is_active=is_active)
    if role:
        query = query.filter(role=role)
    if office_id:
        query = query.filter(office_id=office_id)
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
    description="列出所有待審核的帳號申請（admin 全部，manager 限同辦公室）"
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
    description="更新指定使用者的權限設定（需 admin 角色）"
)
async def update_user_permissions(
    user_id: int,
    request: UpdateUserPermissionsRequest,
    current_user: Users = Depends(require_full_auth)
):
    """更新使用者權限（admin 限定）"""
    if current_user.role != "admin":
        raise AppError(403, "僅系統管理員可修改使用者權限")

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


# ============================================================================
# 批次操作
# ============================================================================

@router.post(
    "/batch-activate",
    summary="批次啟用帳號",
    description="批次啟用多個使用者帳號（需 admin 角色）"
)
async def batch_activate_users(
    user_ids: List[int],
    current_user: Users = Depends(require_full_auth)
):
    """批次啟用帳號（admin 限定）"""
    if current_user.role != "admin":
        raise AppError(403, "僅系統管理員可批次啟用帳號")

    results = []
    success_count = 0
    failed_count = 0

    for user_id in user_ids:
        try:
            user = await Users.get(id=user_id)
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
    description="批次停用多個使用者帳號（需 admin 角色）"
)
async def batch_deactivate_users(
    user_ids: List[int],
    current_user: Users = Depends(require_full_auth)
):
    """批次停用帳號（admin 限定）"""
    if current_user.role != "admin":
        raise AppError(403, "僅系統管理員可批次停用帳號")

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
# 帳號審核 — 私有輔助函數
# ============================================================================

async def _check_manager_office_restriction(actor: UserInfoSchema, target_user_id: int) -> None:
    """若 actor 是 manager，強制驗證 target_user 與 actor 同辦公室"""
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
    description="核准帳號申請並啟用帳號（admin 全部，manager 限同辦公室）"
)
async def approve_user(
    user_id: int,
    request: Request,
    current_user: Users = Depends(require_full_auth)
):
    """核准帳號申請"""
    if current_user.role not in ["admin", "manager"]:
        raise AppError(403, "無審核帳號權限")

    try:
        user = await Users.get(id=user_id)
    except DoesNotExist:
        raise AppError(404, "使用者不存在")

    registration = await _execute_approval(user_id, current_user)

    login_url = f"{EmailConfig.FRONTEND_URL}/login"
    email_svc = EmailService()
    await email_svc.send_approval_notification(user.email, user.username, login_url)

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
        changed_fields={"status": {"before": "pending", "after": "approved"}}
    )

    return {
        "success": True,
        "message": f"帳號 {user.username} 已核准",
        "user_id": user.id,
        "username": user.username
    }


@router.post(
    "/{user_id}/reject",
    summary="駁回帳號申請",
    description="駁回帳號申請（admin 全部，manager 限同辦公室），需提供駁回原因"
)
async def reject_user(
    user_id: int,
    request: Request,
    body: RejectUserRequest,
    current_user: Users = Depends(require_full_auth)
):
    """駁回帳號申請"""
    if current_user.role not in ["admin", "manager"]:
        raise AppError(403, "無審核帳號權限")

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
