import { api } from './client'
import type { 
  Conversation, 
  Message, 
  ConversationCreateRequest, 
  MessageSendRequest,
  MessageUpdateRequest,
  PaginatedResponse 
} from '@/types'

export const conversationApi = {
  // Get all conversations for current user
  getConversations: async (page: number = 1, size: number = 50): Promise<PaginatedResponse<Conversation>> => {
    const response = await api.get<PaginatedResponse<Conversation>>(
      `/api/v1/sa/conversation/list?page=${page}&size=${size}`
    )
    return response.data
  },

  // Get specific conversation
  getConversation: async (conversationId: string): Promise<Conversation> => {
    const response = await api.get<Conversation>(`/api/v1/sa/conversation/${conversationId}`)
    return response.data
  },

  // Create new conversation
  createConversation: async (request: ConversationCreateRequest): Promise<Conversation> => {
    const response = await api.post<Conversation>('/api/v1/sa/conversation/', {
      title: request.title
    })
    return response.data
  },

  // Update conversation
  updateConversation: async (conversationId: string, updates: Partial<Conversation>): Promise<Conversation> => {
    const response = await api.put<Conversation>(`/api/v1/sa/conversation/${conversationId}`, updates)
    return response.data
  },

  // Delete conversation
  deleteConversation: async (conversationId: string): Promise<void> => {
    await api.delete(`/api/v1/sa/conversation/${conversationId}`)
  },

  // Get messages for a conversation
  getMessages: async (conversationId: string, page: number = 1, size: number = 50): Promise<PaginatedResponse<Message>> => {
    const response = await api.get<PaginatedResponse<Message>>(
      `/api/v1/sa/conversation/${conversationId}/messages?page=${page}&size=${size}`
    )
    return response.data
  },

  // Send message in conversation
  sendMessage: async (request: MessageSendRequest): Promise<Message> => {
    const response = await api.post<Message>(
      `/api/v1/sa/conversation/${request.conversation_id}/send-message`,
      {
        question: request.question
      }
    )
    return response.data
  },

  // Get specific message
  getMessage: async (messageId: string): Promise<Message> => {
    const response = await api.get<Message>(`/api/v1/sa/conversation/message/${messageId}`)
    return response.data
  },

  // Update message (edit question)
  updateMessage: async (messageId: string, request: MessageUpdateRequest): Promise<Message> => {
    const response = await api.put<Message>(`/api/v1/sa/conversation/message/${messageId}`, {
      question: request.question
    })
    return response.data
  },

  // Delete message
  deleteMessage: async (messageId: string): Promise<void> => {
    await api.delete(`/api/v1/sa/conversation/message/${messageId}`)
  },

  // Regenerate message response
  regenerateMessage: async (messageId: string): Promise<Message> => {
    const response = await api.post<Message>(`/api/v1/sa/conversation/message/${messageId}/regenerate`)
    return response.data
  },

  // Get conversation statistics
  getConversationStats: async (conversationId: string): Promise<{
    message_count: number
    total_tokens_used: number
    average_response_time: number
    created_at: string
    last_activity: string
  }> => {
    const response = await api.get(`/api/v1/sa/conversation/${conversationId}/stats`)
    return response.data
  },

  // Search conversations
  searchConversations: async (query: string, page: number = 1, size: number = 20): Promise<PaginatedResponse<Conversation>> => {
    const response = await api.get<PaginatedResponse<Conversation>>(
      `/api/v1/sa/conversation/search?q=${encodeURIComponent(query)}&page=${page}&size=${size}`
    )
    return response.data
  },

  // Archive conversation
  archiveConversation: async (conversationId: string): Promise<Conversation> => {
    const response = await api.patch<Conversation>(`/api/v1/sa/conversation/${conversationId}/archive`)
    return response.data
  },

  // Unarchive conversation
  unarchiveConversation: async (conversationId: string): Promise<Conversation> => {
    const response = await api.patch<Conversation>(`/api/v1/sa/conversation/${conversationId}/unarchive`)
    return response.data
  },

  // Export conversation
  exportConversation: async (conversationId: string, format: 'json' | 'txt' | 'md' = 'md'): Promise<Blob> => {
    const response = await api.get(`/api/v1/sa/conversation/${conversationId}/export?format=${format}`, {
      responseType: 'blob'
    })
    return response.data
  },

  // Share conversation (get share link)
  shareConversation: async (conversationId: string): Promise<{ share_url: string; expires_at: string }> => {
    const response = await api.post(`/api/v1/sa/conversation/${conversationId}/share`)
    return response.data
  },

  // Get shared conversation (public access)
  getSharedConversation: async (shareToken: string): Promise<{
    conversation: Conversation
    messages: Message[]
  }> => {
    const response = await api.get(`/api/v1/public/conversation/shared/${shareToken}`)
    return response.data
  }
}