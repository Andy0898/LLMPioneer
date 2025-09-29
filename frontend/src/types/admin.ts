export interface SystemStats {
  users: {
    total: number
    change: number
  }
  conversations: {
    active: number
    change: number
  }
  knowledgeBase: {
    total: number
    change: number
  }
  system: {
    uptime: number
    status: string
    cpu: number
    memory: number
    disk: number
    network: number
  }
  userActivity?: Array<{
    date: string
    value: number
  }>
  activities?: Array<{
    timestamp: string
    user: string
    action: string
    status: string
  }>
  topUsers?: Array<{
    rank: number
    username: string
    conversations: number
    lastActive: string
  }>
  errorLogs?: Array<{
    timestamp: string
    level: string
    module: string
    message: string
    stackTrace?: string
  }>
}

export interface User {
  id: string
  username: string
  email: string
  fullName: string
  avatar?: string
  role: string
  permissions: string[]
  is_active: boolean
  last_login?: string
  created_at: string
  statusChanging?: boolean
}

export interface Role {
  id: string
  name: string
  description: string
  permissions: string[]
  userCount: number
  isSystem: boolean
  created_at: string
}

export interface Permission {
  id: string
  name: string
  description: string
  module: string
  action: string
}