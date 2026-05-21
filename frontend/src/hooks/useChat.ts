import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { chatAPI } from '@api/chat'
import { useChatStore } from '@stores/chatStore'
import type { ChatMessage } from '@types/index'

export const useChat = (notebookId: string) => {
  const queryClient = useQueryClient()
  const { i18n } = useTranslation()
  const messages = useChatStore((state) => state.messages)
  const messagesByNotebook = useChatStore((state) => state.messagesByNotebook)
  const setCurrentNotebook = useChatStore((state) => state.setCurrentNotebook)
  const setMessages = useChatStore((state) => state.setMessages)
  const addMessage = useChatStore((state) => state.addMessage)
  const setLoading = useChatStore((state) => state.setLoading)

  // Cargar el notebook actual cuando cambia
  useEffect(() => {
    if (notebookId) {
      setCurrentNotebook(notebookId)
    }
  }, [notebookId, setCurrentNotebook])

  const historyQuery = useQuery({
    queryKey: ['chat', notebookId],
    queryFn: async () => {
      if (!notebookId) return []
      try {
        const response = await chatAPI.getHistory(notebookId)
        const msgs = response.data
        console.log('Chat history loaded for notebook:', notebookId, msgs)
        // Solo actualizar si no hay mensajes en el store (primera carga)
        if (!messagesByNotebook[notebookId] || messagesByNotebook[notebookId].length === 0) {
          setMessages(notebookId, msgs as ChatMessage[])
        }
        return msgs
      } catch (error) {
        console.error('Error fetching chat history:', error)
        return []
      }
    },
    enabled: !!notebookId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  const askAIMutation = useMutation({
    mutationFn: ({ message, systemPrompt }: { message: string; systemPrompt?: string }) => {
      if (!notebookId) {
        return Promise.reject(new Error('Notebook ID is required'))
      }
      setLoading(true)
      console.log('Sending message to AI:', { notebookId, message, systemPrompt, language: i18n.language })
      return chatAPI.askAI(notebookId, message, systemPrompt, i18n.language)
    },
    onSuccess: (response) => {
      console.log('AI response received:', response.data)
      const { user_message, assistant_message } = response.data
      if (user_message && assistant_message) {
        // Add messages to store for this notebook
        addMessage(notebookId, user_message)
        addMessage(notebookId, assistant_message)
        console.log('Messages updated in store for notebook:', notebookId)
      } else {
        console.warn('Invalid response structure:', response.data)
      }
      setLoading(false)
    },
    onError: (error) => {
      console.error('Error sending message:', error)
      setLoading(false)
    },
  })

  return {
    messages,
    isLoading: historyQuery.isLoading || historyQuery.isFetching,
    sendMessage: askAIMutation.mutate,
    isSending: askAIMutation.isPending,
    error: historyQuery.error || askAIMutation.error,
  }
}
