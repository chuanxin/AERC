/**
 * router/index.ts
 *
 * Automatic routes for `./src/pages/*.vue`
 */

// Composables
import { createRouter, createWebHistory } from 'vue-router/auto'
import { setupLayouts } from 'virtual:generated-layouts'
import { routes } from 'vue-router/auto-routes'
import { createAuthMiddleware } from '@/services/navguardService'

// Define which routes are accessible without authentication
const publicRoutes = [
  '/login',
  '/login/reset',
  '/login/signup',
  '/login/migrate',
  // 注意：/login/change-password 刻意不列入 publicRoutes
  // 需要有效 JWT（已登入）才能訪問，navguard 會攔截未登入者
]

// Create auth middleware
const authGuard = createAuthMiddleware({
  publicRoutes,
  loginRedirectPath: '/login',
  onAuthFailure: (to, from) => {
    // Optional: Show a notification to the user
    console.log('Authentication required. Redirecting to login page.')
  }
})

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL || '/'),
  routes: setupLayouts(routes),
  scrollBehavior(to, from, savedPosition) {
    // 如果有保存的位置（例如使用瀏覽器的前進/後退按鈕），則滾動到該位置
    if (savedPosition) {
      return savedPosition
    }
    // 如果路由有 hash（例如 #section），則滾動到該元素
    if (to.hash) {
      return { el: to.hash, behavior: 'smooth' }
    }
    // 否則滾動到頂部
    return { top: 0, behavior: 'smooth' }
  }
})

// TODO: fix Docker Container Route Navigation Double-Click Issue
// Issue: After Docker image rebuild, every first-time visited route requires double-click to navigate successfully
// Root Cause: authGuard middleware blocks navigation due to async fetchCurrentUser() calls failing/hanging after container restart
// Impact: Poor UX - users must click twice on every new route after deployment
// Priority: High - affects core navigation functionality
// Solution: Implement authentication state caching and Docker restart detection in navguardService.ts
// Register global navigation guard
router.beforeEach(authGuard)

// Workaround for https://github.com/vitejs/vite/issues/11804
router.onError((err, to) => {
  if (err?.message?.includes?.('Failed to fetch dynamically imported module')) {
    if (!localStorage.getItem('vuetify:dynamic-reload')) {
      console.log('Reloading page to fix dynamic import error')
      localStorage.setItem('vuetify:dynamic-reload', 'true')
      location.assign(to.fullPath)
    } else {
      console.error('Dynamic import error, reloading page did not fix it', err)
    }
  } else {
    console.error(err)
  }
})

router.isReady().then(() => {
  localStorage.removeItem('vuetify:dynamic-reload')
})

export default router
