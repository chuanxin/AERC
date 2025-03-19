<template>
  <v-app :theme="themeStore.theme">
    <router-view />
  </v-app>
</template>

<script lang="ts" setup>
  import { useThemeStore } from '@/stores/theme'

  const themeStore = useThemeStore()
</script>

<style scoped>

</style>
