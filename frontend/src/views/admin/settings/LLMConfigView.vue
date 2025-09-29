<template>
  <div class="llm-config-view">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-900">LLM Configuration</h1>
      <el-button type="primary" @click="saveConfiguration">
        <el-icon><Check /></el-icon>
        Save Configuration
      </el-button>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- LLM Provider Settings -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-semibold mb-4">LLM Provider</h3>
        <el-form :model="config" label-width="120px">
          <el-form-item label="Provider">
            <el-select v-model="config.provider" placeholder="Select LLM Provider">
              <el-option label="OpenAI" value="openai" />
              <el-option label="Azure OpenAI" value="azure_openai" />
              <el-option label="Anthropic" value="anthropic" />
              <el-option label="Google Gemini" value="gemini" />
              <el-option label="Ollama" value="ollama" />
            </el-select>
          </el-form-item>
          <el-form-item label="Model">
            <el-input v-model="config.model" placeholder="e.g., gpt-4, claude-3" />
          </el-form-item>
          <el-form-item label="API Key">
            <el-input v-model="config.apiKey" type="password" placeholder="Enter API Key" />
          </el-form-item>
          <el-form-item label="Base URL">
            <el-input v-model="config.baseUrl" placeholder="API Base URL (optional)" />
          </el-form-item>
        </el-form>
      </div>

      <!-- Model Parameters -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-semibold mb-4">Model Parameters</h3>
        <el-form :model="config" label-width="120px">
          <el-form-item label="Temperature">
            <el-slider 
              v-model="config.temperature" 
              :min="0" 
              :max="2" 
              :step="0.1" 
              show-input 
            />
          </el-form-item>
          <el-form-item label="Max Tokens">
            <el-input-number 
              v-model="config.maxTokens" 
              :min="1" 
              :max="32000" 
              :step="100"
            />
          </el-form-item>
          <el-form-item label="Top P">
            <el-slider 
              v-model="config.topP" 
              :min="0" 
              :max="1" 
              :step="0.01" 
              show-input 
            />
          </el-form-item>
          <el-form-item label="Frequency Penalty">
            <el-slider 
              v-model="config.frequencyPenalty" 
              :min="0" 
              :max="2" 
              :step="0.1" 
              show-input 
            />
          </el-form-item>
        </el-form>
      </div>

      <!-- Embedding Configuration -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-semibold mb-4">Embedding Configuration</h3>
        <el-form :model="config.embedding" label-width="120px">
          <el-form-item label="Provider">
            <el-select v-model="config.embedding.provider" placeholder="Select Embedding Provider">
              <el-option label="OpenAI" value="openai" />
              <el-option label="Azure OpenAI" value="azure_openai" />
              <el-option label="Ollama" value="ollama" />
            </el-select>
          </el-form-item>
          <el-form-item label="Model">
            <el-input v-model="config.embedding.model" placeholder="e.g., text-embedding-ada-002" />
          </el-form-item>
        </el-form>
      </div>

      <!-- System Settings -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-semibold mb-4">System Settings</h3>
        <el-form :model="config" label-width="120px">
          <el-form-item label="Enable Logging">
            <el-switch v-model="config.enableLogging" />
          </el-form-item>
          <el-form-item label="Rate Limiting">
            <el-switch v-model="config.enableRateLimit" />
          </el-form-item>
          <el-form-item label="Requests/Min">
            <el-input-number 
              v-model="config.requestsPerMinute" 
              :min="1" 
              :max="1000" 
              :disabled="!config.enableRateLimit"
            />
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Check } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const config = ref({
  provider: 'openai',
  model: 'gpt-4',
  apiKey: '',
  baseUrl: '',
  temperature: 0.7,
  maxTokens: 2000,
  topP: 1.0,
  frequencyPenalty: 0.0,
  embedding: {
    provider: 'openai',
    model: 'text-embedding-ada-002'
  },
  enableLogging: true,
  enableRateLimit: false,
  requestsPerMinute: 60
})

const saveConfiguration = async () => {
  try {
    // TODO: Implement save configuration API call
    console.log('Saving configuration:', config.value)
    ElMessage.success('Configuration saved successfully')
  } catch (error) {
    ElMessage.error('Failed to save configuration')
  }
}

onMounted(() => {
  // TODO: Load current configuration from API
  console.log('Loading LLM configuration...')
})
</script>

<style scoped>
.llm-config-view {
  padding: 24px;
}
</style>