<template>
  <v-container>
    <h1>系統管理</h1>
    <p>{{ msg }}</p>
  </v-container>
</template>

<script lang="ts" setup>
import { apiService } from '@/services/http'

const msg = ref('')

const getMessage = async () => {
  try {
    msg.value = await apiService.get('/')
  } catch (error) {
    console.error('無法獲取測試訊息', error)
  }
}

onMounted(() => {
  getMessage()
})
</script>
