"""
權限相關的 Pydantic Schema 定義

定義了統一的權限結構：
- PermissionMode: 權限模式（default/scoped/custom）
- PermissionScope: 權限範圍控制
- UserPermissions: 完整權限設定

Created: 2025-12-08
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Set
from enum import Enum


class PermissionMode(str, Enum):
    """權限模式"""
    DEFAULT = "default"  # 基於角色的預設權限
    SCOPED = "scoped"    # 角色 + 動態範圍限制
    CUSTOM = "custom"    # 完全自訂權限


class PermissionAction(str, Enum):
    """權限操作類型"""
    VIEW = "view"           # 檢視
    CREATE = "create"       # 新增
    EDIT = "edit"           # 編輯
    DELETE = "delete"       # 刪除
    APPROVE = "approve"     # 審核
    EXPORT = "export"       # 匯出
    VIEW_ALL = "view_all"   # 跨管理處全域檢視（admin 獨有）


class ModuleName(str, Enum):
    """系統模組名稱
    # TD-013: 新增 ModuleName 值時必須同步修改 4 處：
    # (1)此 enum (2)CustomModulePermissionsSchema 欄位
    # (3)_check_custom_permission() elif (4)get_user_permissions_summary() modules dict
    """
    GRANTS = "grants"              # 補助申請
    USERS = "users"                # 使用者管理
    REPORTS = "reports"            # 報表系統
    GIS = "gis"                   # GIS 圖台
    OFFICES = "offices"            # 單位管理
    SETTINGS = "settings"          # 系統設定
    # 033 新增
    BATCH_PRINT = "batch_print"        # 批次列印
    DUPLICATE_CHECK = "duplicate_check"  # 重複查核
    MATERIALS = "materials"            # 材料管理
    DOWNLOADS = "downloads"            # 下載管理


class DepartmentFilterSchema(BaseModel):
    """部門篩選設定"""
    branch_codes: Optional[List[str]] = Field(None, description="分站代碼列表")
    station_codes: Optional[List[str]] = Field(None, description="工作站代碼列表")

    class Config:
        json_schema_extra = {
            "example": {
                "branch_codes": ["B01", "B02"],
                "station_codes": ["S001", "S002"]
            }
        }


class PermissionScopeSchema(BaseModel):
    """權限範圍設定（用於 scoped mode）"""
    office_ids: Optional[List[int]] = Field(None, description="允許存取的管理處 ID 列表")
    own_only: Optional[bool] = Field(False, description="是否僅能存取自己建立的資料")
    department_filter: Optional[DepartmentFilterSchema] = Field(None, description="部門篩選條件")

    class Config:
        json_schema_extra = {
            "example": {
                "office_ids": [11, 12],
                "own_only": False,
                "department_filter": {
                    "branch_codes": ["B01"],
                    "station_codes": ["S001", "S002"]
                }
            }
        }


class CustomModulePermissionsSchema(BaseModel):
    """自訂模組權限（用於 custom mode）"""
    grants: Optional[List[PermissionAction]] = Field(None, description="補助申請權限")
    users: Optional[List[PermissionAction]] = Field(None, description="使用者管理權限")
    reports: Optional[List[PermissionAction]] = Field(None, description="報表系統權限")
    gis: Optional[List[PermissionAction]] = Field(None, description="GIS 圖台權限")
    offices: Optional[List[PermissionAction]] = Field(None, description="單位管理權限")
    settings: Optional[List[PermissionAction]] = Field(None, description="系統設定權限")
    # 033 新增（TD-013: 同步新增 ModuleName enum 值時，此處需同步新增欄位）
    batch_print: Optional[List[PermissionAction]] = Field(None, description="批次列印權限")
    duplicate_check: Optional[List[PermissionAction]] = Field(None, description="重複查核權限")
    materials: Optional[List[PermissionAction]] = Field(None, description="材料管理權限")
    downloads: Optional[List[PermissionAction]] = Field(None, description="下載管理權限")

    @field_validator('*', mode='before')
    @classmethod
    def validate_actions(cls, v):
        """驗證並去重權限動作"""
        if v is None:
            return None
        if isinstance(v, list):
            # 去重並驗證
            unique_actions = list(set(v))
            return unique_actions
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "grants": ["view", "create", "edit"],
                "users": ["view"],
                "reports": ["view", "export"],
                "gis": ["view", "edit"],
                "offices": ["view"],
                "settings": []
            }
        }


class UserPermissionsSchema(BaseModel):
    """使用者完整權限設定（統一結構）"""
    mode: Optional[PermissionMode] = Field(PermissionMode.DEFAULT, description="權限模式")
    scope: Optional[PermissionScopeSchema] = Field(None, description="權限範圍（scoped mode 使用）")
    custom: Optional[CustomModulePermissionsSchema] = Field(None, description="自訂權限（custom mode 使用）")

    @field_validator('scope')
    @classmethod
    def validate_scope(cls, v, info):
        """驗證 scope 在 scoped mode 時必須提供"""
        mode = info.data.get('mode')
        if mode == PermissionMode.SCOPED and v is None:
            raise ValueError("scope 在 scoped mode 下必須提供")
        return v

    @field_validator('custom')
    @classmethod
    def validate_custom(cls, v, info):
        """驗證 custom 在 custom mode 時必須提供"""
        mode = info.data.get('mode')
        if mode == PermissionMode.CUSTOM and v is None:
            raise ValueError("custom 在 custom mode 下必須提供")
        return v

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "description": "預設權限模式（基於角色）",
                    "value": {
                        "mode": "default"
                    }
                },
                {
                    "description": "範圍限制模式（角色 + 動態範圍）",
                    "value": {
                        "mode": "scoped",
                        "scope": {
                            "office_ids": [11, 12],
                            "own_only": False,
                            "department_filter": {
                                "branch_codes": ["B01"]
                            }
                        }
                    }
                },
                {
                    "description": "自訂權限模式",
                    "value": {
                        "mode": "custom",
                        "custom": {
                            "grants": ["view", "create", "edit"],
                            "users": ["view"],
                            "reports": ["view", "export"]
                        }
                    }
                }
            ]
        }


# ============================================================================
# Request/Response Schemas
# ============================================================================

class UpdateUserPermissionsRequest(BaseModel):
    """更新使用者權限請求"""
    permissions: UserPermissionsSchema = Field(..., description="權限設定")
    reason: Optional[str] = Field(None, max_length=500, description="變更原因（審計用）")

    class Config:
        json_schema_extra = {
            "example": {
                "permissions": {
                    "mode": "scoped",
                    "scope": {
                        "office_ids": [11],
                        "own_only": True
                    }
                },
                "reason": "限制該使用者僅能存取所屬管理處資料"
            }
        }


class UserPermissionsResponse(BaseModel):
    """使用者權限回應"""
    user_id: int = Field(..., description="使用者 ID")
    username: str = Field(..., description="使用者帳號")
    full_name: Optional[str] = Field(None, description="使用者姓名")
    role: str = Field(..., description="角色")
    permissions: Optional[UserPermissionsSchema] = Field(None, description="權限設定")
    updated_at: Optional[str] = Field(None, description="最後更新時間")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123,
                "username": "user001",
                "full_name": "王小明",
                "role": "業務承辦人",
                "permissions": {
                    "mode": "scoped",
                    "scope": {
                        "office_ids": [11],
                        "own_only": False
                    }
                },
                "updated_at": "2025-12-08T10:30:00Z"
            }
        }


class PermissionCheckRequest(BaseModel):
    """權限檢查請求"""
    module: ModuleName = Field(..., description="模組名稱")
    action: PermissionAction = Field(..., description="操作類型")
    resource_id: Optional[int] = Field(None, description="資源 ID（檢查特定資源權限時使用）")
    office_id: Optional[int] = Field(None, description="管理處 ID（檢查範圍權限時使用）")

    class Config:
        json_schema_extra = {
            "example": {
                "module": "grants",
                "action": "edit",
                "resource_id": 456,
                "office_id": 11
            }
        }


class PermissionCheckResponse(BaseModel):
    """權限檢查回應"""
    allowed: bool = Field(..., description="是否允許")
    reason: Optional[str] = Field(None, description="拒絕原因（若 allowed=False）")

    class Config:
        json_schema_extra = {
            "example": {
                "allowed": True,
                "reason": None
            }
        }


class PermissionTemplateSchema(BaseModel):
    """權限範本定義"""
    name: str = Field(..., max_length=100, description="範本名稱")
    description: Optional[str] = Field(None, max_length=500, description="範本說明")
    permissions: UserPermissionsSchema = Field(..., description="權限設定")
    is_active: bool = Field(True, description="是否啟用")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "一般業務承辦人範本",
                "description": "適用於一般業務承辦人，限制僅能存取所屬管理處資料",
                "permissions": {
                    "mode": "scoped",
                    "scope": {
                        "own_only": False
                    }
                },
                "is_active": True
            }
        }
