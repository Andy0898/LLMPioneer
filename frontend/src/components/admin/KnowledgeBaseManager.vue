<template>
  <div class="knowledge-base-manager">
    <!-- Header Section -->
    <div class="manager-header">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-2xl font-bold text-gray-800 mb-2">Knowledge Base Manager</h2>
          <p class="text-gray-600">Upload, organize, and manage your knowledge base documents</p>
        </div>
        <div class="flex items-center space-x-4">
          <el-button type="success" @click="showUploadDialog = true">
            <el-icon><Upload /></el-icon>
            Upload Documents
          </el-button>
          <el-button type="primary" @click="refreshDocuments">
            <el-icon><Refresh /></el-icon>
            Refresh
          </el-button>
        </div>
      </div>
    </div>

    <!-- Stats Overview -->
    <div class="stats-overview mb-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="stat-card">
          <div class="stat-icon bg-blue-500">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-content">
            <h3 class="stat-label">Total Documents</h3>
            <p class="stat-value">{{ documentStats.total }}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon bg-green-500">
            <el-icon><Check /></el-icon>
          </div>
          <div class="stat-content">
            <h3 class="stat-label">Processed</h3>
            <p class="stat-value">{{ documentStats.processed }}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon bg-yellow-500">
            <el-icon><Loading /></el-icon>
          </div>
          <div class="stat-content">
            <h3 class="stat-label">Processing</h3>
            <p class="stat-value">{{ documentStats.processing }}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon bg-red-500">
            <el-icon><Close /></el-icon>
          </div>
          <div class="stat-content">
            <h3 class="stat-label">Failed</h3>
            <p class="stat-value">{{ documentStats.failed }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="filters-section mb-6">
      <el-card>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <el-input
            v-model="filters.search"
            placeholder="Search documents..."
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          
          <el-select v-model="filters.status" placeholder="Filter by status" clearable>
            <el-option label="All Status" value="" />
            <el-option label="Uploaded" value="uploaded" />
            <el-option label="Processing" value="processing" />
            <el-option label="Processed" value="processed" />
            <el-option label="Failed" value="failed" />
          </el-select>
          
          <el-select v-model="filters.type" placeholder="Filter by type" clearable>
            <el-option label="All Types" value="" />
            <el-option label="PDF" value="pdf" />
            <el-option label="Word" value="docx" />
            <el-option label="Text" value="txt" />
            <el-option label="Markdown" value="md" />
          </el-select>
          
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            range-separator="To"
            start-placeholder="Start date"
            end-placeholder="End date"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="handleDateRangeChange"
          />
        </div>
      </el-card>
    </div>

    <!-- Documents Table -->
    <div class="documents-table">
      <el-card>
        <template #header>
          <div class="flex items-center justify-between">
            <span class="text-lg font-semibold">Documents</span>
            <div class="flex items-center space-x-2">
              <el-button
                size="small"
                :disabled="selectedDocuments.length === 0"
                @click="handleBulkDelete"
              >
                Delete Selected ({{ selectedDocuments.length }})
              </el-button>
              <el-button
                size="small"
                :disabled="selectedDocuments.length === 0"
                @click="handleBulkReprocess"
              >
                Reprocess Selected
              </el-button>
            </div>
          </div>
        </template>

        <el-table
          v-loading="loading"
          :data="filteredDocuments"
          @selection-change="handleSelectionChange"
          row-key="id"
          style="width: 100%"
        >
          <el-table-column type="selection" width="55" />
          
          <el-table-column prop="name" label="Document Name" min-width="200">
            <template #default="scope">
              <div class="flex items-center space-x-2">
                <el-icon :class="getFileIconClass(scope.row.type)">
                  <component :is="getFileIcon(scope.row.type)" />
                </el-icon>
                <span class="font-medium">{{ scope.row.name }}</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="type" label="Type" width="80">
            <template #default="scope">
              <el-tag size="small">{{ scope.row.type.toUpperCase() }}</el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="size" label="Size" width="100">
            <template #default="scope">
              {{ formatFileSize(scope.row.size) }}
            </template>
          </el-table-column>
          
          <el-table-column prop="status" label="Status" width="120">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)" size="small">
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="progress" label="Progress" width="150">
            <template #default="scope">
              <div v-if="scope.row.status === 'processing'">
                <el-progress 
                  :percentage="scope.row.progress || 0" 
                  :stroke-width="6"
                  :show-text="false"
                />
                <span class="text-xs text-gray-500 ml-2">{{ scope.row.progress || 0 }}%</span>
              </div>
              <span v-else-if="scope.row.status === 'processed'" class="text-green-600 text-sm">
                Complete
              </span>
              <span v-else-if="scope.row.status === 'failed'" class="text-red-600 text-sm">
                Failed
              </span>
              <span v-else class="text-gray-500 text-sm">-</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="uploadedAt" label="Uploaded" width="120">
            <template #default="scope">
              {{ formatDate(scope.row.uploadedAt) }}
            </template>
          </el-table-column>
          
          <el-table-column prop="uploadedBy" label="Uploaded By" width="120" />
          
          <el-table-column label="Actions" width="200" fixed="right">
            <template #default="scope">
              <div class="flex items-center space-x-2">
                <el-button
                  type="primary"
                  size="small"
                  @click="viewDocument(scope.row)"
                  :disabled="scope.row.status !== 'processed'"
                >
                  View
                </el-button>
                <el-button
                  type="warning"
                  size="small"
                  @click="reprocessDocument(scope.row)"
                  :disabled="scope.row.status === 'processing'"
                >
                  Reprocess
                </el-button>
                <el-button
                  type="danger"
                  size="small"
                  @click="deleteDocument(scope.row)"
                >
                  Delete
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <!-- Pagination -->
        <div class="flex justify-center mt-6">
          <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>

    <!-- Upload Dialog -->
    <el-dialog
      v-model="showUploadDialog"
      title="Upload Documents"
      width="60%"
      :before-close="handleCloseUploadDialog"
    >
      <div class="upload-section">
        <el-upload
          ref="uploadRef"
          class="upload-demo"
          drag
          :action="uploadUrl"
          :headers="uploadHeaders"
          :data="uploadData"
          :file-list="uploadFileList"
          :before-upload="beforeUpload"
          :on-success="handleUploadSuccess"
          :on-error="handleUploadError"
          :on-remove="handleRemoveFile"
          :on-exceed="handleExceed"
          :limit="5"
          multiple
          accept=".pdf,.doc,.docx,.txt,.md"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            Drop files here or <em>click to upload</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              Supported formats: PDF, DOC, DOCX, TXT, MD (max 50MB per file)
            </div>
          </template>
        </el-upload>

        <!-- Upload Options -->
        <div class="upload-options mt-6">
          <h4 class="text-lg font-semibold mb-4">Processing Options</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <el-checkbox v-model="uploadOptions.extractImages">
                Extract images from documents
              </el-checkbox>
            </div>
            <div>
              <el-checkbox v-model="uploadOptions.enableOCR">
                Enable OCR for scanned documents
              </el-checkbox>
            </div>
            <div>
              <el-checkbox v-model="uploadOptions.splitByChapters">
                Split by chapters/sections
              </el-checkbox>
            </div>
            <div>
              <el-checkbox v-model="uploadOptions.generateSummary">
                Generate document summary
              </el-checkbox>
            </div>
          </div>
          
          <div class="mt-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Processing Priority
            </label>
            <el-radio-group v-model="uploadOptions.priority">
              <el-radio label="low">Low</el-radio>
              <el-radio label="normal">Normal</el-radio>
              <el-radio label="high">High</el-radio>
            </el-radio-group>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end space-x-2">
          <el-button @click="showUploadDialog = false">Cancel</el-button>
          <el-button 
            type="primary" 
            @click="startUpload"
            :disabled="uploadFileList.length === 0"
          >
            Start Upload
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Upload,
  Refresh,
  Document,
  Check,
  Loading,
  Close,
  Search,
  UploadFilled
} from '@element-plus/icons-vue'
import { knowledgeApi } from '@/api'
import { useAuthStore } from '@/stores/auth'
import type { KnowledgeDocument } from '@/types/knowledge'

// Store
const authStore = useAuthStore()

// Reactive state
const loading = ref(false)
const documents = ref<KnowledgeDocument[]>([])
const selectedDocuments = ref<KnowledgeDocument[]>([])
const showUploadDialog = ref(false)

// Upload
const uploadRef = ref()
const uploadFileList = ref([])
const uploadUrl = computed(() => `${import.meta.env.VITE_API_BASE_URL}/knowledge-base/upload`)
const uploadHeaders = computed(() => ({
  'Authorization': `Bearer ${authStore.token}`
}))

// Filters
const filters = reactive({
  search: '',
  status: '',
  type: '',
  dateRange: null as [string, string] | null
})

// Upload options
const uploadOptions = reactive({
  extractImages: true,
  enableOCR: false,
  splitByChapters: true,
  generateSummary: true,
  priority: 'normal'
})

// Pagination
const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

// Computed
const documentStats = computed(() => {
  const stats = {
    total: documents.value.length,
    processed: 0,
    processing: 0,
    failed: 0
  }
  
  documents.value.forEach(doc => {
    switch (doc.status) {
      case 'processed':
        stats.processed++
        break
      case 'processing':
        stats.processing++
        break
      case 'failed':
        stats.failed++
        break
    }
  })
  
  return stats
})

const filteredDocuments = computed(() => {
  let filtered = documents.value
  
  // Search filter
  if (filters.search) {
    filtered = filtered.filter(doc => 
      doc.name.toLowerCase().includes(filters.search.toLowerCase()) ||
      doc.uploadedBy.toLowerCase().includes(filters.search.toLowerCase())
    )
  }
  
  // Status filter
  if (filters.status) {
    filtered = filtered.filter(doc => doc.status === filters.status)
  }
  
  // Type filter
  if (filters.type) {
    filtered = filtered.filter(doc => doc.type === filters.type)
  }
  
  // Date range filter
  if (filters.dateRange) {
    const [startDate, endDate] = filters.dateRange
    filtered = filtered.filter(doc => {
      const uploadDate = new Date(doc.uploadedAt).toISOString().split('T')[0]
      return uploadDate >= startDate && uploadDate <= endDate
    })
  }
  
  return filtered
})

const uploadData = computed(() => ({
  ...uploadOptions
}))

// Lifecycle
onMounted(() => {
  loadDocuments()
})

// Methods
const loadDocuments = async () => {
  try {
    loading.value = true
    const response = await knowledgeApi.getDocuments({
      page: pagination.currentPage,
      pageSize: pagination.pageSize
    })
    documents.value = response.data.documents
    pagination.total = response.data.total
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
  pagination.currentPage = 1
}

const handleDateRangeChange = () => {
  pagination.currentPage = 1
}

const handleSelectionChange = (selection: KnowledgeDocument[]) => {
  selectedDocuments.value = selection
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  loadDocuments()
}

const handleCurrentChange = (page: number) => {
  pagination.currentPage = page
  loadDocuments()
}

// Upload methods
const beforeUpload = (file: File) => {
  const isValidType = ['pdf', 'doc', 'docx', 'txt', 'md'].some(type => 
    file.name.toLowerCase().endsWith(`.${type}`)
  )
  
  if (!isValidType) {
    ElMessage.error('Invalid file type. Supported: PDF, DOC, DOCX, TXT, MD')
    return false
  }
  
  const isValidSize = file.size <= 50 * 1024 * 1024 // 50MB
  if (!isValidSize) {
    ElMessage.error('File size must be less than 50MB')
    return false
  }
  
  return true
}

const handleUploadSuccess = (response: any, file: any) => {
  ElMessage.success(`${file.name} uploaded successfully`)
  loadDocuments()
}

const handleUploadError = (error: any, file: any) => {
  console.error('Upload error:', error)
  ElMessage.error(`Failed to upload ${file.name}`)
}

const handleRemoveFile = (file: any) => {
  const index = uploadFileList.value.findIndex(f => f.uid === file.uid)
  if (index > -1) {
    uploadFileList.value.splice(index, 1)
  }
}

const handleExceed = () => {
  ElMessage.warning('Maximum 5 files can be uploaded at once')
}

const startUpload = () => {
  uploadRef.value?.submit()
}

const handleCloseUploadDialog = () => {
  showUploadDialog.value = false
  uploadFileList.value = []
}

// Document actions
const viewDocument = async (document: KnowledgeDocument) => {
  try {
    const response = await knowledgeApi.getDocumentContent(document.id)
    ElMessage.success('Document content loaded')
  } catch (error) {
    console.error('Failed to load document content:', error)
    ElMessage.error('Failed to load document content')
  }
}

const reprocessDocument = async (document: KnowledgeDocument) => {
  try {
    await ElMessageBox.confirm(
      `Reprocess "${document.name}"? This will replace the current processed content.`,
      'Reprocess Document',
      {
        confirmButtonText: 'Reprocess',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
    )
    
    await knowledgeApi.reprocessDocument(document.id)
    ElMessage.success('Document queued for reprocessing')
    loadDocuments()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Failed to reprocess document')
    }
  }
}

const deleteDocument = async (document: KnowledgeDocument) => {
  try {
    await ElMessageBox.confirm(
      `Delete "${document.name}"? This action cannot be undone.`,
      'Delete Document',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
    )
    
    await knowledgeApi.deleteDocument(document.id)
    ElMessage.success('Document deleted successfully')
    loadDocuments()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Failed to delete document')
    }
  }
}

const handleBulkDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `Delete ${selectedDocuments.value.length} selected documents? This action cannot be undone.`,
      'Bulk Delete',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
    )
    
    const ids = selectedDocuments.value.map(doc => doc.id)
    await knowledgeApi.bulkDeleteDocuments(ids)
    ElMessage.success('Documents deleted successfully')
    selectedDocuments.value = []
    loadDocuments()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Failed to delete documents')
    }
  }
}

const handleBulkReprocess = async () => {
  try {
    await ElMessageBox.confirm(
      `Reprocess ${selectedDocuments.value.length} selected documents?`,
      'Bulk Reprocess',
      {
        confirmButtonText: 'Reprocess',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
    )
    
    const ids = selectedDocuments.value.map(doc => doc.id)
    await knowledgeApi.bulkReprocessDocuments(ids)
    ElMessage.success('Documents queued for reprocessing')
    selectedDocuments.value = []
    loadDocuments()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Failed to reprocess documents')
    }
  }
}

// Utility functions
const getFileIcon = (type: string) => {
  return Document
}

const getFileIconClass = (type: string) => {
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
</script>

<style scoped>
.knowledge-base-manager {
  @apply p-6 bg-gray-50 min-h-screen;
}

.manager-header {
  @apply bg-white rounded-lg p-6 mb-6 shadow-sm;
}

.stats-overview .stat-card {
  @apply bg-white rounded-lg p-4 shadow-sm flex items-center space-x-3;
}

.stat-icon {
  @apply w-10 h-10 rounded-lg flex items-center justify-center text-white;
}

.stat-content {
  @apply flex-1;
}

.stat-label {
  @apply text-sm text-gray-600 mb-1;
}

.stat-value {
  @apply text-xl font-bold text-gray-800;
}

.filters-section {
  @apply mb-6;
}

.documents-table {
  @apply mb-6;
}

.upload-section {
  @apply space-y-6;
}

.upload-options {
  @apply bg-gray-50 p-4 rounded-lg;
}

:deep(.el-upload-dragger) {
  @apply w-full;
}
</style>