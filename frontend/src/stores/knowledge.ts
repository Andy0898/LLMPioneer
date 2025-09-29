import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { 
  Document, 
  DocumentCategory, 
  ProcessingTask, 
  SearchResult,
  DocumentUploadRequest 
} from '@/types'
import { knowledgeApi } from '@/api/knowledge'
import { ElMessage } from 'element-plus'

export const useKnowledgeStore = defineStore('knowledge', () => {
  // State
  const documents = ref<Document[]>([])
  const categories = ref<DocumentCategory[]>([])
  const processingTasks = ref<ProcessingTask[]>([])
  const searchResults = ref<SearchResult[]>([])
  const isLoading = ref(false)
  const isUploading = ref(false)
  const isSearching = ref(false)
  const error = ref<string | null>(null)
  const uploadProgress = ref<{ [documentId: string]: number }>({})

  // Getters
  const totalDocuments = computed(() => documents.value.length)
  const processedDocuments = computed(() => 
    documents.value.filter(doc => doc.processed)
  )
  const pendingDocuments = computed(() => 
    documents.value.filter(doc => !doc.processed)
  )
  const activeTasks = computed(() => 
    processingTasks.value.filter(task => 
      task.status === 'pending' || task.status === 'processing'
    )
  )
  const completedTasks = computed(() =>
    processingTasks.value.filter(task => task.status === 'completed')
  )
  const failedTasks = computed(() =>
    processingTasks.value.filter(task => task.status === 'failed')
  )
  const categorizedDocuments = computed(() => {
    const grouped: { [categoryId: string]: Document[] } = {}
    documents.value.forEach(doc => {
      const categoryId = doc.category_id || 'uncategorized'
      if (!grouped[categoryId]) {
        grouped[categoryId] = []
      }
      grouped[categoryId].push(doc)
    })
    return grouped
  })

  // Actions
  const fetchDocuments = async () => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await knowledgeApi.getDocuments()
      documents.value = response.data
      
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch documents'
      ElMessage.error(error.value)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const fetchCategories = async () => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await knowledgeApi.getCategories()
      categories.value = response.data
      
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch categories'
      ElMessage.error(error.value)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const uploadDocument = async (request: DocumentUploadRequest) => {
    try {
      isUploading.value = true
      error.value = null
      
      const formData = new FormData()
      formData.append('file', request.file)
      if (request.category_id) {
        formData.append('category_id', request.category_id)
      }
      if (request.description) {
        formData.append('description', request.description)
      }
      
      // Track upload progress
      const tempId = `upload_${Date.now()}`
      uploadProgress.value[tempId] = 0
      
      const response = await knowledgeApi.uploadDocument(formData, {
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            uploadProgress.value[tempId] = progress
          }
        }
      })
      
      const newDocument = response.data.document
      const processingTask = response.data.processing_task
      
      // Add to store
      documents.value.unshift(newDocument)
      if (processingTask) {
        processingTasks.value.unshift(processingTask)
      }
      
      // Clean up progress tracking
      delete uploadProgress.value[tempId]
      
      ElMessage.success('Document uploaded successfully!')
      return { document: newDocument, task: processingTask }
      
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to upload document'
      ElMessage.error(error.value)
      throw err
    } finally {
      isUploading.value = false
    }
  }

  const deleteDocument = async (documentId: string) => {
    try {
      isLoading.value = true
      error.value = null
      
      await knowledgeApi.deleteDocument(documentId)
      
      // Remove from store
      documents.value = documents.value.filter(doc => doc.id !== documentId)
      
      // Remove associated processing tasks
      processingTasks.value = processingTasks.value.filter(
        task => task.document_id !== documentId
      )
      
      ElMessage.success('Document deleted successfully!')
      
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to delete document'
      ElMessage.error(error.value)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const createCategory = async (name: string, description?: string, parentId?: string) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await knowledgeApi.createCategory({
        name,
        description,
        parent_id: parentId
      })
      
      const newCategory = response.data
      categories.value.push(newCategory)
      
      ElMessage.success('Category created successfully!')
      return newCategory
      
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to create category'
      ElMessage.error(error.value)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const updateCategory = async (categoryId: string, updates: Partial<DocumentCategory>) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await knowledgeApi.updateCategory(categoryId, updates)
      const updatedCategory = response.data
      
      // Update in store
      const index = categories.value.findIndex(cat => cat.id === categoryId)
      if (index !== -1) {
        categories.value[index] = updatedCategory
      }
      
      ElMessage.success('Category updated successfully!')
      return updatedCategory
      
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to update category'
      ElMessage.error(error.value)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const deleteCategory = async (categoryId: string) => {
    try {
      isLoading.value = true
      error.value = null
      
      await knowledgeApi.deleteCategory(categoryId)
      
      // Remove from store
      categories.value = categories.value.filter(cat => cat.id !== categoryId)
      
      // Update documents that belonged to this category
      documents.value.forEach(doc => {
        if (doc.category_id === categoryId) {
          doc.category_id = undefined
        }
      })
      
      ElMessage.success('Category deleted successfully!')
      
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to delete category'
      ElMessage.error(error.value)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const searchDocuments = async (query: string, filters?: { category_id?: string }) => {
    try {
      isSearching.value = true
      error.value = null
      
      const response = await knowledgeApi.searchDocuments(query, filters)
      searchResults.value = response.data
      
      return searchResults.value
      
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to search documents'
      ElMessage.error(error.value)
      throw err
    } finally {
      isSearching.value = false
    }
  }

  const fetchProcessingTasks = async () => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await knowledgeApi.getProcessingTasks()
      processingTasks.value = response.data
      
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch processing tasks'
      ElMessage.error(error.value)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const updateProcessingTaskStatus = async (taskId: string) => {
    try {
      const response = await knowledgeApi.getProcessingTaskStatus(taskId)
      const updatedTask = response.data
      
      // Update in store
      const index = processingTasks.value.findIndex(task => task.id === taskId)
      if (index !== -1) {
        processingTasks.value[index] = updatedTask
        
        // If task is completed, update document status
        if (updatedTask.status === 'completed') {
          const document = documents.value.find(doc => doc.id === updatedTask.document_id)
          if (document) {
            document.processed = true
            document.processing_status = 'completed'
          }
        }
      }
      
      return updatedTask
      
    } catch (err: any) {
      console.error('Failed to update processing task status:', err)
      throw err
    }
  }

  const pollProcessingTasks = () => {
    const interval = setInterval(async () => {
      const activeTaskIds = activeTasks.value.map(task => task.id)
      
      if (activeTaskIds.length === 0) {
        clearInterval(interval)
        return
      }
      
      try {
        for (const taskId of activeTaskIds) {
          await updateProcessingTaskStatus(taskId)
        }
      } catch (err) {
        console.error('Error polling processing tasks:', err)
      }
    }, 5000) // Poll every 5 seconds
    
    return interval
  }

  const moveDocumentToCategory = async (documentId: string, categoryId: string | null) => {
    try {
      const response = await knowledgeApi.updateDocument(documentId, {
        category_id: categoryId
      })
      
      const updatedDocument = response.data
      
      // Update in store
      const index = documents.value.findIndex(doc => doc.id === documentId)
      if (index !== -1) {
        documents.value[index] = updatedDocument
      }
      
      ElMessage.success('Document moved successfully!')
      return updatedDocument
      
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to move document'
      ElMessage.error(error.value)
      throw err
    }
  }

  const clearSearchResults = () => {
    searchResults.value = []
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // State
    documents: readonly(documents),
    categories: readonly(categories),
    processingTasks: readonly(processingTasks),
    searchResults: readonly(searchResults),
    isLoading: readonly(isLoading),
    isUploading: readonly(isUploading),
    isSearching: readonly(isSearching),
    error: readonly(error),
    uploadProgress: readonly(uploadProgress),
    
    // Getters
    totalDocuments,
    processedDocuments,
    pendingDocuments,
    activeTasks,
    completedTasks,
    failedTasks,
    categorizedDocuments,
    
    // Actions
    fetchDocuments,
    fetchCategories,
    uploadDocument,
    deleteDocument,
    createCategory,
    updateCategory,
    deleteCategory,
    searchDocuments,
    fetchProcessingTasks,
    updateProcessingTaskStatus,
    pollProcessingTasks,
    moveDocumentToCategory,
    clearSearchResults,
    clearError
  }
})