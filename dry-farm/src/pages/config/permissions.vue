<template>
  <v-container
    fluid
    class="grants-container px-6 pb-0 pt-0"
    style="background-color: white"
  >
    <v-empty-state
      headline="群組權限管理功能"
      title="頁面建置中"
      text="此系統功能頁提供帳號群組管理、權限設定等功能。"
      min-height="400"
      icon="mdi-shield-account"
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
    alert('You clicked the action button')
  }

onMounted(() => {
  getMessage()
})
</script>

