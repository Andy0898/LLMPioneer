<template>
  <div class="not-found">
    <div class="not-found-container">
      <div class="error-illustration">
        <el-icon size="120" color="var(--el-color-info)">
          <Search />
        </el-icon>
      </div>
      
      <div class="error-content">
        <h1 class="error-title">404</h1>
        <h2 class="error-subtitle">Page Not Found</h2>
        <p class="error-message">
          The page you're looking for doesn't exist or has been moved.
        </p>
        
        <div class="error-actions">
          <el-button type="primary" size="large" @click="goHome">
            <el-icon><House /></el-icon>
            Go Home
          </el-button>
          <el-button size="large" @click="goBack">
            <el-icon><Back /></el-icon>
            Go Back
          </el-button>
        </div>
        
        <div class="help-links">
          <p>You might be looking for:</p>
          <div class="link-grid">
            <el-link @click="$router.push('/user/dashboard')">
              <el-icon><House /></el-icon>
              Dashboard
            </el-link>
            <el-link @click="$router.push('/user/chat')">
              <el-icon><ChatDotRound /></el-icon>
              AI Chat
            </el-link>
            <el-link @click="$router.push('/user/writing')">
              <el-icon><EditPen /></el-icon>
              Writing Assistant
            </el-link>
            <el-link @click="$router.push('/user/knowledge')">
              <el-icon><Document /></el-icon>
              Knowledge Base
            </el-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { 
  Search, 
  House, 
  Back, 
  ChatDotRound, 
  EditPen, 
  Document 
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const goHome = () => {
  const portal = authStore.portal
  if (portal === 'admin') {
    router.push('/admin/dashboard')
  } else {
    router.push('/user/dashboard')
  }
}

const goBack = () => {
  router.go(-1)
}
</script>

<style scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--el-bg-color-page);
  padding: 20px;
}

.not-found-container {
  text-align: center;
  max-width: 500px;
  width: 100%;
}

.error-illustration {
  margin-bottom: 32px;
  opacity: 0.8;
}

.error-content {
  background: white;
  border-radius: 12px;
  padding: 40px 32px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.error-title {
  font-size: 72px;
  font-weight: 700;
  color: var(--el-color-info);
  margin: 0 0 16px 0;
  line-height: 1;
}

.error-subtitle {
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 0 0 16px 0;
}

.error-message {
  font-size: 16px;
  color: var(--el-text-color-secondary);
  margin: 0 0 32px 0;
  line-height: 1.5;
}

.error-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-bottom: 32px;
  flex-wrap: wrap;
}

.help-links {
  border-top: 1px solid var(--el-border-color-light);
  padding-top: 32px;
}

.help-links p {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin: 0 0 16px 0;
}

.link-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
}

.link-grid .el-link {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.link-grid .el-link:hover {
  background: var(--el-fill-color-light);
}

@media (max-width: 768px) {
  .error-content {
    padding: 32px 24px;
  }
  
  .error-title {
    font-size: 60px;
  }
  
  .error-subtitle {
    font-size: 20px;
  }
  
  .error-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .error-actions .el-button {
    width: 100%;
    max-width: 200px;
  }
  
  .link-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .not-found {
    padding: 16px;
  }
  
  .error-content {
    padding: 24px 20px;
  }
  
  .error-title {
    font-size: 48px;
  }
  
  .error-subtitle {
    font-size: 18px;
  }
  
  .link-grid {
    grid-template-columns: 1fr;
  }
}

/* Animation */
.not-found-container {
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.error-illustration {
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}
</style>