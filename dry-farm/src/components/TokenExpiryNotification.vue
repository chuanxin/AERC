<template>
  <v-dialog
    v-model="isVisible"
    max-width="480"
    persistent
    class="token-expiry-dialog"
  >
    <v-card class="pa-0">
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
        </div>
      </v-card-text>

      <!-- 操作按鈕 -->
      <v-card-actions class="pa-4 pt-0">
        <v-btn
          variant="outlined"
          color="grey-darken-1"
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
          :loading="isRefreshing"
          @click="handleRefresh"
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
import { ref, computed, watch, onUnmounted } from 'vue'
import { useUserStore } from '@/stores/users'

// Props 定義
interface TokenExpiryNotificationProps {
  visible: boolean
  expiresAt: number // Token 到期時間戳 (秒)
}

const props = defineProps<TokenExpiryNotificationProps>()

// Emits 定義
const emit = defineEmits<{
  'update:visible': [visible: boolean]
  'refresh-success': []
  'refresh-failed': []
  'logout': []
}>()

// 狀態管理
const userStore = useUserStore()

// 內部狀態
const isRefreshing = ref(false)
const currentTime = ref(Math.floor(Date.now() / 1000))

// 計算屬性
const isVisible = computed({
  get: () => props.visible,
  set: (value: boolean) => emit('update:visible', value)
})

const remainingTime = computed(() => {
  return Math.max(0, props.expiresAt - currentTime.value)
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

// 倒數計時器
let countdownTimer: ReturnType<typeof setInterval> | null = null

const startCountdown = () => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }

  countdownTimer = setInterval(() => {
    currentTime.value = Math.floor(Date.now() / 1000)

    // 時間到了自動關閉對話框
    if (remainingTime.value <= 0) {
      handleTimeout()
    }
  }, 1000)
}

const stopCountdown = () => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
}

// 事件處理函數
const handleRefresh = async () => {
  isRefreshing.value = true

  try {
    console.log('[TokenExpiryNotification] User requested manual refresh')
    await userStore.refreshToken()

    // 刷新成功，關閉對話框
    isVisible.value = false
    emit('refresh-success')

    console.log('[TokenExpiryNotification] Manual refresh successful')
  } catch (error) {
    console.error('[TokenExpiryNotification] Manual refresh failed:', error)
    emit('refresh-failed')

    // 刷新失敗，可能需要登出
    // 這裡讓用戶選擇是否重試或登出
  } finally {
    isRefreshing.value = false
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
  stopCountdown()
  handleLogout()
}

// 監聽對話框顯示狀態
watch(() => props.visible, (visible) => {
  if (visible) {
    currentTime.value = Math.floor(Date.now() / 1000)
    startCountdown()
  } else {
    stopCountdown()
  }
}, { immediate: true })

// 組件卸載時清理
onUnmounted(() => {
  stopCountdown()
})
</script>

<style scoped>
.token-expiry-dialog :deep(.v-overlay__content) {
  margin: 24px;
}

.countdown-chip {
  font-size: 1.1rem;
  font-weight: 600;
  padding: 12px 16px;
}

.countdown-chip :deep(.v-chip__content) {
  font-weight: 600;
}

/* 警告樣式 */
.bg-warning {
  background-color: rgb(var(--v-theme-warning)) !important;
}

.text-warning-darken-4 {
  color: rgb(var(--v-theme-warning-darken-4)) !important;
}

/* 按鈕樣式調整 */
.v-card-actions .v-btn {
  min-width: 120px;
}

/* 響應式設計 */
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