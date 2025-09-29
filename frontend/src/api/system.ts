import { api } from './client'
import type { SystemStats } from '@/types/admin'

export const systemApi = {
  // Get system statistics
  getSystemStats: () =>
    api.get<SystemStats>('/admin/system/stats'),

  // Clear error logs
  clearErrorLogs: () =>
    api.delete('/admin/system/logs'),

  // Get system health
  getSystemHealth: () =>
    api.get('/admin/system/health'),

  // Update system settings
  updateSystemSettings: (settings: Record<string, any>) =>
    api.put('/admin/system/settings', settings)
}