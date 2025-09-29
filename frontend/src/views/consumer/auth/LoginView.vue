<template>
<template>
  <div class="consumer-login">
    <div class="login-container">
      <div class="login-card">
        <div class="login-header">
          <div class="logo">
            <el-icon size="48" color="#52c41a">
              <ChatDotRound />
            </el-icon>
          </div>
          <h1 class="login-title">Welcome Back</h1>
          <p class="login-subtitle">Sign in to continue to LLM Pioneer</p>
        </div>
        
        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          @submit.prevent="handleLogin"
          size="large"
          label-position="top"
        >
          <el-form-item label="Username" prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="Enter your username"
              prefix-icon="User"
              :disabled="loading"
            />
          </el-form-item>
          
          <el-form-item label="Password" prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="Enter your password"
              prefix-icon="Lock"
              :disabled="loading"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          
          <el-form-item>
            <div class="form-row">
              <el-checkbox v-model="loginForm.rememberMe" :disabled="loading">
                Remember me
              </el-checkbox>
              <el-link type="primary" :underline="false">
                Forgot password?
              </el-link>
            </div>
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              native-type="submit"
              :loading="loading"
              style="width: 100%"
              size="large"
            >
              Sign In
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="login-footer">
          <p>Don't have an account? <el-link type="primary">Sign up</el-link></p>
          <el-divider>OR</el-divider>
          <el-link type="info" @click="$router.push('/admin/login')">
            Admin Portal Login
          </el-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, type FormInstance } from 'element-plus'
import { ChatDotRound } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const loginFormRef = ref<FormInstance>()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
  rememberMe: false
})

const loginRules = {
  username: [
    { required: true, message: 'Please enter your username', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Please enter your password', trigger: 'blur' },
    { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    await loginFormRef.value.validate()
    loading.value = true
    
    await authStore.login({
      username: loginForm.username,
      password: loginForm.password,
      portal: 'consumer'
    })
    
    // Login successful, router will redirect automatically
  } catch (error: any) {
    console.error('Login failed:', error)
    ElMessage.error(error.message || 'Login failed')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.consumer-login {
  min-height: 100vh;
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-container {
  width: 100%;
  max-width: 400px;
}

.login-card {
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  margin-bottom: 16px;
}

.login-title {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #52c41a;
}

.login-subtitle {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.form-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.login-footer {
  text-align: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--el-border-color-light);
}

.login-footer p {
  margin: 0 0 16px 0;
  color: var(--el-text-color-regular);
}

@media (max-width: 480px) {
  .login-card {
    padding: 24px;
  }
  
  .login-title {
    font-size: 20px;
  }
  
  .form-row {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
}
</style>