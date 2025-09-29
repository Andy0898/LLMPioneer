<template>
  <div style="min-height: 100vh; background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); display: flex; align-items: center; justify-content: center; padding: 20px;">
    <div style="background: white; border-radius: 12px; padding: 40px; box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1); max-width: 400px; width: 100%;">
      <h1 style="text-align: center; color: #52c41a; margin-bottom: 20px;">🎉 User Login</h1>
      <p style="text-align: center; margin-bottom: 30px;">This is a simple login page for testing routing.</p>
      
      <form @submit.prevent="handleSubmit" style="display: flex; flex-direction: column; gap: 15px;">
        <input 
          v-model="username" 
          type="text" 
          placeholder="Username" 
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
          style="padding: 12px; background: #52c41a; color: white; border: none; border-radius: 6px; font-size: 16px; cursor: pointer;"
        >
          Sign In
        </button>
      </form>
      
      <div style="text-align: center; margin-top: 20px;">
        <a href="/admin/login" style="color: #1890ff; text-decoration: none;">Go to Admin Login</a>
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
  alert(`Login attempt with username: ${username.value}`)
}
</script>