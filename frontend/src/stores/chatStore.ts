import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { ChatMessage } from '@types/index'

interface ChatMessagesByNotebook {
  [notebookId: string]: ChatMessage[]
}

interface ChatStore {
  messagesByNotebook: ChatMessagesByNotebook
  currentNotebookId: string | null
  messages: ChatMessage[]
  isLoading: boolean
  setCurrentNotebook: (notebookId: string) => void
  setMessages: (notebookId: string, messages: ChatMessage[]) => void
  addMessage: (notebookId: string, message: ChatMessage) => void
  setLoading: (loading: boolean) => void
  clear: (notebookId: string) => void
}

export const useChatStore = create<ChatStore>()(
  persist(
    (set, get) => ({
      messagesByNotebook: {},
      currentNotebookId: null,
      messages: [],
      isLoading: false,
      
      setCurrentNotebook: (notebookId: string) => {
        set((state) => {
          const messages = state.messagesByNotebook[notebookId] || []
          return {
            currentNotebookId: notebookId,
            messages,
          }
        })
      },
      
      setMessages: (notebookId: string, messages: ChatMessage[]) =>
        set((state) => ({
          messagesByNotebook: {
            ...state.messagesByNotebook,
            [notebookId]: messages,
          },
          messages: get().currentNotebookId === notebookId ? messages : state.messages,
        })),
      
      addMessage: (notebookId: string, message: ChatMessage) =>
        set((state) => {
          const notebookMessages = [...(state.messagesByNotebook[notebookId] || []), message]
          return {
            messagesByNotebook: {
              ...state.messagesByNotebook,
              [notebookId]: notebookMessages,
            },
            messages:
              get().currentNotebookId === notebookId ? notebookMessages : state.messages,
          }
        }),
      
      setLoading: (isLoading) => set({ isLoading }),
      
      clear: (notebookId: string) =>
        set((state) => {
          const { [notebookId]: _, ...rest } = state.messagesByNotebook
          return {
            messagesByNotebook: rest,
            messages: get().currentNotebookId === notebookId ? [] : state.messages,
          }
        }),
    }),
    {
      name: 'chat-store',
      version: 2,
    }
  )
)
