<template>
  <div class="loading-spinner" :class="{ 'is-fullscreen': fullscreen, [`size-${size}`]: true }">
    <div v-if="fullscreen" class="spinner-overlay" @click="handleOverlayClick">
      <div class="spinner-container" @click.stop>
        <div class="spinner-content">
          <el-icon class="spinner-icon" :size="iconSize">
            <component :is="spinnerIcon" />
          </el-icon>
          <div v-if="message" class="spinner-message">{{ message }}</div>
          <div v-if="showProgress && progress !== undefined" class="spinner-progress">
            <el-progress 
              :percentage="progress" 
              :show-text="false" 
              :stroke-width="4"
              color="var(--el-color-primary)"
            />
            <span class="progress-text">{{ progress }}%</span>
          </div>
          <el-button 
            v-if="cancellable" 
            size="small" 
            type="danger" 
            @click="handleCancel"
            class="cancel-button"
          >
            Cancel
          </el-button>
        </div>
      </div>
    </div>
    
    <div v-else class="inline-spinner">
      <el-icon class="spinner-icon" :size="iconSize">
        <component :is="spinnerIcon" />
      </el-icon>
      <span v-if="message" class="spinner-message">{{ message }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { Loading, Refresh, Download, Upload } from '@element-plus/icons-vue'

interface Props {
  size?: 'small' | 'medium' | 'large'
  message?: string
  fullscreen?: boolean
  type?: 'loading' | 'processing' | 'uploading' | 'downloading'
  progress?: number
  showProgress?: boolean
  cancellable?: boolean
  backdrop?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'medium',
  fullscreen: false,
  type: 'loading',
  showProgress: false,
  cancellable: false,
  backdrop: true
})

const emit = defineEmits<{
  cancel: []
  overlayClick: []
}>()

// Computed properties
const iconSize = computed(() => {
  const sizes = {
    small: 16,
    medium: 24,
    large: 32
  }
  return sizes[props.size]
})

const spinnerIcon = computed(() => {
  const icons = {
    loading: Loading,
    processing: Refresh,
    uploading: Upload,
    downloading: Download
  }
  return icons[props.type]
})

// Methods
const handleCancel = () => {
  emit('cancel')
}

const handleOverlayClick = () => {
  if (props.backdrop) {
    emit('overlayClick')
  }
}

// Prevent body scroll when fullscreen
onMounted(() => {
  if (props.fullscreen) {
    document.body.style.overflow = 'hidden'
  }
})

onUnmounted(() => {
  if (props.fullscreen) {
    document.body.style.overflow = ''
  }
})
</script>

<style scoped>
.loading-spinner {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.is-fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
}

.spinner-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(2px);
}

.spinner-container {
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  max-width: 320px;
  width: 90%;
  margin: 20px;
}

.spinner-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.spinner-icon {
  color: var(--el-color-primary);
  animation: spin 1s linear infinite;
}

.spinner-message {
  font-size: 14px;
  color: var(--el-text-color-primary);
  text-align: center;
  line-height: 1.4;
  max-width: 250px;
}

.spinner-progress {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-text {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  text-align: center;
}

.cancel-button {
  margin-top: 8px;
}

.inline-spinner {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.inline-spinner .spinner-message {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

/* Size variations */
.size-small .spinner-icon {
  font-size: 16px;
}

.size-small .spinner-message {
  font-size: 12px;
}

.size-medium .spinner-icon {
  font-size: 24px;
}

.size-medium .spinner-message {
  font-size: 14px;
}

.size-large .spinner-icon {
  font-size: 32px;
}

.size-large .spinner-message {
  font-size: 16px;
}

/* Animations */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Pulse animation for processing type */
.loading-spinner[data-type="processing"] .spinner-icon {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.1);
  }
}

/* Upload/Download specific animations */
.loading-spinner[data-type="uploading"] .spinner-icon {
  animation: bounce 1s ease-in-out infinite;
}

.loading-spinner[data-type="downloading"] .spinner-icon {
  animation: bounce 1s ease-in-out infinite reverse;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-4px);
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .spinner-container {
    background: var(--el-bg-color);
    border: 1px solid var(--el-border-color);
  }
  
  .spinner-overlay {
    background: rgba(0, 0, 0, 0.7);
  }
}

/* Responsive design */
@media (max-width: 480px) {
  .spinner-container {
    padding: 24px 20px;
    margin: 16px;
  }
  
  .spinner-content {
    gap: 12px;
  }
  
  .spinner-message {
    font-size: 13px;
    max-width: 200px;
  }
}

/* Reduced motion for accessibility */
@media (prefers-reduced-motion: reduce) {
  .spinner-icon {
    animation: none;
  }
  
  .spinner-icon::after {
    content: '●';
    animation: blink 1s step-end infinite;
  }
}

@keyframes blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0.3;
  }
}
</style>