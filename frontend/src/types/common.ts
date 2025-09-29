export interface ApiResponse<T = any> {
  data: T
  message?: string
  success: boolean
  timestamp: string
}

export interface PaginatedResponse<T = any> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export interface ErrorResponse {
  error: string
  message: string
  status_code: number
  timestamp: string
}

export interface MenuItem {
  id: string
  label: string
  icon?: string
  route?: string
  children?: MenuItem[]
  permission?: string
  badge?: string | number
}

export interface NotificationItem {
  id: string
  title: string
  message: string
  type: 'info' | 'success' | 'warning' | 'error'
  read: boolean
  created_at: string
  action_url?: string
}