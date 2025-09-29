<template>
  <div class="document-viewer">
    <!-- Header -->
    <div class="viewer-header">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <el-icon class="text-2xl text-blue-500"><Document /></el-icon>
          <div>
            <h3 class="text-lg font-semibold text-gray-800">Document Viewer</h3>
            <p class="text-sm text-gray-600">Browse and search your knowledge base</p>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <el-input
            v-model="searchQuery"
            placeholder="Search documents..."
            size="small"
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button @click="refreshDocuments">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <div class="viewer-content">
      <!-- Sidebar - Document List -->
      <div class="documents-sidebar">
        <div class="sidebar-header">
          <h4 class="text-lg font-semibold">Documents</h4>
          <el-select v-model="sortBy" placeholder="Sort by" size="small">
            <el-option label="Name" value="name" />
            <el-option label="Date" value="date" />
            <el-option label="Size" value="size" />
            <el-option label="Type" value="type" />
          </el-select>
        </div>

        <div v-if="loading" class="loading-state">
          <el-skeleton :rows="5" animated />
        </div>

        <div v-else-if="filteredDocuments.length === 0" class="empty-state">
          <el-icon class="empty-icon"><FolderOpened /></el-icon>
          <p>No documents found</p>
        </div>

        <div v-else class="documents-list">
          <div
            v-for="document in filteredDocuments"
            :key="document.id"
            class="document-item"
            :class="{ 'active': selectedDocument?.id === document.id }"
            @click="selectDocument(document)"
          >
            <div class="document-icon">
              <el-icon :class="getIconClass(document.type)">
                <component :is="getIcon(document.type)" />
              </el-icon>
            </div>
            <div class="document-info">
              <h5 class="document-name">{{ document.name }}</h5>
              <div class="document-meta">
                <span class="document-size">{{ formatFileSize(document.size) }}</span>
                <span class="document-date">{{ formatDate(document.uploadedAt) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content Area -->
      <div class="document-content">
        <div v-if="!selectedDocument" class="no-selection">
          <el-icon class="no-selection-icon"><Document /></el-icon>
          <h3>Select a document to view</h3>
          <p>Choose a document from the sidebar to start reading</p>
        </div>

        <div v-else class="document-display">
          <!-- Document Header -->
          <div class="document-header">
            <div class="header-info">
              <h2 class="document-title">{{ selectedDocument.name }}</h2>
              <div class="document-metadata">
                <el-tag :type="getStatusType(selectedDocument.status)" size="small">
                  {{ selectedDocument.status }}
                </el-tag>
                <span class="metadata-item">
                  {{ formatFileSize(selectedDocument.size) }}
                </span>
                <span class="metadata-item">
                  Uploaded {{ formatDate(selectedDocument.uploadedAt) }}
                </span>
                <span class="metadata-item">
                  {{ selectedDocument.wordCount?.toLocaleString() }} words
                </span>
              </div>
            </div>
            <div class="header-actions">
              <el-button size="small" @click="downloadDocument">
                <el-icon><Download /></el-icon>
                Download
              </el-button>
              <el-button size="small" @click="openInChat">
                <el-icon><ChatDotRound /></el-icon>
                Ask About This
              </el-button>
            </div>
          </div>

          <!-- Content Tabs -->
          <el-tabs v-model="activeTab" type="border-card" class="content-tabs">
            <el-tab-pane label="Content" name="content">
              <div class="content-viewer">
                <div v-if="documentLoading" class="content-loading">
                  <el-loading></el-loading>
                </div>
                <div v-else-if="documentContent" class="content-text">
                  <div class="content-search" v-if="contentSearchQuery">
                    <el-input
                      v-model="contentSearchQuery"
                      placeholder="Search in document..."
                      size="small"
                      @input="highlightContent"
                    >
                      <template #prefix>
                        <el-icon><Search /></el-icon>
                      </template>
                    </el-input>
                  </div>
                  <div class="content-body" v-html="highlightedContent"></div>
                </div>
                <div v-else class="content-error">
                  <p>Failed to load document content</p>
                  <el-button @click="loadDocumentContent">Retry</el-button>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="Summary" name="summary">
              <div class="summary-content">
                <div v-if="selectedDocument.summary" class="summary-text">
                  <h4>Document Summary</h4>
                  <p>{{ selectedDocument.summary }}</p>
                </div>
                <div v-else class="no-summary">
                  <p>No summary available for this document</p>
                  <el-button @click="generateSummary" :loading="summaryLoading">
                    Generate Summary
                  </el-button>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="Metadata" name="metadata">
              <div class="metadata-content">
                <el-descriptions border :column="2">
                  <el-descriptions-item label="File Name">
                    {{ selectedDocument.name }}
                  </el-descriptions-item>
                  <el-descriptions-item label="File Type">
                    {{ selectedDocument.type.toUpperCase() }}
                  </el-descriptions-item>
                  <el-descriptions-item label="File Size">
                    {{ formatFileSize(selectedDocument.size) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="Status">
                    <el-tag :type="getStatusType(selectedDocument.status)">
                      {{ selectedDocument.status }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="Uploaded By">
                    {{ selectedDocument.uploadedBy }}
                  </el-descriptions-item>
                  <el-descriptions-item label="Upload Date">
                    {{ formatDateTime(selectedDocument.uploadedAt) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="Word Count" v-if="selectedDocument.wordCount">
                    {{ selectedDocument.wordCount.toLocaleString() }}
                  </el-descriptions-item>
                  <el-descriptions-item label="Processing Time" v-if="selectedDocument.processingTime">
                    {{ selectedDocument.processingTime }}ms
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Document,
  Search,
  Refresh,
  FolderOpened,
  Download,
  ChatDotRound
} from '@element-plus/icons-vue'
import { knowledgeApi } from '@/api'
import { useRouter } from 'vue-router'
import type { KnowledgeDocument } from '@/types/knowledge'

// Router
const router = useRouter()

// Reactive state
const loading = ref(false)
const documentLoading = ref(false)
const summaryLoading = ref(false)
const searchQuery = ref('')
const contentSearchQuery = ref('')
const sortBy = ref('name')
const activeTab = ref('content')
const documents = ref<KnowledgeDocument[]>([])
const selectedDocument = ref<KnowledgeDocument | null>(null)
const documentContent = ref('')

// Computed
const filteredDocuments = computed(() => {
  let filtered = documents.value

  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(doc =>
      doc.name.toLowerCase().includes(query) ||
      doc.uploadedBy.toLowerCase().includes(query)
    )
  }

  // Filter only processed documents
  filtered = filtered.filter(doc => doc.status === 'processed')

  // Sort documents
  return filtered.sort((a, b) => {
    switch (sortBy.value) {
      case 'name':
        return a.name.localeCompare(b.name)
      case 'date':
        return new Date(b.uploadedAt).getTime() - new Date(a.uploadedAt).getTime()
      case 'size':
        return b.size - a.size
      case 'type':
        return a.type.localeCompare(b.type)
      default:
        return 0
    }
  })
})

const highlightedContent = computed(() => {
  if (!documentContent.value || !contentSearchQuery.value) {
    return documentContent.value
  }

  const regex = new RegExp(`(${contentSearchQuery.value})`, 'gi')
  return documentContent.value.replace(regex, '<mark>$1</mark>')
})

// Lifecycle
onMounted(() => {
  loadDocuments()
})

// Methods
const loadDocuments = async () => {
  try {
    loading.value = true
    const response = await knowledgeApi.getDocuments()
    documents.value = response.data.documents || []
  } catch (error) {
    console.error('Failed to load documents:', error)
    ElMessage.error('Failed to load documents')
  } finally {
    loading.value = false
  }
}

const refreshDocuments = () => {
  loadDocuments()
  ElMessage.success('Documents refreshed')
}

const handleSearch = () => {
  // Search filtering is handled by computed property
}

const selectDocument = async (document: KnowledgeDocument) => {
  selectedDocument.value = document
  await loadDocumentContent()
}

const loadDocumentContent = async () => {
  if (!selectedDocument.value) return

  try {
    documentLoading.value = true
    const response = await knowledgeApi.getDocumentContent(selectedDocument.value.id)
    documentContent.value = response.data.content || ''
  } catch (error) {
    console.error('Failed to load document content:', error)
    ElMessage.error('Failed to load document content')
    documentContent.value = ''
  } finally {
    documentLoading.value = false
  }
}

const highlightContent = () => {
  // Highlighting is handled by computed property
}

const generateSummary = async () => {
  if (!selectedDocument.value) return

  try {
    summaryLoading.value = true
    const response = await knowledgeApi.generateSummary(selectedDocument.value.id)
    
    // Update the selected document with the new summary
    if (selectedDocument.value) {
      selectedDocument.value.summary = response.data.summary
    }
    
    ElMessage.success('Summary generated successfully')
  } catch (error) {
    console.error('Failed to generate summary:', error)
    ElMessage.error('Failed to generate summary')
  } finally {
    summaryLoading.value = false
  }
}

const downloadDocument = async () => {
  if (!selectedDocument.value) return

  try {
    const response = await knowledgeApi.downloadDocument(selectedDocument.value.id)
    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = selectedDocument.value.name
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('Document downloaded')
  } catch (error) {
    console.error('Failed to download document:', error)
    ElMessage.error('Failed to download document')
  }
}

const openInChat = () => {
  if (!selectedDocument.value) return
  
  // Navigate to chat with document context
  router.push({
    path: '/user/chat',
    query: {
      document: selectedDocument.value.id,
      message: `Tell me about the document "${selectedDocument.value.name}"`
    }
  })
}

// Utility functions
const getIcon = (type: string) => {
  return Document // Simplified - you could return different icons for different types
}

const getIconClass = (type: string) => {
  switch (type.toLowerCase()) {
    case 'pdf': return 'text-red-500'
    case 'doc':
    case 'docx': return 'text-blue-500'
    case 'txt':
    case 'md': return 'text-gray-500'
    default: return 'text-gray-500'
  }
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'processed': return 'success'
    case 'processing': return 'warning'
    case 'failed': return 'danger'
    default: return 'info'
  }
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString()
}

const formatDateTime = (dateString: string): string => {
  return new Date(dateString).toLocaleString()
}
</script>

<style scoped>
.document-viewer {
  @apply h-full flex flex-col bg-gray-50;
}

.viewer-header {
  @apply bg-white p-6 border-b border-gray-200;
}

.viewer-content {
  @apply flex-1 flex overflow-hidden;
}

.documents-sidebar {
  @apply w-80 bg-white border-r border-gray-200 flex flex-col;
}

.sidebar-header {
  @apply p-4 border-b border-gray-200 flex items-center justify-between;
}

.loading-state, .empty-state {
  @apply p-4;
}

.empty-state {
  @apply text-center text-gray-500;
}

.empty-icon {
  @apply text-4xl mb-2;
}

.documents-list {
  @apply flex-1 overflow-y-auto;
}

.document-item {
  @apply flex items-center space-x-3 p-4 hover:bg-gray-50 cursor-pointer border-b border-gray-100;
}

.document-item.active {
  @apply bg-blue-50 border-blue-200;
}

.document-icon {
  @apply text-xl flex-shrink-0;
}

.document-info {
  @apply flex-1 min-w-0;
}

.document-name {
  @apply font-medium text-gray-800 truncate;
}

.document-meta {
  @apply text-xs text-gray-500 space-x-2;
}

.document-content {
  @apply flex-1 flex flex-col;
}

.no-selection {
  @apply flex-1 flex flex-col items-center justify-center text-gray-500 space-y-4;
}

.no-selection-icon {
  @apply text-6xl;
}

.document-display {
  @apply flex-1 flex flex-col;
}

.document-header {
  @apply bg-white p-6 border-b border-gray-200 flex items-start justify-between;
}

.header-info {
  @apply flex-1;
}

.document-title {
  @apply text-xl font-semibold text-gray-800 mb-2;
}

.document-metadata {
  @apply flex items-center space-x-4 text-sm text-gray-600;
}

.metadata-item {
  @apply border-r border-gray-300 pr-4 last:border-r-0 last:pr-0;
}

.header-actions {
  @apply flex items-center space-x-2;
}

.content-tabs {
  @apply flex-1 flex flex-col;
}

.content-viewer {
  @apply h-full flex flex-col;
}

.content-loading {
  @apply flex-1 flex items-center justify-center;
}

.content-search {
  @apply mb-4;
}

.content-text {
  @apply flex-1 overflow-hidden;
}

.content-body {
  @apply h-full overflow-y-auto p-4 bg-white prose prose-sm max-w-none;
}

.content-error {
  @apply flex-1 flex flex-col items-center justify-center text-gray-500 space-y-4;
}

.summary-content, .metadata-content {
  @apply p-6;
}

.summary-text h4 {
  @apply text-lg font-semibold mb-3;
}

.no-summary {
  @apply text-center text-gray-500 space-y-4;
}

:deep(.el-tabs__content) {
  @apply flex-1 overflow-hidden;
}

:deep(.el-tab-pane) {
  @apply h-full;
}

:deep(mark) {
  @apply bg-yellow-200 text-yellow-900;
}
</style>