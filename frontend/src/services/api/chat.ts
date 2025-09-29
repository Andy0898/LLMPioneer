import { httpClient } from './http'
import type { ChatRequest, ChatResponse, ConversationListResponse } from '@/types/chat'

export const chatApi = {
  // Send message
  sendMessage: (data: ChatRequest) => 
    httpClient.post<ChatResponse>('/chat/send', data),

  // Get conversation history
  getConversation: (conversationId: string) =>
    httpClient.get(`/chat/conversations/${conversationId}`),

  // List conversations
  getConversations: (params?: { page?: number; pageSize?: number }) =>
    httpClient.get<ConversationListResponse>('/chat/conversations', { params }),

  // Create new conversation
  createConversation: () =>
    httpClient.post('/chat/conversations'),

  // Update conversation
  updateConversation: (conversationId: string, data: { title?: string }) =>
    httpClient.patch(`/chat/conversations/${conversationId}`, data),

  // Delete conversation
  deleteConversation: (conversationId: string) =>
    httpClient.delete(`/chat/conversations/${conversationId}`),

  // Toggle favorite
  toggleFavorite: (conversationId: string) =>
    httpClient.patch(`/chat/conversations/${conversationId}/favorite`),

  // Export conversation
  exportConversation: (conversationId: string) =>
    httpClient.get(`/chat/conversations/${conversationId}/export`)
}

export const conversationApi = chatApi