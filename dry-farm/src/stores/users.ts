import { defineStore } from 'pinia'
import { userService, type User, type UserCredentials, type UserRegisterData, type UpdateUserData } from '@/services/userService'
import { wrapAsync, type ApiError } from '@/utils/asyncHelpers'
import { authEvents } from '@/services/api/interceptors'
import { useOfficesStore } from './offices'


// Simple JWT token decoder to check expiration
function parseJwt(token: string): { exp?: number } | null {
  try {
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )
    return JSON.parse(jsonPayload)
  } catch (e) {
    console.error('Error parsing JWT token:', e)
    return null
  }
}

// Check if token is expired
function isTokenExpired(token: string): boolean {
  const decodedToken = parseJwt(token)
  if (!decodedToken || !decodedToken.exp) return true

  // Compare expiration timestamp with current time (in seconds)
  const currentTime = Math.floor(Date.now() / 1000)
  return decodedToken.exp < currentTime
}
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

  // Flag to track if an auto-login attempt has been made
  const hasAttemptedAutoLogin = ref(false)

  // 計算屬性
  const isAuthenticated = computed(() => {
    // Check if token exists and is not expired
    if (!token.value) return false

    // Validate token expiration
    if (isTokenExpired(token.value)) {
      // Token is expired, clear it
      token.value = null
      localStorage.removeItem('auth_token')
      return false
    }

    return !!currentUser.value
  })
  const userFullName = computed(() => currentUser.value?.full_name || currentUser.value?.username || '')
  const officeName = computed(() => currentUser.value?.office?.name || '') // 這裡的 office 是從用戶資料中獲取的

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

    // Check if token is expired before making the request
    if (isTokenExpired(token.value)) {
      // Token is expired, clear it
      token.value = null
      localStorage.removeItem('auth_token')
      return null
    }

    try {
      const user = await userService.getCurrentUser()
      if (user) {
        currentUser.value = user
        hasAttemptedAutoLogin.value = true
        return user
      }
    } catch (error) {
      // If fetching fails, clear token
      token.value = null
      localStorage.removeItem('auth_token')
      throw error
    }

    return null
  }, asyncOptions)

  /**
   * User login
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
   * Check authentication state and token validity
   * @returns Whether user is authenticated with a valid token
   */
  const checkAuth = () => {
    // If no token, user is not authenticated
    if (!token.value) return false

    // Check if token is expired
    if (isTokenExpired(token.value)) {
      // Token is expired, clear it
      token.value = null
      currentUser.value = null
      localStorage.removeItem('auth_token')
      return false
    }

    // Token is valid, but we need to verify if we have a user
    return !!currentUser.value
  }

  /**
   * Attempt automatic login from stored token
   * Used during app initialization
   */
  const attemptAutoLogin = async () => {
    if (hasAttemptedAutoLogin.value) return
    hasAttemptedAutoLogin.value = true

    // If no token, no need to attempt
    if (!token.value) return

    // Check token expiration
    if (isTokenExpired(token.value)) {
      token.value = null
      localStorage.removeItem('auth_token')
      return
    }

    // Token exists and is valid, try to get current user
    await fetchCurrentUser()
  }

  /**
   * Initialize - Check local storage token and try to fetch user info
   */
  function init() {
    // Listen for auth events from API interceptors
    authEvents.on('unauthorized', () => {
      // Clear auth state when receiving unauthorized event
      currentUser.value = null
      token.value = null
      localStorage.removeItem('auth_token')
    })

    // If token exists, attempt to get user info
    if (token.value) {
      // Check token expiration before attempting
      if (!isTokenExpired(token.value)) {
        fetchCurrentUser().catch(() => {
          // Clear token if fetching fails
          token.value = null
          localStorage.removeItem('auth_token')
        })
      } else {
        // Token is expired, clear it
        token.value = null
        localStorage.removeItem('auth_token')
      }

      // Make sure offices are loaded for user data integration
      const officesStore = useOfficesStore()
      officesStore.initializeStore()
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
    hasAttemptedAutoLogin,

    // 計算屬性
    isAuthenticated,
    userFullName,
    officeName,

    // 方法
    login,
    register,
    logout,
    fetchCurrentUser,
    updateProfile,
    changePassword,
    deleteAccount,
    checkAuth,
    attemptAutoLogin,
  }
})
