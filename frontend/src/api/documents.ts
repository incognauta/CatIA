import { apiClient } from './client'
import type { Document, APIResponse } from '@types/index'

export const documentsAPI = {
  getAll: (notebookId: string) =>
    apiClient.get<APIResponse<Document>>(`/documents/?notebook=${notebookId}`),
  
  upload: (notebookId: string, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('notebook', notebookId)
    
    return apiClient.post<Document>('/documents/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  
  delete: (id: string) =>
    apiClient.delete(`/documents/${id}/`),
}
