<template>
  <el-dialog
    v-model="visible"
    :title="title"
    :width="width"
    :destroy-on-close="true"
    :close-on-click-modal="closeOnClickModal"
    :close-on-press-escape="closeOnPressEscape"
    :show-close="showClose"
    :modal="modal"
    :lock-scroll="lockScroll"
    class="confirm-dialog"
    :class="typeClass"
  >
    <!-- Dialog Content -->
    <div class="dialog-content">
      <!-- Icon -->
      <div v-if="showIcon" class="dialog-icon">
        <el-icon :size="iconSize" :color="iconColor">
          <component :is="dialogIcon" />
        </el-icon>
      </div>
      
      <!-- Message -->
      <div class="dialog-message">
        <div v-if="message" class="message-text" v-html="message"></div>
        <slot v-else />
        
        <!-- Details -->
        <div v-if="details" class="message-details">
          <el-collapse>
            <el-collapse-item title="Show details" name="details">
              <div class="details-content" v-html="details"></div>
            </el-collapse-item>
          </el-collapse>
        </div>
        
        <!-- Input field for prompt type -->
        <div v-if="type === 'prompt'" class="dialog-input">
          <el-input
            v-model="inputValue"
            :placeholder="inputPlaceholder"
            :type="inputType"
            :rows="inputType === 'textarea' ? 3 : undefined"
            :maxlength="inputMaxLength"
            :show-word-limit="showWordLimit"
            clearable
            @keyup.enter="handleConfirm"
          />
          <div v-if="inputError" class="input-error">{{ inputError }}</div>
        </div>
        
        <!-- Checkbox for "Don't ask again" -->
        <div v-if="showDontAskAgain" class="dialog-checkbox">
          <el-checkbox v-model="dontAskAgain">
            Don't ask me again
          </el-checkbox>
        </div>
      </div>
    </div>
    
    <!-- Dialog Footer -->
    <template #footer>
      <div class="dialog-footer">
        <el-button 
          v-if="showCancelButton"
          @click="handleCancel"
          :disabled="loading"
        >
          {{ cancelText }}
        </el-button>
        
        <el-button
          :type="confirmButtonType"
          :loading="loading"
          @click="handleConfirm"
          :disabled="isConfirmDisabled"
        >
          {{ confirmText }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, ref, watch, nextTick } from 'vue'
import { 
  Warning, 
  CircleCheck, 
  CircleClose, 
  InfoFilled, 
  QuestionFilled,
  Delete,
  Edit
} from '@element-plus/icons-vue'

interface Props {
  visible: boolean
  title?: string
  message?: string
  details?: string
  type?: 'warning' | 'error' | 'success' | 'info' | 'confirm' | 'prompt' | 'delete'
  width?: string | number
  showIcon?: boolean
  showClose?: boolean
  showCancelButton?: boolean
  showDontAskAgain?: boolean
  closeOnClickModal?: boolean
  closeOnPressEscape?: boolean
  modal?: boolean
  lockScroll?: boolean
  confirmText?: string
  cancelText?: string
  loading?: boolean
  inputPlaceholder?: string
  inputType?: 'text' | 'password' | 'textarea'
  inputMaxLength?: number
  showWordLimit?: boolean
  inputValidator?: (value: string) => string | null
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Confirm',
  type: 'confirm',
  width: '420px',
  showIcon: true,
  showClose: true,
  showCancelButton: true,
  showDontAskAgain: false,
  closeOnClickModal: false,
  closeOnPressEscape: true,
  modal: true,
  lockScroll: true,
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  loading: false,
  inputPlaceholder: 'Please enter...',
  inputType: 'text',
  showWordLimit: false
})

const emit = defineEmits<{
  'update:visible': [visible: boolean]
  confirm: [value?: string, dontAskAgain?: boolean]
  cancel: []
}>()

// Reactive state
const inputValue = ref('')
const inputError = ref('')
const dontAskAgain = ref(false)

// Computed properties
const typeClass = computed(() => `dialog-${props.type}`)

const dialogIcon = computed(() => {
  const icons = {
    warning: Warning,
    error: CircleClose,
    success: CircleCheck,
    info: InfoFilled,
    confirm: QuestionFilled,
    prompt: Edit,
    delete: Delete
  }
  return icons[props.type]
})

const iconColor = computed(() => {
  const colors = {
    warning: 'var(--el-color-warning)',
    error: 'var(--el-color-danger)',
    success: 'var(--el-color-success)',
    info: 'var(--el-color-info)',
    confirm: 'var(--el-color-primary)',
    prompt: 'var(--el-color-primary)',
    delete: 'var(--el-color-danger)'
  }
  return colors[props.type]
})

const iconSize = computed(() => {
  return props.type === 'delete' ? 32 : 28
})

const confirmButtonType = computed(() => {
  const types = {
    warning: 'warning',
    error: 'danger',
    success: 'success',
    info: 'primary',
    confirm: 'primary',
    prompt: 'primary',
    delete: 'danger'
  }
  return types[props.type] as any
})

const isConfirmDisabled = computed(() => {
  if (props.loading) return true
  
  if (props.type === 'prompt') {
    if (!inputValue.value.trim()) return true
    if (inputError.value) return true
  }
  
  return false
})

// Methods
const handleConfirm = async () => {
  if (props.type === 'prompt') {
    // Validate input
    if (props.inputValidator) {
      const error = props.inputValidator(inputValue.value)
      if (error) {
        inputError.value = error
        return
      }
    }
    
    emit('confirm', inputValue.value, dontAskAgain.value)
  } else {
    emit('confirm', undefined, dontAskAgain.value)
  }
}

const handleCancel = () => {
  emit('cancel')
  emit('update:visible', false)
}

// Watch for input changes to clear errors
watch(() => inputValue.value, () => {
  if (inputError.value) {
    inputError.value = ''
  }
})

// Focus input when dialog opens for prompt type
watch(() => props.visible, async (newVisible) => {
  if (newVisible && props.type === 'prompt') {
    await nextTick()
    const input = document.querySelector('.confirm-dialog .el-input__inner') as HTMLInputElement
    if (input) {
      input.focus()
    }
  }
  
  // Reset state when dialog closes
  if (!newVisible) {
    inputValue.value = ''
    inputError.value = ''
    dontAskAgain.value = false
  }
})
</script>

<style scoped>
.confirm-dialog {
  --dialog-border-radius: 8px;
}

.confirm-dialog :deep(.el-dialog) {
  border-radius: var(--dialog-border-radius);
}

.confirm-dialog :deep(.el-dialog__header) {
  padding: 20px 20px 10px;
}

.confirm-dialog :deep(.el-dialog__body) {
  padding: 10px 20px 20px;
}

.confirm-dialog :deep(.el-dialog__footer) {
  padding: 20px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.dialog-content {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.dialog-icon {
  flex-shrink: 0;
  margin-top: 2px;
}

.dialog-message {
  flex: 1;
}

.message-text {
  font-size: 14px;
  line-height: 1.6;
  color: var(--el-text-color-primary);
  margin-bottom: 16px;
}

.message-details {
  margin-top: 16px;
}

.details-content {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  background: var(--el-fill-color-extra-light);
  padding: 12px;
  border-radius: 4px;
  border: 1px solid var(--el-border-color-lighter);
  white-space: pre-wrap;
  word-break: break-word;
}

.dialog-input {
  margin-top: 16px;
}

.input-error {
  color: var(--el-color-danger);
  font-size: 12px;
  margin-top: 4px;
}

.dialog-checkbox {
  margin-top: 16px;
  display: flex;
  justify-content: flex-start;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* Type-specific styles */
.dialog-warning :deep(.el-dialog__title) {
  color: var(--el-color-warning);
}

.dialog-error :deep(.el-dialog__title) {
  color: var(--el-color-danger);
}

.dialog-success :deep(.el-dialog__title) {
  color: var(--el-color-success);
}

.dialog-delete :deep(.el-dialog__title) {
  color: var(--el-color-danger);
}

/* Special styling for delete confirmation */
.dialog-delete .dialog-content {
  background: var(--el-color-danger-light-9);
  padding: 16px;
  border-radius: 6px;
  border: 1px solid var(--el-color-danger-light-7);
}

.dialog-delete .message-text {
  font-weight: 500;
}

/* Responsive design */
@media (max-width: 768px) {
  .confirm-dialog :deep(.el-dialog) {
    width: 90% !important;
    margin: 5vh auto;
  }
  
  .dialog-content {
    flex-direction: column;
    gap: 12px;
  }
  
  .dialog-icon {
    align-self: center;
  }
  
  .message-text {
    text-align: center;
  }
  
  .dialog-footer {
    flex-direction: column-reverse;
  }
  
  .dialog-footer .el-button {
    width: 100%;
  }
}

/* Animation enhancements */
.confirm-dialog :deep(.el-dialog) {
  animation: dialogSlideIn 0.3s ease-out;
}

@keyframes dialogSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Loading state */
.confirm-dialog :deep(.el-button.is-loading) {
  pointer-events: none;
}

/* Focus styles */
.dialog-input :deep(.el-input__inner:focus) {
  border-color: var(--el-color-primary);
  box-shadow: 0 0 0 2px var(--el-color-primary-light-8);
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .dialog-content {
    border: 2px solid var(--el-border-color);
    border-radius: 4px;
    padding: 12px;
  }
  
  .dialog-icon {
    border: 1px solid currentColor;
    border-radius: 50%;
    padding: 4px;
  }
}
</style>