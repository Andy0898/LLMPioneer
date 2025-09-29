<template>
  <div class="message-bubble" :class="messageClass">
    <div v-if="!message.isUser" class="assistant-avatar">
      <el-avatar :size="32" :src="assistantAvatar">
        <el-icon><Robot /></el-icon>
      </el-avatar>
    </div>
    
    <div class="message-content">
      <!-- Message Header -->
      <div v-if="!message.isUser" class="message-header">
        <span class="assistant-name">LLM Pioneer Assistant</span>
        <span class="message-time">{{ formatTime(message.timestamp) }}</span>
      </div>
      
      <!-- Message Text -->
      <div class="message-text" :class="textClass">
        <div v-if="isEditing" class="edit-container">
          <el-input
            v-model="editText"
            type="textarea"
            :rows="3"
            resize="none"
            @keydown.ctrl.enter="saveEdit"
          />
          <div class="edit-actions">
            <el-button size="small" @click="cancelEdit">Cancel</el-button>
            <el-button size="small" type="primary" @click="saveEdit">Save</el-button>
          </div>
        </div>
        
        <div v-else class="message-display">
          <!-- Render markdown or plain text -->
          <div v-if="message.isUser" class="user-message">
            {{ message.text }}
          </div>
          <div v-else class="assistant-message" v-html="renderedText"></div>
          
          <!-- Attachments -->
          <div v-if="message.attachments?.length" class="attachments">
            <div
              v-for="attachment in message.attachments"
              :key="attachment.id"
              class="attachment"
            >
              <el-icon><Paperclip /></el-icon>
              <span>{{ attachment.name }}</span>
              <span class="attachment-size">({{ formatFileSize(attachment.size) }})</span>
            </div>
          </div>
          
          <!-- Sources -->
          <div v-if="message.sources?.length" class="sources">
            <h4 class="sources-title">Sources:</h4>
            <div class="sources-list">
              <div
                v-for="source in message.sources"
                :key="source.id"
                class="source-item"
                @click="viewSource(source)"
              >
                <el-icon><Document /></el-icon>
                <span>{{ source.title }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Message Actions -->
      <div v-if="!isEditing" class="message-actions" :class="actionsClass">
        <el-button
          v-if="message.isUser"
          size="small"
          text
          @click="startEdit"
        >
          <el-icon><Edit /></el-icon>
        </el-button>
        
        <el-button
          v-if="!message.isUser"
          size="small"
          text
          @click="copyMessage"
        >
          <el-icon><CopyDocument /></el-icon>
        </el-button>
        
        <el-button
          v-if="!message.isUser"
          size="small"
          text
          @click="regenerateMessage"
        >
          <el-icon><Refresh /></el-icon>
        </el-button>
        
        <el-button
          size="small"
          text
          type="danger"
          @click="deleteMessage"
        >
          <el-icon><Delete /></el-icon>
        </el-button>
        
        <span class="message-time" v-if="message.isUser">
          {{ formatTime(message.timestamp) }}
        </span>
      </div>
    </div>
    
    <div v-if="message.isUser" class="user-avatar">
      <el-avatar :size="32" :src="userAvatar">
        <el-icon><User /></el-icon>
      </el-avatar>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Robot,
  User,
  Edit,
  CopyDocument,
  Refresh,
  Delete,
  Paperclip,
  Document
} from '@element-plus/icons-vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { useAuthStore } from '@/stores/auth'
import type { Message, Source } from '@/types/chat'

// Props
interface Props {
  message: Message
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  edit: [messageId: string, newText: string]
  delete: [messageId: string]
  regenerate: [messageId: string]
}>()

// Store
const authStore = useAuthStore()

// Reactive state
const isEditing = ref(false)
const editText = ref('')

// Computed
const messageClass = computed(() => ({
  'user-message-bubble': props.message.isUser,
  'assistant-message-bubble': !props.message.isUser
}))

const textClass = computed(() => ({
  'user-text': props.message.isUser,
  'assistant-text': !props.message.isUser
}))

const actionsClass = computed(() => ({
  'user-actions': props.message.isUser,
  'assistant-actions': !props.message.isUser
}))

const assistantAvatar = computed(() => 
  'https://via.placeholder.com/32/409EFF/ffffff?text=AI'
)

const userAvatar = computed(() => 
  authStore.user?.avatar || 'https://via.placeholder.com/32/67C23A/ffffff?text=U'
)

const renderedText = computed(() => {
  if (props.message.isUser) {
    return props.message.text
  }
  
  try {
    // Configure marked for safe HTML rendering
    marked.setOptions({
      breaks: true,
      gfm: true
    })
    
    const html = marked(props.message.text)
    return DOMPurify.sanitize(html)
  } catch (error) {
    console.error('Failed to render markdown:', error)
    return props.message.text
  }
})

// Methods
const startEdit = () => {
  if (!props.message.isUser) return
  
  isEditing.value = true
  editText.value = props.message.text
}

const cancelEdit = () => {
  isEditing.value = false
  editText.value = ''
}

const saveEdit = () => {
  if (!editText.value.trim()) {
    ElMessage.warning('Message cannot be empty')
    return
  }
  
  emit('edit', props.message.id, editText.value.trim())
  isEditing.value = false
  editText.value = ''
}

const copyMessage = async () => {
  try {
    await navigator.clipboard.writeText(props.message.text)
    ElMessage.success('Message copied to clipboard')
  } catch (error) {
    ElMessage.error('Failed to copy message')
  }
}

const regenerateMessage = () => {
  emit('regenerate', props.message.id)
}

const deleteMessage = () => {
  emit('delete', props.message.id)
}

const viewSource = (source: Source) => {
  // Handle source viewing - could open in modal or navigate to document
  console.log('View source:', source)
  ElMessage.info(`Opening source: ${source.title}`)
}

const formatTime = (timestamp: string): string => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  
  return date.toLocaleDateString()
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>

<style scoped>
.message-bubble {
  @apply flex space-x-3 max-w-full;
}

.user-message-bubble {
  @apply flex-row-reverse space-x-reverse;
}

.assistant-message-bubble {
  @apply flex-row;
}

.assistant-avatar,
.user-avatar {
  @apply flex-shrink-0;
}

.message-content {
  @apply flex-1 min-w-0;
}

.message-header {
  @apply flex items-center space-x-2 mb-1;
}

.assistant-name {
  @apply text-sm font-medium text-gray-700;
}

.message-text {
  @apply rounded-lg px-4 py-3 max-w-2xl;
}

.user-text {
  @apply bg-blue-500 text-white ml-auto;
  border-radius: 18px 18px 4px 18px;
}

.assistant-text {
  @apply bg-gray-100 text-gray-800;
  border-radius: 18px 18px 18px 4px;
}

.message-display {
  @apply space-y-3;
}

.user-message {
  @apply whitespace-pre-wrap break-words;
}

.assistant-message {
  @apply prose prose-sm max-w-none;
}

.edit-container {
  @apply space-y-2;
}

.edit-actions {
  @apply flex justify-end space-x-2;
}

.attachments {
  @apply space-y-2 mt-3 pt-3 border-t border-gray-200;
}

.attachment {
  @apply flex items-center space-x-2 text-sm text-gray-600 bg-gray-50 rounded px-2 py-1;
}

.attachment-size {
  @apply text-xs text-gray-500;
}

.sources {
  @apply mt-3 pt-3 border-t border-gray-200;
}

.sources-title {
  @apply text-sm font-medium text-gray-700 mb-2;
}

.sources-list {
  @apply space-y-1;
}

.source-item {
  @apply flex items-center space-x-2 text-sm text-blue-600 hover:text-blue-800 cursor-pointer;
}

.message-actions {
  @apply flex items-center space-x-1 mt-2 opacity-0 group-hover:opacity-100 transition-opacity;
}

.message-bubble:hover .message-actions {
  @apply opacity-100;
}

.user-actions {
  @apply justify-end;
}

.assistant-actions {
  @apply justify-start;
}

.message-time {
  @apply text-xs text-gray-500 ml-2;
}

/* Assistant message prose styling */
.assistant-message :deep(h1),
.assistant-message :deep(h2),
.assistant-message :deep(h3) {
  @apply text-gray-800 font-semibold mt-4 mb-2;
}

.assistant-message :deep(h1) {
  @apply text-lg;
}

.assistant-message :deep(h2) {
  @apply text-base;
}

.assistant-message :deep(h3) {
  @apply text-sm;
}

.assistant-message :deep(p) {
  @apply mb-3 leading-relaxed;
}

.assistant-message :deep(ul),
.assistant-message :deep(ol) {
  @apply mb-3 pl-4;
}

.assistant-message :deep(li) {
  @apply mb-1;
}

.assistant-message :deep(code) {
  @apply bg-gray-200 text-gray-800 px-1 py-0.5 rounded text-sm font-mono;
}

.assistant-message :deep(pre) {
  @apply bg-gray-800 text-gray-100 p-3 rounded-lg overflow-x-auto mb-3;
}

.assistant-message :deep(pre code) {
  @apply bg-transparent text-gray-100 p-0;
}

.assistant-message :deep(blockquote) {
  @apply border-l-4 border-gray-300 pl-4 italic text-gray-600 mb-3;
}

.assistant-message :deep(table) {
  @apply border-collapse border border-gray-300 mb-3;
}

.assistant-message :deep(th),
.assistant-message :deep(td) {
  @apply border border-gray-300 px-2 py-1 text-sm;
}

.assistant-message :deep(th) {
  @apply bg-gray-100 font-semibold;
}
</style>