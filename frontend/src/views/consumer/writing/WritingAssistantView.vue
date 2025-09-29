<template>
  <div class="writing-assistant-view">
    <div class="flex h-full">
      <!-- Writing Tools Sidebar -->
      <div class="w-80 border-r border-gray-200 bg-gray-50">
        <div class="p-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold">Writing Tools</h3>
        </div>
        <div class="p-4 space-y-4">
          <el-card class="cursor-pointer hover:shadow-md transition-shadow" @click="selectTool('improve')">
            <div class="text-center">
              <el-icon class="text-2xl text-blue-500 mb-2"><Edit /></el-icon>
              <div class="font-medium">Improve Text</div>
              <div class="text-sm text-gray-500">Enhance clarity and style</div>
            </div>
          </el-card>
          
          <el-card class="cursor-pointer hover:shadow-md transition-shadow" @click="selectTool('summarize')">
            <div class="text-center">
              <el-icon class="text-2xl text-green-500 mb-2"><Document /></el-icon>
              <div class="font-medium">Summarize</div>
              <div class="text-sm text-gray-500">Create concise summaries</div>
            </div>
          </el-card>
          
          <el-card class="cursor-pointer hover:shadow-md transition-shadow" @click="selectTool('translate')">
            <div class="text-center">
              <el-icon class="text-2xl text-purple-500 mb-2"><Switch /></el-icon>
              <div class="font-medium">Translate</div>
              <div class="text-sm text-gray-500">Multi-language support</div>
            </div>
          </el-card>
          
          <el-card class="cursor-pointer hover:shadow-md transition-shadow" @click="selectTool('grammar')">
            <div class="text-center">
              <el-icon class="text-2xl text-orange-500 mb-2"><Check /></el-icon>
              <div class="font-medium">Grammar Check</div>
              <div class="text-sm text-gray-500">Fix grammar and spelling</div>
            </div>
          </el-card>
        </div>
      </div>

      <!-- Main Writing Area -->
      <div class="flex-1 flex flex-col">
        <!-- Header -->
        <div class="p-4 border-b border-gray-200 bg-white">
          <div class="flex justify-between items-center">
            <h2 class="text-lg font-semibold">{{ selectedToolTitle }}</h2>
            <div class="flex space-x-2">
              <el-button @click="clearText">Clear</el-button>
              <el-button type="primary" @click="processText" :loading="processing">
                Process Text
              </el-button>
            </div>
          </div>
        </div>

        <!-- Writing Interface -->
        <div class="flex-1 grid grid-cols-2 gap-4 p-4">
          <!-- Input Area -->
          <div class="flex flex-col">
            <div class="mb-2 font-medium">Input Text</div>
            <el-input
              v-model="inputText"
              type="textarea"
              :rows="20"
              placeholder="Enter your text here..."
              class="flex-1"
            />
            <div class="mt-2 text-sm text-gray-500">
              {{ inputText.length }} characters
            </div>
          </div>

          <!-- Output Area -->
          <div class="flex flex-col">
            <div class="mb-2 font-medium">Processed Text</div>
            <div class="flex-1 border border-gray-300 rounded-md p-3 bg-gray-50 overflow-y-auto">
              <div v-if="processing" class="flex items-center justify-center h-full">
                <el-icon class="animate-spin text-2xl"><Loading /></el-icon>
                <span class="ml-2">Processing...</span>
              </div>
              <div v-else-if="outputText" class="whitespace-pre-wrap">{{ outputText }}</div>
              <div v-else class="text-gray-500 italic">Processed text will appear here...</div>
            </div>
            <div class="mt-2 flex justify-between items-center">
              <div class="text-sm text-gray-500">
                {{ outputText.length }} characters
              </div>
              <el-button 
                v-if="outputText" 
                size="small" 
                @click="copyToClipboard"
                :icon="copySuccess ? 'Check' : 'CopyDocument'"
              >
                {{ copySuccess ? 'Copied!' : 'Copy' }}
              </el-button>
            </div>
          </div>
        </div>

        <!-- Additional Options -->
        <div v-if="selectedTool === 'translate'" class="p-4 border-t border-gray-200 bg-gray-50">
          <div class="flex items-center space-x-4">
            <span class="font-medium">Target Language:</span>
            <el-select v-model="targetLanguage" style="width: 200px">
              <el-option label="Chinese" value="zh" />
              <el-option label="English" value="en" />
              <el-option label="Spanish" value="es" />
              <el-option label="French" value="fr" />
              <el-option label="German" value="de" />
              <el-option label="Japanese" value="ja" />
              <el-option label="Korean" value="ko" />
            </el-select>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Edit, Document, Switch, Check, Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

type WritingTool = 'improve' | 'summarize' | 'translate' | 'grammar'

const selectedTool = ref<WritingTool>('improve')
const inputText = ref('')
const outputText = ref('')
const processing = ref(false)
const targetLanguage = ref('zh')
const copySuccess = ref(false)

const toolTitles = {
  improve: 'Text Improvement',
  summarize: 'Text Summarization',
  translate: 'Text Translation',
  grammar: 'Grammar Check'
}

const selectedToolTitle = computed(() => toolTitles[selectedTool.value])

const selectTool = (tool: WritingTool) => {
  selectedTool.value = tool
  outputText.value = ''
}

const clearText = () => {
  inputText.value = ''
  outputText.value = ''
}

const processText = async () => {
  if (!inputText.value.trim()) {
    ElMessage.warning('Please enter some text to process')
    return
  }

  processing.value = true
  outputText.value = ''

  try {
    // TODO: Implement actual API calls for each tool
    await new Promise(resolve => setTimeout(resolve, 2000)) // Simulate API call
    
    // Placeholder responses for each tool
    switch (selectedTool.value) {
      case 'improve':
        outputText.value = `[Improved version of the text would appear here]\n\n${inputText.value}`
        break
      case 'summarize':
        outputText.value = `[Summary]: This is a placeholder summary of the input text. The actual summarization will be implemented with AI integration.`
        break
      case 'translate':
        outputText.value = `[Translated to ${targetLanguage.value}]: This is a placeholder translation. The actual translation will be implemented with AI integration.`
        break
      case 'grammar':
        outputText.value = `[Grammar-checked version of the text would appear here]\n\n${inputText.value}`
        break
    }
  } catch (error) {
    ElMessage.error('Failed to process text')
  } finally {
    processing.value = false
  }
}

const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(outputText.value)
    copySuccess.value = true
    ElMessage.success('Text copied to clipboard')
    setTimeout(() => {
      copySuccess.value = false
    }, 2000)
  } catch (error) {
    ElMessage.error('Failed to copy text')
  }
}
</script>

<style scoped>
.writing-assistant-view {
  height: calc(100vh - 64px);
}
</style>