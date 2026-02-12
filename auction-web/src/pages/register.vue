<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" sm="6" md="4">
        <v-card class="mt-12">
          <v-card-title class="text-h5 text-center">Register</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="submit">
              <v-text-field v-model="form.email" label="Email" type="email" variant="outlined" />
              <v-text-field v-model="form.username" label="Username" variant="outlined" />
              <v-text-field v-model="form.password" label="Password" type="password" variant="outlined" />
              <v-alert v-if="error" type="error" density="compact" class="mb-4">{{ error }}</v-alert>
              <v-btn type="submit" color="primary" size="large" block :loading="loading">Register</v-btn>
            </v-form>
            <div class="text-center mt-4">
              <router-link to="/login">Already have an account? Login</router-link>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { userService } from '@/services/userService'

const router = useRouter()
const form = reactive({ email: '', username: '', password: '' })
const error = ref('')
const loading = ref(false)

async function submit() {
  loading.value = true
  error.value = ''
  try {
    await userService.register(form)
    router.push('/login')
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>
