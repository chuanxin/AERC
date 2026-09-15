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
    CustomModulePermissionsSchema,
    PermissionMode,
    PermissionAction,
    ModuleName,
    UserPermissionsSchema
)


def _normalize_custom_actions(c) -> Optional[tuple]:
    """把 custom 各模組的動作清單壓成可比較的集合形狀。

    動作是集合，排列不帶訊息——同一組動作以不同排列提交，效果完全相同。

    必須容忍 JSONB 髒資料：`before` 側取自 users.permissions（JSONB），
    沒有任何東西在驗證它。直接 `frozenset(v)` 有三種踩法，皆實測：
      - v 為字串 → frozenset("view") 靜默拆成 {'v','i','e','w'}
      - v 為 int → TypeError
      - c 本身非 dict → .items() 拋 AttributeError
    後兩者會冒到全域 handler → 500。**防禦層若在它宣稱要防禦的輸入上崩潰，
    就失去存在意義**，故非預期型別一律轉為可辨識標記，不與任何合法值相等。

    勿寫 map(str, v)：`class PermissionAction(str, Enum)` 的成員在 Python
    3.12+ 起 str(member) 回傳 'PermissionAction.VIEW' 而非 'view'。不需要
    轉換——str-Enum 繼承 str 的 __hash__／__eq__，frozenset 比對本就相等。
    """
    if c is None:
        return None
    if not isinstance(c, dict):
        return ("<malformed-custom>", repr(c))
    out = []
    for key, value in c.items():
        if value is None:
            out.append((key, frozenset()))
        elif isinstance(value, (list, tuple)):
            out.append((key, frozenset(value)))
        else:
            out.append((key, ("<malformed-actions>", repr(value))))
    # 只以模組名排序，避免比較異質的第二元素
    return tuple(sorted(out, key=lambda kv: kv[0]))


def effective_permission_key(p: Optional[dict]) -> tuple:
    """把權限設定壓成「效果上等於什麼」的可比較形狀（041 FR-015～FR-015c）。

    None、{} 與 {"mode": "default"} 三者等價——現況 191 個帳號的
    permissions 全為 NULL，對其提交「沿用角色預設」是必經的第一次提交，
    逐字比較會把它記成一次變更，而有效權限根本沒變。

    只編碼**模式定義**，不編碼實作缺陷：
      - default 模式忽略 scope，因為 check_permission() 在該分支根本不
        呼叫 _check_scope_permission()——這是模式定義。
      - scoped 模式**比較整個 scope dict**，不因 department_filter 目前
        是未實作的 TODO 而挑欄位——那是實作缺陷。把缺陷編進等價判定，
        會在缺陷日後被修復時讓歷史稽核紀錄的語意靜默改變，且把「有人
        改了設定」記成「無變更」本身就是隱瞞。
      - 未定義的 mode 照實輸出，必然與任何合法設定不等 → 記為一次變更，
        這是正確的：那確實是一次從異常狀態到正常狀態的變更。
    """
    if p is None:
        p = {}
    elif not isinstance(p, dict):
        # JSONB 可存任意 JSON 值（字串／陣列／數字），而 users.permissions 的
        # 寫入端只有本端點（保證 dict）——非 dict 值必然是繞過本端點寫進來的。
        # 照實記錄且必然與任何合法設定不等（FR-015b 的延伸），不拋例外：
        # 這個函數是給稽核比較用的，在髒資料上崩潰會讓成功路徑變成 500。
        return ("<malformed-permissions>", repr(p), None)

    mode = p.get("mode") or PermissionMode.DEFAULT.value
    return (
        mode,
        p.get("scope") if mode == PermissionMode.SCOPED.value else None,
        _normalize_custom_actions(p.get("custom"))
        if mode == PermissionMode.CUSTOM.value else None,
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
            # 040 新增：僅 admin 可管理公告
            ModuleName.ANNOUNCEMENTS: {PermissionAction.VIEW, PermissionAction.CREATE, PermissionAction.EDIT, PermissionAction.DELETE},
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
            ModuleName.ANNOUNCEMENTS: set(),
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
            ModuleName.ANNOUNCEMENTS: set(),
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
            ModuleName.ANNOUNCEMENTS: set(),
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
        elif module == ModuleName.ANNOUNCEMENTS:
            module_permissions = custom.announcements

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
                    "announcements": [a.value for a in user_permissions.custom.announcements] if user_permissions.custom.announcements else [],
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
            #
            # TD-013 第六處（040 修正）：原為硬編碼的 6 個模組清單，
            # 導致只授予 security / materials / downloads / batch_print /
            # duplicate_check / announcements 任一者的合法設定會被回絕 400。
            # 改為對 schema 欄位迭代後，此同步點永久消失——新增 ModuleName
            # 時不需要再記得改這裡。此變更嚴格放寬：只會讓原本被誤拒的合法
            # 設定通過，不會讓任何原本能通過的變成不通過。
            has_permission = any(
                getattr(permissions.custom, field_name, None)
                for field_name in CustomModulePermissionsSchema.model_fields
            )

            if not has_permission:
                return False, "custom mode 至少要設定一個模組的權限"

        return True, None

    @staticmethod
    def validate_within_admin_ceiling(
        permissions: UserPermissionsSchema
    ) -> tuple[bool, list[str]]:
        """檢查授出的權限是否為 admin 角色預設權限的子集（041 FR-007～FR-010）。

        **這不是提權防線。** admin 可以合法地把自己擁有的全部操作授給任一
        低權限帳號，只要在上限內就通過——擋提權的是端點的角色判定。本函數
        防的是「授出一個系統從不檢查、因此永遠不生效的組合」：實測 12 個模組
        × 7 個動作 = 84 種組合中，admin 預設只涵蓋 38 種，11 個模組有缺口
        （例如 gis 無 delete、downloads 只有 view）。那些組合授出後既不報錯
        也不生效，設定者卻以為授權成功。這是**設定衛生**。

        只有 custom 模式需要檢查，且這是可證明的恆真而非偷懶：
          - default → check_permission() 走 _check_default_permission()，
            動作集合 = 目標角色預設，而實測每個角色的預設皆為 admin 的子集
          - scoped → **同樣先走 _check_default_permission()**，動作集合與
            default 相同；_check_scope_permission() 只能回傳拒絕、無法新增
            任何動作。此論證與 scope 是否生效無關——即使三項範圍設定全部
            失效（department_filter 目前正是如此），結論依然成立
          - custom → 呼叫者自由列舉模組與動作，是唯一能超出的路徑

        不檢查 scope 三欄（office_ids／own_only／department_filter，FR-008a）：
        範圍設定只能收窄可存取的資料、無法授予操作，涵蓋全部管理處的
        office_ids 效果至多等同於不設限，對「上限」這個問題本身不相干。

        Returns:
            (是否通過, 超出項清單)。超出項格式為 "模組.動作"，**全部收集**
            後一次回傳而非遇到第一個就返回——FR-010 要求逐項指出，設定者
            才不必逐次試錯。
        """
        mode = permissions.mode or PermissionMode.DEFAULT
        if mode != PermissionMode.CUSTOM or permissions.custom is None:
            return True, []

        ceiling = PermissionService.DEFAULT_ROLE_PERMISSIONS["admin"]
        exceeded: list[str] = []
        # 迭代 schema 欄位而非硬編碼模組清單——硬編碼會製造 TD-013 的第七個
        # 同步點。040 已在 validate_permissions_structure 用此法消除該同步點。
        # 未知的模組鍵不可能出現在這裡：Pydantic v2 預設 extra='ignore'，
        # 解析當下即丟棄，不需要為那條不可達路徑寫防禦分支。
        for field_name in CustomModulePermissionsSchema.model_fields:
            actions = getattr(permissions.custom, field_name, None)
            if not actions:
                continue
            allowed = ceiling.get(ModuleName(field_name), set())
            for action in actions:
                if action not in allowed:
                    exceeded.append(f"{field_name}.{action.value}")

        return (not exceeded), exceeded

    @staticmethod
    def is_deviated_from_role_default(permissions: Optional[dict]) -> bool:
        """帳號的權限設定是否已偏離其角色預設（041 FR-016～FR-018）。

        輸入型別**釘死為 DB 原始 JSONB dict**，不接受 UserPermissionsSchema、
        不做兩收容忍：唯一呼叫端 list_users 手上的 user.permissions 就是
        dict | None。日後若有持 schema 的呼叫端，由該端 .model_dump()。

        判定對象是**設定**而非當下的有效行為：一個只設了 department_filter
        的 scoped 帳號，雖因該篩選未實作而實際行為等同 default，仍回傳
        True。這不是誤報——FR-016 要防的是「被改動過而看不出來」，而範圍
        設定形同虛設的帳號正是管理者最需要被提醒的對象。

        判定規則只有這一份，前端不得重新實作等價判斷——那正是 TD-014
        記載的既有病灶（前端 ROLE_RESTRICTED_ROUTES 與後端矩陣雙維護）。
        """
        if not isinstance(permissions, dict):
            # None（從未設定）→ 沿用角色預設，未偏離。
            # 其餘非 dict 值（JSONB 可存字串／陣列／數字）是繞過本端點寫進來的
            # 髒資料——**一律標記**。理由與 scoped 相同：異常設定正是管理者最
            # 需要看見的東西。且此處由 list_users 逐筆呼叫，在髒資料上拋
            # AttributeError 會讓整個帳號管理頁 500。
            return permissions is not None
        if not permissions:
            return False
        mode = permissions.get("mode")
        return mode not in (None, PermissionMode.DEFAULT.value)


# 全域實例
permission_service = PermissionService()
