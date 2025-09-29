import { httpClient } from './http'
import type { SystemStats } from '@/types/admin'

export const systemApi = {
  // Get system statistics
  getSystemStats: () =>
    httpClient.get<SystemStats>('/admin/system/stats'),

  // Clear error logs
  clearErrorLogs: () =>
    httpClient.delete('/admin/system/logs'),

  // Get system health
  getSystemHealth: () =>
    httpClient.get('/admin/system/health'),

  // Update system settings
  updateSystemSettings: (settings: Record<string, any>) =>
    httpClient.put('/admin/system/settings', settings)
}