<template>
  <v-chip :color="isUrgent ? 'error' : 'primary'" :size="size">
    <v-icon start>mdi-clock</v-icon>
    {{ display }}
  </v-chip>
</template>

<script setup lang="ts">
defineProps<{
  display: string
  isUrgent: boolean
  size?: 'small' | 'default' | 'large'
}>()
</script>
