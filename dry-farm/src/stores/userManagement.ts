/**
 * 使用者管理 Store（管理員功能）
 *
 * 提供使用者管理相關功能：
 * - 使用者列表查詢（篩選、分頁、搜尋）
 * - 批次啟用/停用帳號
 * - 權限管理
 * - 帳號審核
 *
 * Created: 2025-12-08
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiService } from '@/services/api/http'
import { USER_MANAGEMENT, PERMISSIONS } from '@/services/api/endpoints'
import { wrapAsync } from '@/utils/asyncHelpers'
import type {
  UserListResponse,
  UserListQuery,
  UserDetail,
  BatchOperationResponse,
  PendingApprovalResponse,
  UserApprovalResponse
} from '@/types/userManagement'
import type {
  UpdateUserPermissionsRequest,
  UserPermissionsResponse,
  PermissionCheckRequest,
  PermissionCheckResponse,
  PermissionsSummary
} from '@/types/permissions'

/**
 * 使用者管理 Store
 */
export const useUserManagementStore = defineStore('userManagement', () => {
  // ============================================================================
  // State
  // ============================================================================

  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 使用者列表
  const users = ref<UserListResponse | null>(null)

  // 待審核帳號列表
  const pendingUsers = ref<PendingApprovalResponse | null>(null)

  // 當前選中的使用者
  const selectedUsers = ref<number[]>([])

  // 權限摘要（當前使用者）
  const permissionsSummary = ref<PermissionsSummary | null>(null)

  // ============================================================================
  // Computed
  // ============================================================================

  const hasError = computed(() => error.value !== null)
  const hasUsers = computed(() => users.value !== null && users.value.users.length > 0)
  const hasPendingUsers = computed(() => pendingUsers.value !== null && pendingUsers.value.users.length > 0)
  const selectedCount = computed(() => selectedUsers.value.length)

  // ============================================================================
  // Async Options
  // ============================================================================

  const asyncOptions = {
    loadingRef: isLoading,
    errorRef: error
  }

  // ============================================================================
  // User List Methods
  // ============================================================================

  /**
   * 取得使用者列表
   */
  const fetchUsers = wrapAsync(async (query: UserListQuery = {}) => {
    const params = new URLSearchParams()
    if (query.page) params.append('page', query.page.toString())
    if (query.page_size) params.append('page_size', query.page_size.toString())
    if (query.is_active !== undefined) params.append('is_active', query.is_active.toString())
    if (query.role) params.append('role', query.role)
    if (query.office_id) params.append('office_id', query.office_id.toString())
    if (query.search) params.append('search', query.search)

    const url = params.toString() ? `${USER_MANAGEMENT.LIST}?${params.toString()}` : USER_MANAGEMENT.LIST
    const response = await apiService.get<UserListResponse>(url)

    users.value = response
    return response
  }, asyncOptions)

  /**
   * 取得單一使用者詳細資訊
   */
  const fetchUser = wrapAsync(async (userId: number) => {
    const response = await apiService.get<UserDetail>(USER_MANAGEMENT.DETAIL(userId))
    return response
  }, asyncOptions)

  /**
   * 刷新使用者列表（保持當前查詢參數）
   */
  const refreshUsers = async (query?: UserListQuery) => {
    await fetchUsers(query)
  }

  // ============================================================================
  // Permission Management Methods
  // ============================================================================

  /**
   * 更新使用者權限
   */
  const updateUserPermissions = wrapAsync(async (
    userId: number,
    request: UpdateUserPermissionsRequest
  ) => {
    const response = await apiService.patch<UserPermissionsResponse>(
      USER_MANAGEMENT.UPDATE_PERMISSIONS(userId),
      request
    )
    return response
  }, asyncOptions)

  /**
   * 檢查權限
   */
  const checkPermission = wrapAsync(async (request: PermissionCheckRequest) => {
    const response = await apiService.post<PermissionCheckResponse>(
      PERMISSIONS.CHECK,
      request
    )
    return response
  }, asyncOptions)

  /**
   * 取得權限摘要（當前使用者）
   */
  const fetchPermissionsSummary = wrapAsync(async () => {
    const response = await apiService.get<PermissionsSummary>(PERMISSIONS.SUMMARY)
    permissionsSummary.value = response
    return response
  }, asyncOptions)

  // ============================================================================
  // Batch Operations Methods
  // ============================================================================

  /**
   * 批次啟用帳號
   */
  const batchActivateUsers = wrapAsync(async (userIds: number[]) => {
    const response = await apiService.post<BatchOperationResponse>(
      USER_MANAGEMENT.BATCH_ACTIVATE,
      userIds
    )
    return response
  }, asyncOptions)

  /**
   * 批次停用帳號
   */
  const batchDeactivateUsers = wrapAsync(async (userIds: number[]) => {
    const response = await apiService.post<BatchOperationResponse>(
      USER_MANAGEMENT.BATCH_DEACTIVATE,
      userIds
    )
    return response
  }, asyncOptions)

  // ============================================================================
  // User Approval Methods
  // ============================================================================

  /**
   * 取得待審核帳號列表
   */
  const fetchPendingApprovalUsers = wrapAsync(async (
    page: number = 1,
    pageSize: number = 20
  ) => {
    const url = `${USER_MANAGEMENT.PENDING_APPROVAL}?page=${page}&page_size=${pageSize}`
    const response = await apiService.get<PendingApprovalResponse>(url)

    pendingUsers.value = response
    return response
  }, asyncOptions)

  /**
   * 審核通過帳號
   */
  const approveUser = wrapAsync(async (userId: number) => {
    const response = await apiService.post<UserApprovalResponse>(
      USER_MANAGEMENT.APPROVE(userId)
    )
    return response
  }, asyncOptions)

  /**
   * 拒絕帳號申請
   */
  const rejectUser = wrapAsync(async (userId: number, reason?: string) => {
    const response = await apiService.post<UserApprovalResponse>(
      USER_MANAGEMENT.REJECT(userId),
      { reason }
    )
    return response
  }, asyncOptions)

  // ============================================================================
  // Selection Methods
  // ============================================================================

  /**
   * 選擇使用者
   */
  const selectUser = (userId: number) => {
    if (!selectedUsers.value.includes(userId)) {
      selectedUsers.value.push(userId)
    }
  }

  /**
   * 取消選擇使用者
   */
  const deselectUser = (userId: number) => {
    const index = selectedUsers.value.indexOf(userId)
    if (index > -1) {
      selectedUsers.value.splice(index, 1)
    }
  }

  /**
   * 切換使用者選擇狀態
   */
  const toggleUserSelection = (userId: number) => {
    if (selectedUsers.value.includes(userId)) {
      deselectUser(userId)
    } else {
      selectUser(userId)
    }
  }

  /**
   * 全選
   */
  const selectAll = () => {
    if (users.value) {
      selectedUsers.value = users.value.users.map(user => user.id)
    }
  }

  /**
   * 取消全選
   */
  const deselectAll = () => {
    selectedUsers.value = []
  }

  /**
   * 切換全選狀態
   */
  const toggleSelectAll = () => {
    if (selectedUsers.value.length === users.value?.users.length) {
      deselectAll()
    } else {
      selectAll()
    }
  }

  // ============================================================================
  // Utility Methods
  // ============================================================================

  /**
   * 清除錯誤訊息
   */
  const clearError = () => {
    error.value = null
  }

  /**
   * 重置狀態
   */
  const reset = () => {
    users.value = null
    pendingUsers.value = null
    selectedUsers.value = []
    permissionsSummary.value = null
    error.value = null
  }

  // ============================================================================
  // Return
  // ============================================================================

  return {
    // State
    isLoading,
    error,
    users,
    pendingUsers,
    selectedUsers,
    permissionsSummary,

    // Computed
    hasError,
    hasUsers,
    hasPendingUsers,
    selectedCount,

    // User List Methods
    fetchUsers,
    fetchUser,
    refreshUsers,

    // Permission Methods
    updateUserPermissions,
    checkPermission,
    fetchPermissionsSummary,

    // Batch Operations
    batchActivateUsers,
    batchDeactivateUsers,

    // User Approval
    fetchPendingApprovalUsers,
    approveUser,
    rejectUser,

    // Selection Methods
    selectUser,
    deselectUser,
    toggleUserSelection,
    selectAll,
    deselectAll,
    toggleSelectAll,

    // Utility
    clearError,
    reset
  }
})
