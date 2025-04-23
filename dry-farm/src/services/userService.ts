import { apiService } from './api/http'
import { AUTH, USERS } from './api/endpoints'

export interface UserCredentials {
  username: string
  password: string
}

export interface UserRegisterData extends UserCredentials {
  full_name?: string
  office_id?: number
}

export interface User {
  id: number
  username: string
  full_name?: string
  created_at?: string
  office?: {
    id: number
    name: string
    short_name: string
    code: string
  }
}

export interface LoginResponse {
  message: string
  access_token?: string
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
  /**
   * 用戶登入
   * @param credentials 登入憑證
   */
  async login(credentials: UserCredentials): Promise<LoginResponse> {
    try {
      console.log('發送登入請求，憑證:', credentials);

      const response = await apiService.postForm<LoginResponse>(AUTH.LOGIN, {
        username: credentials.username,
        password: credentials.password
      })

      console.log('登入響應:', response);

      // 處理 token
      const token = response?.access_token;
      if (token) {
        localStorage.setItem('auth_token', token);
      }

      return response;
    } catch (error) {
      console.error('登入失敗:', error);

      if (error instanceof Error && 'response' in error && error.response) {
        console.error('錯誤資訊:', {
          status: (error as { response: { status: number } }).response.status,
          data: (error as { response: { data: unknown } }).response.data
        });
      }

      throw error;
    }
  },

  /**
   * 用戶註冊
   * @param userData 註冊資料
   */
  async register(userData: UserRegisterData): Promise<User> {
    try {
      console.log('發送註冊請求，資料:', userData)
      const response = await apiService.post<User>(
        AUTH.REGISTER,
        userData as unknown as Record<string, unknown>
      )
      return response
    } catch (error) {
      console.error('註冊失敗:', error)
      throw error
    }
  },

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
   * 變更密碼
   * @param oldPassword 舊密碼
   * @param newPassword 新密碼
   */
  async changePassword(oldPassword: string, newPassword: string): Promise<void> {
    try {
      const response = await apiService.post<void>(AUTH.CHANGE_PASSWORD, {
        old_password: oldPassword,
        new_password: newPassword
      })
      return response
    } catch (error) {
      console.error('變更密碼失敗:', error)
      throw error
    }
  }
}
