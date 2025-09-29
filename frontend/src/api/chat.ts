import { api } from './client'
import type { ChatRequest, ChatResponse, ConversationListResponse } from '@/types/chat'

export const chatApi = {
  // Send message
  sendMessage: (data: ChatRequest) => 
    api.post<ChatResponse>('/chat/send', data),

  // Get conversation history
  getConversation: (conversationId: string) =>
    api.get(`/chat/conversations/${conversationId}`),

  // List conversations
  getConversations: (params?: { page?: number; pageSize?: number }) =>
    api.get<ConversationListResponse>('/chat/conversations', { params }),

  // Create new conversation
  createConversation: () =>
    api.post('/chat/conversations'),

  // Update conversation
  updateConversation: (conversationId: string, data: { title?: string }) =>
    api.patch(`/chat/conversations/${conversationId}`, data),

  // Delete conversation
  deleteConversation: (conversationId: string) =>
    api.delete(`/chat/conversations/${conversationId}`),

  // Toggle favorite
  toggleFavorite: (conversationId: string) =>
    api.patch(`/chat/conversations/${conversationId}/favorite`),

  // Export conversation
  exportConversation: (conversationId: string) =>
    api.get(`/chat/conversations/${conversationId}/export`)
}