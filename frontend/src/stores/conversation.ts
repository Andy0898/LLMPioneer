import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { 
  Conversation, 
  Message, 
  ConversationCreateRequest, 
  MessageSendRequest,
  MessageUpdateRequest 
} from '@/types'
import { conversationApi } from '@/api/conversation'
import { ElMessage } from 'element-plus'

export const useConversationStore = defineStore('conversation', () => {
  // State
  const conversations = ref<Conversation[]>([])
  const activeConversation = ref<Conversation | null>(null)
  const messages = ref<Message[]>([])
  const isLoading = ref(false)
  const isTyping = ref(false)
  const isSending = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const totalConversations = computed(() => conversations.value.length)
  const activeConversationMessages = computed(() => 
    messages.value.filter(msg => msg.conversation_id === activeConversation.value?.id)
  )
  const hasActiveConversation = computed(() => !!activeConversation.value)
  const sortedConversations = computed(() => 
    [...conversations.value].sort((a, b) => 
      new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    )
  )

  // Actions
  const fetchConversations = async () => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await conversationApi.getConversations()
      conversations.value = response.data
      
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch conversations'
      ElMessage.error(error.value)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const createConversation = async (request: ConversationCreateRequest) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await conversationApi.createConversation(request)
      const newConversation = response.data
      
      conversations.value.unshift(newConversation)
      activeConversation.value = newConversation
      
      // If there's an initial message, send it
      if (request.initial_message) {
        await sendMessage({
          question: request.initial_message,
          conversation_id: newConversation.id
        })
      }
      
      ElMessage.success('Conversation created successfully!')
      return newConversation
      
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to create conversation'
      ElMessage.error(error.value)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const selectConversation = async (conversationId: string) => {
    try {
      const conversation = conversations.value.find(c => c.id === conversationId)
      if (!conversation) {
        throw new Error('Conversation not found')
      }
      
      activeConversation.value = conversation
      await fetchMessages(conversationId)
      
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to select conversation'
      ElMessage.error(error.value)
      throw err
    }
  }

  const fetchMessages = async (conversationId: string) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await conversationApi.getMessages(conversationId)
      messages.value = response.data
      
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch messages'
      ElMessage.error(error.value)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const sendMessage = async (request: MessageSendRequest) => {
    try {
      isSending.value = true
      isTyping.value = true
      error.value = null
      
      // Create optimistic message
      const optimisticMessage: Message = {
        id: `temp_${Date.now()}`,
        conversation_id: request.conversation_id,
        question: request.question,
        answer: undefined,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        is_active: true
      }
      
      messages.value.push(optimisticMessage)
      
      const response = await conversationApi.sendMessage(request)
      const newMessage = response.data
      
      // Replace optimistic message with real message
      const index = messages.value.findIndex(m => m.id === optimisticMessage.id)
      if (index !== -1) {
        messages.value[index] = newMessage
      }
      
      // Update conversation's last message time
      const conversation = conversations.value.find(c => c.id === request.conversation_id)
      if (conversation) {
        conversation.updated_at = newMessage.updated_at
        conversation.message_count = (conversation.message_count || 0) + 1
        conversation.last_message_at = newMessage.created_at
      }
      
      return newMessage
      
    } catch (err: any) {
      // Remove optimistic message on error
      messages.value = messages.value.filter(m => !m.id.startsWith('temp_'))
      
      error.value = err.response?.data?.message || 'Failed to send message'
      ElMessage.error(error.value)
      throw err
    } finally {
      isSending.value = false
      isTyping.value = false
    }
  }

  const updateMessage = async (messageId: string, request: MessageUpdateRequest) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await conversationApi.updateMessage(messageId, request)
      const updatedMessage = response.data
      
      // Update message in store
      const index = messages.value.findIndex(m => m.id === messageId)
      if (index !== -1) {
        messages.value[index] = updatedMessage
      }
      
      ElMessage.success('Message updated successfully!')
      return updatedMessage
      
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to update message'
      ElMessage.error(error.value)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const deleteConversation = async (conversationId: string) => {
    try {
      isLoading.value = true
      error.value = null
      
      await conversationApi.deleteConversation(conversationId)
      
      // Remove from store
      conversations.value = conversations.value.filter(c => c.id !== conversationId)
      
      // Clear active conversation if it was deleted
      if (activeConversation.value?.id === conversationId) {
        activeConversation.value = null
        messages.value = []
      }
      
      ElMessage.success('Conversation deleted successfully!')
      
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to delete conversation'
      ElMessage.error(error.value)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const deleteMessage = async (messageId: string) => {
    try {
      isLoading.value = true
      error.value = null
      
      await conversationApi.deleteMessage(messageId)
      
      // Remove from store
      messages.value = messages.value.filter(m => m.id !== messageId)
      
      // Update conversation message count
      if (activeConversation.value) {
        const conversation = conversations.value.find(c => c.id === activeConversation.value!.id)
        if (conversation && conversation.message_count > 0) {
          conversation.message_count -= 1
        }
      }
      
      ElMessage.success('Message deleted successfully!')
      
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to delete message'
      ElMessage.error(error.value)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const clearActiveConversation = () => {
    activeConversation.value = null
    messages.value = []
  }

  const clearError = () => {
    error.value = null
  }

  const updateConversationTitle = async (conversationId: string, title: string) => {
    try {
      const response = await conversationApi.updateConversation(conversationId, { title })
      const updatedConversation = response.data
      
      // Update in store
      const index = conversations.value.findIndex(c => c.id === conversationId)
      if (index !== -1) {
        conversations.value[index] = updatedConversation
      }
      
      // Update active conversation if it's the one being updated
      if (activeConversation.value?.id === conversationId) {
        activeConversation.value = updatedConversation
      }
      
      ElMessage.success('Conversation title updated!')
      return updatedConversation
      
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to update conversation title'
      ElMessage.error(error.value)
      throw err
    }
  }

  // Real-time typing simulation
  const simulateTyping = (duration: number = 2000) => {
    isTyping.value = true
    setTimeout(() => {
      isTyping.value = false
    }, duration)
  }

  return {
    // State
    conversations: readonly(conversations),
    activeConversation: readonly(activeConversation),
    messages: readonly(messages),
    isLoading: readonly(isLoading),
    isTyping: readonly(isTyping),
    isSending: readonly(isSending),
    error: readonly(error),
    
    // Getters
    totalConversations,
    activeConversationMessages,
    hasActiveConversation,
    sortedConversations,
    
    // Actions
    fetchConversations,
    createConversation,
    selectConversation,
    fetchMessages,
    sendMessage,
    updateMessage,
    deleteConversation,
    deleteMessage,
    clearActiveConversation,
    clearError,
    updateConversationTitle,
    simulateTyping
  }
})