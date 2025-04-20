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
    publicRoutes = ['/login'],
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

        // User is authenticated, proceed
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

    // User has token and is already authenticated
    return next();
  };
}
