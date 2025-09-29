<template>
  <div class="writing-assistant">
    <!-- Header -->
    <div class="assistant-header">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <el-icon class="text-2xl text-blue-500"><EditPen /></el-icon>
          <div>
            <h3 class="text-lg font-semibold text-gray-800">Writing Assistant</h3>
            <p class="text-sm text-gray-600">AI-powered writing help and suggestions</p>
          </div>
        </div>
        <el-button @click="clearContent" :disabled="!content.trim()">
          <el-icon><Delete /></el-icon>
          Clear
        </el-button>
      </div>
    </div>

    <!-- Writing Tools -->
    <div class="writing-tools">
      <div class="tools-grid">
        <el-button
          v-for="tool in writingTools"
          :key="tool.key"
          @click="useTool(tool.key)"
          :loading="loading && activeTool === tool.key"
          :disabled="!content.trim() && tool.requiresContent"
          class="tool-button"
        >
          <el-icon><component :is="tool.icon" /></el-icon>
          {{ tool.name }}
        </el-button>
      </div>
    </div>

    <!-- Content Editor -->
    <div class="content-editor">
      <el-input
        v-model="content"
        type="textarea"
        :rows="12"
        placeholder="Start writing here, or paste your text to get AI assistance..."
        resize="vertical"
        @input="handleContentChange"
        class="editor-textarea"
      />
      
      <div class="editor-stats">
        <div class="stats-left">
          <span class="stat-item">{{ wordCount }} words</span>
          <span class="stat-item">{{ charCount }} characters</span>
          <span class="stat-item">{{ readingTime }} min read</span>
        </div>
        <div class="stats-right">
          <el-button size="small" @click="copyContent" :disabled="!content.trim()">
            <el-icon><CopyDocument /></el-icon>
            Copy
          </el-button>
        </div>
      </div>
    </div>

    <!-- Suggestions Panel -->
    <div v-if="suggestions.length > 0" class="suggestions-panel">
      <h4 class="suggestions-title">AI Suggestions</h4>
      <div class="suggestions-list">
        <div
          v-for="suggestion in suggestions"
          :key="suggestion.id"
          class="suggestion-item"
        >
          <div class="suggestion-header">
            <span class="suggestion-type">{{ suggestion.type }}</span>
            <el-button
              size="small"
              type="primary"
              text
              @click="applySuggestion(suggestion)"
            >
              Apply
            </el-button>
          </div>
          <p class="suggestion-text">{{ suggestion.text }}</p>
          <div v-if="suggestion.original" class="suggestion-diff">
            <div class="diff-original">
              <span class="diff-label">Original:</span>
              <span>{{ suggestion.original }}</span>
            </div>
            <div class="diff-suggested">
              <span class="diff-label">Suggested:</span>
              <span>{{ suggestion.suggested }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Templates -->
    <div class="templates-section">
      <h4 class="section-title">Writing Templates</h4>
      <div class="templates-grid">
        <div
          v-for="template in templates"
          :key="template.id"
          class="template-card"
          @click="useTemplate(template)"
        >
          <div class="template-icon">
            <el-icon><component :is="template.icon" /></el-icon>
          </div>
          <h5 class="template-title">{{ template.name }}</h5>
          <p class="template-description">{{ template.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  EditPen,
  Delete,
  CopyDocument,
  Check,
  Refresh,
  Star,
  Document,
  ChatDotRound,
  Search,
  Edit,
  List
} from '@element-plus/icons-vue'
import { writingApi } from '@/api'

// Reactive state
const content = ref('')
const loading = ref(false)
const activeTool = ref<string | null>(null)
const suggestions = ref<any[]>([])

// Writing tools configuration
const writingTools = [
  {
    key: 'improve',
    name: 'Improve',
    icon: Star,
    requiresContent: true
  },
  {
    key: 'grammar',
    name: 'Grammar',
    icon: Check,
    requiresContent: true
  },
  {
    key: 'tone',
    name: 'Tone',
    icon: Edit,
    requiresContent: true
  },
  {
    key: 'summarize',
    name: 'Summarize',
    icon: List,
    requiresContent: true
  },
  {
    key: 'expand',
    name: 'Expand',
    icon: ChatDotRound,
    requiresContent: true
  },
  {
    key: 'translate',
    name: 'Translate',
    icon: Search,
    requiresContent: true
  }
]

// Templates
const templates = [
  {
    id: 'email',
    name: 'Email',
    description: 'Professional email template',
    icon: Document,
    content: `Subject: [Your Subject]

Dear [Recipient],

[Opening greeting and context]

[Main content/request]

[Closing and next steps]

Best regards,
[Your name]`
  },
  {
    id: 'report',
    name: 'Report',
    description: 'Business report structure',
    icon: Document,
    content: `# [Report Title]

## Executive Summary
[Brief overview of key findings]

## Introduction
[Background and purpose]

## Methodology
[How the analysis was conducted]

## Findings
[Key results and insights]

## Recommendations
[Suggested actions]

## Conclusion
[Summary and next steps]`
  },
  {
    id: 'proposal',
    name: 'Proposal',
    description: 'Project proposal template',
    icon: Document,
    content: `# [Proposal Title]

## Problem Statement
[Define the problem you're solving]

## Proposed Solution
[Your recommended approach]

## Benefits
[Expected outcomes and value]

## Timeline
[Project phases and milestones]

## Budget
[Cost breakdown]

## Next Steps
[How to proceed]`
  }
]

// Computed
const wordCount = computed(() => {
  return content.value.trim().split(/\s+/).filter(word => word.length > 0).length
})

const charCount = computed(() => {
  return content.value.length
})

const readingTime = computed(() => {
  // Average reading speed: 200 words per minute
  const wordsPerMinute = 200
  return Math.max(1, Math.ceil(wordCount.value / wordsPerMinute))
})

// Watch for content changes to get suggestions
watch(content, async (newContent) => {
  if (newContent.trim().length > 50) {
    await getSuggestions()
  } else {
    suggestions.value = []
  }
}, { debounce: 1000 })

// Methods
const handleContentChange = () => {
  // Real-time content analysis could be added here
}

const useTool = async (toolKey: string) => {
  if (!content.value.trim()) {
    ElMessage.warning('Please enter some text first')
    return
  }

  try {
    loading.value = true
    activeTool.value = toolKey
    
    const response = await writingApi.useTool(toolKey, content.value)
    
    switch (toolKey) {
      case 'improve':
      case 'grammar':
      case 'tone':
        content.value = response.data.result
        ElMessage.success('Text improved')
        break
      case 'summarize':
        suggestions.value = [{
          id: Date.now(),
          type: 'Summary',
          text: response.data.result,
          action: 'replace'
        }]
        break
      case 'expand':
        suggestions.value = [{
          id: Date.now(),
          type: 'Expansion',
          text: response.data.result,
          action: 'append'
        }]
        break
      case 'translate':
        suggestions.value = [{
          id: Date.now(),
          type: 'Translation',
          text: response.data.result,
          action: 'replace'
        }]
        break
    }
  } catch (error) {
    console.error('Failed to use tool:', error)
    ElMessage.error('Failed to process text')
  } finally {
    loading.value = false
    activeTool.value = null
  }
}

const getSuggestions = async () => {
  try {
    const response = await writingApi.getSuggestions(content.value)
    suggestions.value = response.data.suggestions
  } catch (error) {
    console.error('Failed to get suggestions:', error)
  }
}

const applySuggestion = (suggestion: any) => {
  switch (suggestion.action) {
    case 'replace':
      content.value = suggestion.text
      break
    case 'append':
      content.value += '\n\n' + suggestion.text
      break
    case 'insert':
      // Handle insertion at specific position
      content.value = suggestion.text
      break
  }
  
  // Remove applied suggestion
  const index = suggestions.value.findIndex(s => s.id === suggestion.id)
  if (index > -1) {
    suggestions.value.splice(index, 1)
  }
  
  ElMessage.success('Suggestion applied')
}

const useTemplate = (template: any) => {
  if (content.value.trim()) {
    ElMessage.confirm(
      'This will replace your current content. Continue?',
      'Use Template',
      {
        confirmButtonText: 'Replace',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
    ).then(() => {
      content.value = template.content
      ElMessage.success('Template applied')
    }).catch(() => {
      // User cancelled
    })
  } else {
    content.value = template.content
    ElMessage.success('Template applied')
  }
}

const clearContent = () => {
  content.value = ''
  suggestions.value = []
  ElMessage.success('Content cleared')
}

const copyContent = async () => {
  try {
    await navigator.clipboard.writeText(content.value)
    ElMessage.success('Content copied to clipboard')
  } catch (error) {
    ElMessage.error('Failed to copy content')
  }
}
</script>

<style scoped>
.writing-assistant {
  @apply p-6 space-y-6 bg-gray-50 min-h-screen;
}

.assistant-header {
  @apply bg-white rounded-lg p-6 shadow-sm;
}

.writing-tools {
  @apply bg-white rounded-lg p-6 shadow-sm;
}

.tools-grid {
  @apply grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3;
}

.tool-button {
  @apply flex flex-col items-center space-y-2 p-4 h-auto;
}

.content-editor {
  @apply bg-white rounded-lg shadow-sm overflow-hidden;
}

.editor-textarea {
  @apply border-0;
}

.editor-stats {
  @apply flex items-center justify-between p-4 bg-gray-50 border-t border-gray-200;
}

.stats-left {
  @apply flex items-center space-x-4 text-sm text-gray-600;
}

.stat-item {
  @apply border-r border-gray-300 pr-4 last:border-r-0 last:pr-0;
}

.stats-right {
  @apply flex items-center space-x-2;
}

.suggestions-panel {
  @apply bg-white rounded-lg p-6 shadow-sm;
}

.suggestions-title {
  @apply text-lg font-semibold text-gray-800 mb-4;
}

.suggestions-list {
  @apply space-y-4;
}

.suggestion-item {
  @apply border border-gray-200 rounded-lg p-4;
}

.suggestion-header {
  @apply flex items-center justify-between mb-2;
}

.suggestion-type {
  @apply bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm font-medium;
}

.suggestion-text {
  @apply text-gray-700 mb-3;
}

.suggestion-diff {
  @apply space-y-1 text-sm;
}

.diff-original,
.diff-suggested {
  @apply flex items-start space-x-2;
}

.diff-label {
  @apply font-medium text-gray-600 min-w-0 flex-shrink-0;
}

.diff-original {
  @apply text-red-600;
}

.diff-suggested {
  @apply text-green-600;
}

.templates-section {
  @apply bg-white rounded-lg p-6 shadow-sm;
}

.section-title {
  @apply text-lg font-semibold text-gray-800 mb-4;
}

.templates-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4;
}

.template-card {
  @apply border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-md transition-all cursor-pointer;
}

.template-icon {
  @apply text-blue-500 text-2xl mb-3;
}

.template-title {
  @apply font-semibold text-gray-800 mb-2;
}

.template-description {
  @apply text-sm text-gray-600;
}

:deep(.el-textarea__inner) {
  @apply border-0 focus:border-0 focus:ring-0 resize-none;
}
</style>