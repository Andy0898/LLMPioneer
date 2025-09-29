<template>
  <div class="admin-dashboard">
    <div class="dashboard-content">
      <!-- Stats Cards -->
      <div class="stats-grid">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="24" color="#1890ff">
                <User />
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">1,234</div>
              <div class="stat-label">Total Users</div>
            </div>
          </div>
        </el-card>
        
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="24" color="#52c41a">
                <ChatDotRound />
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">5,678</div>
              <div class="stat-label">Conversations</div>
            </div>
          </div>
        </el-card>
        
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="24" color="#faad14">
                <Document />
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">891</div>
              <div class="stat-label">Documents</div>
            </div>
          </div>
        </el-card>
        
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="24" color="#722ed1">
                <TrendCharts />
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">98.5%</div>
              <div class="stat-label">Uptime</div>
            </div>
          </div>
        </el-card>
      </div>
      
      <!-- Charts and Recent Activity -->
      <div class="dashboard-grid">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Usage Analytics</span>
              <el-button text>View Details</el-button>
            </div>
          </template>
          <div class="chart-placeholder">
            <p>Usage charts will be implemented here</p>
          </div>
        </el-card>
        
        <el-card class="activity-card">
          <template #header>
            <div class="card-header">
              <span>Recent Activity</span>
              <el-button text>View All</el-button>
            </div>
          </template>
          <div class="activity-list">
            <div v-for="activity in recentActivities" :key="activity.id" class="activity-item">
              <div class="activity-icon">
                <el-icon :color="activity.color">
                  <component :is="activity.icon" />
                </el-icon>
              </div>
              <div class="activity-content">
                <div class="activity-text">{{ activity.text }}</div>
                <div class="activity-time">{{ activity.time }}</div>
              </div>
            </div>
          </div>
        </el-card>
      </div>
      
      <!-- Quick Actions -->
      <el-card class="quick-actions-card">
        <template #header>
          <span>Quick Actions</span>
        </template>
        <div class="quick-actions">
          <el-button type="primary" @click="$router.push('/admin/users')">
            <el-icon><User /></el-icon>
            Manage Users
          </el-button>
          <el-button type="success" @click="$router.push('/admin/knowledge')">
            <el-icon><Document /></el-icon>
            Knowledge Base
          </el-button>
          <el-button type="warning" @click="$router.push('/admin/settings/llm')">
            <el-icon><Setting /></el-icon>
            LLM Config
          </el-button>
          <el-button type="info">
            <el-icon><Download /></el-icon>
            Export Data
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { 
  User, 
  ChatDotRound, 
  Document, 
  TrendCharts, 
  Setting, 
  Download,
  Plus,
  Edit,
  Delete
} from '@element-plus/icons-vue'

const recentActivities = ref([
  {
    id: 1,
    icon: User,
    color: '#1890ff',
    text: 'New user registered: john.doe@example.com',
    time: '2 minutes ago'
  },
  {
    id: 2,
    icon: Document,
    color: '#52c41a',
    text: 'Document uploaded: Project Requirements.pdf',
    time: '5 minutes ago'
  },
  {
    id: 3,
    icon: ChatDotRound,
    color: '#faad14',
    text: 'High conversation volume detected',
    time: '10 minutes ago'
  },
  {
    id: 4,
    icon: Setting,
    color: '#722ed1',
    text: 'LLM configuration updated',
    time: '15 minutes ago'
  }
])
</script>

<style scoped>
.admin-dashboard {
  padding: 0;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.stat-card {
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background: var(--el-fill-color-light);
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

.chart-card,
.activity-card {
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-placeholder {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--el-fill-color-extra-light);
  border-radius: 8px;
  color: var(--el-text-color-secondary);
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.activity-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--el-fill-color-light);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
}

.activity-text {
  font-size: 14px;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}

.activity-time {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.quick-actions-card {
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.quick-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

@media (max-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
  }
  
  .quick-actions {
    flex-direction: column;
  }
  
  .quick-actions .el-button {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>