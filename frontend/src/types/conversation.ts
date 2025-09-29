export interface Conversation {
  id: string
  title: string
  user_id: string
  created_at: string
  updated_at: string
  is_active: boolean
  message_count: number
  last_message_at?: string
}

export interface Message {
  id: string
  conversation_id: string
  question: string
  answer?: string
  created_at: string
  updated_at: string
  is_active: boolean
  tokens_used?: number
  processing_time?: number
}

export interface ConversationCreateRequest {
  title: string
  initial_message?: string
}

export interface MessageSendRequest {
  question: string
  conversation_id: string
}

export interface MessageUpdateRequest {
  question: string
}

export interface ConversationState {
  conversations: Conversation[]
  activeConversation: Conversation | null
  messages: Message[]
  isLoading: boolean
  isTyping: boolean
  error: string | null
}