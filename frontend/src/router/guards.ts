import type { RouteLocationNormalized } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export const requiresAuth = (to: RouteLocationNormalized) => {
  const authStore = useAuthStore()
  return authStore.isAuthenticated
}

export const requiresGuest = (to: RouteLocationNormalized) => {
  const authStore = useAuthStore()
  return !authStore.isAuthenticated
}

export const requiresRole = (role: string) => {
  return (to: RouteLocationNormalized) => {
    const authStore = useAuthStore()
    return authStore.user?.roles.some(userRole => userRole.name === role) || false
  }
}

export const requiresPermission = (permission: string) => {
  return (to: RouteLocationNormalized) => {
    const authStore = useAuthStore()
    return authStore.checkPermission(permission)
  }
}

export const requiresPortal = (portal: 'admin' | 'consumer') => {
  return (to: RouteLocationNormalized) => {
    const authStore = useAuthStore()
    return authStore.portal === portal
  }
}

export const getRedirectPath = (userPortal: 'admin' | 'consumer' | null) => {
  switch (userPortal) {
    case 'admin':
      return '/admin/dashboard'
    case 'consumer':
      return '/user/dashboard'
    default:
      return '/user/login'
  }
}

export const getLoginPath = (portal: 'admin' | 'consumer') => {
  return portal === 'admin' ? '/admin/login' : '/user/login'
}