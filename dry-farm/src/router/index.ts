/**
 * router/index.ts
 *
 * Automatic routes for `./src/pages/*.vue`
 */

// Composables
import { createRouter, createWebHistory } from 'vue-router/auto'
import { setupLayouts } from 'virtual:generated-layouts'
import { routes } from 'vue-router/auto-routes'
import type {
  RouteLocationNormalized,
  NavigationGuardNext,
} from 'vue-router'
import { createAuthMiddleware } from '@/services/navguardService'
import { useUserStore } from '@/stores/users'

// ── Scroll Configuration ─────────────────────────────────────────────────────
// Fixed header height. Adjust if the layout header height changes.
export const SCROLL_PADDING = 0

/**
 * Scroll position — mirrors vue-router's return type for scrollBehavior, but
 * split out into a named type for readability.
 */
export type ScrollBehaviorPosition = {
  el?: string | HTMLElement
  x?: number
  y?: number
  top?: number
  left?: number
  behavior?: 'auto' | 'smooth' | 'instant'
}

/**
 * Controls scroll behavior for a specific route.
 *
 * @example
 * // In route meta:
 *   meta: { scrollBehavior: 'none' }    // disable scrolling entirely
 *   meta: { scrollBehavior: 'instant' } // no animation
 *   meta: { scrollBehavior: 'smooth' }  // explicit smooth (default)
 *   meta: { scrollBehavior: 'no-save' } // always go top, ignore browser history
 *   meta: { scrollBehavior: (to) => ({ top: 0 }) } // custom function
 */
export type RouteScrollBehavior =
  | 'none'
  | 'instant'
  | 'smooth'
  | 'no-save'
  | ((to: RouteLocationNormalized) => ScrollBehaviorPosition | null | undefined | Promise<ScrollBehaviorPosition | null | undefined>)

/**
 * Default scroll behavior — the "standard" case for most routes.
 *
 * Priority (matching vue-router docs):
 *   1. Saved position (browser forward/back)
 *   2. Route hash → target element (only if element exists in DOM)
 *   3. Scroll to top with padding for fixed header
 *
 * Returns null/undefined when the caller should skip scrolling
 * (e.g. modal routes that override behavior at the route level).
 */
export function defaultScrollBehavior(
  to: RouteLocationNormalized,
  _from: RouteLocationNormalized,
  savedPosition: ScrollBehaviorPosition | null,
): ScrollBehaviorPosition | false | void {
  if (savedPosition) {
    return savedPosition
  }

  if (to.hash) {
    try {
      const target = document.querySelector(to.hash)
      if (target) {
        return { el: to.hash, behavior: 'smooth', top: 0 }
      }
    } catch {
      // querySelector should never throw; guard defensively.
    }
  }

  return { top: SCROLL_PADDING, behavior: 'smooth' }
}

/**
 * Resolve the scroll behavior for a route.
 *
 * 1. Route-level `meta.scrollBehavior` overrides everything.
 * 2. Fallback to `defaultScrollBehavior`.
 *
 * Returns `null` / `undefined` when scrolling should be skipped entirely.
 */
export function resolveScrollBehavior(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  savedPosition: ScrollBehaviorPosition | null,
): ScrollBehaviorPosition | false | void | Promise<ScrollBehaviorPosition | false | void> {
  // 1. Route-level override (function or string)
  if (typeof to.meta.scrollBehavior === 'function') {
    return to.meta.scrollBehavior(to)
  }

  const mode = to.meta.scrollBehavior as RouteScrollBehavior | undefined
  switch (mode) {
    case 'none':
      // `false` tells vue-router to skip scrolling entirely.
      return false
    case 'no-save':
      // Always go to top, regardless of browser history.
      return { top: SCROLL_PADDING, behavior: 'smooth' }
    case 'instant':
      return defaultScrollBehavior(to, from, savedPosition)
    case 'smooth':
    case undefined:
    default:
      return defaultScrollBehavior(to, from, savedPosition)
  }
}

// ── Public Routes (no auth required) ────────────────────────────────────────
const publicRoutes = [
  '/login',
  '/login/reset',
  '/login/signup',
  '/login/migrate',
  // 注意：/login/change-password 刻意不列入 publicRoutes
  // 需要有效 JWT（已登入）才能訪問，navguard 會攔截未登入者
  '/verify-email', // 039-account-verification-profile：驗證信連結落地頁，token 本身即為憑證
]

// ── Auth Middleware ──────────────────────────────────────────────────────────
const authGuard = createAuthMiddleware({
  publicRoutes,
  loginRedirectPath: '/login',
  onAuthFailure: () => {
    console.log('Authentication required. Redirecting to login page.')
  },
})

// ── Route Role Guard ────────────────────────────────────────────────────────
// 路由准入規則：每條路由對應後端 DEFAULT_ROLE_PERMISSIONS 矩陣中的一個 module.action
// 前端不再 hardcode allowedRoles — 由後端 /users/whoami 回傳的 permissions_summary 驅動
// TD-014 Phase A: 新增受限路由只需在此加一條 requiredPermission，不再需要同步修改後端
type RouteRule = {
  requiredPermission: { module: string; action: string }
  redirectTo: string | ((from: RouteLocationNormalized) => string)
}

const ROLE_RESTRICTED_ROUTES: Record<string, RouteRule> = {
  '/statistics': { requiredPermission: { module: 'reports', action: 'view' }, redirectTo: '/403' },
  '/grants/query': { requiredPermission: { module: 'batch_print', action: 'view' }, redirectTo: '/403' },
  '/config/accounts': {
    requiredPermission: { module: 'users', action: 'view' },
    redirectTo: (from) => (from.name != null ? from.path : '/'),
  },
  '/config/security': { requiredPermission: { module: 'security', action: 'view' }, redirectTo: '/403' },
  '/budget': { requiredPermission: { module: 'reports', action: 'view' }, redirectTo: '/403' },
}

function roleGuard(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext,
) {
  if (to.path === '/403') return next()

  const rule = Object.entries(ROLE_RESTRICTED_ROUTES).find(([prefix]) =>
    to.path === prefix || to.path.startsWith(prefix + '/'),
  )
  if (!rule) return next()

  const [, { requiredPermission, redirectTo }] = rule

  // authGuard（async）先於 roleGuard 執行，fetchCurrentUser 已完成，store 已就緒
  const modules = useUserStore().currentUser?.permissions_summary?.modules ?? {}
  const allowed = (modules[requiredPermission.module] ?? []).includes(requiredPermission.action)

  if (!allowed) {
    const target = typeof redirectTo === 'function' ? redirectTo(from) : redirectTo
    return next(target)
  }
  return next()
}

// ── Router Instance ──────────────────────────────────────────────────────────
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL || '/'),
  routes: setupLayouts(routes),
  scrollBehavior: resolveScrollBehavior,
})

// TODO: fix Docker Container Route Navigation Double-Click Issue
// Issue: After Docker image rebuild, every first-time visited route requires double-click to navigate successfully
// Root Cause: authGuard middleware blocks navigation due to async fetchCurrentUser() calls failing/hanging after container restart
// Impact: Poor UX - users must click twice on every new route after deployment
// Priority: High - affects core navigation functionality
// Solution: Implement authentication state caching and Docker restart detection in navguardService.ts
// Register global navigation guards
router.beforeEach(authGuard)
router.beforeEach(roleGuard)

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
