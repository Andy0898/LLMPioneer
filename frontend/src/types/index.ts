// Basic type definitions for the application

export interface User {
  id: string
  username: string
  email: string
  roles: Role[]
  permissions: Permission[]
  profile?: UserProfile
}

export interface Role {
  id: string
  name: string
  description?: string
}

export interface Permission {
  id: string
  resource: string
  action: string
  description?: string
}

export interface UserProfile {
  firstName?: string
  lastName?: string
  avatar?: string
  phone?: string
}

export interface AuthState {
  user: User | null
  token: string | null
  portal: 'admin' | 'consumer' | null
  isLoading: boolean
  error: string | null
}

export interface LoginCredentials {
  username: string
  password: string
  portal: 'admin' | 'consumer'
}

export interface AuthResponse {
  access_token: string
  user: User
  expires_in: number
}