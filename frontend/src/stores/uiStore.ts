import { create } from 'zustand'

interface UIStore {
  isSidebarOpen: boolean
  isDocsModalOpen: boolean
  isChatOpen: boolean
  toggleSidebar: () => void
  openDocsModal: () => void
  closeDocsModal: () => void
  toggleChat: () => void
}

export const useUIStore = create<UIStore>((set) => ({
  isSidebarOpen: true,
  isDocsModalOpen: false,
  isChatOpen: true,
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  openDocsModal: () => set({ isDocsModalOpen: true }),
  closeDocsModal: () => set({ isDocsModalOpen: false }),
  toggleChat: () => set((state) => ({ isChatOpen: !state.isChatOpen })),
}))
