import { apiClient } from './client'
import type { User, LoginResponse } from '@types/index'

export const authAPI = {
  login: (email: string, password: string) =>
    apiClient.post<LoginResponse>('/auth/login/', { email, password }),
  
  register: (email: string, password: string, password_confirm: string, username: string, first_name?: string, last_name?: string) =>
    apiClient.post<LoginResponse>('/auth/register/', { 
      email, 
      password, 
      password_confirm, 
      username, 
      first_name: first_name || '',
      last_name: last_name || ''
    }),
  
  getProfile: () =>
    apiClient.get<User>('/auth/profile/'),
  
  logout: () =>
    apiClient.post('/auth/logout/'),
}
