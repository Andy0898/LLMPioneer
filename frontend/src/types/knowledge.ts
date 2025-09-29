export interface Document {
  id: string
  filename: string
  file_size: number
  file_type: string
  category_id?: string
  upload_path: string
  processed: boolean
  processing_status: ProcessingStatus
  chunks_count?: number
  created_at: string
  updated_at: string
}

export interface DocumentCategory {
  id: string
  name: string
  description?: string
  parent_id?: string
  document_count: number
  created_at: string
  updated_at: string
}

export interface ProcessingTask {
  id: string
  task_id: string
  document_id: string
  status: ProcessingStatus
  progress: number
  error_message?: string
  started_at: string
  completed_at?: string
}

export type ProcessingStatus = 
  | 'pending' 
  | 'processing' 
  | 'completed' 
  | 'failed' 
  | 'cancelled'

export interface DocumentUploadRequest {
  file: File
  category_id?: string
  description?: string
}

export interface SearchResult {
  id: string
  content: string
  document_id: string
  document_name: string
  score: number
  chunk_index: number
}

export interface KnowledgeBaseState {
  documents: Document[]
  categories: DocumentCategory[]
  processingTasks: ProcessingTask[]
  searchResults: SearchResult[]
  isLoading: boolean
  error: string | null
}