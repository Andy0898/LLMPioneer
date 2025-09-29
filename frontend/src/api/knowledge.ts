import { api, uploadWithProgress } from './client'
import type { 
  Document, 
  DocumentCategory, 
  ProcessingTask, 
  SearchResult,
  PaginatedResponse 
} from '@/types'

export const knowledgeApi = {
  // Document management
  getDocuments: async (page: number = 1, size: number = 50): Promise<PaginatedResponse<Document>> => {
    const response = await api.get<PaginatedResponse<Document>>(
      `/api/v1/sa/document/list?page=${page}&size=${size}`
    )
    return response.data
  },

  getDocument: async (documentId: string): Promise<Document> => {
    const response = await api.get<Document>(`/api/v1/sa/document/${documentId}`)
    return response.data
  },

  uploadDocument: async (formData: FormData, config?: { onUploadProgress?: (progress: any) => void }): Promise<{
    document: Document
    processing_task: ProcessingTask
  }> => {
    const response = await uploadWithProgress('/api/v1/sa/document/upload', formData, config)
    return response.data
  },

  updateDocument: async (documentId: string, updates: Partial<Document>): Promise<Document> => {
    const response = await api.put<Document>(`/api/v1/sa/document/${documentId}`, updates)
    return response.data
  },

  deleteDocument: async (documentId: string): Promise<void> => {
    await api.delete(`/api/v1/sa/document/${documentId}`)
  },

  downloadDocument: async (documentId: string): Promise<Blob> => {
    const response = await api.get(`/api/v1/sa/document/${documentId}/download`, {
      responseType: 'blob'
    })
    return response.data
  },

  // Document processing
  reprocessDocument: async (documentId: string): Promise<ProcessingTask> => {
    const response = await api.post<ProcessingTask>(`/api/v1/sa/document/${documentId}/reprocess`)
    return response.data
  },

  getProcessingTasks: async (page: number = 1, size: number = 50): Promise<PaginatedResponse<ProcessingTask>> => {
    const response = await api.get<PaginatedResponse<ProcessingTask>>(
      `/api/v1/sa/document/processing-tasks?page=${page}&size=${size}`
    )
    return response.data
  },

  getProcessingTaskStatus: async (taskId: string): Promise<ProcessingTask> => {
    const response = await api.get<ProcessingTask>(`/api/v1/sa/document/processing-task/${taskId}`)
    return response.data
  },

  cancelProcessingTask: async (taskId: string): Promise<void> => {
    await api.post(`/api/v1/sa/document/processing-task/${taskId}/cancel`)
  },

  // Document categories
  getCategories: async (): Promise<DocumentCategory[]> => {
    const response = await api.get<DocumentCategory[]>('/api/v1/sa/document-category/list')
    return response.data
  },

  getCategory: async (categoryId: string): Promise<DocumentCategory> => {
    const response = await api.get<DocumentCategory>(`/api/v1/sa/document-category/${categoryId}`)
    return response.data
  },

  createCategory: async (category: {
    name: string
    description?: string
    parent_id?: string
  }): Promise<DocumentCategory> => {
    const response = await api.post<DocumentCategory>('/api/v1/sa/document-category/', category)
    return response.data
  },

  updateCategory: async (categoryId: string, updates: Partial<DocumentCategory>): Promise<DocumentCategory> => {
    const response = await api.put<DocumentCategory>(`/api/v1/sa/document-category/${categoryId}`, updates)
    return response.data
  },

  deleteCategory: async (categoryId: string): Promise<void> => {
    await api.delete(`/api/v1/sa/document-category/${categoryId}`)
  },

  getCategoryDocuments: async (categoryId: string, page: number = 1, size: number = 50): Promise<PaginatedResponse<Document>> => {
    const response = await api.get<PaginatedResponse<Document>>(
      `/api/v1/sa/document-category/${categoryId}/documents?page=${page}&size=${size}`
    )
    return response.data
  },

  // Search and retrieval
  searchDocuments: async (
    query: string, 
    filters?: { 
      category_id?: string
      file_type?: string
      processed?: boolean
    },
    page: number = 1,
    size: number = 20
  ): Promise<SearchResult[]> => {
    const params = new URLSearchParams({
      q: query,
      page: page.toString(),
      size: size.toString()
    })
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) {
          params.append(key, value.toString())
        }
      })
    }
    
    const response = await api.get<SearchResult[]>(`/api/v1/sa/document/search?${params.toString()}`)
    return response.data
  },

  // Vector similarity search
  vectorSearch: async (
    query: string,
    options?: {
      top_k?: number
      similarity_threshold?: number
      category_id?: string
    }
  ): Promise<SearchResult[]> => {
    const response = await api.post<SearchResult[]>('/api/v1/sa/document/vector-search', {
      query,
      ...options
    })
    return response.data
  },

  // Document chunks
  getDocumentChunks: async (documentId: string, page: number = 1, size: number = 50): Promise<PaginatedResponse<{
    id: string
    content: string
    chunk_index: number
    embedding_vector?: number[]
    created_at: string
  }>> => {
    const response = await api.get<PaginatedResponse<any>>(
      `/api/v1/sa/document/${documentId}/chunks?page=${page}&size=${size}`
    )
    return response.data
  },

  // Document statistics
  getDocumentStats: async (): Promise<{
    total_documents: number
    processed_documents: number
    pending_documents: number
    failed_documents: number
    total_size_bytes: number
    total_chunks: number
    categories_count: number
    recent_uploads: Document[]
  }> => {
    const response = await api.get('/api/v1/sa/document/stats')
    return response.data
  },

  // Bulk operations
  bulkDeleteDocuments: async (documentIds: string[]): Promise<{
    deleted_count: number
    failed_ids: string[]
  }> => {
    const response = await api.post('/api/v1/sa/document/bulk-delete', {
      document_ids: documentIds
    })
    return response.data
  },

  bulkMoveDocuments: async (documentIds: string[], categoryId: string | null): Promise<{
    updated_count: number
    failed_ids: string[]
  }> => {
    const response = await api.post('/api/v1/sa/document/bulk-move', {
      document_ids: documentIds,
      category_id: categoryId
    })
    return response.data
  },

  bulkReprocessDocuments: async (documentIds: string[]): Promise<{
    processing_tasks: ProcessingTask[]
    failed_ids: string[]
  }> => {
    const response = await api.post('/api/v1/sa/document/bulk-reprocess', {
      document_ids: documentIds
    })
    return response.data
  },

  // Export/Import
  exportDocuments: async (options: {
    category_id?: string
    format: 'json' | 'csv' | 'xlsx'
    include_content?: boolean
  }): Promise<Blob> => {
    const params = new URLSearchParams()
    Object.entries(options).forEach(([key, value]) => {
      if (value !== undefined) {
        params.append(key, value.toString())
      }
    })
    
    const response = await api.get(`/api/v1/sa/document/export?${params.toString()}`, {
      responseType: 'blob'
    })
    return response.data
  },

  importDocuments: async (file: File, options?: {
    category_id?: string
    auto_process?: boolean
  }): Promise<{
    imported_count: number
    failed_count: number
    processing_tasks: ProcessingTask[]
  }> => {
    const formData = new FormData()
    formData.append('file', file)
    
    if (options) {
      Object.entries(options).forEach(([key, value]) => {
        if (value !== undefined) {
          formData.append(key, value.toString())
        }
      })
    }
    
    const response = await api.post('/api/v1/sa/document/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  }
}