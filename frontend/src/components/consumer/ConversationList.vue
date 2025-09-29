<template>
  <div class="conversation-list">
    <!-- Header -->
    <div class="list-header">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold text-gray-800">Conversations</h3>
        <el-button type="primary" size="small" @click="createNewConversation">
          <el-icon><Plus /></el-icon>
          New Chat
        </el-button>
      </div>
      
      <!-- Search -->
      <el-input
        v-model="searchQuery"
        placeholder="Search conversations..."
        size="small"
        clearable
        class="mt-3"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <!-- Filters -->
    <div class="filters">
      <el-radio-group v-model="activeFilter" size="small">
        <el-radio-button label="all">All</el-radio-button>
        <el-radio-button label="recent">Recent</el-radio-button>
        <el-radio-button label="favorites">Favorites</el-radio-button>
      </el-radio-group>
    </div>

    <!-- Conversations -->
    <div class="conversations-container">
      <div v-if="loading" class="loading-state">
        <el-skeleton :rows="3" animated />
      </div>
      
      <div v-else-if="filteredConversations.length === 0" class="empty-state">
        <el-icon class="empty-icon"><ChatDotRound /></el-icon>
        <p class="empty-text">No conversations found</p>
        <el-button type="primary" size="small" @click="createNewConversation">
          Start your first conversation
        </el-button>
      </div>
      
      <div v-else class="conversations">
        <div
          v-for="conversation in filteredConversations"
          :key="conversation.id"
          class="conversation-item"
          :class="{ 'active': conversation.id === currentConversationId }"
          @click="selectConversation(conversation.id)"
        >
          <div class="conversation-content">
            <div class="conversation-header">
              <h4 class="conversation-title">{{ conversation.title || 'New Conversation' }}</h4>
              <div class="conversation-meta">
                <span class="conversation-time">{{ formatTime(conversation.updatedAt) }}</span>
                <el-dropdown @command="handleConversationAction">
                  <el-button text size="small" @click.stop>
                    <el-icon><MoreFilled /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item :command="`favorite:${conversation.id}`">
                        <el-icon><Star /></el-icon>
                        {{ conversation.isFavorite ? 'Unfavorite' : 'Favorite' }}
                      </el-dropdown-item>
                      <el-dropdown-item :command="`rename:${conversation.id}`">
                        <el-icon><Edit /></el-icon>
                        Rename
                      </el-dropdown-item>
                      <el-dropdown-item :command="`export:${conversation.id}`">
                        <el-icon><Download /></el-icon>
                        Export
                      </el-dropdown-item>
                      <el-dropdown-item 
                        :command="`delete:${conversation.id}`" 
                        class="text-red-600"
                      >
                        <el-icon><Delete /></el-icon>
                        Delete
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
            
            <p class="conversation-preview">{{ conversation.lastMessage || 'No messages yet' }}</p>
            
            <div class="conversation-stats">
              <span class="message-count">
                <el-icon><ChatDotRound /></el-icon>
                {{ conversation.messageCount }} messages
              </span>
              <el-icon v-if="conversation.isFavorite" class="favorite-icon">
                <Star />
              </el-icon>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Rename Dialog -->
    <el-dialog
      v-model="showRenameDialog"
      title="Rename Conversation"
      width="400px"
    >
      <el-form @submit.prevent="saveRename">
        <el-form-item label="Title">
          <el-input
            v-model="renameTitle"
            placeholder="Enter conversation title"
            maxlength="100"
            show-word-limit
            @keydown.enter="saveRename"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="flex justify-end space-x-2">
          <el-button @click="showRenameDialog = false">Cancel</el-button>
          <el-button type="primary" @click="saveRename">Save</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Search,
  ChatDotRound,
  MoreFilled,
  Star,
  Edit,
  Download,
  Delete
} from '@element-plus/icons-vue'
import { useConversationStore } from '@/stores/conversation'
import { conversationApi } from '@/api'
import type { Conversation } from '@/types/chat'

// Store
const conversationStore = useConversationStore()

// Reactive state
const loading = ref(false)
const searchQuery = ref('')
const activeFilter = ref('all')
const conversations = ref<Conversation[]>([])
const showRenameDialog = ref(false)
const renameTitle = ref('')
const renameConversationId = ref<string | null>(null)

// Computed
const currentConversationId = computed(() => conversationStore.currentConversationId)

const filteredConversations = computed(() => {
  let filtered = conversations.value

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(conv => 
      conv.title?.toLowerCase().includes(query) ||
      conv.lastMessage?.toLowerCase().includes(query)
    )
  }

  // Type filter
  switch (activeFilter.value) {
    case 'recent':
      filtered = filtered.filter(conv => {
        const dayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000)
        return new Date(conv.updatedAt) > dayAgo
      })
      break
    case 'favorites':
      filtered = filtered.filter(conv => conv.isFavorite)
      break
  }

  // Sort by updated time (most recent first)
  return filtered.sort((a, b) => 
    new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
  )
})

// Lifecycle
onMounted(() => {
  loadConversations()
})

// Watch for conversation store changes
watch(
  () => conversationStore.conversations,
  (newConversations) => {
    conversations.value = newConversations
  },
  { immediate: true, deep: true }
)

// Methods
const loadConversations = async () => {
  try {
    loading.value = true
    await conversationStore.loadConversations()
  } catch (error) {
    console.error('Failed to load conversations:', error)
    ElMessage.error('Failed to load conversations')
  } finally {
    loading.value = false
  }
}

const createNewConversation = async () => {
  try {
    const newConversation = await conversationStore.createConversation()
    ElMessage.success('New conversation created')
    selectConversation(newConversation.id)
  } catch (error) {
    console.error('Failed to create conversation:', error)
    ElMessage.error('Failed to create new conversation')
  }
}

const selectConversation = async (conversationId: string) => {
  try {
    await conversationStore.setCurrentConversation(conversationId)
  } catch (error) {
    console.error('Failed to select conversation:', error)
    ElMessage.error('Failed to load conversation')
  }
}

const handleConversationAction = async (command: string) => {
  const [action, conversationId] = command.split(':')
  
  switch (action) {
    case 'favorite':
      await toggleFavorite(conversationId)
      break
    case 'rename':
      await startRename(conversationId)
      break
    case 'export':
      await exportConversation(conversationId)
      break
    case 'delete':
      await deleteConversation(conversationId)
      break
  }
}

const toggleFavorite = async (conversationId: string) => {
  try {
    await conversationStore.toggleFavorite(conversationId)
    ElMessage.success('Conversation updated')
  } catch (error) {
    console.error('Failed to toggle favorite:', error)
    ElMessage.error('Failed to update conversation')
  }
}

const startRename = async (conversationId: string) => {
  const conversation = conversations.value.find(c => c.id === conversationId)
  if (conversation) {
    renameConversationId.value = conversationId
    renameTitle.value = conversation.title || ''
    showRenameDialog.value = true
  }
}

const saveRename = async () => {
  if (!renameConversationId.value || !renameTitle.value.trim()) {
    ElMessage.warning('Please enter a valid title')
    return
  }

  try {
    await conversationStore.updateConversation(renameConversationId.value, {
      title: renameTitle.value.trim()
    })
    
    showRenameDialog.value = false
    renameConversationId.value = null
    renameTitle.value = ''
    
    ElMessage.success('Conversation renamed')
  } catch (error) {
    console.error('Failed to rename conversation:', error)
    ElMessage.error('Failed to rename conversation')
  }
}

const exportConversation = async (conversationId: string) => {
  try {
    const conversation = conversations.value.find(c => c.id === conversationId)
    if (!conversation) return

    const response = await conversationApi.exportConversation(conversationId)
    
    const blob = new Blob([JSON.stringify(response.data, null, 2)], {
      type: 'application/json'
    })
    
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `conversation-${conversation.title || conversationId}-${new Date().toISOString().split('T')[0]}.json`
    link.click()
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('Conversation exported')
  } catch (error) {
    console.error('Failed to export conversation:', error)
    ElMessage.error('Failed to export conversation')
  }
}

const deleteConversation = async (conversationId: string) => {
  try {
    const conversation = conversations.value.find(c => c.id === conversationId)
    if (!conversation) return

    await ElMessageBox.confirm(
      `Delete "${conversation.title || 'Untitled Conversation'}"? This action cannot be undone.`,
      'Delete Conversation',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
    )
    
    await conversationStore.deleteConversation(conversationId)
    ElMessage.success('Conversation deleted')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete conversation:', error)
      ElMessage.error('Failed to delete conversation')
    }
  }
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
</script>

<style scoped>
.conversation-list {
  @apply h-full flex flex-col bg-white border-r border-gray-200;
}

.list-header {
  @apply p-4 border-b border-gray-200;
}

.filters {
  @apply p-4 border-b border-gray-200;
}

.conversations-container {
  @apply flex-1 overflow-y-auto;
}

.loading-state {
  @apply p-4;
}

.empty-state {
  @apply flex flex-col items-center justify-center h-full text-center space-y-4 p-8;
}

.empty-icon {
  @apply text-4xl text-gray-300;
}

.empty-text {
  @apply text-gray-500;
}

.conversations {
  @apply divide-y divide-gray-100;
}

.conversation-item {
  @apply p-4 hover:bg-gray-50 cursor-pointer transition-colors;
}

.conversation-item.active {
  @apply bg-blue-50 border-r-2 border-blue-500;
}

.conversation-content {
  @apply space-y-2;
}

.conversation-header {
  @apply flex items-start justify-between;
}

.conversation-title {
  @apply font-medium text-gray-800 text-sm truncate flex-1 mr-2;
}

.conversation-meta {
  @apply flex items-center space-x-2 flex-shrink-0;
}

.conversation-time {
  @apply text-xs text-gray-500;
}

.conversation-preview {
  @apply text-sm text-gray-600 line-clamp-2 leading-relaxed;
}

.conversation-stats {
  @apply flex items-center justify-between text-xs text-gray-500;
}

.message-count {
  @apply flex items-center space-x-1;
}

.favorite-icon {
  @apply text-yellow-500;
}

/* Line clamp utility */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>