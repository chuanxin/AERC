"""
權限管理 API 端點

提供權限檢查與查詢功能：
- 權限檢查
- 當前使用者權限摘要
- 權限範本管理（未來擴展）

Created: 2025-12-08
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.jwthandler import get_current_user
from src.database.models import Users
from src.schemas.permissions import (
    PermissionCheckRequest,
    PermissionCheckResponse,
    ModuleName,
    PermissionAction,
    UserPermissionsSchema
)
from src.services.permission_service import permission_service


router = APIRouter()


# ============================================================================
# 權限檢查
# ============================================================================

@router.post(
    "/check",
    response_model=PermissionCheckResponse,
    summary="檢查使用者權限",
    description="檢查當前使用者是否有執行特定操作的權限"
)
async def check_permission(
    request: PermissionCheckRequest,
    current_user: Users = Depends(get_current_user)
):
    """
    檢查使用者權限

    Args:
        request: 權限檢查請求
            - module: 模組名稱
            - action: 操作類型
            - resource_id: 資源 ID（可選）
            - office_id: 管理處 ID（可選）

    Returns:
        {
            "allowed": bool,
            "reason": Optional[str]
        }
    """
    # 解析使用者權限
    user_permissions = None
    if current_user.permissions:
        try:
            user_permissions = UserPermissionsSchema(**current_user.permissions)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"權限設定格式錯誤: {str(e)}"
            )

    # 執行權限檢查
    allowed, reason = permission_service.check_permission(
        user_role=current_user.role or "一般使用者",
        user_permissions=user_permissions,
        module=request.module,
        action=request.action,
        user_office_id=current_user.office_id,
        resource_office_id=request.office_id,
        resource_creator_id=None,  # TODO: 需要從 resource_id 查詢
        user_id=current_user.id
    )

    return PermissionCheckResponse(
        allowed=allowed,
        reason=reason
    )


@router.get(
    "/summary",
    summary="取得當前使用者權限摘要",
    description="取得當前使用者的完整權限摘要（用於前端顯示）"
)
async def get_permissions_summary(
    current_user: Users = Depends(get_current_user)
):
    """
    取得當前使用者權限摘要

    Returns:
        {
            "user_id": int,
            "username": str,
            "role": str,
            "permissions": {
                "mode": "default" | "scoped" | "custom",
                "modules": {
                    "grants": ["view", "create", ...],
                    "users": [...],
                    ...
                }
            },
            "scope": {...} (如果是 scoped mode)
        }
    """
    # 解析使用者權限
    user_permissions = None
    if current_user.permissions:
        try:
            user_permissions = UserPermissionsSchema(**current_user.permissions)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"權限設定格式錯誤: {str(e)}"
            )

    # 取得權限摘要
    summary = permission_service.get_user_permissions_summary(
        user_role=current_user.role or "一般使用者",
        user_permissions=user_permissions
    )

    # 組合回應
    response = {
        "user_id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
        "permissions": summary
    }

    # 如果是 scoped mode，額外返回 scope 資訊
    if user_permissions and user_permissions.scope:
        response["scope"] = user_permissions.scope.model_dump(exclude_none=True)

    return response


# ============================================================================
# 權限範本（未來擴展）
# ============================================================================

# TODO: 實作權限範本功能
# - GET /templates - 列出所有權限範本
# - POST /templates - 建立新範本
# - PATCH /templates/{id} - 更新範本
# - DELETE /templates/{id} - 刪除範本
# - POST /templates/{id}/apply - 將範本套用到使用者
