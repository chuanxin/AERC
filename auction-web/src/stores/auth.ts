import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { userService } from '@/services/userService'
import type { User, LoginCredentials } from '@/types/user'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref(localStorage.getItem('token') || '')

  const isLoggedIn = computed(() => !!token.value)

  async function login(credentials: LoginCredentials) {
    const response = await userService.login(credentials)
    token.value = response.access_token
    localStorage.setItem('token', response.access_token)
    await fetchUser()
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      user.value = await userService.getMe()
    } catch {
      logout()
    }
  }

  function logout() {
    user.value = null
    token.value = ''
    localStorage.removeItem('token')
  }

  // Auto-fetch user if token exists
  if (token.value) {
    fetchUser()
  }

  return { user, token, isLoggedIn, login, fetchUser, logout }
})
