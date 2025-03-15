<template>
  <v-app-bar class="px-3">
    <v-spacer />

    <v-btn
      :prepend-icon="themeStore.theme === 'light' ? 'mdi-weather-sunny' : 'mdi-weather-night'"
      text="Toggle Theme"
      slim
      @click="themeStore.toggleTheme"
    />
  </v-app-bar>
</template>

<script lang="ts" setup>
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()
</script>
