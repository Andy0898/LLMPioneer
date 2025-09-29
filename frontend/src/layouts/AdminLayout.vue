<template>
  <el-container class="admin-layout">
    <!-- Main Application Container -->
    <el-container direction="vertical">
      <!-- Header -->
      <AppHeader
        :title="pageTitle"
        portal="admin"
        :breadcrumb="breadcrumb"
        @search="handleGlobalSearch"
        @notification-click="handleNotificationClick"
      />
      
      <!-- Content Container -->
      <el-container class="content-container">
        <!-- Sidebar -->
        <AppSidebar
          :menu-items="adminMenuItems"
          portal="admin"
          :default-collapsed="sidebarCollapsed"
          @collapse="handleSidebarCollapse"
          @menu-select="handleMenuSelect"
        />
        
        <!-- Main Content Area -->
        <el-main class="main-content" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
          <!-- Page Header -->
          <div v-if="showPageHeader" class="page-header">
            <div class="page-header-content">
              <div class="page-title-section">
                <h1 class="page-title">{{ pageTitle }}</h1>
                <p v-if="pageDescription" class="page-description">
                  {{ pageDescription }}
                </p>
              </div>
              
              <!-- Page Actions -->
              <div v-if="$slots.actions" class="page-actions">
                <slot name="actions" />
              </div>
            </div>
          </div>
          
          <!-- Content Area with Error Boundary -->
          <div class="content-area">
            <ErrorBoundary @error="handleError" @retry="handleRetry">
              <router-view />
            </ErrorBoundary>
          </div>
          
          <!-- Global Loading Overlay -->
          <LoadingSpinner
            v-if="globalLoading"
            :fullscreen="true"
            :message="loadingMessage"
            :cancellable="loadingCancellable"
            @cancel="handleLoadingCancel"
          />
        </el-main>
      </el-container>
    </el-container>
    
    <!-- Global Dialogs -->
    <ConfirmDialog
      v-model:visible="confirmDialog.visible"
      :title="confirmDialog.title"
      :message="confirmDialog.message"
      :type="confirmDialog.type"
      :loading="confirmDialog.loading"
      @confirm="handleConfirmDialog"
      @cancel="handleCancelDialog"
    />
    
    <!-- Quick Actions Fab (Mobile) -->
    <div v-if="isMobile" class="quick-actions-fab">
      <el-button
        circle
        type="primary"
        size="large"
        @click="showQuickActions"
      >
        <el-icon><Plus /></el-icon>
      </el-button>
    </div>
    
    <!-- Mobile Menu Overlay -->
    <div 
      v-if="isMobile && mobileMenuOpen" 
      class="mobile-menu-overlay"
      @click="closeMobileMenu"
    />
  </el-container>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted, provide } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { AppHeader, AppSidebar, LoadingSpinner, ErrorBoundary, ConfirmDialog } from '@/components'
import { ADMIN_MENU_ITEMS } from '@/router/constants'
import type { NotificationItem } from '@/types'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// Layout state
const route = useRoute()
const authStore = useAuthStore()

// Reactive state
const sidebarCollapsed = ref(false)
const globalLoading = ref(false)
const loadingMessage = ref('')
const loadingCancellable = ref(false)
const isMobile = ref(false)
const mobileMenuOpen = ref(false)
const confirmDialog = ref({
  visible: false,
  title: '',
  message: '',
  type: 'confirm' as any,
  loading: false,
  resolve: null as any,
  reject: null as any
})

// Computed properties
const pageTitle = computed(() => {
  return (route.meta.title as string) || 'Admin Dashboard'
})

const pageDescription = computed(() => {
  return route.meta.description as string || ''
})

const breadcrumb = computed(() => {
  return (route.meta.breadcrumb as string[]) || []
})

const showPageHeader = computed(() => {
  return route.meta.showHeader !== false
})

const adminMenuItems = computed(() => {
  // Filter menu items based on user permissions
  return ADMIN_MENU_ITEMS.filter(item => {
    if (!item.permission) return true
    return authStore.checkPermission(item.permission)
  }).map(item => ({
    ...item,
    children: item.children?.filter(child => {
      if (!child.permission) return true
      return authStore.checkPermission(child.permission)
    })
  }))
})

// Methods
const handleSidebarCollapse = (collapsed: boolean) => {
  sidebarCollapsed.value = collapsed
}

const handleMenuSelect = (route: string) => {
  // Close mobile menu when item is selected
  if (isMobile.value) {
    mobileMenuOpen.value = false
  }
}

const handleGlobalSearch = (query: string) => {
  // Implement global search functionality
  console.log('Global search:', query)
  ElMessage.info(`Searching for: ${query}`)
}

const handleNotificationClick = (notification: NotificationItem) => {
  console.log('Notification clicked:', notification)
}

const handleError = (error: Error, info: string) => {
  console.error('Layout error:', error, info)
  ElMessage.error('An error occurred in the application')
}

const handleRetry = () => {
  // Implement retry logic
  window.location.reload()
}

const handleLoadingCancel = () => {
  globalLoading.value = false
  ElMessage.info('Operation cancelled')
}

const handleConfirmDialog = (value?: string) => {
  confirmDialog.value.loading = true
  
  if (confirmDialog.value.resolve) {
    confirmDialog.value.resolve(value)
  }
  
  setTimeout(() => {
    confirmDialog.value.visible = false
    confirmDialog.value.loading = false
  }, 300)
}

const handleCancelDialog = () => {
  if (confirmDialog.value.reject) {
    confirmDialog.value.reject(new Error('Cancelled'))
  }
  
  confirmDialog.value.visible = false
}

const showQuickActions = () => {
  // Show quick actions menu for mobile
  ElMessage.info('Quick actions menu')
}

const closeMobileMenu = () => {
  mobileMenuOpen.value = false
}

// Responsive handling
const handleResize = () => {
  isMobile.value = window.innerWidth < 768
  
  if (!isMobile.value) {
    mobileMenuOpen.value = false
  }
}

// Global loading methods
const showLoading = (message: string = 'Loading...', cancellable: boolean = false) => {
  globalLoading.value = true
  loadingMessage.value = message
  loadingCancellable.value = cancellable
}

const hideLoading = () => {
  globalLoading.value = false
  loadingMessage.value = ''
  loadingCancellable.value = false
}

// Global confirm dialog
const showConfirm = (options: {
  title?: string
  message: string
  type?: 'confirm' | 'warning' | 'error' | 'info'
}): Promise<any> => {
  return new Promise((resolve, reject) => {
    confirmDialog.value = {
      visible: true,
      title: options.title || 'Confirm',
      message: options.message,
      type: options.type || 'confirm',
      loading: false,
      resolve,
      reject
    }
  })
}

// Provide layout methods to child components
provide('layout', {
  showLoading,
  hideLoading,
  showConfirm
})

// Lifecycle
onMounted(() => {
  handleResize()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.admin-layout {
  height: 100vh;
  background: var(--el-bg-color-page);
}

.content-container {
  height: calc(100vh - 60px);
  overflow: hidden;
}

.main-content {
  padding: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: var(--el-bg-color-page);
  transition: margin-left 0.3s ease;
}

.main-content.sidebar-collapsed {
  margin-left: 0;
}

.page-header {
  background: white;
  border-bottom: 1px solid var(--el-border-color-light);
  padding: 24px 32px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.page-header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  max-width: 1200px;
  margin: 0 auto;
}

.page-title-section {
  flex: 1;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 0 0 8px 0;
  line-height: 1.2;
}

.page-description {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin: 0;
  line-height: 1.4;
}

.page-actions {
  flex-shrink: 0;
  margin-left: 24px;
}

.content-area {
  flex: 1;
  overflow: auto;
  padding: 24px 32px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.quick-actions-fab {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 100;
}

.mobile-menu-overlay {
  position: fixed;
  top: 60px;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
}

/* Admin portal specific styling */
.admin-layout {
  --admin-primary: #1890ff;
  --admin-primary-light: #40a9ff;
  --admin-primary-dark: #096dd9;
}

.page-header {
  background: linear-gradient(135deg, #f0f8ff 0%, #ffffff 100%);
  border-bottom: 2px solid var(--admin-primary);
}

.page-title {
  color: var(--admin-primary-dark);
}

/* Responsive design */
@media (max-width: 1200px) {
  .page-header-content,
  .content-area {
    max-width: none;
  }
  
  .content-area {
    padding: 20px 24px;
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 16px 20px;
  }
  
  .page-header-content {
    flex-direction: column;
    gap: 16px;
  }
  
  .page-actions {
    margin-left: 0;
    width: 100%;
  }
  
  .content-area {
    padding: 16px 20px;
  }
  
  .page-title {
    font-size: 20px;
  }
}

@media (max-width: 480px) {
  .page-header {
    padding: 12px 16px;
  }
  
  .content-area {
    padding: 12px 16px;
  }
  
  .page-title {
    font-size: 18px;
  }
  
  .quick-actions-fab {
    bottom: 16px;
    right: 16px;
  }
}

/* Animation for smooth transitions */
.main-content {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-header {
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Scrollbar styling */
.content-area::-webkit-scrollbar {
  width: 6px;
}

.content-area::-webkit-scrollbar-track {
  background: var(--el-fill-color-light);
}

.content-area::-webkit-scrollbar-thumb {
  background: var(--el-border-color-darker);
  border-radius: 3px;
}

.content-area::-webkit-scrollbar-thumb:hover {
  background: var(--el-text-color-placeholder);
}

/* Focus management for accessibility */
.main-content:focus-within {
  outline: none;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .page-header {
    border-bottom: 3px solid var(--admin-primary);
  }
  
  .page-title {
    font-weight: 700;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .main-content,
  .page-header {
    transition: none;
    animation: none;
  }
}
</style>