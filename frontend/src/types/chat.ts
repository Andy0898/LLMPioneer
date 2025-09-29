export interface Message {
  id: string
  text: string
  isUser: boolean
  timestamp: string
  attachments?: AttachedFile[]
  sources?: Source[]
}

export interface AttachedFile {
  id: string
  name: string
  size: number
  type: string
  file?: File
}

export interface Source {
  id: string
  title: string
  url?: string
  snippet?: string
}

export interface Conversation {
  id: string
  title?: string
  messages: Message[]
  createdAt: string
  updatedAt: string
  lastMessage?: string
  messageCount: number
  isFavorite: boolean
}

export interface ChatRequest {
  message: string
  conversationId?: string
  attachments?: AttachedFile[]
  regenerate?: boolean
}

export interface ChatResponse {
  messageId: string
  response: string
  sources?: Source[]
  conversationId: string
}

export interface ConversationListResponse {
  conversations: Conversation[]
  total: number
  page: number
  pageSize: number
}