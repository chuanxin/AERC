<template>
  <v-app>
    <v-app-bar color="primary" density="comfortable">
      <v-app-bar-nav-icon @click="drawer = !drawer" />
      <v-toolbar-title>
        <router-link to="/" class="text-white text-decoration-none">
          Auction Platform
        </router-link>
      </v-toolbar-title>
      <v-spacer />
      <template v-if="auth.isLoggedIn">
        <v-btn icon to="/user/my-bids">
          <v-icon>mdi-gavel</v-icon>
        </v-btn>
        <v-btn @click="auth.logout">Logout</v-btn>
      </template>
      <template v-else>
        <v-btn to="/login">Login</v-btn>
        <v-btn to="/register" variant="outlined">Register</v-btn>
      </template>
    </v-app-bar>

    <v-navigation-drawer v-model="drawer" temporary>
      <v-list nav>
        <v-list-item to="/" prepend-icon="mdi-home" title="Home" />
        <v-list-item to="/auctions" prepend-icon="mdi-shopping" title="Auctions" />
        <template v-if="auth.isLoggedIn">
          <v-divider />
          <v-list-item to="/user/my-bids" prepend-icon="mdi-gavel" title="My Bids" />
          <v-list-item to="/user/my-auctions" prepend-icon="mdi-storefront" title="My Auctions" />
          <v-list-item to="/auctions/create" prepend-icon="mdi-plus" title="Create Auction" />
        </template>
      </v-list>
    </v-navigation-drawer>

    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const drawer = ref(false)
const auth = useAuthStore()
</script>
