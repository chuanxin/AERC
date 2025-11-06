<template>
  <v-container
    fluid
    class="grants-container px-6 pb-0 pt-0"
    style="background-color: white"
  >
    <v-empty-state
      headline="帳號管理功能"
      title="頁面建置中"
      text="此系統功能頁提供使用者帳號管理、權限設定等功能。"
      min-height="400"
      icon="mdi-account-cog"
      @click:action="onClickAction"
    />
  </v-container>
</template>

<script lang="ts" setup>
import { apiService } from '@/services/api/http'

const msg = ref('')

const getMessage = async () => {
  try {
    msg.value = await apiService.get('/')
  } catch (error) {
    console.error('無法獲取測試訊息', error)
  }
}

function onClickAction () {
    alert('此功能開發中，敬請期待')
  }

onMounted(() => {
  getMessage()
})
</script>

