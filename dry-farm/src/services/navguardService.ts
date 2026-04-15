import type { NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { useUserStore } from '@/stores/users'

export interface AuthMiddlewareOptions {
  // Routes that don't require authentication
  publicRoutes?: string[];
  // Custom redirection path (defaults to /login)
  loginRedirectPath?: string;
  // Callback for custom handling before redirection
  onAuthFailure?: (to: RouteLocationNormalized, from: RouteLocationNormalized) => void;
}

/**
 * Authentication middleware factory
 * Creates a navigation guard that checks if the user is authenticated
 */
export function createAuthMiddleware(options: AuthMiddlewareOptions = {}) {
  const {
    publicRoutes = [],  // 預設為空陣列，強制在 router 中定義
    loginRedirectPath = '/login',
    onAuthFailure
  } = options;

  return async function authMiddleware(
    to: RouteLocationNormalized,
    from: RouteLocationNormalized,
    next: NavigationGuardNext
  ) {
    // Skip auth check for public routes
    if (publicRoutes.includes(to.path) || to.matched.some(record => record.meta.public)) {
      return next();
    }

    const userStore = useUserStore();

    // Check if there's a token in localStorage
    const token = localStorage.getItem('auth_token');

    // If no token at all, redirect to login
    if (!token) {
      if (onAuthFailure) {
        onAuthFailure(to, from);
      }
      return next({
        path: loginRedirectPath,
        query: { redirect: to.fullPath } // To redirect back after login
      });
    }

    // If there's a token but no current user, try to fetch the user
    // （頁面 Refresh 場景：fetchCurrentUser 會從 /users/whoami 重建 passwordExpired 狀態）
    if (token && !userStore.currentUser) {
      try {
        // Try to fetch current user
        const user = await userStore.fetchCurrentUser();

        // If user fetching fails, redirect to login
        if (!user) {
          if (onAuthFailure) {
            onAuthFailure(to, from);
          }
          return next({
            path: loginRedirectPath,
            query: { redirect: to.fullPath }
          });
        }

        // fetch 完成後檢查密碼過期（Refresh 後的主要攔截點）
        if (userStore.passwordExpired && !to.path.startsWith('/login')) {
          return next({ path: '/login/change-password' });
        }

        // User is authenticated and password not expired, proceed
        return next();
      } catch {
        // Error fetching user, redirect to login
        if (onAuthFailure) {
          onAuthFailure(to, from);
        }
        return next({
          path: loginRedirectPath,
          query: { redirect: to.fullPath }
        });
      }
    }

    // 密碼過期攔截（已認證使用者在頁面間導航的場景）
    if (userStore.passwordExpired && !to.path.startsWith('/login')) {
      return next({ path: '/login/change-password' });
    }

    // User has token and is already authenticated
    return next();
  };
}
