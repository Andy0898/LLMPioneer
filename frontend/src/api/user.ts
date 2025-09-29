import { api } from './client'
import type { 
  User, 
  Role, 
  Permission,
  PaginatedResponse 
} from '@/types'

export const userApi = {
  // User management
  getUsers: async (page: number = 1, size: number = 50, search?: string): Promise<PaginatedResponse<User>> => {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString()
    })
    
    if (search) {
      params.append('search', search)
    }
    
    const response = await api.get<PaginatedResponse<User>>(`/api/v1/manage/users?${params.toString()}`)
    return response.data
  },

  getUser: async (userId: string): Promise<User> => {
    const response = await api.get<User>(`/api/v1/manage/users/${userId}`)
    return response.data
  },

  createUser: async (userData: {
    username: string
    email: string
    password: string
    full_name?: string
    roles?: string[]
  }): Promise<User> => {
    const response = await api.post<User>('/api/v1/manage/users', userData)
    return response.data
  },

  updateUser: async (userId: string, updates: Partial<User>): Promise<User> => {
    const response = await api.put<User>(`/api/v1/manage/users/${userId}`, updates)
    return response.data
  },

  deleteUser: async (userId: string): Promise<void> => {
    await api.delete(`/api/v1/manage/users/${userId}`)
  },

  activateUser: async (userId: string): Promise<User> => {
    const response = await api.patch<User>(`/api/v1/manage/users/${userId}/activate`)
    return response.data
  },

  deactivateUser: async (userId: string): Promise<User> => {
    const response = await api.patch<User>(`/api/v1/manage/users/${userId}/deactivate`)
    return response.data
  },

  resetUserPassword: async (userId: string): Promise<{ temporary_password: string }> => {
    const response = await api.post<{ temporary_password: string }>(`/api/v1/manage/users/${userId}/reset-password`)
    return response.data
  },

  // User roles
  getUserRoles: async (userId: string): Promise<Role[]> => {
    const response = await api.get<Role[]>(`/api/v1/manage/users/${userId}/roles`)
    return response.data
  },

  assignUserRoles: async (userId: string, roleIds: string[]): Promise<User> => {
    const response = await api.post<User>(`/api/v1/manage/users/${userId}/roles`, {
      role_ids: roleIds
    })
    return response.data
  },

  removeUserRole: async (userId: string, roleId: string): Promise<User> => {
    const response = await api.delete<User>(`/api/v1/manage/users/${userId}/roles/${roleId}`)
    return response.data
  },

  // User permissions
  getUserPermissions: async (userId: string): Promise<Permission[]> => {
    const response = await api.get<Permission[]>(`/api/v1/manage/users/${userId}/permissions`)
    return response.data
  },

  // User statistics
  getUserStats: async (): Promise<{
    total_users: number
    active_users: number
    inactive_users: number
    users_created_today: number
    users_created_this_week: number
    users_created_this_month: number
    recent_users: User[]
  }> => {
    const response = await api.get('/api/v1/manage/users/stats')
    return response.data
  },

  // Bulk operations
  bulkActivateUsers: async (userIds: string[]): Promise<{
    activated_count: number
    failed_ids: string[]
  }> => {
    const response = await api.post('/api/v1/manage/users/bulk-activate', {
      user_ids: userIds
    })
    return response.data
  },

  bulkDeactivateUsers: async (userIds: string[]): Promise<{
    deactivated_count: number
    failed_ids: string[]
  }> => {
    const response = await api.post('/api/v1/manage/users/bulk-deactivate', {
      user_ids: userIds
    })
    return response.data
  },

  bulkDeleteUsers: async (userIds: string[]): Promise<{
    deleted_count: number
    failed_ids: string[]
  }> => {
    const response = await api.post('/api/v1/manage/users/bulk-delete', {
      user_ids: userIds
    })
    return response.data
  },

  // Export users
  exportUsers: async (format: 'csv' | 'xlsx' = 'csv'): Promise<Blob> => {
    const response = await api.get(`/api/v1/manage/users/export?format=${format}`, {
      responseType: 'blob'
    })
    return response.data
  }
}

export const roleApi = {
  // Role management
  getRoles: async (): Promise<Role[]> => {
    const response = await api.get<Role[]>('/api/v1/manage/roles')
    return response.data
  },

  getRole: async (roleId: string): Promise<Role> => {
    const response = await api.get<Role>(`/api/v1/manage/roles/${roleId}`)
    return response.data
  },

  createRole: async (roleData: {
    name: string
    description?: string
    permissions?: string[]
  }): Promise<Role> => {
    const response = await api.post<Role>('/api/v1/manage/roles', roleData)
    return response.data
  },

  updateRole: async (roleId: string, updates: Partial<Role>): Promise<Role> => {
    const response = await api.put<Role>(`/api/v1/manage/roles/${roleId}`, updates)
    return response.data
  },

  deleteRole: async (roleId: string): Promise<void> => {
    await api.delete(`/api/v1/manage/roles/${roleId}`)
  },

  // Role permissions
  getRolePermissions: async (roleId: string): Promise<Permission[]> => {
    const response = await api.get<Permission[]>(`/api/v1/manage/roles/${roleId}/permissions`)
    return response.data
  },

  assignRolePermissions: async (roleId: string, permissionIds: string[]): Promise<Role> => {
    const response = await api.post<Role>(`/api/v1/manage/roles/${roleId}/permissions`, {
      permission_ids: permissionIds
    })
    return response.data
  },

  removeRolePermission: async (roleId: string, permissionId: string): Promise<Role> => {
    const response = await api.delete<Role>(`/api/v1/manage/roles/${roleId}/permissions/${permissionId}`)
    return response.data
  }
}

export const permissionApi = {
  // Permission management
  getPermissions: async (): Promise<Permission[]> => {
    const response = await api.get<Permission[]>('/api/v1/manage/permissions')
    return response.data
  },

  getPermission: async (permissionId: string): Promise<Permission> => {
    const response = await api.get<Permission>(`/api/v1/manage/permissions/${permissionId}`)
    return response.data
  },

  createPermission: async (permissionData: {
    name: string
    resource: string
    action: string
    description?: string
  }): Promise<Permission> => {
    const response = await api.post<Permission>('/api/v1/manage/permissions', permissionData)
    return response.data
  },

  updatePermission: async (permissionId: string, updates: Partial<Permission>): Promise<Permission> => {
    const response = await api.put<Permission>(`/api/v1/manage/permissions/${permissionId}`, updates)
    return response.data
  },

  deletePermission: async (permissionId: string): Promise<void> => {
    await api.delete(`/api/v1/manage/permissions/${permissionId}`)
  },

  // Permission groups/resources
  getPermissionResources: async (): Promise<string[]> => {
    const response = await api.get<string[]>('/api/v1/manage/permissions/resources')
    return response.data
  },

  getPermissionActions: async (): Promise<string[]> => {
    const response = await api.get<string[]>('/api/v1/manage/permissions/actions')
    return response.data
  }
}