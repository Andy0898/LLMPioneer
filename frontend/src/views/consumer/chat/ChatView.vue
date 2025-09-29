<template>
  <div class="chat-view">
    <div class="flex h-full">
      <!-- Conversation List Sidebar -->
      <div class="w-80 border-r border-gray-200 bg-gray-50">
        <div class="p-4 border-b border-gray-200">
          <el-button type="primary" class="w-full" @click="startNewConversation">
            <el-icon><Plus /></el-icon>
            New Chat
          </el-button>
        </div>
        <div class="p-4">
          <h3 class="text-sm font-medium text-gray-500 mb-3">Recent Conversations</h3>
          <div class="space-y-2">
            <div 
              v-for="conversation in conversations" 
              :key="conversation.id"
              :class="[
                'p-3 rounded-lg cursor-pointer transition-colors',
                conversation.id === currentConversationId 
                  ? 'bg-blue-100 border border-blue-200' 
                  : 'hover:bg-gray-100'
              ]"
              @click="selectConversation(conversation.id)"
            >
              <div class="font-medium text-sm truncate">{{ conversation.title }}</div>
              <div class="text-xs text-gray-500 mt-1">
                {{ formatDate(conversation.updatedAt) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Chat Interface -->
      <div class="flex-1 flex flex-col">
        <!-- Chat Header -->
        <div class="p-4 border-b border-gray-200 bg-white">
          <h2 class="text-lg font-semibold">{{ currentConversationTitle }}</h2>
        </div>

        <!-- Messages Area -->
        <div class="flex-1 overflow-y-auto p-4 space-y-4" ref="messagesContainer">
          <div 
            v-for="message in messages" 
            :key="message.id"
            :class="[
              'flex',
              message.role === 'user' ? 'justify-end' : 'justify-start'
            ]"
          >
            <div 
              :class="[
                'max-w-3xl rounded-lg p-4',
                message.role === 'user' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-100 text-gray-900'
              ]"
            >
              <div class="whitespace-pre-wrap">{{ message.content }}</div>
              <div class="text-xs mt-2 opacity-70">
                {{ formatTime(message.createdAt) }}
              </div>
            </div>
          </div>
          
          <!-- Typing Indicator -->
          <div v-if="isTyping" class="flex justify-start">
            <div class="bg-gray-100 rounded-lg p-4 max-w-3xl">
              <div class="flex space-x-2">
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Input Area -->
        <div class="p-4 border-t border-gray-200 bg-white">
          <div class="flex space-x-4">
            <el-input
              v-model="newMessage"
              type="textarea"
              :rows="3"
              placeholder="Type your message here..."
              @keydown.ctrl.enter="sendMessage"
              :disabled="isTyping"
            />
            <el-button 
              type="primary" 
              @click="sendMessage"
              :loading="isTyping"
              :disabled="!newMessage.trim()"
            >
              <el-icon><Plus /></el-icon>
              Send
            </el-button>
          </div>
          <div class="text-xs text-gray-500 mt-2">
            Press Ctrl+Enter to send
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { Plus } from '@element-plus/icons-vue'

interface Conversation {
  id: string
  title: string
  updatedAt: string
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  createdAt: string
}

const conversations = ref<Conversation[]>([])
const messages = ref<Message[]>([])
const newMessage = ref('')
const isTyping = ref(false)
const currentConversationId = ref<string | null>(null)
const currentConversationTitle = ref('New Chat')
const messagesContainer = ref<HTMLElement | null>(null)

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString()
}

const formatTime = (date: string) => {
  return new Date(date).toLocaleTimeString()
}

const startNewConversation = () => {
  currentConversationId.value = null
  currentConversationTitle.value = 'New Chat'
  messages.value = []
  newMessage.value = ''
}

const selectConversation = (conversationId: string) => {
  currentConversationId.value = conversationId
  const conversation = conversations.value.find(c => c.id === conversationId)
  if (conversation) {
    currentConversationTitle.value = conversation.title
    // TODO: Load messages for this conversation
    messages.value = []
  }
}

const sendMessage = async () => {
  if (!newMessage.value.trim() || isTyping.value) return

  const userMessage: Message = {
    id: Date.now().toString(),
    role: 'user' as const,
    content: newMessage.value.trim(),
    createdAt: new Date().toISOString()
  }

  messages.value.push(userMessage)
  newMessage.value = ''
  isTyping.value = true

  // Scroll to bottom
  await nextTick()
  messagesContainer.value?.scrollTo({ top: messagesContainer.value.scrollHeight, behavior: 'smooth' })

  try {
    // TODO: Send message to API and get response
    await new Promise(resolve => setTimeout(resolve, 2000)) // Simulate API call
    
    const aiMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant' as const,
      content: 'This is a placeholder response. The actual AI integration will be implemented later.',
      createdAt: new Date().toISOString()
    }

    messages.value.push(aiMessage)
    
    // Scroll to bottom
    await nextTick()
    messagesContainer.value?.scrollTo({ top: messagesContainer.value.scrollHeight, behavior: 'smooth' })
  } catch (error) {
    console.error('Error sending message:', error)
  } finally {
    isTyping.value = false
  }
}

onMounted(() => {
  // TODO: Load conversations from API
  conversations.value = [
    {
      id: '1',
      title: 'Welcome Chat',
      updatedAt: new Date().toISOString()
    }
  ]
})
</script>

<style scoped>
.chat-view {
  height: calc(100vh - 64px); /* Adjust based on your header height */
}
</style>