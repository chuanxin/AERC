"""
使用者帳號管理 API 端點

提供帳號管理功能：
- 使用者列表查詢（支援篩選、分頁、搜尋）
- 使用者詳細資訊
- 批次啟用/停用帳號
- 帳號審核功能

Created: 2025-12-08
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from tortoise.exceptions import DoesNotExist

from src.auth.guard import require_full_auth
from src.database.models import Users
from src.schemas.users import UserInfoSchema
from src.schemas.permissions import (
    UpdateUserPermissionsRequest,
    UserPermissionsResponse,
    UserPermissionsSchema
)
from src.services.permission_service import permission_service
from datetime import datetime, timezone


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
    page: int = Query(1, ge=1, description="頁碼"),
    page_size: int = Query(20, ge=1, le=100, description="每頁筆數"),
    is_active: Optional[bool] = Query(None, description="帳號狀態篩選"),
    role: Optional[str] = Query(None, description="角色篩選"),
    office_id: Optional[int] = Query(None, description="管理處 ID 篩選"),
    search: Optional[str] = Query(None, description="搜尋關鍵字（帳號、姓名、Email）"),
    current_user: Users = Depends(require_full_auth)
):
    """
    取得使用者列表（分頁）

    Args:
        page: 頁碼（從 1 開始）
        page_size: 每頁筆數
        is_active: 帳號狀態篩選
        role: 角色篩選
        office_id: 管理處篩選
        search: 搜尋關鍵字

    Returns:
        {
            "total": 總筆數,
            "page": 當前頁碼,
            "page_size": 每頁筆數,
            "total_pages": 總頁數,
            "users": [使用者列表]
        }
    """
    # 建立查詢
    query = Users.all().prefetch_related('office')

    # 篩選條件
    if is_active is not None:
        query = query.filter(is_active=is_active)

    if role:
        query = query.filter(role=role)

    if office_id:
        query = query.filter(office_id=office_id)

    # 搜尋關鍵字
    if search:
        from tortoise.expressions import Q
        query = query.filter(
            Q(username__icontains=search) |
            Q(full_name__icontains=search) |
            Q(email__icontains=search)
        )

    # 計算總數
    total = await query.count()

    # 分頁
    offset = (page - 1) * page_size
    users = await query.offset(offset).limit(page_size).all()

    # 轉換為 Schema
    users_data = [
        {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
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

    total_pages = (total + page_size - 1) // page_size

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "users": users_data
    }


@router.get(
    "/{user_id}",
    response_model=UserInfoSchema,
    summary="取得單一使用者詳細資訊",
    description="根據使用者 ID 取得詳細資訊"
)
async def get_user(
    user_id: int,
    current_user: Users = Depends(require_full_auth)
):
    """取得單一使用者詳細資訊"""
    try:
        user = await Users.get(id=user_id).prefetch_related('office')
        return UserInfoSchema.model_validate(user)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"使用者 ID {user_id} 不存在"
        )


# ============================================================================
# 權限管理
# ============================================================================

@router.patch(
    "/{user_id}/permissions",
    response_model=UserPermissionsResponse,
    summary="更新使用者權限",
    description="更新指定使用者的權限設定"
)
async def update_user_permissions(
    user_id: int,
    request: UpdateUserPermissionsRequest,
    current_user: Users = Depends(require_full_auth)
):
    """
    更新使用者權限

    需要系統管理員權限
    """
    # TODO: 檢查當前使用者是否有權限管理其他使用者權限
    # if current_user.role != "系統管理員":
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="僅系統管理員可修改使用者權限"
    #     )

    # 驗證權限結構
    valid, error_msg = permission_service.validate_permissions_structure(request.permissions)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"權限設定不合法: {error_msg}"
        )

    try:
        user = await Users.get(id=user_id)

        # 更新權限
        user.permissions = request.permissions.model_dump(exclude_none=True)
        await user.save()

        # TODO: 記錄審計日誌
        # await AuditLog.create(
        #     user_id=current_user.id,
        #     action="update_permissions",
        #     target_user_id=user_id,
        #     reason=request.reason,
        #     old_value=...,
        #     new_value=user.permissions
        # )

        return UserPermissionsResponse(
            user_id=user.id,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            permissions=UserPermissionsSchema(**user.permissions) if user.permissions else None,
            updated_at=datetime.now(timezone.utc).isoformat()
        )
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"使用者 ID {user_id} 不存在"
        )


# ============================================================================
# 批次操作
# ============================================================================

@router.post(
    "/batch-activate",
    summary="批次啟用帳號",
    description="批次啟用多個使用者帳號"
)
async def batch_activate_users(
    user_ids: List[int],
    current_user: Users = Depends(require_full_auth)
):
    """
    批次啟用帳號

    Args:
        user_ids: 使用者 ID 列表

    Returns:
        {
            "success": 成功數量,
            "failed": 失敗數量,
            "details": [詳細結果]
        }
    """
    # TODO: 檢查權限
    # if current_user.role != "系統管理員":
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="僅系統管理員可批次啟用帳號"
    #     )

    results = []
    success_count = 0
    failed_count = 0

    for user_id in user_ids:
        try:
            user = await Users.get(id=user_id)
            user.is_active = True
            await user.save()

            results.append({
                "user_id": user_id,
                "username": user.username,
                "success": True,
                "message": "啟用成功"
            })
            success_count += 1
        except DoesNotExist:
            results.append({
                "user_id": user_id,
                "success": False,
                "message": "使用者不存在"
            })
            failed_count += 1
        except Exception as e:
            results.append({
                "user_id": user_id,
                "success": False,
                "message": str(e)
            })
            failed_count += 1

    return {
        "success": success_count,
        "failed": failed_count,
        "details": results
    }


@router.post(
    "/batch-deactivate",
    summary="批次停用帳號",
    description="批次停用多個使用者帳號"
)
async def batch_deactivate_users(
    user_ids: List[int],
    current_user: Users = Depends(require_full_auth)
):
    """
    批次停用帳號

    Args:
        user_ids: 使用者 ID 列表

    Returns:
        {
            "success": 成功數量,
            "failed": 失敗數量,
            "details": [詳細結果]
        }
    """
    # TODO: 檢查權限
    # if current_user.role != "系統管理員":
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="僅系統管理員可批次停用帳號"
    #     )

    results = []
    success_count = 0
    failed_count = 0

    for user_id in user_ids:
        try:
            user = await Users.get(id=user_id)

            # 不能停用自己的帳號
            if user.id == current_user.id:
                results.append({
                    "user_id": user_id,
                    "username": user.username,
                    "success": False,
                    "message": "不能停用自己的帳號"
                })
                failed_count += 1
                continue

            user.is_active = False
            await user.save()

            results.append({
                "user_id": user_id,
                "username": user.username,
                "success": True,
                "message": "停用成功"
            })
            success_count += 1
        except DoesNotExist:
            results.append({
                "user_id": user_id,
                "success": False,
                "message": "使用者不存在"
            })
            failed_count += 1
        except Exception as e:
            results.append({
                "user_id": user_id,
                "success": False,
                "message": str(e)
            })
            failed_count += 1

    return {
        "success": success_count,
        "failed": failed_count,
        "details": results
    }


# ============================================================================
# 帳號審核
# ============================================================================

@router.get(
    "/pending-approval",
    summary="取得待審核帳號列表",
    description="列出所有待審核的帳號申請（is_active=False + email_verified=True）"
)
async def get_pending_approval_users(
    page: int = Query(1, ge=1, description="頁碼"),
    page_size: int = Query(20, ge=1, le=100, description="每頁筆數"),
    current_user: Users = Depends(require_full_auth)
):
    """
    取得待審核帳號列表

    篩選條件：
    - is_active = False（尚未啟用）
    - email_verified = True（Email 已驗證）
    """
    # TODO: 檢查權限
    # if current_user.role not in ["系統管理員", "管理處主管"]:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="無審核帳號權限"
    #     )

    query = Users.filter(
        is_active=False,
        email_verified=True
    ).prefetch_related('office')

    # 計算總數
    total = await query.count()

    # 分頁
    offset = (page - 1) * page_size
    users = await query.offset(offset).limit(page_size).all()

    # 轉換為資料
    users_data = [
        {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "job_title": user.job_title,
            "phone": user.phone,
            "phone_ext": user.phone_ext,
            "mobile": user.mobile,
            "role": user.role,
            "office": {
                "id": user.office.id,
                "name": user.office.name,
                "short_name": user.office.short_name,
            } if user.office else None,
            "department": user.department,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
        for user in users
    ]

    total_pages = (total + page_size - 1) // page_size

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "users": users_data
    }


@router.post(
    "/{user_id}/approve",
    summary="審核通過帳號",
    description="審核通過帳號申請並啟用帳號"
)
async def approve_user(
    user_id: int,
    current_user: Users = Depends(require_full_auth)
):
    """
    審核通過帳號

    將 is_active 設為 True
    """
    # TODO: 檢查權限
    # if current_user.role not in ["系統管理員", "管理處主管"]:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="無審核帳號權限"
    #     )

    try:
        user = await Users.get(id=user_id)

        if user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="該帳號已啟用"
            )

        # 啟用帳號
        user.is_active = True
        await user.save()

        # TODO: 發送審核通過通知信
        # email_service = EmailService()
        # await email_service.send_approval_notification(user)

        # TODO: 記錄審計日誌
        # await AuditLog.create(
        #     user_id=current_user.id,
        #     action="approve_user",
        #     target_user_id=user_id
        # )

        return {
            "success": True,
            "message": f"帳號 {user.username} 審核通過",
            "user_id": user.id,
            "username": user.username
        }
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"使用者 ID {user_id} 不存在"
        )


@router.post(
    "/{user_id}/reject",
    summary="拒絕帳號申請",
    description="拒絕帳號申請並刪除該筆申請記錄"
)
async def reject_user(
    user_id: int,
    reason: Optional[str] = None,
    current_user: Users = Depends(require_full_auth)
):
    """
    拒絕帳號申請

    刪除該筆申請記錄
    """
    # TODO: 檢查權限
    # if current_user.role not in ["系統管理員", "管理處主管"]:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="無審核帳號權限"
    #     )

    try:
        user = await Users.get(id=user_id)

        if user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="無法拒絕已啟用的帳號"
            )

        username = user.username
        email = user.email

        # TODO: 發送拒絕通知信
        # email_service = EmailService()
        # await email_service.send_rejection_notification(user, reason)

        # TODO: 記錄審計日誌（在刪除前）
        # await AuditLog.create(
        #     user_id=current_user.id,
        #     action="reject_user",
        #     target_user_id=user_id,
        #     reason=reason
        # )

        # 刪除帳號
        await user.delete()

        return {
            "success": True,
            "message": f"帳號申請 {username} 已拒絕",
            "username": username,
            "email": email,
            "reason": reason
        }
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"使用者 ID {user_id} 不存在"
        )
