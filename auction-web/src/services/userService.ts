import api from './api'
import type { User, LoginCredentials, RegisterData } from '@/types/user'

export const userService = {
  async login(credentials: LoginCredentials): Promise<{ access_token: string }> {
    const { data } = await api.post('/auth/login', credentials)
    return data
  },

  async register(registerData: RegisterData): Promise<User> {
    const { data } = await api.post('/auth/register', registerData)
    return data
  },

  async getMe(): Promise<User> {
    const { data } = await api.get('/auth/me')
    return data
  },
}
