import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import type { User, LoginCredentials } from '@/types/auth'

// Mock the API
vi.mock('@/api', () => ({
  authApi: {
    login: vi.fn(),
    logout: vi.fn(),
    getCurrentUser: vi.fn(),
    refreshToken: vi.fn()
  }
}))

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}
vi.stubGlobal('localStorage', localStorageMock)

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  const mockUser: User = {
    id: '1',
    username: 'testuser',
    email: 'test@example.com',
    roles: [{ id: '1', name: 'user', permissions: ['read'] }],
    permissions: ['read'],
    avatar: 'avatar.jpg'
  }

  const mockCredentials: LoginCredentials = {
    username: 'testuser',
    password: 'password123'
  }

  it('initializes with default state', () => {
    const authStore = useAuthStore()
    
    expect(authStore.user).toBeNull()
    expect(authStore.token).toBeNull()
    expect(authStore.refreshToken).toBeNull()
    expect(authStore.isAuthenticated).toBe(false)
    expect(authStore.portal).toBeNull()
  })

  it('handles successful login', async () => {
    const { authApi } = await import('@/api')
    vi.mocked(authApi.login).mockResolvedValue({
      data: {
        user: mockUser,
        token: 'access-token',
        refreshToken: 'refresh-token'
      }
    })

    const authStore = useAuthStore()
    await authStore.login(mockCredentials)

    expect(authStore.user).toEqual(mockUser)
    expect(authStore.token).toBe('access-token')
    expect(authStore.refreshToken).toBe('refresh-token')
    expect(authStore.isAuthenticated).toBe(true)
    expect(localStorageMock.setItem).toHaveBeenCalledWith('auth_token', 'access-token')
    expect(localStorageMock.setItem).toHaveBeenCalledWith('refresh_token', 'refresh-token')
  })

  it('handles login failure', async () => {
    const { authApi } = await import('@/api')
    vi.mocked(authApi.login).mockRejectedValue(new Error('Invalid credentials'))

    const authStore = useAuthStore()
    
    await expect(authStore.login(mockCredentials)).rejects.toThrow('Invalid credentials')
    expect(authStore.user).toBeNull()
    expect(authStore.token).toBeNull()
    expect(authStore.isAuthenticated).toBe(false)
  })

  it('handles logout', async () => {
    const { authApi } = await import('@/api')
    vi.mocked(authApi.logout).mockResolvedValue({ data: {} })

    const authStore = useAuthStore()
    
    // Set initial state
    authStore.user = mockUser
    authStore.token = 'access-token'
    authStore.refreshToken = 'refresh-token'

    await authStore.logout()

    expect(authStore.user).toBeNull()
    expect(authStore.token).toBeNull()
    expect(authStore.refreshToken).toBeNull()
    expect(authStore.isAuthenticated).toBe(false)
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token')
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token')
  })

  it('checks permissions correctly', () => {
    const authStore = useAuthStore()
    authStore.user = mockUser

    expect(authStore.checkPermission('read')).toBe(true)
    expect(authStore.checkPermission('write')).toBe(false)
  })

  it('checks roles correctly', () => {
    const authStore = useAuthStore()
    authStore.user = mockUser

    expect(authStore.hasRole('user')).toBe(true)
    expect(authStore.hasRole('admin')).toBe(false)
  })

  it('initializes from stored token', () => {
    localStorageMock.getItem.mockImplementation((key) => {
      if (key === 'auth_token') return 'stored-token'
      if (key === 'refresh_token') return 'stored-refresh-token'
      return null
    })

    const authStore = useAuthStore()
    authStore.initializeAuth()

    expect(authStore.token).toBe('stored-token')
    expect(authStore.refreshToken).toBe('stored-refresh-token')
  })

  it('handles token refresh', async () => {
    const { authApi } = await import('@/api')
    vi.mocked(authApi.refreshToken).mockResolvedValue({
      data: {
        token: 'new-access-token',
        refreshToken: 'new-refresh-token'
      }
    })

    const authStore = useAuthStore()
    authStore.refreshToken = 'old-refresh-token'

    await authStore.refreshTokens()

    expect(authStore.token).toBe('new-access-token')
    expect(authStore.refreshToken).toBe('new-refresh-token')
    expect(localStorageMock.setItem).toHaveBeenCalledWith('auth_token', 'new-access-token')
    expect(localStorageMock.setItem).toHaveBeenCalledWith('refresh_token', 'new-refresh-token')
  })

  it('handles failed token refresh', async () => {
    const { authApi } = await import('@/api')
    vi.mocked(authApi.refreshToken).mockRejectedValue(new Error('Refresh failed'))

    const authStore = useAuthStore()
    authStore.token = 'old-token'
    authStore.refreshToken = 'old-refresh-token'

    await expect(authStore.refreshTokens()).rejects.toThrow('Refresh failed')
    
    // Should clear auth state on refresh failure
    expect(authStore.token).toBeNull()
    expect(authStore.refreshToken).toBeNull()
  })

  it('gets current user', async () => {
    const { authApi } = await import('@/api')
    vi.mocked(authApi.getCurrentUser).mockResolvedValue({
      data: mockUser
    })

    const authStore = useAuthStore()
    await authStore.getCurrentUser()

    expect(authStore.user).toEqual(mockUser)
  })
})