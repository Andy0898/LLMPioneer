<template>
  <div style="min-height: 100vh; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; padding: 20px;">
    <div style="background: white; border-radius: 12px; padding: 40px; box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1); max-width: 400px; width: 100%;">
      <h1 style="text-align: center; color: #1890ff; margin-bottom: 20px;">🔧 Admin Login</h1>
      <p style="text-align: center; margin-bottom: 30px;">Administrator portal access</p>
      
      <form @submit.prevent="handleSubmit" style="display: flex; flex-direction: column; gap: 15px;">
        <input 
          v-model="username" 
          type="text" 
          placeholder="Admin Username" 
          style="padding: 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px;"
        />
        <input 
          v-model="password" 
          type="password" 
          placeholder="Password" 
          style="padding: 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px;"
        />
        <button 
          type="submit" 
          style="padding: 12px; background: #1890ff; color: white; border: none; border-radius: 6px; font-size: 16px; cursor: pointer;"
        >
          Admin Sign In
        </button>
      </form>
      
      <div style="text-align: center; margin-top: 20px;">
        <a href="/user/login" style="color: #52c41a; text-decoration: none;">Go to User Login</a>
      </div>
      
      <div style="text-align: center; margin-top: 10px;">
        <a href="/" style="color: #666; text-decoration: none; font-size: 14px;">← Back to Home</a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const username = ref('')
const password = ref('')

const handleSubmit = () => {
  alert(`Admin login attempt with username: ${username.value}`)
}
</script>