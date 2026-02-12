<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" sm="6" md="4">
        <v-card class="mt-12">
          <v-card-title class="text-h5 text-center">Login</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="submit">
              <v-text-field v-model="username" label="Username" variant="outlined" />
              <v-text-field v-model="password" label="Password" type="password" variant="outlined" />
              <v-alert v-if="error" type="error" density="compact" class="mb-4">{{ error }}</v-alert>
              <v-btn type="submit" color="primary" size="large" block :loading="loading">Login</v-btn>
            </v-form>
            <div class="text-center mt-4">
              <router-link to="/register">Don't have an account? Register</router-link>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  loading.value = true
  error.value = ''
  try {
    await auth.login({ username: username.value, password: password.value })
    router.push('/')
  } catch {
    error.value = 'Invalid credentials'
  } finally {
    loading.value = false
  }
}
</script>
