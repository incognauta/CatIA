// Auth
export interface User {
  id: string
  email: string
  username: string
  subscription_tier: 'free' | 'pro' | 'enterprise'
  email_verified: boolean
  profile?: UserProfile
}

export interface UserProfile {
  id: string
  bio?: string
  avatar_url?: string
  preferred_language: string
}

export interface LoginResponse {
  access: string
  refresh?: string
  user: User
}

// Notebooks
export interface Notebook {
  id: string
  user: string
  name: string
  description?: string
  slug: string
  color?: string
  icon?: string
  is_default: boolean
  created_at: string
  updated_at: string
  documents_count?: number
  messages_count?: number
}

// Documents
export interface Document {
  id: string
  notebook: string
  file: File | null
  original_filename: string
  file_type: 'pdf' | 'docx' | 'txt' | 'image'
  file_size: number
  pages: number
  content: string
  content_markdown: string
  is_scanned: boolean
  created_at: string
  updated_at: string
}

// Chat
export interface ChatMessage {
  id: string
  user: string
  notebook: string
  document?: string
  role: 'user' | 'assistant'
  content: string
  tokens_used: number
  created_at: string
  updated_at: string
}

export interface AskAIRequest {
  notebook: string
  message: string
  system_prompt?: string
}

export interface AskAIResponse {
  user_message: ChatMessage
  assistant_message: ChatMessage
  tokens_used: number
  context_docs: number
  model: string
}

// API Generic
export interface APIResponse<T> {
  count?: number
  next?: string
  previous?: string
  results?: T[]
  [key: string]: any
}

export interface APIError {
  error: string
  status: number
  details?: Record<string, any>
}
