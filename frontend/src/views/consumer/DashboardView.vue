<template>
  <div class="consumer-dashboard">
    <div class="dashboard-content">
      <!-- Welcome Section -->
      <div class="welcome-section">
        <el-card class="welcome-card">
          <div class="welcome-content">
            <div class="welcome-text">
              <h2>Welcome back, {{ userName }}!</h2>
              <p>Ready to explore AI-powered conversations and smart writing assistance?</p>
            </div>
            <div class="welcome-actions">
              <el-button type="primary" size="large" @click="$router.push('/user/chat')">
                <el-icon><ChatDotRound /></el-icon>
                Start New Chat
              </el-button>
            </div>
          </div>
        </el-card>
      </div>
      
      <!-- Quick Stats -->
      <div class="stats-grid">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon chat">
              <el-icon size="20">
                <ChatDotRound />
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">24</div>
              <div class="stat-label">Conversations</div>
            </div>
          </div>
        </el-card>
        
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon document">
              <el-icon size="20">
                <Document />
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">12</div>
              <div class="stat-label">Documents</div>
            </div>
          </div>
        </el-card>
        
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon writing">
              <el-icon size="20">
                <EditPen />
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">8</div>
              <div class="stat-label">Writing Projects</div>
            </div>
          </div>
        </el-card>
      </div>
      
      <!-- Main Content Grid -->
      <div class="content-grid">
        <!-- Recent Conversations -->
        <el-card class="conversations-card">
          <template #header>
            <div class="card-header">
              <span>Recent Conversations</span>
              <el-button text @click="$router.push('/user/chat')">View All</el-button>
            </div>
          </template>
          <div class="conversations-list">
            <div 
              v-for="conversation in recentConversations" 
              :key="conversation.id" 
              class="conversation-item"
              @click="openConversation(conversation.id)"
            >
              <div class="conversation-content">
                <div class="conversation-title">{{ conversation.title }}</div>
                <div class="conversation-preview">{{ conversation.lastMessage }}</div>
              </div>
              <div class="conversation-meta">
                <div class="conversation-time">{{ formatTime(conversation.updatedAt) }}</div>
                <el-tag size="small" :type="conversation.status === 'active' ? 'success' : 'info'">
                  {{ conversation.messageCount }} messages
                </el-tag>
              </div>
            </div>
            
            <div v-if="recentConversations.length === 0" class="empty-state">
              <el-icon size="48" color="var(--el-text-color-placeholder)">
                <ChatDotRound />
              </el-icon>
              <p>No conversations yet</p>
              <el-button type="primary" @click="$router.push('/user/chat')">
                Start Your First Chat
              </el-button>
            </div>
          </div>
        </el-card>
        
        <!-- Quick Actions -->
        <el-card class="actions-card">
          <template #header>
            <span>Quick Actions</span>
          </template>
          <div class="action-buttons">
            <el-button 
              class="action-button" 
              @click="$router.push('/user/chat')"
            >
              <div class="action-content">
                <el-icon size="24" color="#52c41a">
                  <ChatDotRound />
                </el-icon>
                <div>
                  <div class="action-title">AI Chat</div>
                  <div class="action-desc">Start a conversation</div>
                </div>
              </div>
            </el-button>
            
            <el-button 
              class="action-button" 
              @click="$router.push('/user/writing')"
            >
              <div class="action-content">
                <el-icon size="24" color="#1890ff">
                  <EditPen />
                </el-icon>
                <div>
                  <div class="action-title">Writing Assistant</div>
                  <div class="action-desc">Get writing help</div>
                </div>
              </div>
            </el-button>
            
            <el-button 
              class="action-button" 
              @click="$router.push('/user/knowledge')"
            >
              <div class="action-content">
                <el-icon size="24" color="#faad14">
                  <Document />
                </el-icon>
                <div>
                  <div class="action-title">Documents</div>
                  <div class="action-desc">Upload & search files</div>
                </div>
              </div>
            </el-button>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { 
  ChatDotRound, 
  Document, 
  EditPen
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const userName = computed(() => authStore.user?.full_name || authStore.user?.username || 'User')

const recentConversations = ref([
  {
    id: '1',
    title: 'Project Planning Discussion',
    lastMessage: 'Can you help me create a project timeline?',
    updatedAt: new Date(Date.now() - 3600000).toISOString(),
    messageCount: 15,
    status: 'active'
  },
  {
    id: '2',
    title: 'Code Review Help',
    lastMessage: 'I need help reviewing this Python code.',
    updatedAt: new Date(Date.now() - 7200000).toISOString(),
    messageCount: 8,
    status: 'completed'
  },
  {
    id: '3',
    title: 'Writing Assistance',
    lastMessage: 'Help me improve this blog post draft.',
    updatedAt: new Date(Date.now() - 86400000).toISOString(),
    messageCount: 12,
    status: 'active'
  }
])

const openConversation = (id: string) => {
  router.push(`/user/chat/${id}`)
}

const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (hours < 1) return 'Just now'
  if (hours < 24) return `${hours}h ago`
  if (days < 7) return `${days}d ago`
  return date.toLocaleDateString()
}
</script>

<style scoped>
.consumer-dashboard {
  padding: 0;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.welcome-section {
  margin-bottom: 8px;
}

.welcome-card {
  border: none;
  background: linear-gradient(135deg, #f6ffed 0%, #ffffff 100%);
  border-left: 4px solid #52c41a;
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
}

.welcome-text h2 {
  margin: 0 0 8px 0;
  color: #389e0d;
  font-size: 24px;
  font-weight: 600;
}

.welcome-text p {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat-card {
  border: none;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon.chat {
  background: #f6ffed;
  color: #52c41a;
}

.stat-icon.document {
  background: #fff7e6;
  color: #faad14;
}

.stat-icon.writing {
  background: #f0f8ff;
  color: #1890ff;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}

.conversations-card,
.actions-card {
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.conversations-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.conversation-item {
  padding: 16px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--el-bg-color);
}

.conversation-item:hover {
  border-color: #52c41a;
  background: #f6ffed;
}

.conversation-content {
  margin-bottom: 8px;
}

.conversation-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}

.conversation-preview {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.4;
}

.conversation-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.conversation-time {
  font-size: 11px;
  color: var(--el-text-color-placeholder);
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--el-text-color-secondary);
}

.empty-state p {
  margin: 16px 0 24px 0;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-button {
  height: auto;
  padding: 16px;
  border: 1px solid var(--el-border-color-light);
  background: var(--el-bg-color);
  transition: all 0.3s ease;
}

.action-button:hover {
  border-color: #52c41a;
  background: #f6ffed;
}

.action-content {
  display: flex;
  align-items: center;
  gap: 12px;
  text-align: left;
  width: 100%;
}

.action-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 2px;
}

.action-desc {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .welcome-content {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
  
  .welcome-text h2 {
    font-size: 20px;
  }
  
  .stat-value {
    font-size: 18px;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .conversation-item {
    padding: 12px;
  }
  
  .action-button {
    padding: 12px;
  }
}
</style>