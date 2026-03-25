import { apiClient } from './client'
import type { Notebook, APIResponse } from '@types/index'

export const notebooksAPI = {
  getAll: () =>
    apiClient.get<APIResponse<Notebook>>('/notebooks/'),
  
  getOne: (id: string) =>
    apiClient.get<Notebook>(`/notebooks/${id}/`),
  
  create: (name: string, description?: string, color?: string, icon?: string) => {
    // Generar slug automáticamente desde el nombre
    const slug = name.toLowerCase().replace(/\s+/g, '-').slice(0, 50)
    
    return apiClient.post<Notebook>('/notebooks/', {
      name,
      slug,
      description: description || '',
      color: color || '#7C3AED', // Color púrpura por defecto
      icon: icon || '📓',
      is_default: false,
    })
  },
  
  update: (id: string, data: Partial<Notebook>) =>
    apiClient.patch<Notebook>(`/notebooks/${id}/`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/notebooks/${id}/`),
}
