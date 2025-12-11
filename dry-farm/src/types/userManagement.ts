/**
 * 使用者管理相關的 TypeScript 類型定義
 *
 * Created: 2025-12-08
 */

import type { UserPermissions } from './permissions'

/**
 * 簡化的單位資訊
 */
export interface SimpleOffice {
  id: number
  name: string
  short_name: string
  code: string
  classification: number
  is_funding_source: boolean
}

/**
 * 使用者資訊（列表用）
 */
export interface UserListItem {
  id: number
  username: string
  full_name?: string
  email?: string
  job_title?: string
  is_active: boolean
  role?: string
  permissions?: UserPermissions
  office?: SimpleOffice
  created_at?: string
  last_login?: string
}

/**
 * 使用者詳細資訊
 */
export interface UserDetail extends UserListItem {
  phone?: string
  phone_ext?: string
  mobile?: string
  department?: any  // JSONB 欄位
  email_verified?: boolean
  password_expired?: boolean
}

/**
 * 使用者列表回應
 */
export interface UserListResponse {
  total: number
  page: number
  page_size: number
  total_pages: number
  users: UserListItem[]
}

/**
 * 使用者列表查詢參數
 */
export interface UserListQuery {
  page?: number
  page_size?: number
  is_active?: boolean
  role?: string
  office_id?: number
  search?: string
}

/**
 * 批次操作請求
 */
export interface BatchOperationRequest {
  user_ids: number[]
}

/**
 * 批次操作回應
 */
export interface BatchOperationResponse {
  success: number
  failed: number
  details: Array<{
    user_id: number
    username?: string
    success: boolean
    message: string
  }>
}

/**
 * 帳號審核操作回應
 */
export interface UserApprovalResponse {
  success: boolean
  message: string
  user_id?: number
  username?: string
}

/**
 * 帳號拒絕請求
 */
export interface UserRejectionRequest {
  reason?: string
}

/**
 * 待審核帳號資訊
 */
export interface PendingApprovalUser {
  id: number
  username: string
  full_name?: string
  email?: string
  job_title?: string
  phone?: string
  phone_ext?: string
  mobile?: string
  role?: string
  office?: SimpleOffice
  department?: any
  created_at?: string
}

/**
 * 待審核帳號列表回應
 */
export interface PendingApprovalResponse {
  total: number
  page: number
  page_size: number
  total_pages: number
  users: PendingApprovalUser[]
}

/**
 * 使用者狀態統計
 */
export interface UserStatistics {
  total_users: number
  active_users: number
  inactive_users: number
  pending_approval: number
  by_role: Record<string, number>
  by_office: Record<string, number>
}

/**
 * 使用者篩選選項
 */
export interface UserFilterOptions {
  roles: string[]
  offices: SimpleOffice[]
  statuses: Array<{
    label: string
    value: boolean | null
  }>
}
