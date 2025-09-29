// Route names constants
export const ROUTE_NAMES = {
  // Admin routes
  ADMIN_LOGIN: 'AdminLogin',
  ADMIN_DASHBOARD: 'AdminDashboard',
  ADMIN_USERS: 'AdminUsers',
  ADMIN_ROLES: 'AdminRoles',
  ADMIN_KNOWLEDGE: 'AdminKnowledge',
  ADMIN_LLM_CONFIG: 'AdminLLMConfig',
  
  // Consumer routes
  CONSUMER_LOGIN: 'ConsumerLogin',
  CONSUMER_DASHBOARD: 'ConsumerDashboard',
  CONSUMER_CHAT: 'ConsumerChat',
  CONSUMER_CHAT_CONVERSATION: 'ConsumerChatConversation',
  CONSUMER_WRITING: 'ConsumerWriting',
  CONSUMER_KNOWLEDGE: 'ConsumerKnowledge',
  
  // Error routes
  NOT_FOUND: 'NotFound',
  FORBIDDEN: 'Forbidden'
} as const

// Route paths constants
export const ROUTE_PATHS = {
  HOME: '/',
  
  // Admin paths
  ADMIN_ROOT: '/admin',
  ADMIN_LOGIN: '/admin/login',
  ADMIN_DASHBOARD: '/admin/dashboard',
  ADMIN_USERS: '/admin/users',
  ADMIN_ROLES: '/admin/roles',
  ADMIN_KNOWLEDGE: '/admin/knowledge',
  ADMIN_LLM_CONFIG: '/admin/settings/llm',
  
  // Consumer paths
  CONSUMER_ROOT: '/user',
  CONSUMER_LOGIN: '/user/login',
  CONSUMER_DASHBOARD: '/user/dashboard',
  CONSUMER_CHAT: '/user/chat',
  CONSUMER_WRITING: '/user/writing',
  CONSUMER_KNOWLEDGE: '/user/knowledge'
} as const

// Menu configuration for navigation
export const ADMIN_MENU_ITEMS = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: 'Dashboard',
    route: ROUTE_PATHS.ADMIN_DASHBOARD,
    permission: null
  },
  {
    id: 'users',
    label: 'User Management',
    icon: 'User',
    route: ROUTE_PATHS.ADMIN_USERS,
    permission: 'user:read'
  },
  {
    id: 'roles',
    label: 'Role Management',
    icon: 'UserFilled',
    route: ROUTE_PATHS.ADMIN_ROLES,
    permission: 'role:read'
  },
  {
    id: 'knowledge',
    label: 'Knowledge Base',
    icon: 'FolderOpened',
    route: ROUTE_PATHS.ADMIN_KNOWLEDGE,
    permission: 'knowledge:read'
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: 'Setting',
    children: [
      {
        id: 'llm-config',
        label: 'LLM Configuration',
        icon: 'cpu',
        route: ROUTE_PATHS.ADMIN_LLM_CONFIG,
        permission: 'system:configure'
      }
    ]
  }
]

export const CONSUMER_MENU_ITEMS = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: 'House',
    route: ROUTE_PATHS.CONSUMER_DASHBOARD
  },
  {
    id: 'chat',
    label: 'AI Chat',
    icon: 'ChatDotRound',
    route: ROUTE_PATHS.CONSUMER_CHAT
  },
  {
    id: 'writing',
    label: 'Writing Assistant',
    icon: 'EditPen',
    route: ROUTE_PATHS.CONSUMER_WRITING
  },
  {
    id: 'knowledge',
    label: 'Personal Knowledge',
    icon: 'Document',
    route: ROUTE_PATHS.CONSUMER_KNOWLEDGE
  }
]