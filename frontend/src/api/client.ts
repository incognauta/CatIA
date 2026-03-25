import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosError } from 'axios'
import { useAuthStore } from '@stores/authStore'
import type { APIError } from '@types/index'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api/v1'

class APIClient {
  private client: AxiosInstance
  private static instance: APIClient

  private constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor - Agregar JWT
    this.client.interceptors.request.use((config: InternalAxiosRequestConfig) => {
      const token = useAuthStore.getState().token
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    // Response interceptor - Handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<APIError>) => {
        if (error.response?.status === 401) {
          useAuthStore.getState().logout()
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  public static getInstance(): APIClient {
    if (!APIClient.instance) {
      APIClient.instance = new APIClient()
    }
    return APIClient.instance
  }

  public getClient(): AxiosInstance {
    return this.client
  }
}

export const apiClient = APIClient.getInstance().getClient()
