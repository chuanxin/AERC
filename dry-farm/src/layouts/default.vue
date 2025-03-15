<template>
  <v-app :theme="themeStore.theme">
    <NavBar />
    <VNavigationDrawer />
    <v-main>
      <router-view />
    </v-main>

    <!-- <AppFooter /> -->
  </v-app>
</template>

<script lang="ts" setup>
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()
</script>
