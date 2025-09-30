<template>
  <v-app :theme="themeStore.theme">
    <router-view />

    <!-- 全域 Token 到期提醒彈窗 -->
    <TokenExpiryNotification
      v-model:visible="userStore.showExpiryNotification"
      :expires-at="userStore.notificationExpiresAt"
      @refresh-success="handleRefreshSuccess"
      @refresh-failed="handleRefreshFailed"
      @logout="handleLogout"
    />
  </v-app>
</template>

<script lang="ts" setup>
  import { useThemeStore } from '@/stores/theme'
  import { useUserStore } from '@/stores/users'
  import { useRouter } from 'vue-router'
  import TokenExpiryNotification from '@/components/TokenExpiryNotification.vue'

  const themeStore = useThemeStore()
  const userStore = useUserStore()
  const router = useRouter()

  // 事件處理函數
  const handleRefreshSuccess = () => {
    console.log('[App] Token refresh from notification successful')
  }

  const handleRefreshFailed = () => {
    console.error('[App] Token refresh from notification failed')
    // 可以在這裡顯示錯誤訊息給用戶
  }

  const handleLogout = async () => {
    console.log('[App] User chose to logout from expiry notification')

    // 執行登出並跳轉到登入頁面
    try {
      await userStore.logout()
      console.log('[App] Logout successful, redirecting to login')

      // 跳轉到登入頁面
      await router.push('/login')
    } catch (error) {
      console.error('[App] Logout failed:', error)

      // 即使登出失敗，也要跳轉到登入頁面
      await router.push('/login')
    }
  }
</script>

<style scoped>

</style>
