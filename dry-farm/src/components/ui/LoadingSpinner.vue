<template>
  <div :class="['spinner', sizeClass]">
    <div class="spinner-border" role="status">
      <span class="sr-only">載入中...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md'
})

const sizeClass = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'spinner-sm'
    case 'lg':
      return 'spinner-lg'
    default:
      return 'spinner-md'
  }
})
</script>

<style scoped>
.spinner {
  @apply inline-block;
}

.spinner-border {
  @apply border-2 border-solid border-current border-r-transparent rounded-full animate-spin;
}

.spinner-sm .spinner-border {
  @apply w-4 h-4;
}

.spinner-md .spinner-border {
  @apply w-6 h-6;
}

.spinner-lg .spinner-border {
  @apply w-8 h-8;
}

.sr-only {
  @apply sr-only;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
