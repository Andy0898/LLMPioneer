import { defineStore } from 'pinia'
import { ref, computed, readonly } from 'vue'
import type { User, AuthState, LoginCredentials, Permission } from '@/types'
import { authApi } from '@/api/auth'
import router from '@/router'
import { ElMessage } from 'element-plus'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const portal = ref<'admin' | 'consumer' | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const permissions = computed(() => user.value?.permissions || [])
  const roles = computed(() => user.value?.roles || [])
  const isAdmin = computed(() => roles.value.some(role => role.name === 'admin' || role.name === 'super_admin'))

  // Actions
  const login = async (credentials: LoginCredentials) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await authApi.login(credentials)
      
      // Store authentication data
      token.value = response.access_token
      user.value = response.user
      portal.value = credentials.portal
      
      // Store token in localStorage for persistence
      localStorage.setItem('auth_token', response.access_token)
      localStorage.setItem('auth_portal', credentials.portal)
      localStorage.setItem('auth_user', JSON.stringify(response.user))
      
      ElMessage.success('Login successful!')
      
      // Redirect to appropriate dashboard
      const dashboardRoute = credentials.portal === 'admin' ? '/admin/dashboard' : '/user/dashboard'
      await router.push(dashboardRoute)
      
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Login failed'
      ElMessage.error(error.value || 'Login failed')
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    try {
      if (token.value) {
        await authApi.logout()
      }
    } catch (err) {
      console.warn('Logout API call failed:', err)
    } finally {
      // Clear all authentication data
      user.value = null
      token.value = null
      portal.value = null
      error.value = null
      
      // Clear localStorage
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_portal')
      localStorage.removeItem('auth_user')
      
      // Redirect to login
      await router.push('/user/login')
      
      ElMessage.success('Logged out successfully')
    }
  }

  const refreshToken = async () => {
    try {
      if (!token.value) return false
      
      const response = await authApi.refreshToken()
      token.value = response.access_token
      
      // Update localStorage
      localStorage.setItem('auth_token', response.access_token)
      
      return true
    } catch (err) {
      console.error('Token refresh failed:', err)
      await logout()
      return false
    }
  }

  const checkAuthStatus = () => {
    // Check localStorage for existing authentication
    const storedToken = localStorage.getItem('auth_token')
    const storedPortal = localStorage.getItem('auth_portal') as 'admin' | 'consumer' | null
    const storedUser = localStorage.getItem('auth_user')
    
    if (storedToken && storedPortal && storedUser) {
      try {
        token.value = storedToken
        portal.value = storedPortal
        user.value = JSON.parse(storedUser)
        
        // Verify token validity with server
        refreshToken()
      } catch (err) {
        console.error('Failed to restore auth state:', err)
        logout()
      }
    }
  }

  const checkPermission = (permissionName: string): boolean => {
    if (!user.value) return false
    
    return permissions.value.some(permission => {
      const [resource, action] = permissionName.split(':')
      return permission.resource === resource && permission.action === action
    })
  }

  const hasRole = (roleName: string): boolean => {
    if (!user.value) return false
    return roles.value.some(role => role.name === roleName)
  }

  const hasAnyRole = (roleNames: string[]): boolean => {
    if (!user.value) return false
    return roleNames.some(roleName => hasRole(roleName))
  }

  const updateUser = (userData: Partial<User>) => {
    if (user.value) {
      user.value = { ...user.value, ...userData }
      localStorage.setItem('auth_user', JSON.stringify(user.value))
    }
  }

  const clearError = () => {
    error.value = null
  }

  // Initialize auth state on store creation
  checkAuthStatus()

  return {
    // State
    user: readonly(user),
    token: readonly(token),
    portal: readonly(portal),
    isLoading: readonly(isLoading),
    error: readonly(error),
    
    // Getters
    isAuthenticated,
    permissions,
    roles,
    isAdmin,
    
    // Actions
    login,
    logout,
    refreshToken,
    checkAuthStatus,
    checkPermission,
    hasRole,
    hasAnyRole,
    updateUser,
    clearError
  }
})