export interface User {
  id: string
  username: string
  email: string
  full_name?: string
  roles: Role[]
  permissions: Permission[]
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Role {
  id: string
  name: string
  description?: string
  permissions: Permission[]
  is_active: boolean
}

export interface Permission {
  id: string
  name: string
  resource: string
  action: string
  description?: string
}

export interface LoginCredentials {
  username: string
  password: string
  portal: 'admin' | 'consumer'
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  permissions: Permission[]
  portal: 'admin' | 'consumer' | null
}