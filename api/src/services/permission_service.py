"""
權限檢查服務

提供統一的權限檢查邏輯，支援三種權限模式：
1. default: 基於角色的預設權限
2. scoped: 角色 + 動態範圍限制
3. custom: 完全自訂權限

Created: 2025-12-08
"""

from typing import Optional, List, Set
from src.schemas.permissions import (
    PermissionMode,
    PermissionAction,
    ModuleName,
    UserPermissionsSchema
)


class PermissionService:
    """權限檢查服務"""

    # 角色權限矩陣為代碼層 SSOT（非資料庫），變更需部署；個別使用者覆蓋儲存於 users.permissions (JSONB)
    DEFAULT_ROLE_PERMISSIONS = {
        "admin": {
            ModuleName.GRANTS: {PermissionAction.VIEW, PermissionAction.CREATE, PermissionAction.EDIT, PermissionAction.DELETE, PermissionAction.APPROVE, PermissionAction.EXPORT, PermissionAction.VIEW_ALL},
            ModuleName.USERS: {PermissionAction.VIEW, PermissionAction.CREATE, PermissionAction.EDIT, PermissionAction.DELETE, PermissionAction.APPROVE, PermissionAction.VIEW_ALL},
            ModuleName.REPORTS: {PermissionAction.VIEW, PermissionAction.EXPORT, PermissionAction.VIEW_ALL},
            ModuleName.GIS: {PermissionAction.VIEW, PermissionAction.EDIT},
            ModuleName.OFFICES: {PermissionAction.VIEW, PermissionAction.CREATE, PermissionAction.EDIT, PermissionAction.DELETE},
            ModuleName.SETTINGS: {PermissionAction.VIEW, PermissionAction.EDIT},
            ModuleName.BATCH_PRINT: {PermissionAction.VIEW},
            ModuleName.DUPLICATE_CHECK: {PermissionAction.VIEW},
            ModuleName.MATERIALS: {PermissionAction.VIEW, PermissionAction.CREATE, PermissionAction.EDIT, PermissionAction.DELETE},
            ModuleName.DOWNLOADS: {PermissionAction.VIEW},
            # 032 新增：僅 admin 可管理 IP 白名單與查詢待驗證 OTP
            ModuleName.SECURITY: {PermissionAction.VIEW, PermissionAction.CREATE, PermissionAction.EDIT},
        },
        "manager": {
            # manager.GRANTS: VIEW + CREATE + EDIT + APPROVE + EXPORT（本辦管理者可建立及編輯本辦案件）
            ModuleName.GRANTS: {PermissionAction.VIEW, PermissionAction.CREATE, PermissionAction.EDIT, PermissionAction.APPROVE, PermissionAction.EXPORT},
            ModuleName.USERS: {PermissionAction.VIEW, PermissionAction.APPROVE, PermissionAction.EDIT},
            ModuleName.REPORTS: {PermissionAction.VIEW, PermissionAction.EXPORT},
            ModuleName.GIS: {PermissionAction.VIEW, PermissionAction.EDIT},
            ModuleName.OFFICES: {PermissionAction.VIEW},
            ModuleName.SETTINGS: {PermissionAction.VIEW},
            ModuleName.BATCH_PRINT: {PermissionAction.VIEW},
            ModuleName.DUPLICATE_CHECK: {PermissionAction.VIEW},
            ModuleName.MATERIALS: {PermissionAction.VIEW},
            ModuleName.DOWNLOADS: {PermissionAction.VIEW},
            ModuleName.SECURITY: set(),
        },
        "staff": {
            # staff 權限與 manager 對齊，唯一差異：USERS 模組無權限
            ModuleName.GRANTS: {PermissionAction.VIEW, PermissionAction.CREATE, PermissionAction.EDIT, PermissionAction.APPROVE, PermissionAction.EXPORT},
            ModuleName.USERS: set(),
            ModuleName.REPORTS: {PermissionAction.VIEW, PermissionAction.EXPORT},
            ModuleName.GIS: {PermissionAction.VIEW, PermissionAction.EDIT},
            ModuleName.OFFICES: {PermissionAction.VIEW},
            ModuleName.SETTINGS: {PermissionAction.VIEW},
            ModuleName.BATCH_PRINT: {PermissionAction.VIEW},
            ModuleName.DUPLICATE_CHECK: {PermissionAction.VIEW},
            ModuleName.MATERIALS: {PermissionAction.VIEW},
            ModuleName.DOWNLOADS: {PermissionAction.VIEW},
            ModuleName.SECURITY: set(),
        },
        "user": {
            # user.GRANTS: VIEW + CREATE + EDIT + APPROVE
            # APPROVE 用於現場勘查步驟的狀態更新（approved/rejected）
            ModuleName.GRANTS: {PermissionAction.VIEW, PermissionAction.CREATE, PermissionAction.EDIT, PermissionAction.APPROVE},
            ModuleName.USERS: set(),
            # user.REPORTS: 空集合（033 需求：user 無統計報表存取權）
            ModuleName.REPORTS: set(),
            ModuleName.GIS: {PermissionAction.VIEW},
            ModuleName.OFFICES: {PermissionAction.VIEW},
            ModuleName.SETTINGS: set(),
            ModuleName.BATCH_PRINT: set(),
            ModuleName.DUPLICATE_CHECK: {PermissionAction.VIEW},
            ModuleName.MATERIALS: {PermissionAction.VIEW},
            ModuleName.DOWNLOADS: {PermissionAction.VIEW},
            ModuleName.SECURITY: set(),
        },
    }

    @staticmethod
    def check_permission(
        user_role: str,
        user_permissions: Optional[UserPermissionsSchema],
        module: ModuleName,
        action: PermissionAction,
        user_office_id: Optional[int] = None,
        resource_office_id: Optional[int] = None,
        resource_creator_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        檢查使用者是否有權限執行特定操作

        Args:
            user_role: 使用者角色
            user_permissions: 使用者權限設定（可為 None，表示使用預設）
            module: 模組名稱
            action: 操作類型
            user_office_id: 使用者所屬管理處 ID
            resource_office_id: 資源所屬管理處 ID（檢查範圍權限時使用）
            resource_creator_id: 資源建立者 ID（檢查 own_only 時使用）
            user_id: 當前使用者 ID（檢查 own_only 時使用）

        Returns:
            (是否允許, 拒絕原因)
        """
        # 如果沒有權限設定，使用 default mode
        if user_permissions is None:
            user_permissions = UserPermissionsSchema(mode=PermissionMode.DEFAULT)

        mode = user_permissions.mode or PermissionMode.DEFAULT

        # 1. Default Mode: 基於角色的預設權限
        if mode == PermissionMode.DEFAULT:
            return PermissionService._check_default_permission(user_role, module, action)

        # 2. Scoped Mode: 角色 + 動態範圍限制
        elif mode == PermissionMode.SCOPED:
            # 先檢查基礎權限
            allowed, reason = PermissionService._check_default_permission(user_role, module, action)
            if not allowed:
                return False, reason

            # 再檢查範圍限制
            if user_permissions.scope:
                return PermissionService._check_scope_permission(
                    user_permissions.scope,
                    user_office_id,
                    resource_office_id,
                    resource_creator_id,
                    user_id
                )
            return True, None

        # 3. Custom Mode: 完全自訂權限
        elif mode == PermissionMode.CUSTOM:
            return PermissionService._check_custom_permission(
                user_permissions.custom,
                module,
                action
            )

        return False, "未知的權限模式"

    @staticmethod
    def _check_default_permission(
        user_role: str,
        module: ModuleName,
        action: PermissionAction
    ) -> tuple[bool, Optional[str]]:
        """檢查預設角色權限"""
        # 取得角色的權限矩陣
        role_permissions = PermissionService.DEFAULT_ROLE_PERMISSIONS.get(user_role)
        if not role_permissions:
            return False, f"未定義的角色: {user_role}"

        # 取得該模組的允許操作
        module_actions = role_permissions.get(module, set())

        if action in module_actions:
            return True, None
        else:
            return False, f"角色 '{user_role}' 無 '{module.value}' 模組的 '{action.value}' 權限"

    @staticmethod
    def _check_scope_permission(
        scope,
        user_office_id: Optional[int],
        resource_office_id: Optional[int],
        resource_creator_id: Optional[int],
        user_id: Optional[int]
    ) -> tuple[bool, Optional[str]]:
        """檢查範圍權限"""
        # 檢查 office_ids 限制
        if scope.office_ids is not None:
            if resource_office_id is None:
                return False, "無法確認資源所屬管理處"

            if resource_office_id not in scope.office_ids:
                return False, f"無權存取該管理處資料（允許範圍: {scope.office_ids}）"

        # 檢查 own_only 限制
        if scope.own_only:
            if resource_creator_id is None or user_id is None:
                return False, "無法確認資源所有權"

            if resource_creator_id != user_id:
                return False, "僅能存取自己建立的資料"

        # TODO: 實作 department_filter 檢查（需要資源的部門資訊）
        # if scope.department_filter:
        #     ...

        return True, None

    @staticmethod
    def _check_custom_permission(
        custom,
        module: ModuleName,
        action: PermissionAction
    ) -> tuple[bool, Optional[str]]:
        """檢查自訂權限
        # TD-013: 新增 ModuleName 時此函數需同步新增 elif 分支
        """
        if custom is None:
            return False, "自訂權限未設定"

        # 取得該模組的自訂權限列表
        module_permissions = None
        if module == ModuleName.GRANTS:
            module_permissions = custom.grants
        elif module == ModuleName.USERS:
            module_permissions = custom.users
        elif module == ModuleName.REPORTS:
            module_permissions = custom.reports
        elif module == ModuleName.GIS:
            module_permissions = custom.gis
        elif module == ModuleName.OFFICES:
            module_permissions = custom.offices
        elif module == ModuleName.SETTINGS:
            module_permissions = custom.settings
        elif module == ModuleName.BATCH_PRINT:
            module_permissions = custom.batch_print
        elif module == ModuleName.DUPLICATE_CHECK:
            module_permissions = custom.duplicate_check
        elif module == ModuleName.MATERIALS:
            module_permissions = custom.materials
        elif module == ModuleName.DOWNLOADS:
            module_permissions = custom.downloads
        elif module == ModuleName.SECURITY:
            module_permissions = custom.security

        if module_permissions is None:
            return False, f"模組 '{module.value}' 無自訂權限"

        if action in module_permissions:
            return True, None
        else:
            return False, f"自訂權限中無 '{module.value}' 模組的 '{action.value}' 權限"

    @staticmethod
    def get_user_permissions_summary(
        user_role: str,
        user_permissions: Optional[UserPermissionsSchema]
    ) -> dict:
        """
        取得使用者權限摘要（用於前端顯示）

        Returns:
            {
                "mode": "default" | "scoped" | "custom",
                "modules": {
                    "grants": ["view", "create", ...],
                    "users": [...],
                    ...
                }
            }
        """
        if user_permissions is None:
            user_permissions = UserPermissionsSchema(mode=PermissionMode.DEFAULT)

        mode = user_permissions.mode or PermissionMode.DEFAULT

        if mode == PermissionMode.DEFAULT or mode == PermissionMode.SCOPED:
            # 使用角色預設權限
            role_permissions = PermissionService.DEFAULT_ROLE_PERMISSIONS.get(user_role, {})
            modules = {
                module.value: [action.value for action in actions]
                for module, actions in role_permissions.items()
            }
        elif mode == PermissionMode.CUSTOM:
            # 使用自訂權限
            if user_permissions.custom is None:
                modules = {}
            else:
                # TD-013: 新增 ModuleName 時此 dict 需同步新增鍵
                modules = {
                    "grants": [a.value for a in user_permissions.custom.grants] if user_permissions.custom.grants else [],
                    "users": [a.value for a in user_permissions.custom.users] if user_permissions.custom.users else [],
                    "reports": [a.value for a in user_permissions.custom.reports] if user_permissions.custom.reports else [],
                    "gis": [a.value for a in user_permissions.custom.gis] if user_permissions.custom.gis else [],
                    "offices": [a.value for a in user_permissions.custom.offices] if user_permissions.custom.offices else [],
                    "settings": [a.value for a in user_permissions.custom.settings] if user_permissions.custom.settings else [],
                    "batch_print": [a.value for a in user_permissions.custom.batch_print] if user_permissions.custom.batch_print else [],
                    "duplicate_check": [a.value for a in user_permissions.custom.duplicate_check] if user_permissions.custom.duplicate_check else [],
                    "materials": [a.value for a in user_permissions.custom.materials] if user_permissions.custom.materials else [],
                    "downloads": [a.value for a in user_permissions.custom.downloads] if user_permissions.custom.downloads else [],
                    "security": [a.value for a in user_permissions.custom.security] if user_permissions.custom.security else [],
                }
        else:
            modules = {}

        return {
            "mode": mode.value if mode else "default",
            "modules": modules
        }

    @staticmethod
    def validate_permissions_structure(permissions: UserPermissionsSchema) -> tuple[bool, Optional[str]]:
        """
        驗證權限結構是否合法

        Returns:
            (是否合法, 錯誤訊息)
        """
        mode = permissions.mode or PermissionMode.DEFAULT

        # Scoped mode 必須有 scope
        if mode == PermissionMode.SCOPED:
            if permissions.scope is None:
                return False, "scoped mode 必須提供 scope 設定"

        # Custom mode 必須有 custom
        if mode == PermissionMode.CUSTOM:
            if permissions.custom is None:
                return False, "custom mode 必須提供 custom 設定"

            # 至少要有一個模組有權限
            has_permission = any([
                permissions.custom.grants,
                permissions.custom.users,
                permissions.custom.reports,
                permissions.custom.gis,
                permissions.custom.offices,
                permissions.custom.settings,
            ])

            if not has_permission:
                return False, "custom mode 至少要設定一個模組的權限"

        return True, None


# 全域實例
permission_service = PermissionService()
