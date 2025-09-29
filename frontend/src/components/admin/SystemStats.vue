<template>
  <div class="system-stats">
    <!-- Header Section -->
    <div class="stats-header">
      <h2 class="text-2xl font-bold text-gray-800 mb-2">System Statistics</h2>
      <p class="text-gray-600 mb-6">Real-time system performance and usage metrics</p>
      
      <!-- Refresh Controls -->
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center space-x-4">
          <el-switch
            v-model="autoRefresh"
            active-text="Auto Refresh"
            @change="handleAutoRefreshToggle"
          />
          <el-select v-model="refreshInterval" placeholder="Refresh Interval" style="width: 150px">
            <el-option label="5 seconds" :value="5000" />
            <el-option label="10 seconds" :value="10000" />
            <el-option label="30 seconds" :value="30000" />
            <el-option label="1 minute" :value="60000" />
          </el-select>
        </div>
        <el-button type="primary" @click="refreshStats" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh Now
        </el-button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !stats" class="flex justify-center items-center h-64">
      <el-loading></el-loading>
    </div>

    <!-- Stats Content -->
    <div v-else class="stats-content">
      <!-- Quick Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="stat-card">
          <div class="stat-icon bg-blue-500">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-content">
            <h3 class="stat-label">Total Users</h3>
            <p class="stat-value">{{ stats?.users?.total || 0 }}</p>
            <p class="stat-change" :class="getChangeClass(stats?.users?.change || 0)">
              {{ formatChange(stats?.users?.change || 0) }}
            </p>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon bg-green-500">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <div class="stat-content">
            <h3 class="stat-label">Active Conversations</h3>
            <p class="stat-value">{{ stats?.conversations?.active || 0 }}</p>
            <p class="stat-change" :class="getChangeClass(stats?.conversations?.change || 0)">
              {{ formatChange(stats?.conversations?.change || 0) }}
            </p>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon bg-yellow-500">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-content">
            <h3 class="stat-label">Knowledge Base Items</h3>
            <p class="stat-value">{{ stats?.knowledgeBase?.total || 0 }}</p>
            <p class="stat-change" :class="getChangeClass(stats?.knowledgeBase?.change || 0)">
              {{ formatChange(stats?.knowledgeBase?.change || 0) }}
            </p>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon bg-purple-500">
            <el-icon><Monitor /></el-icon>
          </div>
          <div class="stat-content">
            <h3 class="stat-label">System Uptime</h3>
            <p class="stat-value">{{ formatUptime(stats?.system?.uptime || 0) }}</p>
            <p class="stat-change text-green-600">{{ stats?.system?.status || 'Healthy' }}</p>
          </div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <!-- User Activity Chart -->
        <div class="chart-container">
          <h3 class="chart-title">User Activity (Last 7 Days)</h3>
          <div class="chart-content">
            <canvas ref="userActivityChart" width="400" height="200"></canvas>
          </div>
        </div>

        <!-- System Performance Chart -->
        <div class="chart-container">
          <h3 class="chart-title">System Performance</h3>
          <div class="chart-content">
            <div class="performance-metrics">
              <div class="metric">
                <label>CPU Usage</label>
                <el-progress 
                  :percentage="stats?.system?.cpu || 0" 
                  :color="getPerformanceColor(stats?.system?.cpu || 0)"
                />
              </div>
              <div class="metric">
                <label>Memory Usage</label>
                <el-progress 
                  :percentage="stats?.system?.memory || 0" 
                  :color="getPerformanceColor(stats?.system?.memory || 0)"
                />
              </div>
              <div class="metric">
                <label>Disk Usage</label>
                <el-progress 
                  :percentage="stats?.system?.disk || 0" 
                  :color="getPerformanceColor(stats?.system?.disk || 0)"
                />
              </div>
              <div class="metric">
                <label>Network I/O</label>
                <el-progress 
                  :percentage="stats?.system?.network || 0" 
                  :color="getPerformanceColor(stats?.system?.network || 0)"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Detailed Tables -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Recent Activities -->
        <div class="table-container">
          <h3 class="table-title">Recent Activities</h3>
          <el-table :data="stats?.activities || []" style="width: 100%" max-height="300">
            <el-table-column prop="timestamp" label="Time" width="120">
              <template #default="scope">
                {{ formatTime(scope.row.timestamp) }}
              </template>
            </el-table-column>
            <el-table-column prop="user" label="User" width="120" />
            <el-table-column prop="action" label="Action" />
            <el-table-column prop="status" label="Status" width="100">
              <template #default="scope">
                <el-tag 
                  :type="getStatusType(scope.row.status)" 
                  size="small"
                >
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- Top Users -->
        <div class="table-container">
          <h3 class="table-title">Most Active Users</h3>
          <el-table :data="stats?.topUsers || []" style="width: 100%" max-height="300">
            <el-table-column prop="rank" label="#" width="50" />
            <el-table-column prop="username" label="User" />
            <el-table-column prop="conversations" label="Conversations" width="120" align="center" />
            <el-table-column prop="lastActive" label="Last Active" width="120">
              <template #default="scope">
                {{ formatTime(scope.row.lastActive) }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <!-- Error Logs Section -->
      <div class="mt-8">
        <div class="table-container">
          <div class="flex items-center justify-between mb-4">
            <h3 class="table-title">Recent Error Logs</h3>
            <el-button type="danger" size="small" @click="clearErrorLogs">
              Clear Logs
            </el-button>
          </div>
          <el-table 
            :data="stats?.errorLogs || []" 
            style="width: 100%" 
            max-height="250"
            :row-class-name="getRowClassName"
          >
            <el-table-column prop="timestamp" label="Time" width="150">
              <template #default="scope">
                {{ formatDateTime(scope.row.timestamp) }}
              </template>
            </el-table-column>
            <el-table-column prop="level" label="Level" width="100">
              <template #default="scope">
                <el-tag 
                  :type="getLogLevelType(scope.row.level)" 
                  size="small"
                >
                  {{ scope.row.level.toUpperCase() }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="module" label="Module" width="120" />
            <el-table-column prop="message" label="Message" />
            <el-table-column label="Actions" width="100">
              <template #default="scope">
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="viewErrorDetails(scope.row)"
                >
                  Details
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>

    <!-- Error Details Modal -->
    <el-dialog 
      v-model="errorDetailsVisible" 
      title="Error Details" 
      width="60%"
      :before-close="handleCloseErrorDetails"
    >
      <div v-if="selectedError">
        <el-descriptions border :column="1">
          <el-descriptions-item label="Timestamp">
            {{ formatDateTime(selectedError.timestamp) }}
          </el-descriptions-item>
          <el-descriptions-item label="Level">
            <el-tag :type="getLogLevelType(selectedError.level)">
              {{ selectedError.level.toUpperCase() }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Module">
            {{ selectedError.module }}
          </el-descriptions-item>
          <el-descriptions-item label="Message">
            {{ selectedError.message }}
          </el-descriptions-item>
          <el-descriptions-item label="Stack Trace" v-if="selectedError.stackTrace">
            <pre class="error-stack">{{ selectedError.stackTrace }}</pre>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="errorDetailsVisible = false">Close</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Refresh, 
  User, 
  ChatDotRound, 
  Document, 
  Monitor 
} from '@element-plus/icons-vue'
import { systemApi } from '@/api'
import type { SystemStats } from '@/types/admin'

// Reactive state
const loading = ref(false)
const autoRefresh = ref(true)
const refreshInterval = ref(10000)
const stats = ref<SystemStats | null>(null)
const errorDetailsVisible = ref(false)
const selectedError = ref<any>(null)

// Chart references
const userActivityChart = ref<HTMLCanvasElement | null>(null)

// Auto refresh timer
let refreshTimer: NodeJS.Timeout | null = null

// Lifecycle
onMounted(async () => {
  await loadStats()
  if (autoRefresh.value) {
    startAutoRefresh()
  }
})

onUnmounted(() => {
  stopAutoRefresh()
})

// Watch for auto refresh changes
watch([autoRefresh, refreshInterval], () => {
  if (autoRefresh.value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
})

// Methods
const loadStats = async () => {
  try {
    loading.value = true
    const response = await systemApi.getSystemStats()
    stats.value = response.data
    
    // Update charts after data loads
    await nextTick()
    updateCharts()
  } catch (error) {
    console.error('Failed to load system stats:', error)
    ElMessage.error('Failed to load system statistics')
  } finally {
    loading.value = false
  }
}

const refreshStats = async () => {
  await loadStats()
  ElMessage.success('Statistics refreshed')
}

const startAutoRefresh = () => {
  stopAutoRefresh()
  refreshTimer = setInterval(() => {
    loadStats()
  }, refreshInterval.value)
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

const handleAutoRefreshToggle = () => {
  if (autoRefresh.value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

const updateCharts = () => {
  if (!userActivityChart.value || !stats.value) return
  
  // Simple chart implementation (in a real app, use Chart.js or similar)
  const ctx = userActivityChart.value.getContext('2d')
  if (!ctx) return
  
  // Clear canvas
  ctx.clearRect(0, 0, userActivityChart.value.width, userActivityChart.value.height)
  
  // Draw simple line chart for user activity
  const data = stats.value.userActivity || []
  if (data.length === 0) return
  
  const width = userActivityChart.value.width
  const height = userActivityChart.value.height
  const padding = 40
  
  ctx.strokeStyle = '#409EFF'
  ctx.lineWidth = 2
  ctx.beginPath()
  
  data.forEach((point, index) => {
    const x = padding + (index / (data.length - 1)) * (width - 2 * padding)
    const y = height - padding - (point.value / Math.max(...data.map(p => p.value))) * (height - 2 * padding)
    
    if (index === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  })
  
  ctx.stroke()
}

// Utility functions
const formatChange = (change: number): string => {
  const sign = change >= 0 ? '+' : ''
  return `${sign}${change}%`
}

const getChangeClass = (change: number): string => {
  if (change > 0) return 'text-green-600'
  if (change < 0) return 'text-red-600'
  return 'text-gray-600'
}

const formatUptime = (seconds: number): string => {
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  
  if (days > 0) return `${days}d ${hours}h`
  if (hours > 0) return `${hours}h ${minutes}m`
  return `${minutes}m`
}

const getPerformanceColor = (percentage: number): string => {
  if (percentage < 60) return '#67c23a'
  if (percentage < 80) return '#e6a23c'
  return '#f56c6c'
}

const formatTime = (timestamp: string): string => {
  return new Date(timestamp).toLocaleTimeString()
}

const formatDateTime = (timestamp: string): string => {
  return new Date(timestamp).toLocaleString()
}

const getStatusType = (status: string): string => {
  switch (status.toLowerCase()) {
    case 'success': return 'success'
    case 'error': return 'danger'
    case 'warning': return 'warning'
    default: return 'info'
  }
}

const getLogLevelType = (level: string): string => {
  switch (level.toLowerCase()) {
    case 'error': return 'danger'
    case 'warning': return 'warning'
    case 'info': return 'info'
    case 'debug': return ''
    default: return 'info'
  }
}

const getRowClassName = ({ row }: { row: any }): string => {
  if (row.level === 'error') return 'error-row'
  if (row.level === 'warning') return 'warning-row'
  return ''
}

const viewErrorDetails = (error: any) => {
  selectedError.value = error
  errorDetailsVisible.value = true
}

const handleCloseErrorDetails = () => {
  errorDetailsVisible.value = false
  selectedError.value = null
}

const clearErrorLogs = async () => {
  try {
    await ElMessageBox.confirm(
      'This will clear all error logs. Continue?',
      'Clear Error Logs',
      {
        confirmButtonText: 'Clear',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
    )
    
    await systemApi.clearErrorLogs()
    await loadStats()
    ElMessage.success('Error logs cleared successfully')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Failed to clear error logs')
    }
  }
}
</script>

<style scoped>
.system-stats {
  @apply p-6 bg-gray-50 min-h-screen;
}

.stats-header {
  @apply bg-white rounded-lg p-6 mb-6 shadow-sm;
}

.stat-card {
  @apply bg-white rounded-lg p-6 shadow-sm flex items-center space-x-4 hover:shadow-md transition-shadow;
}

.stat-icon {
  @apply w-12 h-12 rounded-lg flex items-center justify-center text-white text-xl;
}

.stat-content {
  @apply flex-1;
}

.stat-label {
  @apply text-sm text-gray-600 mb-1;
}

.stat-value {
  @apply text-2xl font-bold text-gray-800 mb-1;
}

.stat-change {
  @apply text-sm font-medium;
}

.chart-container {
  @apply bg-white rounded-lg p-6 shadow-sm;
}

.chart-title {
  @apply text-lg font-semibold text-gray-800 mb-4;
}

.chart-content {
  @apply h-48 flex items-center justify-center;
}

.performance-metrics {
  @apply space-y-4 w-full;
}

.metric {
  @apply space-y-2;
}

.metric label {
  @apply text-sm font-medium text-gray-700;
}

.table-container {
  @apply bg-white rounded-lg p-6 shadow-sm;
}

.table-title {
  @apply text-lg font-semibold text-gray-800 mb-4;
}

.error-stack {
  @apply bg-gray-100 p-3 rounded text-sm font-mono max-h-48 overflow-y-auto;
}

:deep(.error-row) {
  @apply bg-red-50;
}

:deep(.warning-row) {
  @apply bg-yellow-50;
}

:deep(.el-progress-bar__outer) {
  @apply bg-gray-200;
}
</style>