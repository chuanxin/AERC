/**
 * main.ts
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */

// Plugins
import { registerPlugins } from '@/plugins'

// Components
import App from './App.vue'

// Composables
import { createApp } from 'vue'
import { useUserStore } from '@/stores/users'

// FontAwesome
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { fas } from '@fortawesome/free-solid-svg-icons' // 引入 Solid 圖示
import { far } from '@fortawesome/free-regular-svg-icons' // 引入 Regular 圖示
import { fab } from '@fortawesome/free-brands-svg-icons' // 引入 Brands 圖示

library.add(fas, far, fab)

// Create the Vue application
const app = createApp(App)

// Register plugins (Pinia, Router, Vuetify, etc.)
registerPlugins(app)

app.component('fai', FontAwesomeIcon)

// Initialize authentication, but mount the app immediately
// Don't wait for authentication to complete
app.mount('#app')

// After app is mounted, attempt to restore user session
// This ensures the app loads quickly even if API is slow
const initializeAuth = async () => {
  try {
    // Access the user store
    const userStore = useUserStore()

    // Attempt to log in with stored token if available
    // This is non-blocking - the app will already be mounted
    await userStore.attemptAutoLogin()
  } catch (error) {
    console.error('Failed to initialize authentication:', error)
    // App continues to function even if auth initialization fails
  }
}

// Start authentication initialization
initializeAuth()
