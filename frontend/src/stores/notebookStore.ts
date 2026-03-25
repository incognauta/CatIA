import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface NotebookContent {
  [notebookId: string]: {
    content: string
    lastSaved: string
  }
}

interface NotebookContentStore {
  contents: NotebookContent
  setContent: (notebookId: string, content: string) => void
  getContent: (notebookId: string) => string
  clear: (notebookId: string) => void
}

export const useNotebookContentStore = create<NotebookContentStore>()(
  persist(
    (set, get) => ({
      contents: {},
      setContent: (notebookId: string, content: string) =>
        set((state) => ({
          contents: {
            ...state.contents,
            [notebookId]: {
              content,
              lastSaved: new Date().toISOString(),
            },
          },
        })),
      getContent: (notebookId: string) => {
        const state = get()
        return state.contents[notebookId]?.content || ''
      },
      clear: (notebookId: string) =>
        set((state) => {
          const { [notebookId]: _, ...rest } = state.contents
          return { contents: rest }
        }),
    }),
    {
      name: 'notebook-content-store',
      version: 1,
    }
  )
)
