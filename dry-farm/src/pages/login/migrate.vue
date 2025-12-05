<template>
  <v-container class="migration-container">
    <v-card max-width="600" class="mx-auto">
      <v-card-title>帳號轉移</v-card-title>

      <!-- Step 1: 驗證 OTP -->
      <div v-if="step === 'verify-otp'">
        <v-card-text>
          <p>請輸入您收到的6位數驗證碼</p>
          <v-text-field
            v-model="otp"
            label="驗證碼"
            maxlength="6"
          />
        </v-card-text>
        <v-card-actions>
          <v-btn @click="verifyOTP" :loading="loading">驗證</v-btn>
        </v-card-actions>
      </div>

      <!-- Step 2: 更新個人資訊 + 設定密碼 -->
      <div v-if="step === 'update-info'">
        <v-card-text>
          <v-alert type="info" class="mb-4">
            請確認並更新您的個人資訊，並設定新的登入密碼
          </v-alert>

          <v-text-field v-model="userInfo.full_name" label="姓名" />
          <v-text-field v-model="userInfo.phone" label="聯絡電話" />
          <v-text-field v-model="userInfo.phone_ext" label="分機" />
          <v-text-field v-model="userInfo.mobile" label="手機" />

          <v-divider class="my-4" />

          <v-text-field
            v-model="newPassword"
            label="新密碼"
            type="password"
            hint="至少8字元，需包含以下4項中至少3項：數字、大寫、小寫、特殊符號"
            persistent-hint
          />
          <v-text-field
            v-model="confirmPassword"
            label="確認密碼"
            type="password"
          />
        </v-card-text>
        <v-card-actions>
          <v-btn @click="completeMigration" :loading="loading">完成轉移</v-btn>
        </v-card-actions>
      </div>

      <!-- Step 3: 完成 -->
      <div v-if="step === 'completed'">
        <v-card-text>
          <v-alert type="success">
            帳號轉移成功！3秒後將跳轉至登入頁面...
          </v-alert>
        </v-card-text>
      </div>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiService } from '@/services/api/http'
import { USERS } from '@/services/api/endpoints'

// 類型定義
interface UserInfo {
  username?: string
  full_name: string
  email?: string
  office_name?: string
  department?: string
  job_title?: string
  phone: string
  phone_ext: string
  mobile: string
}

interface OTPVerifyResponse {
  message: string
  success: boolean
  user_info: UserInfo
}

interface MigrationCompleteResponse {
  message: string
  success: boolean
}

interface ValidationError {
  loc: string[]
  msg: string
  type: string
}

const route = useRoute()
const router = useRouter()

const token = ref(route.query.token as string)
const step = ref('verify-otp')
const loading = ref(false)

const otp = ref('')
const userInfo = ref<UserInfo>({
  full_name: '',
  phone: '',
  phone_ext: '',
  mobile: ''
})

const newPassword = ref('')
const confirmPassword = ref('')

const verifyOTP = async () => {
  loading.value = true
  try {
    const response = await apiService.post<OTPVerifyResponse>(USERS.MIGRATE_VERIFY_OTP, {
      token: token.value,
      otp: otp.value
    })

    if (response.success) {
      // 填充使用者資訊
      userInfo.value = response.user_info
      step.value = 'update-info'
    }
  } catch {
    alert('驗證碼錯誤或已過期')
  } finally {
    loading.value = false
  }
}

const completeMigration = async () => {
  console.log('=== completeMigration START ===')
  console.log('Current state:', {
    token: token.value,
    otp: otp.value,
    userInfo: userInfo.value,
    newPassword: newPassword.value ? '***' : '(empty)',
    confirmPassword: confirmPassword.value ? '***' : '(empty)'
  })

  if (newPassword.value !== confirmPassword.value) {
    alert('密碼與確認密碼不符')
    return
  }

  loading.value = true
  try {
    // 準備請求資料：只發送非空值
    const payload: Record<string, string> = {
      token: token.value,
      otp: otp.value,
      new_password: newPassword.value,
      confirm_password: confirmPassword.value
    }

    // 只添加有值的欄位
    if (userInfo.value.full_name) payload.full_name = userInfo.value.full_name
    if (userInfo.value.phone) payload.phone = userInfo.value.phone
    if (userInfo.value.phone_ext) payload.phone_ext = userInfo.value.phone_ext
    if (userInfo.value.mobile) payload.mobile = userInfo.value.mobile

    console.log('Migration payload:', payload)
    console.log('Sending request to:', USERS.MIGRATE)

    const response = await apiService.post<MigrationCompleteResponse>(USERS.MIGRATE, payload)

    if (response.success) {
      step.value = 'completed'

      // 3秒後跳轉登入頁
      setTimeout(() => {
        router.push('/login')
      }, 3000)
    }
  } catch (error: any) {
    console.error('=== Migration error ===')
    console.error('Full error object:', error)
    console.error('Response data:', error?.response?.data)
    console.error('Response status:', error?.response?.status)

    // 處理 Pydantic 驗證錯誤（422）
    let errorMessage = '轉移失敗，請稍後再試'
    if (error?.response?.data?.detail) {
      const detail = error.response.data.detail
      console.log('Error detail:', detail)

      if (Array.isArray(detail)) {
        // Pydantic 驗證錯誤格式
        errorMessage = detail.map((err: ValidationError) =>
          `${err.loc?.join('.') || '欄位'}: ${err.msg}`
        ).join('\n')
      } else if (typeof detail === 'string') {
        errorMessage = detail
      } else {
        // 其他格式，直接 JSON 化
        errorMessage = JSON.stringify(detail, null, 2)
      }
    }

    console.error('Final error message:', errorMessage)
    alert(errorMessage)
  } finally {
    loading.value = false
  }
}
</script>

<route lang="yaml">
meta:
  layout: auth
  public: true
</route>
