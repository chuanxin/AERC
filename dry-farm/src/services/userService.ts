import { apiService } from './api/http'
import { AUTH, USERS } from './api/endpoints'
import { getServerPublicKey } from './authKeyService'
import { encryptPassword, generateNonce } from '@/utils/passwordEncryption'

export interface UserCredentials {
  username: string
  password: string
}

export interface UserRegisterData extends UserCredentials {
  full_name?: string
  office_id?: number
}

export interface PermissionsSummary {
  mode: 'default' | 'scoped' | 'custom'
  modules: Record<string, string[]>
}

export interface User {
  id: number
  username: string
  full_name?: string
  role?: string
  created_at?: string
  password_expired?: boolean
  permissions_summary?: PermissionsSummary
  office?: {
    id: number
    name: string
    short_name: string
    code: string
  }
}

export interface LoginResponse {
  message?: string
  access_token?: string
  password_expired?: boolean
  mfa_required?: boolean
  mfa_token?: string
}

export interface UpdateUserData {
  username?: string
  full_name?: string
  email?: string
  password?: string
  new_password?: string
}

// 用戶服務
export const userService = {
  // 037-login-captcha-image：login()（呼叫 AUTH.LOGIN / POST /login）已移除——後端端點
  // 本身已刪除（FR-005a），全 repo 搜尋確認零呼叫端後直接刪除，非保留註解痕跡的對象。

  // 037-login-captcha-image：register() 整段是死碼（2026-08-09 第三方審查發現，見 037
  // spec.md Clarifications 第三題）。唯一呼叫端 stores/users.ts::register() 已於本功能
  // 整段註解，全 repo 搜尋確認此函式目前零呼叫端；真正的註冊功能由 signup.vue 走完全獨立的
  // POST /users/register（帳號審核流程）提供。AUTH.REGISTER 常數本身不受影響（mapping.ts
  // 仍有欄位映射引用），僅此函式本體註解。
  // /**
  //  * 用戶註冊
  //  * @param userData 註冊資料
  //  */
  // async register(userData: UserRegisterData): Promise<User> {
  //   try {
  //     console.log('發送註冊請求，資料:', userData)
  //     const response = await apiService.post<User>(
  //       AUTH.REGISTER,
  //       userData as unknown as Record<string, unknown>
  //     )
  //     return response
  //   } catch (error) {
  //     console.error('註冊失敗:', error)
  //     throw error
  //   }
  // },

  /**
   * 獲取用使用者資訊
   * @returns 使用者資訊
   */
  async getCurrentUser(): Promise<User> {
    try {
      const response = await apiService.get<User>(AUTH.ME)
      return response
    } catch (error) {
      console.error('獲取用戶資訊失敗:', error)
      throw error
    }
  },

  /**
   * 使用者登出
   */
  async logout(): Promise<void> {
    localStorage.removeItem('auth_token')
    document.cookie = 'Authorization=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
  },

  /**
   * 刷新 Token
   * @returns 新的登入回應
   */
  async refreshToken(): Promise<LoginResponse> {
    try {
      const response = await apiService.post<LoginResponse>(AUTH.REFRESH, {})
      return response
    } catch (error) {
      console.error('Token 刷新失敗:', error)
      throw error
    }
  },

  /**
   * 删除使用者帳號
   * @param userId 使用者ID
   */
  async deleteAccount(userId: number): Promise<{ message: string }> {
    try {
      const response = await apiService.delete<{ message: string }>(USERS.DELETE(userId))
      return response
    } catch (error) {
      console.error('刪除帳號失敗:', error)
      throw error
    }
  },

  /**
   * 更新使用者資料
   * @param userId 用戶ID
   * @param userData 要更新的資料
   */
  async updateProfile(userId: number, userData: UpdateUserData): Promise<User> {
    try {
      const response = await apiService.put<User>(
        USERS.UPDATE(userId),
        userData as unknown as Record<string, unknown>
      )
      return response
    } catch (error) {
      console.error('更新用戶資料失敗:', error)
      throw error
    }
  },

  /**
   * 密碼過期強制更換（JWT 已驗證身份，無需提供舊密碼）
   * @param newPassword 新密碼
   */
  async changePassword(newPassword: string): Promise<true> {
    const keyInfo = await getServerPublicKey()
    const { encrypted_password, encrypted_key, iv } = await encryptPassword(
      newPassword,
      keyInfo.publicKey,
    )

    await apiService.post<void>(AUTH.CHANGE_PASSWORD, {
      encrypted_password,
      encrypted_key,
      iv,
      kid: keyInfo.kid,
      timestamp: Date.now(),
      nonce: generateNonce(),
    })

    return true
  }
}
