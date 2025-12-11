/**
 * 權限相關的 TypeScript 類型定義
 *
 * 對應後端 schemas/permissions.py 的結構
 *
 * Created: 2025-12-08
 */

/**
 * 權限模式
 */
export enum PermissionMode {
  DEFAULT = 'default',  // 基於角色的預設權限
  SCOPED = 'scoped',    // 角色 + 動態範圍限制
  CUSTOM = 'custom'     // 完全自訂權限
}

/**
 * 權限操作類型
 */
export enum PermissionAction {
  VIEW = 'view',        // 檢視
  CREATE = 'create',    // 新增
  EDIT = 'edit',        // 編輯
  DELETE = 'delete',    // 刪除
  APPROVE = 'approve',  // 審核
  EXPORT = 'export'     // 匯出
}

/**
 * 系統模組名稱
 */
export enum ModuleName {
  GRANTS = 'grants',      // 補助申請
  USERS = 'users',        // 使用者管理
  REPORTS = 'reports',    // 報表系統
  GIS = 'gis',           // GIS 圖台
  OFFICES = 'offices',    // 單位管理
  SETTINGS = 'settings'  // 系統設定
}

/**
 * 部門篩選設定
 */
export interface DepartmentFilter {
  branch_codes?: string[]   // 分站代碼列表
  station_codes?: string[]  // 工作站代碼列表
}

/**
 * 權限範圍設定（用於 scoped mode）
 */
export interface PermissionScope {
  office_ids?: number[]              // 允許存取的管理處 ID 列表
  own_only?: boolean                 // 是否僅能存取自己建立的資料
  department_filter?: DepartmentFilter  // 部門篩選條件
}

/**
 * 自訂模組權限（用於 custom mode）
 */
export interface CustomModulePermissions {
  grants?: PermissionAction[]    // 補助申請權限
  users?: PermissionAction[]     // 使用者管理權限
  reports?: PermissionAction[]   // 報表系統權限
  gis?: PermissionAction[]       // GIS 圖台權限
  offices?: PermissionAction[]   // 單位管理權限
  settings?: PermissionAction[]  // 系統設定權限
}

/**
 * 使用者完整權限設定（統一結構）
 */
export interface UserPermissions {
  mode?: PermissionMode                    // 權限模式
  scope?: PermissionScope                  // 權限範圍（scoped mode 使用）
  custom?: CustomModulePermissions         // 自訂權限（custom mode 使用）
}

/**
 * 更新使用者權限請求
 */
export interface UpdateUserPermissionsRequest {
  permissions: UserPermissions  // 權限設定
  reason?: string              // 變更原因（審計用）
}

/**
 * 使用者權限回應
 */
export interface UserPermissionsResponse {
  user_id: number
  username: string
  full_name?: string
  role: string
  permissions?: UserPermissions
  updated_at?: string
}

/**
 * 權限檢查請求
 */
export interface PermissionCheckRequest {
  module: ModuleName
  action: PermissionAction
  resource_id?: number    // 資源 ID（檢查特定資源權限時使用）
  office_id?: number      // 管理處 ID（檢查範圍權限時使用）
}

/**
 * 權限檢查回應
 */
export interface PermissionCheckResponse {
  allowed: boolean
  reason?: string  // 拒絕原因（若 allowed=false）
}

/**
 * 權限摘要
 */
export interface PermissionsSummary {
  user_id: number
  username: string
  role: string
  permissions: {
    mode: PermissionMode
    modules: {
      [key: string]: PermissionAction[]
    }
  }
  scope?: PermissionScope  // 如果是 scoped mode
}

/**
 * 權限範本定義
 */
export interface PermissionTemplate {
  id?: number
  name: string
  description?: string
  permissions: UserPermissions
  is_active: boolean
}

/**
 * 模組權限顯示名稱映射
 */
export const MODULE_NAMES: Record<ModuleName, string> = {
  [ModuleName.GRANTS]: '補助申請',
  [ModuleName.USERS]: '使用者管理',
  [ModuleName.REPORTS]: '報表系統',
  [ModuleName.GIS]: 'GIS 圖台',
  [ModuleName.OFFICES]: '單位管理',
  [ModuleName.SETTINGS]: '系統設定'
}

/**
 * 操作權限顯示名稱映射
 */
export const ACTION_NAMES: Record<PermissionAction, string> = {
  [PermissionAction.VIEW]: '檢視',
  [PermissionAction.CREATE]: '新增',
  [PermissionAction.EDIT]: '編輯',
  [PermissionAction.DELETE]: '刪除',
  [PermissionAction.APPROVE]: '審核',
  [PermissionAction.EXPORT]: '匯出'
}

/**
 * 權限模式顯示名稱映射
 */
export const MODE_NAMES: Record<PermissionMode, string> = {
  [PermissionMode.DEFAULT]: '預設權限（基於角色）',
  [PermissionMode.SCOPED]: '範圍限制權限',
  [PermissionMode.CUSTOM]: '自訂權限'
}

/**
 * 預設角色列表
 */
export const DEFAULT_ROLES = [
  '系統管理員',
  '管理處主管',
  '業務承辦人',
  '一般使用者'
] as const

export type DefaultRole = typeof DEFAULT_ROLES[number]
