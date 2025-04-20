import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { userService, type User, type UserCredentials, type UserRegisterData, type UpdateUserData } from '@/services/userService'
import { wrapAsync, type ApiError } from '@/utils/asyncHelpers'

/**
 * 用戶管理存儲
 * 處理用戶認證、個人資料管理及相關狀態
 */
export const useUserStore = defineStore('user', () => {
  // 狀態定義
  const currentUser = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('auth_token'))
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 計算屬性
  const isAuthenticated = computed(() => !!token.value && !!currentUser.value)
  const userFullName = computed(() => currentUser.value?.full_name || currentUser.value?.username || '')

  // 共享的異步選項對象
  const asyncOptions = {
    loadingRef: isLoading,
    errorRef: error
  }

  /**
   * 獲取當前用戶信息
   * @returns 用戶信息或 null（如果獲取失敗）
   */
  const fetchCurrentUser = wrapAsync(async () => {
    if (!token.value) return null

    const user = await userService.getCurrentUser()
    if (user) {
      currentUser.value = user
      return user
    }

    // 如果獲取失敗，清除 token
    token.value = null
    localStorage.removeItem('auth_token')
    return null
  }, asyncOptions)

  /**
   * 用戶登入
   * @param credentials 登入憑證
   * @returns 登入後的用戶信息或 null（如果登入失敗）
   */
  const login = wrapAsync(async (credentials: UserCredentials) => {
    const response = await userService.login(credentials)

    // 保存令牌
    if (response?.access_token) {
      token.value = response.access_token
      localStorage.setItem('auth_token', response.access_token)

      // 獲取用戶信息
      return await fetchCurrentUser()
    }

    return null
  }, {
    ...asyncOptions,
    errorFormatter: (err: unknown) => {
      // API 錯誤處理
      if (err && typeof err === 'object') {
        const apiError = err as ApiError
        return apiError.response?.data?.detail ||
               apiError.response?.data?.message ||
               apiError.message ||
               '登入失敗'
      }
      return '登入失敗'
    }
  })

  /**
   * 用戶註冊
   * @param userData 註冊資料
   * @returns 新創建的用戶或 null（如果註冊失敗）
   */
  const register = wrapAsync(async (userData: UserRegisterData) => {
    const newUser = await userService.register(userData)

    // 註冊成功後自動登入
    if (newUser) {
      await login({
        username: userData.username,
        password: userData.password
      })
    }

    return newUser
  }, asyncOptions)

  /**
   * 用戶登出
   */
  const logout = wrapAsync(async () => {
    try {
      await userService.logout()
    } finally {
      // 無論後端是否成功，都清除本地狀態
      currentUser.value = null
      token.value = null
      localStorage.removeItem('auth_token')
    }
    return true
  }, asyncOptions)

  /**
   * 更新用戶資料
   * @param userData 要更新的資料
   * @returns 更新後的用戶資料或 null（如果更新失敗）
   */
  const updateProfile = wrapAsync(async (userData: UpdateUserData) => {
    if (!currentUser.value?.id) {
      throw new Error('未登入')
    }

    const updatedUser = await userService.updateProfile(
      currentUser.value.id,
      userData
    )

    if (updatedUser) {
      currentUser.value = updatedUser
    }

    return updatedUser
  }, asyncOptions)

  /**
   * 變更密碼
   * @param oldPassword 舊密碼
   * @param newPassword 新密碼
   * @returns 操作是否成功
   */
  const changePassword = wrapAsync(async (oldPassword: string, newPassword: string) => {
    if (!currentUser.value) {
      throw new Error('未登入')
    }

    return await userService.changePassword(oldPassword, newPassword)
  }, {
    ...asyncOptions,
    errorFormatter: (err: unknown) => {
      if (err && typeof err === 'object') {
        const apiError = err as ApiError
        return apiError.response?.data?.detail || '密碼變更失敗'
      }
      return '密碼變更失敗'
    }
  })

  /**
   * 刪除用戶帳號
   * @returns 操作是否成功
   */
  const deleteAccount = wrapAsync(async () => {
    if (!currentUser.value?.id) {
      throw new Error('未登入')
    }

    await userService.deleteAccount(currentUser.value.id)

    // 清除本地狀態
    currentUser.value = null
    token.value = null
    localStorage.removeItem('auth_token')

    return true
  }, asyncOptions)

  /**
   * 初始化 - 檢查本地存儲中的令牌並嘗試獲取用戶信息
   */
  function init() {
    if (token.value) {
      fetchCurrentUser().catch(() => {
        // 獲取失敗時清除令牌
        token.value = null
        localStorage.removeItem('auth_token')
      })
    }
  }

  // 立即初始化
  init()

  // 返回公開的狀態和方法
  return {
    // 狀態
    currentUser,
    token,
    isLoading,
    error,

    // 計算屬性
    isAuthenticated,
    userFullName,

    // 方法
    login,
    register,
    logout,
    fetchCurrentUser,
    updateProfile,
    changePassword,
    deleteAccount
  }
})
