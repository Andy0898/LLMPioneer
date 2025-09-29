<template>
  <el-container class="consumer-layout">
    <!-- Main Application Container -->
    <el-container direction="vertical">
      <!-- Header -->
      <AppHeader
        :title="pageTitle"
        portal="consumer"
        :breadcrumb="breadcrumb"
        @search="handleGlobalSearch"
        @notification-click="handleNotificationClick"
      />
      
      <!-- Content Container -->
      <el-container class="content-container">
        <!-- Sidebar -->
        <AppSidebar
          :menu-items="consumerMenuItems"
          portal="consumer"
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
            :progress="loadingProgress"
            :show-progress="showLoadingProgress"
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
    
    <!-- Quick Start Guide (First Time Users) -->
    <div v-if="showQuickStart" class="quick-start-overlay">
      <div class="quick-start-content">
        <div class="quick-start-header">
          <h2>Welcome to LLM Pioneer!</h2>
          <el-button text @click="dismissQuickStart">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
        <div class="quick-start-body">
          <p>Get started with these features:</p>
          <div class="feature-cards">
            <div class="feature-card" @click="navigateToChat">
              <el-icon size="24"><ChatDotRound /></el-icon>
              <h3>AI Chat</h3>
              <p>Start conversations with AI assistants</p>
            </div>
            <div class="feature-card" @click="navigateToWriting">
              <el-icon size="24"><EditPen /></el-icon>
              <h3>Writing Assistant</h3>
              <p>Get help with writing and content creation</p>
            </div>
            <div class="feature-card" @click="navigateToKnowledge">
              <el-icon size="24"><Document /></el-icon>
              <h3>Knowledge Base</h3>
              <p>Upload and search through your documents</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Floating Action Button for Quick Access -->
    <div class="floating-actions">
      <el-button-group vertical>
        <el-button
          circle
          type="primary"
          size="large"
          @click="quickNewChat"
          title="Quick Chat"
        >
          <el-icon><ChatDotRound /></el-icon>
        </el-button>
        <el-button
          circle
          type="success"
          size="large"
          @click="quickUpload"
          title="Quick Upload"
        >
          <el-icon><Upload /></el-icon>
        </el-button>
      </el-button-group>
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
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { AppHeader, AppSidebar, LoadingSpinner, ErrorBoundary, ConfirmDialog } from '@/components'
import { CONSUMER_MENU_ITEMS } from '@/router/constants'
import type { NotificationItem } from '@/types'
import { 
  Close, 
  ChatDotRound, 
  EditPen, 
  Document, 
  Upload 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// Layout state
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// Reactive state
const sidebarCollapsed = ref(false)
const globalLoading = ref(false)
const loadingMessage = ref('')
const loadingProgress = ref(0)
const showLoadingProgress = ref(false)
const loadingCancellable = ref(false)
const isMobile = ref(false)
const mobileMenuOpen = ref(false)
const showQuickStart = ref(false)
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
  return (route.meta.title as string) || 'Dashboard'
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

const consumerMenuItems = computed(() => {
  return CONSUMER_MENU_ITEMS
})

// Methods
const handleSidebarCollapse = (collapsed: boolean) => {
  sidebarCollapsed.value = collapsed
}

const handleMenuSelect = (route: string) => {
  if (isMobile.value) {
    mobileMenuOpen.value = false
  }
}

const handleGlobalSearch = (query: string) => {
  // Implement global search across conversations and documents
  router.push(`/user/search?q=${encodeURIComponent(query)}`)
}

const handleNotificationClick = (notification: NotificationItem) => {
  console.log('Notification clicked:', notification)
}

const handleError = (error: Error, info: string) => {
  console.error('Layout error:', error, info)
  ElMessage.error('An error occurred in the application')
}

const handleRetry = () => {
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

const quickNewChat = () => {
  router.push('/user/chat')
}

const quickUpload = () => {
  router.push('/user/knowledge')
}

const navigateToChat = () => {
  router.push('/user/chat')
  dismissQuickStart()
}

const navigateToWriting = () => {
  router.push('/user/writing')
  dismissQuickStart()
}

const navigateToKnowledge = () => {
  router.push('/user/knowledge')
  dismissQuickStart()
}

const dismissQuickStart = () => {
  showQuickStart.value = false
  localStorage.setItem('quick-start-dismissed', 'true')
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
const showLoading = (
  message: string = 'Loading...', 
  options: {
    cancellable?: boolean
    showProgress?: boolean
    progress?: number
  } = {}
) => {
  globalLoading.value = true
  loadingMessage.value = message
  loadingCancellable.value = options.cancellable || false
  showLoadingProgress.value = options.showProgress || false
  loadingProgress.value = options.progress || 0
}

const updateLoadingProgress = (progress: number) => {
  loadingProgress.value = progress
}

const hideLoading = () => {
  globalLoading.value = false
  loadingMessage.value = ''
  loadingCancellable.value = false
  showLoadingProgress.value = false
  loadingProgress.value = 0
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

// Check if user is new and should see quick start
const checkQuickStart = () => {
  const dismissed = localStorage.getItem('quick-start-dismissed')
  const isNewUser = !authStore.user?.last_login_at
  
  if (!dismissed && isNewUser) {
    showQuickStart.value = true
  }
}

// Provide layout methods to child components
provide('layout', {
  showLoading,
  hideLoading,
  updateLoadingProgress,
  showConfirm
})

// Lifecycle
onMounted(() => {
  handleResize()
  checkQuickStart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.consumer-layout {
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

.floating-actions {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 100;
}

.floating-actions .el-button-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.15));
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

/* Quick Start Guide Styles */
.quick-start-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.quick-start-content {
  background: white;
  border-radius: 12px;
  max-width: 600px;
  width: 100%;
  max-height: 80vh;
  overflow-y: auto;
  animation: quickStartSlideIn 0.3s ease-out;
}

.quick-start-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 0;
  border-bottom: 1px solid var(--el-border-color-light);
  margin-bottom: 24px;
}

.quick-start-header h2 {
  margin: 0;
  color: var(--consumer-primary, #52c41a);
  font-size: 20px;
  font-weight: 600;
}

.quick-start-body {
  padding: 0 24px 24px;
}

.quick-start-body p {
  color: var(--el-text-color-regular);
  margin-bottom: 20px;
}

.feature-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.feature-card {
  text-align: center;
  padding: 20px;
  border: 2px solid var(--el-border-color-light);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.feature-card:hover {
  border-color: var(--consumer-primary, #52c41a);
  background: var(--el-color-success-light-9);
  transform: translateY(-2px);
}

.feature-card .el-icon {
  color: var(--consumer-primary, #52c41a);
  margin-bottom: 12px;
}

.feature-card h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.feature-card p {
  margin: 0;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.4;
}

/* Consumer portal specific styling */
.consumer-layout {
  --consumer-primary: #52c41a;
  --consumer-primary-light: #73d13d;
  --consumer-primary-dark: #389e0d;
}

.page-header {
  background: linear-gradient(135deg, #f6ffed 0%, #ffffff 100%);
  border-bottom: 2px solid var(--consumer-primary);
}

.page-title {
  color: var(--consumer-primary-dark);
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
  
  .floating-actions {
    bottom: 16px;
    right: 16px;
  }
  
  .feature-cards {
    grid-template-columns: 1fr;
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
  
  .quick-start-overlay {
    padding: 16px;
  }
  
  .quick-start-header,
  .quick-start-body {
    padding-left: 16px;
    padding-right: 16px;
  }
}

/* Animations */
@keyframes quickStartSlideIn {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

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

/* Floating action animations */
.floating-actions .el-button {
  transition: all 0.3s ease;
}

.floating-actions .el-button:hover {
  transform: scale(1.1);
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

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .main-content,
  .page-header,
  .quick-start-content,
  .feature-card,
  .floating-actions .el-button {
    transition: none;
    animation: none;
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .page-header {
    border-bottom: 3px solid var(--consumer-primary);
  }
  
  .feature-card {
    border-width: 3px;
  }
  
  .page-title {
    font-weight: 700;
  }
}
</style>