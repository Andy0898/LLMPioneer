<template>
  <div class="error-boundary">
    <slot v-if="!hasError" />
    
    <div v-else class="error-container">
      <div class="error-content">
        <!-- Error Icon -->
        <div class="error-icon">
          <el-icon size="48" color="var(--el-color-danger)">
            <component :is="errorIcon" />
          </el-icon>
        </div>
        
        <!-- Error Title -->
        <h2 class="error-title">{{ errorTitle }}</h2>
        
        <!-- Error Message -->
        <p class="error-message">{{ errorMessage }}</p>
        
        <!-- Error Details (Development Mode) -->
        <div v-if="showDetails && errorDetails" class="error-details">
          <el-collapse>
            <el-collapse-item title="Error Details" name="details">
              <pre class="error-stack">{{ errorDetails }}</pre>
            </el-collapse-item>
          </el-collapse>
        </div>
        
        <!-- Action Buttons -->
        <div class="error-actions">
          <el-button type="primary" @click="handleRetry">
            <el-icon><Refresh /></el-icon>
            Try Again
          </el-button>
          
          <el-button @click="handleGoHome">
            <el-icon><House /></el-icon>
            Go Home
          </el-button>
          
          <el-button v-if="showReportButton" type="danger" @click="handleReportError">
            <el-icon><Warning /></el-icon>
            Report Issue
          </el-button>
        </div>
        
        <!-- Support Information -->
        <div v-if="showSupport" class="error-support">
          <p class="support-text">
            If this problem persists, please contact our support team.
          </p>
          <div class="support-actions">
            <el-button link @click="copyErrorInfo">
              <el-icon><CopyDocument /></el-icon>
              Copy Error Info
            </el-button>
            <el-button link @click="openSupport">
              <el-icon><ChatDotRound /></el-icon>
              Contact Support
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onErrorCaptured, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Warning,
  Refresh, 
  House, 
  CopyDocument, 
  ChatDotRound,
  CircleClose,
  WarnTriangleFilled
} from '@element-plus/icons-vue'

interface Props {
  fallback?: any
  onError?: (error: Error, instance: any, info: string) => void
  showDetails?: boolean
  showReportButton?: boolean
  showSupport?: boolean
  autoRetry?: boolean
  maxRetries?: number
}

const props = withDefaults(defineProps<Props>(), {
  showDetails: import.meta.env.DEV,
  showReportButton: true,
  showSupport: true,
  autoRetry: false,
  maxRetries: 3
})

const emit = defineEmits<{
  error: [error: Error, info: string]
  retry: []
  report: [error: Error, info: string]
}>()

const router = useRouter()

// Reactive state
const hasError = ref(false)
const error = ref<Error | null>(null)
const errorInfo = ref('')
const retryCount = ref(0)

// Computed properties
const errorTitle = computed(() => {
  if (!error.value) return 'Something went wrong'
  
  const errorType = error.value.name
  const titles: Record<string, string> = {
    'ChunkLoadError': 'Failed to Load Application',
    'NetworkError': 'Connection Problem',
    'TypeError': 'Application Error',
    'ReferenceError': 'Application Error',
    'SyntaxError': 'Application Error',
    'TimeoutError': 'Request Timeout',
    'AuthenticationError': 'Authentication Required',
    'PermissionError': 'Access Denied'
  }
  
  return titles[errorType] || 'Unexpected Error'
})

const errorMessage = computed(() => {
  if (!error.value) return 'An unexpected error occurred. Please try again.'
  
  const errorType = error.value.name
  const messages: Record<string, string> = {
    'ChunkLoadError': 'The application failed to load properly. This might be due to a network issue or an outdated cache.',
    'NetworkError': 'Unable to connect to the server. Please check your internet connection and try again.',
    'TypeError': 'A technical error occurred while processing your request.',
    'ReferenceError': 'A technical error occurred while processing your request.',
    'SyntaxError': 'A technical error occurred while processing your request.',
    'TimeoutError': 'The request took too long to complete. Please try again.',
    'AuthenticationError': 'Your session has expired. Please log in again.',
    'PermissionError': 'You do not have permission to access this resource.'
  }
  
  return messages[errorType] || error.value.message || 'An unexpected error occurred.'
})

const errorDetails = computed(() => {
  if (!error.value) return null
  return `${error.value.name}: ${error.value.message}

${error.value.stack || ''}

Component Info: ${errorInfo.value}`
})

const errorIcon = computed(() => {
  if (!error.value) return Warning
  
  const errorType = error.value.name
  const icons: Record<string, any> = {
    'ChunkLoadError': Refresh,
    'NetworkError': Warning,
    'AuthenticationError': Warning,
    'PermissionError': CircleClose
  }
  
  return icons[errorType] || WarnTriangleFilled
})

// Error capture
onErrorCaptured((err: Error, instance: any, info: string) => {
  console.error('Error captured by ErrorBoundary:', err, info)
  
  hasError.value = true
  error.value = err
  errorInfo.value = info
  
  // Call custom error handler
  if (props.onError) {
    props.onError(err, instance, info)
  }
  
  // Emit error event
  emit('error', err, info)
  
  // Auto retry for certain errors
  if (props.autoRetry && shouldAutoRetry(err) && retryCount.value < props.maxRetries) {
    setTimeout(() => {
      handleRetry()
    }, 2000)
  }
  
  // Prevent the error from propagating
  return false
})

// Methods
const shouldAutoRetry = (err: Error): boolean => {
  const retryableErrors = ['ChunkLoadError', 'NetworkError', 'TimeoutError']
  return retryableErrors.includes(err.name)
}

const handleRetry = () => {
  retryCount.value++
  hasError.value = false
  error.value = null
  errorInfo.value = ''
  emit('retry')
  
  // Force re-render by reloading the page for certain errors
  if (error.value?.name === 'ChunkLoadError') {
    window.location.reload()
  }
}

const handleGoHome = () => {
  router.push('/')
}

const handleReportError = () => {
  if (error.value) {
    emit('report', error.value, errorInfo.value)
    
    // You can integrate with error reporting services here
    // Example: Sentry, LogRocket, etc.
    console.log('Reporting error:', {
      error: error.value,
      info: errorInfo.value,
      url: window.location.href,
      userAgent: navigator.userAgent,
      timestamp: new Date().toISOString()
    })
    
    ElMessage.success('Error report sent successfully')
  }
}

const copyErrorInfo = async () => {
  if (!errorDetails.value) return
  
  try {
    await navigator.clipboard.writeText(errorDetails.value)
    ElMessage.success('Error information copied to clipboard')
  } catch (err) {
    console.error('Failed to copy error info:', err)
    ElMessage.error('Failed to copy error information')
  }
}

const openSupport = () => {
  // Open support page or email
  window.open('mailto:support@llmpioneer.com?subject=Error Report&body=' + encodeURIComponent(errorDetails.value || ''))
}

// Reset error state when route changes
watch(() => router.currentRoute.value.path, () => {
  if (hasError.value) {
    hasError.value = false
    error.value = null
    errorInfo.value = ''
    retryCount.value = 0
  }
})
</script>

<style scoped>
.error-boundary {
  width: 100%;
  height: 100%;
}

.error-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 20px;
  background: var(--el-bg-color);
}

.error-content {
  max-width: 600px;
  width: 100%;
  text-align: center;
  background: white;
  border-radius: 12px;
  padding: 40px 32px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--el-border-color-light);
}

.error-icon {
  margin-bottom: 24px;
}

.error-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 0 0 16px 0;
}

.error-message {
  font-size: 16px;
  color: var(--el-text-color-regular);
  line-height: 1.6;
  margin: 0 0 24px 0;
}

.error-details {
  margin: 24px 0;
  text-align: left;
}

.error-stack {
  background: var(--el-fill-color-extra-light);
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  padding: 12px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: var(--el-text-color-regular);
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 200px;
  overflow-y: auto;
}

.error-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 24px;
}

.error-support {
  border-top: 1px solid var(--el-border-color-lighter);
  padding-top: 24px;
  margin-top: 24px;
}

.support-text {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin: 0 0 16px 0;
}

.support-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

/* Responsive design */
@media (max-width: 768px) {
  .error-container {
    padding: 16px;
    min-height: 300px;
  }
  
  .error-content {
    padding: 32px 24px;
  }
  
  .error-title {
    font-size: 20px;
  }
  
  .error-message {
    font-size: 14px;
  }
  
  .error-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .error-actions .el-button {
    width: 100%;
    max-width: 200px;
  }
}

@media (max-width: 480px) {
  .error-content {
    padding: 24px 16px;
  }
  
  .error-title {
    font-size: 18px;
  }
  
  .support-actions {
    flex-direction: column;
    align-items: center;
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .error-content {
    background: var(--el-bg-color-page);
    border-color: var(--el-border-color);
  }
}

/* Animation for error appearance */
.error-content {
  animation: errorFadeIn 0.3s ease-out;
}

@keyframes errorFadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Loading state for retry button */
.error-actions .el-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>