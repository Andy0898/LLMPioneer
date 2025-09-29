// Mock API functions for authentication
// In a real application, these would make actual HTTP requests

import type { LoginCredentials, AuthResponse } from '@/types'

export const authApi = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    // Mock login - in real app this would be an HTTP request
    console.log('Mock login attempt:', credentials)
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Mock successful response
    return {
      access_token: 'mock_token_' + Date.now(),
      user: {
        id: '1',
        username: credentials.username,
        email: `${credentials.username}@example.com`,
        roles: [
          {
            id: '1',
            name: credentials.portal === 'admin' ? 'admin' : 'user'
          }
        ],
        permissions: [
          {
            id: '1',
            resource: 'dashboard',
            action: 'read'
          }
        ]
      },
      expires_in: 3600
    }
  },

  async logout(): Promise<void> {
    // Mock logout
    console.log('Mock logout')
    await new Promise(resolve => setTimeout(resolve, 500))
  },

  async refreshToken(): Promise<{ access_token: string }> {
    // Mock token refresh
    console.log('Mock token refresh')
    await new Promise(resolve => setTimeout(resolve, 500))
    
    return {
      access_token: 'refreshed_token_' + Date.now()
    }
  }
}