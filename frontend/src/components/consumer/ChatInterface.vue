<template>
  <div class="chat-interface">
    <!-- Chat Header -->
    <div class="chat-header">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <el-avatar :size="40" :src="assistantAvatar">
            <el-icon><Robot /></el-icon>
          </el-avatar>
          <div>
            <h3 class="font-semibold text-gray-800">LLM Pioneer Assistant</h3>
            <p class="text-sm text-gray-600" :class="statusClass">{{ statusText }}</p>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <el-button size="small" @click="clearChat" :disabled="messages.length === 0">
            <el-icon><Delete /></el-icon>
            Clear
          </el-button>
          <el-button size="small" @click="exportChat" :disabled="messages.length === 0">
            <el-icon><Download /></el-icon>
            Export
          </el-button>
        </div>
      </div>
    </div>

    <!-- Messages Container -->
    <div ref="messagesContainer" class="messages-container" @scroll="handleScroll">
      <div v-if="loading && messages.length === 0" class="loading-placeholder">
        <el-skeleton :rows="3" animated />
      </div>
      
      <div v-else-if="messages.length === 0" class="empty-state">
        <el-icon class="empty-icon"><ChatDotRound /></el-icon>
        <h3>Start a conversation</h3>
        <p>Ask me anything about your knowledge base or get help with your work.</p>
        
        <!-- Quick Actions -->
        <div class="quick-actions">
          <el-button
            v-for="action in quickActions"
            :key="action.text"
            @click="sendQuickAction(action.text)"
            class="quick-action-btn"
          >
            {{ action.text }}
          </el-button>
        </div>
      </div>

      <div v-else class="messages-list">
        <message-bubble
          v-for="message in messages"
          :key="message.id"
          :message="message"
          @edit="handleEditMessage"
          @delete="handleDeleteMessage"
          @regenerate="handleRegenerateMessage"
        />
        
        <!-- Typing Indicator -->
        <div v-if="isAssistantTyping" class="typing-indicator">
          <div class="typing-bubble">
            <div class="typing-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="input-area">
      <div class="input-container">
        <!-- File Upload -->
        <div v-if="attachedFiles.length > 0" class="attached-files">
          <div
            v-for="file in attachedFiles"
            :key="file.id"
            class="attached-file"
          >
            <el-icon><Paperclip /></el-icon>
            <span>{{ file.name }}</span>
            <el-button
              size="small"
              type="danger"
              text
              @click="removeAttachedFile(file.id)"
            >
              <el-icon><Close /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- Message Input -->
        <div class="message-input-wrapper">
          <el-input
            v-model="messageText"
            type="textarea"
            :rows="inputRows"
            placeholder="Type your message here... (Ctrl+Enter to send)"
            resize="none"
            @keydown="handleKeyDown"
            @input="handleInputChange"
            class="message-input"
            :disabled="loading"
          />
          
          <!-- Input Actions -->
          <div class="input-actions">
            <el-upload
              :show-file-list="false"
              :before-upload="handleFileAttach"
              accept=".txt,.md,.pdf,.doc,.docx"
              :disabled="loading"
            >
              <el-button text :disabled="loading">
                <el-icon><Paperclip /></el-icon>
              </el-button>
            </el-upload>
            
            <el-button
              type="primary"
              @click="sendMessage"
              :loading="loading"
              :disabled="!messageText.trim() || loading"
              class="send-button"
            >
              <el-icon><Promotion /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Robot,
  Delete,
  Download,
  ChatDotRound,
  Paperclip,
  Close,
  Promotion
} from '@element-plus/icons-vue'
import MessageBubble from './MessageBubble.vue'
import { chatApi } from '@/api'
import { useConversationStore } from '@/stores/conversation'
import type { Message, AttachedFile } from '@/types/chat'

// Store
const conversationStore = useConversationStore()

// Reactive state
const loading = ref(false)
const messageText = ref('')
const messages = ref<Message[]>([])
const attachedFiles = ref<AttachedFile[]>([])
const isAssistantTyping = ref(false)
const messagesContainer = ref<HTMLElement>()

// Quick actions for empty state
const quickActions = [
  { text: "What can you help me with?" },
  { text: "Summarize my recent documents" },
  { text: "Help me write a report" },
  { text: "Search knowledge base" }
]

// Computed
const assistantAvatar = computed(() => 
  'https://via.placeholder.com/40/409EFF/ffffff?text=AI'
)

const statusClass = computed(() => ({
  'text-green-600': !loading.value,
  'text-yellow-600': loading.value
}))

const statusText = computed(() => 
  loading.value ? 'Thinking...' : 'Online'
)

const inputRows = computed(() => {
  const lines = messageText.value.split('\n').length
  return Math.min(Math.max(lines, 1), 4)
})

// Lifecycle
onMounted(() => {
  loadConversation()
  scrollToBottom()
})

// Watch for new messages to auto-scroll
watch(messages, () => {
  nextTick(() => scrollToBottom())
}, { deep: true })

// Methods
const loadConversation = async () => {
  try {
    const conversation = conversationStore.getCurrentConversation()
    if (conversation) {
      messages.value = conversation.messages
    }
  } catch (error) {
    console.error('Failed to load conversation:', error)
  }
}

const sendMessage = async () => {
  if (!messageText.value.trim() || loading.value) return

  const userMessage: Message = {
    id: Date.now().toString(),
    text: messageText.value,
    isUser: true,
    timestamp: new Date().toISOString(),
    attachments: [...attachedFiles.value]
  }

  messages.value.push(userMessage)
  const currentMessage = messageText.value
  messageText.value = ''
  attachedFiles.value = []
  
  try {
    loading.value = true
    isAssistantTyping.value = true
    
    const response = await chatApi.sendMessage({
      message: currentMessage,
      conversationId: conversationStore.currentConversationId,
      attachments: userMessage.attachments
    })

    const assistantMessage: Message = {
      id: response.data.messageId,
      text: response.data.response,
      isUser: false,
      timestamp: new Date().toISOString(),
      sources: response.data.sources
    }

    messages.value.push(assistantMessage)
    
    // Update conversation store
    conversationStore.addMessage(userMessage)
    conversationStore.addMessage(assistantMessage)
    
  } catch (error) {
    console.error('Failed to send message:', error)
    ElMessage.error('Failed to send message. Please try again.')
  } finally {
    loading.value = false
    isAssistantTyping.value = false
  }
}

const sendQuickAction = (actionText: string) => {
  messageText.value = actionText
  sendMessage()
}

const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && event.ctrlKey) {
    event.preventDefault()
    sendMessage()
  }
}

const handleInputChange = () => {
  // Auto-resize logic could be added here if needed
}

const handleFileAttach = (file: File) => {
  if (file.size > 10 * 1024 * 1024) { // 10MB limit
    ElMessage.error('File size must be less than 10MB')
    return false
  }

  const attachedFile: AttachedFile = {
    id: Date.now().toString(),
    name: file.name,
    size: file.size,
    type: file.type,
    file
  }

  attachedFiles.value.push(attachedFile)
  return false // Prevent auto upload
}

const removeAttachedFile = (fileId: string) => {
  const index = attachedFiles.value.findIndex(f => f.id === fileId)
  if (index > -1) {
    attachedFiles.value.splice(index, 1)
  }
}

const handleEditMessage = async (messageId: string, newText: string) => {
  const messageIndex = messages.value.findIndex(m => m.id === messageId)
  if (messageIndex > -1) {
    messages.value[messageIndex].text = newText
    // You might want to re-send the message or mark it as edited
    ElMessage.success('Message updated')
  }
}

const handleDeleteMessage = async (messageId: string) => {
  try {
    await ElMessageBox.confirm(
      'Are you sure you want to delete this message?',
      'Delete Message',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
    )
    
    const messageIndex = messages.value.findIndex(m => m.id === messageId)
    if (messageIndex > -1) {
      messages.value.splice(messageIndex, 1)
      ElMessage.success('Message deleted')
    }
  } catch (error) {
    // User cancelled
  }
}

const handleRegenerateMessage = async (messageId: string) => {
  try {
    loading.value = true
    
    const messageIndex = messages.value.findIndex(m => m.id === messageId)
    if (messageIndex > -1 && messageIndex > 0) {
      const previousMessage = messages.value[messageIndex - 1]
      
      const response = await chatApi.sendMessage({
        message: previousMessage.text,
        conversationId: conversationStore.currentConversationId,
        regenerate: true
      })

      messages.value[messageIndex].text = response.data.response
      messages.value[messageIndex].sources = response.data.sources
      
      ElMessage.success('Response regenerated')
    }
  } catch (error) {
    console.error('Failed to regenerate message:', error)
    ElMessage.error('Failed to regenerate response')
  } finally {
    loading.value = false
  }
}

const clearChat = async () => {
  try {
    await ElMessageBox.confirm(
      'This will clear all messages in the current conversation. Continue?',
      'Clear Chat',
      {
        confirmButtonText: 'Clear',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
    )
    
    messages.value = []
    conversationStore.clearCurrentConversation()
    ElMessage.success('Chat cleared')
  } catch (error) {
    // User cancelled
  }
}

const exportChat = async () => {
  try {
    const chatData = {
      timestamp: new Date().toISOString(),
      messages: messages.value.map(m => ({
        sender: m.isUser ? 'User' : 'Assistant',
        message: m.text,
        timestamp: m.timestamp
      }))
    }
    
    const blob = new Blob([JSON.stringify(chatData, null, 2)], {
      type: 'application/json'
    })
    
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `chat-export-${new Date().toISOString().split('T')[0]}.json`
    link.click()
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('Chat exported successfully')
  } catch (error) {
    ElMessage.error('Failed to export chat')
  }
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const handleScroll = () => {
  // Handle scroll events if needed (e.g., loading more messages)
}
</script>

<style scoped>
.chat-interface {
  @apply h-full flex flex-col bg-white;
}

.chat-header {
  @apply p-4 border-b border-gray-200 bg-white;
}

.messages-container {
  @apply flex-1 overflow-y-auto p-4 space-y-4;
}

.loading-placeholder {
  @apply space-y-4;
}

.empty-state {
  @apply flex flex-col items-center justify-center h-full text-center space-y-6;
}

.empty-icon {
  @apply text-6xl text-gray-300;
}

.empty-state h3 {
  @apply text-xl font-semibold text-gray-700;
}

.empty-state p {
  @apply text-gray-500 max-w-md;
}

.quick-actions {
  @apply flex flex-wrap gap-2 justify-center;
}

.quick-action-btn {
  @apply bg-blue-50 hover:bg-blue-100 text-blue-600 border-blue-200;
}

.messages-list {
  @apply space-y-4;
}

.typing-indicator {
  @apply flex justify-start;
}

.typing-bubble {
  @apply bg-gray-100 rounded-lg px-4 py-2;
}

.typing-dots {
  @apply flex space-x-1;
}

.typing-dots span {
  @apply w-2 h-2 bg-gray-400 rounded-full animate-pulse;
  animation-delay: 0.2s;
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.4s;
}

.typing-dots span:nth-child(3) {
  animation-delay: 0.6s;
}

.input-area {
  @apply border-t border-gray-200 bg-white;
}

.input-container {
  @apply p-4 space-y-3;
}

.attached-files {
  @apply flex flex-wrap gap-2;
}

.attached-file {
  @apply flex items-center space-x-2 bg-blue-50 text-blue-700 px-3 py-1 rounded-lg text-sm;
}

.message-input-wrapper {
  @apply relative;
}

.message-input {
  @apply pr-20;
}

.input-actions {
  @apply absolute right-2 bottom-2 flex items-center space-x-2;
}

.send-button {
  @apply rounded-full w-8 h-8 p-0 flex items-center justify-center;
}

:deep(.el-textarea__inner) {
  @apply resize-none border-gray-300 focus:border-blue-500;
}

:deep(.el-textarea__inner:focus) {
  @apply shadow-sm;
}
</style>