<template>
  <div class="knowledge-base-view">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Knowledge Base Management</h1>
      <el-button type="primary" @click="showUploadDialog = true">
        <el-icon><Upload /></el-icon>
        Upload Document
      </el-button>
    </div>

    <div class="bg-white rounded-lg shadow">
      <div class="p-6">
        <el-table :data="documents" v-loading="loading">
          <el-table-column prop="filename" label="Document Name" />
          <el-table-column prop="category" label="Category">
            <template #default="{ row }">
              <el-tag>{{ row.category }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="size" label="Size">
            <template #default="{ row }">
              {{ formatFileSize(row.size) }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="Status">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="createdAt" label="Uploaded At">
            <template #default="{ row }">
              {{ formatDate(row.createdAt) }}
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="120">
            <template #default="{ row }">
              <el-button size="small" @click="viewDocument(row)">View</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- Upload Document Dialog -->
    <el-dialog v-model="showUploadDialog" title="Upload Document" width="500px">
      <el-form :model="uploadForm" label-width="120px">
        <el-form-item label="Category">
          <el-select v-model="uploadForm.category" placeholder="Select category">
            <el-option label="General" value="general" />
            <el-option label="Technical" value="technical" />
            <el-option label="Business" value="business" />
          </el-select>
        </el-form-item>
        <el-form-item label="File">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :on-change="handleFileChange"
            accept=".pdf,.txt,.doc,.docx"
          >
            <el-button>Select File</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUploadDialog = false">Cancel</el-button>
        <el-button type="primary" @click="uploadDocument">Upload</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Upload } from '@element-plus/icons-vue'

const documents = ref([])
const loading = ref(false)
const showUploadDialog = ref(false)
const uploadForm = ref({
  category: '',
  file: null
})

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString()
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'processed': return 'success'
    case 'processing': return 'warning'
    case 'failed': return 'danger'
    default: return 'info'
  }
}

const viewDocument = (document: any) => {
  // TODO: Implement view document functionality
  console.log('View document:', document)
}

const handleFileChange = (file: any) => {
  uploadForm.value.file = file.raw
}

const uploadDocument = () => {
  // TODO: Implement upload document functionality
  console.log('Upload document:', uploadForm.value)
  showUploadDialog.value = false
}

onMounted(() => {
  // TODO: Load documents from API
  documents.value = []
})
</script>

<style scoped>
.knowledge-base-view {
  padding: 24px;
}
</style>