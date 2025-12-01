<template>
  <v-dialog
    v-model="isVisible"
    max-width="480"
    persistent
    class="token-expiry-dialog"
  >
    <v-card
      rounded="xl"
      elevation="8"
    >
      <!-- 標題區域 -->
      <v-card-title class="d-flex align-center bg-warning text-warning-darken-4 pa-4">
        <v-icon
          class="me-3"
          size="28"
        >
          mdi-clock-alert
        </v-icon>
        <span class="text-h6 font-weight-bold">登入即將逾時</span>
      </v-card-title>

      <!-- 內容區域 -->
      <v-card-text class="pa-6">
        <div class="d-flex flex-column align-center text-center">
          <!-- 倒數計時器 -->
          <div class="mb-4">
            <v-chip
              size="large"
              color="warning"
              variant="outlined"
              rounded="lg"
              class="countdown-chip"
            >
              <v-icon class="me-2">
                mdi-timer-sand
              </v-icon>
              {{ formatTime(remainingTime) }}
            </v-chip>
          </div>

          <!-- 說明文字 -->
          <p class="text-body-1 mb-4">
            為了您的帳戶安全，系統將在 <strong>{{ formatTime(remainingTime) }}</strong> 後自動登出。
          </p>

          <p class="text-body-2 text-medium-emphasis mb-0">
            您可以選擇繼續工作或手動登出
          </p>

          <!-- 錯誤訊息 -->
          <v-alert
            v-if="refreshError"
            type="error"
            variant="tonal"
            density="compact"
            rounded="lg"
            class="mt-4 text-start"
            closable
            @click:close="refreshError = null"
          >
            <div class="text-caption">
              <strong>刷新失敗：</strong>{{ refreshError }}
            </div>
            <div class="text-caption mt-1">
              請檢查網路連線後重試，或選擇登出重新登入
            </div>
          </v-alert>
        </div>
      </v-card-text>

      <!-- 操作按鈕 -->
      <v-card-actions class="pa-4 pt-0">
        <v-btn
          variant="outlined"
          color="grey-darken-1"
          rounded="lg"
          :disabled="isRefreshing"
          @click="handleLogout"
        >
          <v-icon class="me-2">
            mdi-logout
          </v-icon>
          立即登出
        </v-btn>

        <v-spacer />

        <v-btn
          color="primary"
          variant="flat"
          rounded="lg"
          :loading="isRefreshing"
          :disabled="isRefreshing"
          @click.stop.prevent="handleRefresh"
        >
          <v-icon class="me-2">
            mdi-refresh
          </v-icon>
          繼續工作
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '@/stores/users'

// 狀態管理
const userStore = useUserStore()

// Emits 定義
const emit = defineEmits<{
  'refresh-success': []
  'refresh-failed': []
  'logout': []
}>()

// 內部狀態
const isRefreshing = ref(false)
const currentTime = ref(Math.floor(Date.now() / 1000))
const refreshError = ref<string | null>(null)

// 🔥 計算屬性：從 userStore 獲取集中管理的狀態
const isVisible = computed({
  get: () => userStore.showExpiryNotification,
  set: (value: boolean) => {
    userStore.showExpiryNotification = value
  }
})

const tokenExpiresAt = computed(() => userStore.tokenExpiresAt)

const remainingTime = computed(() => {
  return Math.max(0, tokenExpiresAt.value - currentTime.value)
})

// 時間格式化函數
const formatTime = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60

  if (minutes > 0) {
    return `${minutes} 分 ${secs} 秒`
  } else {
    return `${secs} 秒`
  }
}

// 🔥 使用 requestAnimationFrame 實現精確計時（不受標籤頁節流影響）
let rafId: number | null = null
let lastCheckTime = 0
const CHECK_INTERVAL_MS = 1000 // 每秒檢查一次

const checkTokenExpiry = (timestamp: number) => {
  // 節流：每秒最多更新一次
  if (timestamp - lastCheckTime >= CHECK_INTERVAL_MS) {
    lastCheckTime = timestamp
    currentTime.value = Math.floor(Date.now() / 1000)

    const remaining = remainingTime.value

    // 🎯 觸發彈窗的條件：剩餘時間 <= 60 秒且 > 0
    if (remaining <= 60 && remaining > 0 && !isVisible.value) {
      console.log(`[TokenExpiryNotification] Token expiring in ${remaining}s, showing notification`)
      isVisible.value = true
    }

    // 時間到了自動登出
    if (remaining <= 0 && userStore.token) {
      console.log('[TokenExpiryNotification] Token expired, auto logout')
      handleTimeout()
      return // 停止檢查
    }
  }

  // 持續檢查
  rafId = requestAnimationFrame(checkTokenExpiry)
}

const startMonitoring = () => {
  if (rafId) {
    cancelAnimationFrame(rafId)
  }
  lastCheckTime = 0
  rafId = requestAnimationFrame(checkTokenExpiry)
  console.log('[TokenExpiryNotification] Started token expiry monitoring')
}

const stopMonitoring = () => {
  if (rafId) {
    cancelAnimationFrame(rafId)
    rafId = null
    console.log('[TokenExpiryNotification] Stopped token expiry monitoring')
  }
}

// 事件處理函數
const handleRefresh = async () => {
  console.log('[TokenExpiryNotification] User requested manual refresh')

  if (isRefreshing.value) {
    console.warn('[TokenExpiryNotification] Already refreshing, ignoring duplicate request')
    return
  }

  isRefreshing.value = true
  refreshError.value = null

  // 添加超時保護機制 - 30秒後自動重置狀態
  const timeoutId = setTimeout(() => {
    console.error('[TokenExpiryNotification] Refresh timeout after 30 seconds')
    refreshError.value = '請求逾時，請重試'
    isRefreshing.value = false
    emit('refresh-failed')
  }, 30000)

  try {
    console.log('[TokenExpiryNotification] Calling userStore.refreshToken()...')
    const result = await userStore.refreshToken()

    // 清除超時計時器
    clearTimeout(timeoutId)

    console.log('[TokenExpiryNotification] Refresh result:', result ? 'success' : 'null')

    if (result) {
      // 刷新成功，關閉對話框
      console.log('[TokenExpiryNotification] Manual refresh successful, closing dialog')
      isVisible.value = false
      emit('refresh-success')
    } else {
      // 刷新失敗但沒有拋出錯誤
      console.warn('[TokenExpiryNotification] Token refresh returned null')
      refreshError.value = '無法取得新的登入憑證'
      emit('refresh-failed')
    }
  } catch (error) {
    // 清除超時計時器
    clearTimeout(timeoutId)

    console.error('[TokenExpiryNotification] Manual refresh failed:', error)

    // 根據錯誤類型顯示不同訊息
    const errorMessage = error instanceof Error ? error.message : String(error)
    const errorResponse = (error as { response?: { status?: number } })?.response

    if (errorMessage.includes('Network') || errorMessage.includes('network')) {
      refreshError.value = '網路連線異常，請檢查您的網路狀態'
    } else if (errorMessage.includes('timeout') || errorMessage.includes('Timeout')) {
      refreshError.value = '請求逾時，請重試'
    } else if (errorResponse?.status === 401) {
      refreshError.value = '登入憑證已失效'
    } else {
      refreshError.value = errorMessage || '未知錯誤，請重試或重新登入'
    }

    emit('refresh-failed')

    // 如果是 401 或 token 完全失效，應該自動登出
    if (errorResponse?.status === 401 || !userStore.token) {
      console.log('[TokenExpiryNotification] Token completely invalid, will auto logout in 3 seconds')
      setTimeout(() => {
        handleLogout()
      }, 3000) // 3秒後自動登出，給用戶時間看到錯誤訊息
    }
  } finally {
    isRefreshing.value = false
    console.log('[TokenExpiryNotification] Refresh process completed')
  }
}

const handleLogout = () => {
  console.log('[TokenExpiryNotification] User requested logout')
  isVisible.value = false
  emit('logout')
  // 注意：實際的 logout 和路由跳轉在 App.vue 中處理
}

const handleTimeout = () => {
  console.log('[TokenExpiryNotification] Countdown timeout, auto logout')
  stopMonitoring()
  handleLogout()
}

// 🔥 監聽 token 變化：當 token 刷新時，tokenExpiresAt 會自動更新（computed）
// 彈窗會自動根據新的過期時間重新計算倒數
watch(() => userStore.token, (newToken) => {
  if (newToken) {
    console.log('[TokenExpiryNotification] Token updated, new expiry:', new Date(tokenExpiresAt.value * 1000).toISOString())
    // Token 刷新後，如果剩餘時間 > 60 秒，自動關閉彈窗
    if (remainingTime.value > 60) {
      isVisible.value = false
    }
  } else {
    // Token 被清除，停止監控
    stopMonitoring()
    isVisible.value = false
  }
})

// 組件生命週期
onMounted(() => {
  console.log('[TokenExpiryNotification] Component mounted, starting monitoring')
  startMonitoring()
})

onUnmounted(() => {
  console.log('[TokenExpiryNotification] Component unmounted, stopping monitoring')
  stopMonitoring()
})
</script>

<style scoped>
/* 對話框外邊距 */
.token-expiry-dialog :deep(.v-overlay__content) {
  margin: 24px;
}

/* 倒數計時 Chip 樣式 */
.countdown-chip {
  font-size: 1.1rem;
  font-weight: 600;
  padding: 12px 16px;
}

.countdown-chip :deep(.v-chip__content) {
  font-weight: 600;
}

/* 警告顏色樣式 */
.bg-warning {
  background-color: rgb(var(--v-theme-warning)) !important;
}

.text-warning-darken-4 {
  color: rgb(var(--v-theme-warning-darken-4)) !important;
}

/* 按鈕最小寬度 */
.v-card-actions .v-btn {
  min-width: 120px;
}

/* 響應式設計 - 小螢幕優化 */
@media (max-width: 600px) {
  .token-expiry-dialog :deep(.v-overlay__content) {
    margin: 16px;
    max-width: calc(100vw - 32px);
  }

  .countdown-chip {
    font-size: 1rem;
    padding: 10px 14px;
  }

  .v-card-actions {
    flex-direction: column;
    gap: 8px;
  }

  .v-card-actions .v-btn {
    width: 100%;
    min-width: auto;
  }

  .v-card-actions .v-spacer {
    display: none;
  }
}
</style>
