<template>
  <v-container class="verify-email-container">
    <v-card
      max-width="450"
      class="mx-auto"
      rounded
    >
      <v-card-title>Email 驗證</v-card-title>

      <v-card-text>
        <div
          v-if="loading"
          class="d-flex flex-column align-center py-6"
        >
          <v-progress-circular
            indeterminate
            color="primary"
          />
          <p class="mt-4">驗證中，請稍候...</p>
        </div>

        <v-alert
          v-else-if="success"
          type="success"
          rounded
        >
          驗證成功，已送出審核，請等待管理員核准通知。
        </v-alert>

        <v-alert
          v-else
          type="error"
          rounded
        >
          {{ errorMessage }}
        </v-alert>
      </v-card-text>

      <v-card-actions>
        <v-btn
          variant="outlined"
          rounded="lg"
          block
          :ripple="false"
          to="/login"
        >
          返回登入頁
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { userService } from '@/services/userService'

const route = useRoute()

const loading = ref(true)
const success = ref(false)
const errorMessage = ref('連結已過期或無效，請聯繫管理員重新發送驗證信。')

onMounted(async () => {
  const token = route.query.token as string | undefined

  if (!token) {
    loading.value = false
    success.value = false
    errorMessage.value = '缺少驗證連結所需的資訊，請確認連結完整無誤。'
    return
  }

  try {
    const response = await userService.verifyEmail(token)
    success.value = response.success
    if (!response.success) {
      errorMessage.value = response.message || errorMessage.value
    }
  } catch (error: unknown) {
    success.value = false
    const detail = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    errorMessage.value = typeof detail === 'string' ? detail : errorMessage.value
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.verify-email-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
}
</style>
