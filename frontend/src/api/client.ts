import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

// Create axios instance with base configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for auth token injection
apiClient.interceptors.request.use(
  (config) => {
    // Get auth token from localStorage (store might not be initialized yet)
    const token = localStorage.getItem('auth_token')
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Add request timestamp for debugging
    config.metadata = { startTime: Date.now() }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling and token refresh
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log response time for performance monitoring
    const endTime = Date.now()
    const startTime = response.config.metadata?.startTime || endTime
    const duration = endTime - startTime
    
    if (duration > 3000) {
      console.warn(`Slow API response: ${response.config.url} took ${duration}ms`)
    }
    
    return response
  },
  async (error) => {
    const originalRequest = error.config
    
    // Handle different error scenarios
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // Unauthorized - token expired or invalid
          if (!originalRequest._retry) {
            originalRequest._retry = true
            
            try {
              // Attempt to refresh token
              const authStore = useAuthStore()
              const refreshed = await authStore.refreshToken()
              
              if (refreshed) {
                // Retry the original request with new token
                const newToken = localStorage.getItem('auth_token')
                originalRequest.headers.Authorization = `Bearer ${newToken}`
                return apiClient(originalRequest)
              }
            } catch (refreshError) {
              // Refresh failed, redirect to login
              const authStore = useAuthStore()
              await authStore.logout()
              return Promise.reject(refreshError)
            }
          }
          
          // If retry failed or already tried, logout
          const authStore = useAuthStore()
          await authStore.logout()
          break
          
        case 403:
          // Forbidden - insufficient permissions
          ElMessage.error('You do not have permission to perform this action')
          break
          
        case 404:
          // Not found
          ElMessage.error('The requested resource was not found')
          break
          
        case 422:
          // Validation error
          if (data.detail && Array.isArray(data.detail)) {
            const errorMessages = data.detail.map((err: any) => 
              `${err.loc?.join(' -> ') || 'Field'}: ${err.msg}`
            ).join(', ')
            ElMessage.error(`Validation error: ${errorMessages}`)
          } else {
            ElMessage.error(data.message || 'Validation error occurred')
          }
          break
          
        case 429:
          // Rate limiting
          ElMessage.warning('Too many requests. Please try again later.')
          break
          
        case 500:
          // Server error
          ElMessage.error('Server error occurred. Please try again later.')
          break
          
        case 502:
        case 503:
        case 504:
          // Service unavailable
          ElMessage.error('Service temporarily unavailable. Please try again later.')
          break
          
        default:
          // Generic error
          ElMessage.error(data.message || `An error occurred (${status})`)
      }
    } else if (error.request) {
      // Network error
      ElMessage.error('Network error. Please check your connection and try again.')
    } else {
      // Request setup error
      ElMessage.error('Request failed to initialize')
    }
    
    return Promise.reject(error)
  }
)

// Helper function for handling file uploads with progress
export const uploadWithProgress = (
  url: string,
  formData: FormData,
  config: AxiosRequestConfig & { onUploadProgress?: (progress: any) => void } = {}
) => {
  return apiClient.post(url, formData, {
    ...config,
    headers: {
      ...config.headers,
      'Content-Type': 'multipart/form-data',
    },
  })
}

// Helper function for downloading files
export const downloadFile = async (url: string, filename?: string) => {
  try {
    const response = await apiClient.get(url, {
      responseType: 'blob',
    })
    
    // Create download link
    const blob = new Blob([response.data])
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = filename || 'download'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)
    
    return response
  } catch (error) {
    ElMessage.error('Failed to download file')
    throw error
  }
}

// Request/Response type definitions
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
  detail?: any
}

// API request wrapper with better typing
export const api = {
  get: <T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> =>
    apiClient.get(url, config),
    
  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> =>
    apiClient.post(url, data, config),
    
  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> =>
    apiClient.put(url, data, config),
    
  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> =>
    apiClient.patch(url, data, config),
    
  delete: <T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> =>
    apiClient.delete(url, config),
}

export default apiClient