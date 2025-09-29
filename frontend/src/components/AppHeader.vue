<template>
  <el-header class="app-header" :class="portalClass">
    <div class="header-content">
      <!-- Logo and Title -->
      <div class="header-left">
        <div class="logo-section">
          <el-icon size="24" class="logo-icon">
            <component :is="logoIcon" />
          </el-icon>
          <h1 class="app-title">{{ title }}</h1>
        </div>
        
        <!-- Breadcrumb (optional) -->
        <el-breadcrumb v-if="breadcrumb?.length" separator="/" class="breadcrumb">
          <el-breadcrumb-item v-for="item in breadcrumb" :key="item">
            {{ item }}
          </el-breadcrumb-item>
        </el-breadcrumb>
      </div>

      <!-- Header Actions -->
      <div class="header-right">
        <!-- Search -->
        <div v-if="showSearch" class="search-section">
          <el-input
            v-model="searchQuery"
            placeholder="Search..."
            class="search-input"
            clearable
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <!-- Notifications -->
        <el-dropdown v-if="showNotifications" trigger="click" class="notification-dropdown">
          <el-badge :value="unreadCount" :hidden="!unreadCount" class="notification-badge">
            <el-button circle>
              <el-icon><Bell /></el-icon>
            </el-button>
          </el-badge>
          <template #dropdown>
            <el-dropdown-menu class="notification-menu">
              <div class="notification-header">
                <span>Notifications</span>
                <el-button 
                  v-if="unreadCount > 0" 
                  link 
                  size="small" 
                  @click="markAllAsRead"
                >
                  Mark all as read
                </el-button>
              </div>
              <el-scrollbar max-height="300px">
                <div v-if="notifications.length === 0" class="no-notifications">
                  No notifications
                </div>
                <div
                  v-for="notification in notifications"
                  :key="notification.id"
                  class="notification-item"
                  :class="{ 'unread': !notification.read }"
                  @click="handleNotificationClick(notification)"
                >
                  <div class="notification-content">
                    <div class="notification-title">{{ notification.title }}</div>
                    <div class="notification-message">{{ notification.message }}</div>
                    <div class="notification-time">{{ formatTime(notification.created_at) }}</div>
                  </div>
                </div>
              </el-scrollbar>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <!-- User Menu -->
        <el-dropdown trigger="click" class="user-dropdown">
          <div class="user-info">
            <el-avatar :size="32" :src="user?.avatar">
              <el-icon><User /></el-icon>
            </el-avatar>
            <span class="username">{{ user?.full_name || user?.username }}</span>
            <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="$router.push('/profile')">
                <el-icon><User /></el-icon>
                Profile
              </el-dropdown-item>
              <el-dropdown-item @click="$router.push('/settings')">
                <el-icon><Setting /></el-icon>
                Settings
              </el-dropdown-item>
              <el-dropdown-item v-if="isAdmin" @click="togglePortal">
                <el-icon><Switch /></el-icon>
                Switch to {{ otherPortal }} Portal
              </el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout">
                <el-icon><SwitchButton /></el-icon>
                Logout
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
  </el-header>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { User, NotificationItem } from '@/types'
import { 
  Search, 
  Bell, 
  User as UserIcon, 
  Setting, 
  Switch, 
  SwitchButton, 
  ArrowDown,
  Monitor,
  ChatDotRound
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

interface Props {
  title?: string
  portal?: 'admin' | 'consumer'
  showSearch?: boolean
  showNotifications?: boolean
  breadcrumb?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  title: 'LLM Pioneer',
  portal: 'consumer',
  showSearch: true,
  showNotifications: true,
  breadcrumb: () => []
})

const emit = defineEmits<{
  search: [query: string]
  notificationClick: [notification: NotificationItem]
}>()

const router = useRouter()
const authStore = useAuthStore()

// Reactive state
const searchQuery = ref('')
const notifications = ref<NotificationItem[]>([])

// Computed properties
const user = computed(() => authStore.user)
const isAdmin = computed(() => authStore.isAdmin)
const portalClass = computed(() => `portal-${props.portal}`)
const logoIcon = computed(() => props.portal === 'admin' ? Monitor : ChatDotRound)
const otherPortal = computed(() => props.portal === 'admin' ? 'Consumer' : 'Admin')

const unreadCount = computed(() => 
  notifications.value.filter(n => !n.read).length
)

// Methods
const handleSearch = () => {
  if (searchQuery.value.trim()) {
    emit('search', searchQuery.value.trim())
  }
}

const handleLogout = async () => {
  try {
    await authStore.logout()
  } catch (error) {
    ElMessage.error('Logout failed')
  }
}

const togglePortal = () => {
  const targetPortal = props.portal === 'admin' ? 'consumer' : 'admin'
  const targetRoute = targetPortal === 'admin' ? '/admin/dashboard' : '/user/dashboard'
  router.push(targetRoute)
}

const handleNotificationClick = (notification: NotificationItem) => {
  emit('notificationClick', notification)
  
  // Mark as read
  notification.read = true
  
  // Navigate to action URL if provided
  if (notification.action_url) {
    router.push(notification.action_url)
  }
}

const markAllAsRead = () => {
  notifications.value.forEach(n => n.read = true)
}

const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  if (days < 7) return `${days}d ago`
  return date.toLocaleDateString()
}

// Load notifications on mount
onMounted(() => {
  // TODO: Load actual notifications from API
  notifications.value = [
    {
      id: '1',
      title: 'Document Processing Complete',
      message: 'Your document "Project Overview.pdf" has been processed successfully.',
      type: 'success',
      read: false,
      created_at: new Date(Date.now() - 300000).toISOString(), // 5 minutes ago
      action_url: '/user/knowledge'
    },
    {
      id: '2',
      title: 'New Feature Available',
      message: 'The writing assistant now supports multiple languages.',
      type: 'info',
      read: false,
      created_at: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
    }
  ]
})
</script>

<style scoped>
.app-header {
  background: white;
  border-bottom: 1px solid var(--el-border-color);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 0;
  height: 60px;
}

.portal-admin {
  background: linear-gradient(90deg, #1890ff, #40a9ff);
}

.portal-consumer {
  background: linear-gradient(90deg, #52c41a, #73d13d);
}

.portal-admin .header-content,
.portal-consumer .header-content {
  color: white;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 24px;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  color: inherit;
}

.app-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  color: inherit;
}

.breadcrumb {
  margin-left: 24px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.search-section {
  display: flex;
  align-items: center;
}

.search-input {
  width: 300px;
}

.notification-dropdown {
  display: flex;
  align-items: center;
}

.notification-badge :deep(.el-badge__content) {
  background: #f56565;
}

.notification-menu {
  width: 320px;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--el-border-color);
  font-weight: 600;
}

.no-notifications {
  padding: 20px;
  text-align: center;
  color: var(--el-text-color-secondary);
}

.notification-item {
  padding: 12px 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  cursor: pointer;
  transition: background-color 0.2s;
}

.notification-item:hover {
  background: var(--el-fill-color-light);
}

.notification-item.unread {
  background: var(--el-color-primary-light-9);
  border-left: 3px solid var(--el-color-primary);
}

.notification-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.notification-title {
  font-weight: 600;
  font-size: 14px;
}

.notification-message {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.4;
}

.notification-time {
  font-size: 11px;
  color: var(--el-text-color-placeholder);
}

.user-dropdown {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.1);
}

.username {
  font-size: 14px;
  font-weight: 500;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-icon {
  font-size: 12px;
  transition: transform 0.2s;
}

.user-dropdown.is-opened .dropdown-icon {
  transform: rotate(180deg);
}

/* Responsive design */
@media (max-width: 768px) {
  .header-content {
    padding: 0 16px;
  }
  
  .search-input {
    width: 200px;
  }
  
  .username {
    display: none;
  }
  
  .breadcrumb {
    display: none;
  }
}

@media (max-width: 480px) {
  .search-section {
    display: none;
  }
  
  .app-title {
    font-size: 16px;
  }
  
  .header-left {
    gap: 12px;
  }
}
</style>