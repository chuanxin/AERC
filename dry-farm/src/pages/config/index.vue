<template>
  <v-container
    fluid
    class="grants-container px-6 pb-0 pt-0"
    style="background-color: white"
  >
    <v-empty-state
      headline="No Messages Yet"
      text="You haven't received any messages yet. When you do, they'll appear here."
      title="Check back later."
      min-height="400"
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

