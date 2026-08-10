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

// Check if token needs refresh (within 10 minutes of expiration)
function shouldRefreshToken(token: string): boolean {
  const decodedToken = parseJwt(token)
  if (!decodedToken || !decodedToken.exp) return false

  // Check if token expires within 5 minutes (300 seconds)
  const currentTime = Math.floor(Date.now() / 1000)
  const refreshThreshold = 300
  return (decodedToken.exp - currentTime) < refreshThreshold
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
  // 密碼過期狀態（不存放在客戶端 localStorage，透過 fetchCurrentUser 在 Refresh 後重建）
  const passwordExpired = ref<boolean>(false)

  // Flag to track if an auto-login attempt has been made
  const hasAttemptedAutoLogin = ref(false)

  // 防重複刷新：追蹤正在進行的刷新請求
  let isRefreshing = false
  let refreshPromise: Promise<string | null> | null = null

  // 🔥 防重複請求：追蹤正在進行的 fetchCurrentUser 請求
  let isFetchingUser = false
  let fetchUserPromise: Promise<User | null> | null = null

  // 🔥 集中式 Token 狀態管理：從 token 實時計算過期時間（Single Source of Truth）
  const showExpiryNotification = ref(false)

  // 從 token 實時計算過期時間，而非存儲快照
  const tokenExpiresAt = computed(() => {
    if (!token.value) return 0
    const decoded = parseJwt(token.value)
    return decoded?.exp || 0
  })

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

  // 權限查詢 helper — 從 permissions_summary（/users/whoami 回傳）讀取
  // module 對應後端 ModuleName enum value（snake_case）
  // action 對應後端 PermissionAction enum value：view | create | edit | delete | approve | export
  function can(module: string, action: string): boolean {
    const modules = currentUser.value?.permissions_summary?.modules ?? {}
    return (modules[module] ?? []).includes(action)
  }

  function canAny(module: string, actions: string[]): boolean {
    const allowed = currentUser.value?.permissions_summary?.modules?.[module] ?? []
    return actions.some(a => allowed.includes(a))
  }

  // 共享的異步選項對象
  const asyncOptions = {
    loadingRef: isLoading,
    errorRef: error
  }

  /**
   * 獲取當前用戶信息（帶請求去重機制）
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

    // 🔥 請求去重：如果正在請求中，返回現有 Promise
    if (isFetchingUser && fetchUserPromise) {
      console.log('🔄 [fetchCurrentUser] Already fetching user, returning existing promise')
      return fetchUserPromise
    }

    // 標記為正在請求
    isFetchingUser = true

    // 創建請求 Promise
    fetchUserPromise = (async () => {
      try {
        console.log('📡 [fetchCurrentUser] Fetching user data...')
        const user = await userService.getCurrentUser()
        if (user) {
          currentUser.value = user
          hasAttemptedAutoLogin.value = true
          // T013：從 /users/whoami 回應同步密碼過期狀態（Refresh 後重建）
          passwordExpired.value = user.password_expired ?? false
          console.log('✅ [fetchCurrentUser] User data fetched successfully:', user.username)
          return user
        }
        return null
      } catch (error) {
        // If fetching fails, clear token
        console.error('❌ [fetchCurrentUser] Failed to fetch user:', error)
        token.value = null
        localStorage.removeItem('auth_token')
        throw error
      } finally {
        // 重置請求狀態
        isFetchingUser = false
        fetchUserPromise = null
      }
    })()

    return fetchUserPromise
  }, asyncOptions)

  // 037-login-captcha-image：login() wrapper 已移除（POST /login 端點本身已於後端移除，
  // 唯一呼叫端——generateCaptcha catch 分支的 fallback、下方 register() 的自動登入——皆已
  // 移除或註解，全 repo 搜尋確認零呼叫端後直接刪除，非保留註解痕跡的對象；FR-005a）

  // 037-login-captcha-image：register() 整段是死碼（2026-08-09 第三方審查發現，見 037
  // spec.md Clarifications 第三題）。唯一呼叫端 login/index.vue::handleRegistration() 已於
  // 本功能整段註解，全 repo 搜尋確認 register()／userService.register() 目前零呼叫端；真正
  // 的註冊功能由 signup.vue 走完全獨立的 POST /users/register（帳號審核流程）提供，跟這裡
  // 無關。⚠️ 此區塊為過渡態註解，非可回復的功能開關：內部呼叫的 login()（見下方 login()
  // 定義處另一段註解）其呼叫目標將於本功能被正式刪除，屆時單純解除本區塊註解也無法運作，
  // 只能整段連同 login() 一起清除或改寫。保留註解僅為留存可回溯軌跡，供之後確認無虞後
  // 正式清除（連同下方 return 區塊中的 `register,` 匯出一併清除）。
  // /**
  //  * 用戶註冊
  //  * @param userData 註冊資料
  //  * @returns 新創建的用戶或 null（如果註冊失敗）
  //  */
  // const register = wrapAsync(async (userData: UserRegisterData) => {
  //   const newUser = await userService.register(userData)
  //
  //   // 註冊成功後自動登入
  //   if (newUser) {
  //     await login({
  //       username: userData.username,
  //       password: userData.password
  //     })
  //   }
  //
  //   return newUser
  // }, asyncOptions)

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
   * 刷新 Token（防重複版本）
   * @returns 新的 Token 或 null（如果刷新失敗）
   */
  const refreshToken = async (): Promise<string | null> => {
    if (!token.value) {
      throw new Error('無有效 Token 可刷新')
    }

    // 如果已經在刷新中，返回同一個 Promise
    if (isRefreshing && refreshPromise) {
      console.log('[UserStore] Token refresh already in progress, waiting...')
      return refreshPromise
    }

    // 標記為正在刷新，並創建刷新 Promise
    isRefreshing = true
    refreshPromise = (async () => {
      try {
        console.log('[UserStore] Starting token refresh...')
        const response = await userService.refreshToken()

        if (response?.access_token) {
          token.value = response.access_token
          localStorage.setItem('auth_token', response.access_token)
          console.log('[UserStore] Token refreshed successfully')

          return response.access_token
        }

        throw new Error('刷新 Token 失敗')
      } catch (error) {
        // 刷新失敗，清除 Token
        console.warn('[UserStore] Token refresh failed, logging out:', error)
        token.value = null
        currentUser.value = null
        localStorage.removeItem('auth_token')
        throw error
      } finally {
        // 重置刷新狀態
        isRefreshing = false
        refreshPromise = null
      }
    })()

    return refreshPromise
  }

  /**
   * 檢查並自動刷新 Token（如果需要）
   */
  const checkAndRefreshToken = async (): Promise<boolean> => {
    if (!token.value) return false

    if (isTokenExpired(token.value)) {
      // Token 已過期，無法刷新
      logout()
      return false
    }

    if (shouldRefreshToken(token.value)) {
      try {
        await refreshToken()
        return true
      } catch {
        return false
      }
    }

    return true // Token 還有效，不需刷新
  }


  /**
   * 更新用戶資料
   * @param userData 要更新的資料
   * @returns 更新後的用戶資料或 null（如果更新失敗）
   */
  const updateProfile = wrapAsync(async (userData: UpdateUserData) => {
    // 🔥 Linus式修復：使用嚴格比較，避免 ID 為 0 的用戶被誤判為未登入
    if (!currentUser.value || currentUser.value.id === null || currentUser.value.id === undefined) {
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
   * 密碼過期強制更換（JWT 已驗證身份，無需提供舊密碼）
   * @param newPassword 新密碼
   * @returns 操作是否成功
   */
  const changePassword = wrapAsync(async (newPassword: string) => {
    if (!currentUser.value) {
      throw new Error('未登入')
    }

    await userService.changePassword(newPassword)
    // 更換成功後清除密碼過期狀態
    passwordExpired.value = false
    return true  // 明確回傳 true，與失敗時的 null 區分（void return 導致 undefined 也是 falsy）
  }, {
    ...asyncOptions,
    errorFormatter: (err: unknown) => {
      if (err && typeof err === 'object') {
        const apiError = err as { response?: { data?: { detail?: unknown } }; message?: string }
        const detail = apiError.response?.data?.detail
        // Pydantic 422 validation error：detail 為陣列，取 msg 欄位並去除 "Value error, " 前綴
        if (Array.isArray(detail)) {
          const msg = detail
            .map((d: { msg?: string }) => (d.msg ?? '').replace(/^Value error,\s*/, ''))
            .filter(Boolean)
            .join('；')
          return msg || '密碼變更失敗'
        }
        // 一般後端錯誤：detail 為字串
        if (typeof detail === 'string') return detail
        return (apiError as ApiError).message || '密碼變更失敗'
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

  // 設置 token（供外部直接設置使用）
  const setToken = (newToken: string) => {
    token.value = newToken
  }

  // 返回公開的狀態和方法
  return {
    // 狀態
    currentUser,
    token,
    isLoading,
    error,
    hasAttemptedAutoLogin,
    passwordExpired,

    // 手動提醒相關狀態
    showExpiryNotification,
    tokenExpiresAt,

    // 計算屬性
    isAuthenticated,
    userFullName,
    officeName,
    can,
    canAny,

    // 方法
    // login, // 037-login-captcha-image：login() wrapper 已移除（POST /login 端點本身已刪除）
    // register, // 037-login-captcha-image：register() 本體已整段註解（死碼），匯出一併移除
    logout,
    refreshToken,
    checkAndRefreshToken,
    fetchCurrentUser,
    updateProfile,
    changePassword,
    deleteAccount,
    checkAuth,
    attemptAutoLogin,
    setToken,
  }
})
