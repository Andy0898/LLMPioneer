<template>
  <div class="personal-knowledge-view">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Personal Knowledge Base</h1>
      <el-button type="primary" @click="showUploadDialog = true">
        <el-icon><Upload /></el-icon>
        Upload Document
      </el-button>
    </div>

    <!-- Search and Filter -->
    <div class="bg-white rounded-lg shadow p-4 mb-6">
      <div class="flex space-x-4">
        <el-input
          v-model="searchQuery"
          placeholder="Search documents..."
          style="width: 300px"
          @input="searchDocuments"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="selectedCategory" placeholder="All Categories" style="width: 200px" @change="filterDocuments">
          <el-option label="All Categories" value="" />
          <el-option label="Personal Notes" value="personal" />
          <el-option label="Research" value="research" />
          <el-option label="Projects" value="projects" />
          <el-option label="References" value="references" />
        </el-select>
      </div>
    </div>

    <!-- Documents Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <el-card 
        v-for="document in filteredDocuments" 
        :key="document.id"
        class="cursor-pointer hover:shadow-lg transition-shadow"
        @click="viewDocument(document)"
      >
        <div class="flex flex-col h-full">
          <div class="flex items-start justify-between mb-3">
            <div class="flex-1">
              <h3 class="font-semibold text-gray-900 mb-1 line-clamp-2">{{ document.title }}</h3>
              <p class="text-sm text-gray-600 line-clamp-3">{{ document.summary }}</p>
            </div>
            <el-dropdown @command="handleDocumentAction">
              <el-button text>
                <el-icon><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item :command="{action: 'edit', document}">Edit</el-dropdown-item>
                  <el-dropdown-item :command="{action: 'download', document}">Download</el-dropdown-item>
                  <el-dropdown-item :command="{action: 'delete', document}" divided>Delete</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          
          <div class="flex items-center justify-between mt-auto">
            <el-tag size="small" :type="getCategoryType(document.category)">
              {{ document.category }}
            </el-tag>
            <span class="text-xs text-gray-500">
              {{ formatDate(document.updatedAt) }}
            </span>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Empty State -->
    <div v-if="filteredDocuments.length === 0" class="text-center py-12">
      <el-icon class="text-6xl text-gray-300 mb-4"><Document /></el-icon>
      <h3 class="text-lg font-medium text-gray-900 mb-2">No documents found</h3>
      <p class="text-gray-500 mb-4">
        {{ searchQuery || selectedCategory ? 'Try adjusting your search criteria' : 'Upload your first document to get started' }}
      </p>
      <el-button type="primary" @click="showUploadDialog = true">
        Upload Document
      </el-button>
    </div>

    <!-- Upload Dialog -->
    <el-dialog v-model="showUploadDialog" title="Upload Document" width="500px">
      <el-form :model="uploadForm" label-width="120px">
        <el-form-item label="Title">
          <el-input v-model="uploadForm.title" placeholder="Document title" />
        </el-form-item>
        <el-form-item label="Category">
          <el-select v-model="uploadForm.category" placeholder="Select category">
            <el-option label="Personal Notes" value="personal" />
            <el-option label="Research" value="research" />
            <el-option label="Projects" value="projects" />
            <el-option label="References" value="references" />
          </el-select>
        </el-form-item>
        <el-form-item label="Summary">
          <el-input 
            v-model="uploadForm.summary" 
            type="textarea" 
            :rows="3"
            placeholder="Brief summary of the document"
          />
        </el-form-item>
        <el-form-item label="File">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :on-change="handleFileChange"
            accept=".pdf,.txt,.doc,.docx,.md"
            :limit="1"
          >
            <el-button>Select File</el-button>
            <template #tip>
              <div class="el-upload__tip">
                Supported formats: PDF, TXT, DOC, DOCX, MD (max 10MB)
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUploadDialog = false">Cancel</el-button>
        <el-button type="primary" @click="uploadDocument" :loading="uploading">
          Upload
        </el-button>
      </template>
    </el-dialog>

    <!-- Document Viewer Dialog -->
    <el-dialog v-model="showViewerDialog" :title="viewingDocument?.title" width="80%" fullscreen>
      <div v-if="viewingDocument" class="space-y-4">
        <div class="flex items-center space-x-4">
          <el-tag :type="getCategoryType(viewingDocument.category)">
            {{ viewingDocument.category }}
          </el-tag>
          <span class="text-sm text-gray-500">
            Last updated: {{ formatDate(viewingDocument.updatedAt) }}
          </span>
        </div>
        <div class="prose max-w-none">
          <p class="text-gray-600 italic mb-4">{{ viewingDocument.summary }}</p>
          <div class="whitespace-pre-wrap">{{ viewingDocument.content || 'Content not available' }}</div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Upload, Search, Document, MoreFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

interface PersonalDocument {
  id: string
  title: string
  summary: string
  category: string
  content?: string
  filename: string
  size: number
  updatedAt: string
}

const documents = ref<PersonalDocument[]>([])
const searchQuery = ref('')
const selectedCategory = ref('')
const showUploadDialog = ref(false)
const showViewerDialog = ref(false)
const viewingDocument = ref<PersonalDocument | null>(null)
const uploading = ref(false)

const uploadForm = ref({
  title: '',
  category: '',
  summary: '',
  file: null as File | null
})

const filteredDocuments = computed(() => {
  let filtered = documents.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(doc => 
      doc.title.toLowerCase().includes(query) ||
      doc.summary.toLowerCase().includes(query)
    )
  }

  if (selectedCategory.value) {
    filtered = filtered.filter(doc => doc.category === selectedCategory.value)
  }

  return filtered
})

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString()
}

const getCategoryType = (category: string) => {
  const types: Record<string, string> = {
    personal: 'primary',
    research: 'success',
    projects: 'warning',
    references: 'info'
  }
  return types[category] || 'default'
}

const searchDocuments = () => {
  // Debounce search if needed
  console.log('Searching:', searchQuery.value)
}

const filterDocuments = () => {
  console.log('Filtering by category:', selectedCategory.value)
}

const viewDocument = (document: PersonalDocument) => {
  viewingDocument.value = document
  showViewerDialog.value = true
}

const handleDocumentAction = (command: { action: string; document: PersonalDocument }) => {
  const { action, document } = command
  
  switch (action) {
    case 'edit':
      // TODO: Implement edit functionality
      ElMessage.info('Edit functionality will be implemented')
      break
    case 'download':
      // TODO: Implement download functionality
      ElMessage.info('Download functionality will be implemented')
      break
    case 'delete':
      // TODO: Implement delete functionality
      ElMessage.info('Delete functionality will be implemented')
      break
  }
}

const handleFileChange = (file: any) => {
  uploadForm.value.file = file.raw
  // Auto-fill title if not set
  if (!uploadForm.value.title) {
    uploadForm.value.title = file.name.replace(/\.[^/.]+$/, '')
  }
}

const uploadDocument = async () => {
  if (!uploadForm.value.file || !uploadForm.value.title || !uploadForm.value.category) {
    ElMessage.warning('Please fill in all required fields')
    return
  }

  uploading.value = true

  try {
    // TODO: Implement actual upload API call
    await new Promise(resolve => setTimeout(resolve, 2000)) // Simulate upload
    
    ElMessage.success('Document uploaded successfully')
    showUploadDialog.value = false
    
    // Reset form
    uploadForm.value = {
      title: '',
      category: '',
      summary: '',
      file: null
    }
    
    // TODO: Refresh documents list
  } catch (error) {
    ElMessage.error('Failed to upload document')
  } finally {
    uploading.value = false
  }
}

onMounted(() => {
  // TODO: Load user's documents from API
  documents.value = [
    {
      id: '1',
      title: 'Getting Started with AI',
      summary: 'A comprehensive guide to understanding artificial intelligence basics and applications.',
      category: 'research',
      filename: 'ai-guide.pdf',
      size: 1024000,
      updatedAt: new Date().toISOString()
    },
    {
      id: '2',
      title: 'Project Meeting Notes',
      summary: 'Notes from the quarterly project review meeting discussing goals and milestones.',
      category: 'projects',
      filename: 'meeting-notes.txt',
      size: 512000,
      updatedAt: new Date(Date.now() - 86400000).toISOString()
    }
  ]
})
</script>

<style scoped>
.personal-knowledge-view {
  padding: 24px;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.prose {
  line-height: 1.6;
}
</style>