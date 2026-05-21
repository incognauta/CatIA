import { apiClient } from './client'
import type { ChatMessage, AskAIResponse } from '@types/index'

export const chatAPI = {
  getMessages: (notebookId: string) =>
    apiClient.get<ChatMessage[]>(`/chat/?notebook=${notebookId}`),
  
  getHistory: (notebookId: string) =>
    apiClient.get<ChatMessage[]>(`/chat/history/?notebook=${notebookId}`),
  
  askAI: (notebookId: string, message: string, systemPrompt?: string, language?: string) =>
    apiClient.post<AskAIResponse>('/chat/ask_ai/', {
      notebook: notebookId,
      message,
      system_prompt: systemPrompt,
      language: language || 'es',
    }),
  
  clearHistory: (notebookId: string) =>
    apiClient.delete(`/chat/clear_history/?notebook=${notebookId}`),
}
