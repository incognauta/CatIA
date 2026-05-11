import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useNotebook } from '@hooks/useNotebooks'
import { useChat } from '@hooks/useChat'
import { useDocuments } from '@hooks/useDocuments'
import { useUIStore } from '@stores/uiStore'
import { useNotebookContentStore } from '@stores/notebookStore'
import { ArrowLeft, FileCode, MessageCircle, Settings } from 'lucide-react'
import NotebookCanvas from '@components/notebook/NotebookCanvas'
import ChatSidebar from '@components/chat/ChatSidebar'
import { ChatSettings } from '@components/chat/ChatSettings'
import DocumentsModal from '@components/documents/DocumentsModal'

export default function NotebookPage() {
  const { notebookId } = useParams<{ notebookId: string }>()
  const navigate = useNavigate()
  const { data: notebook, isLoading } = useNotebook(notebookId || '')
  const { messages, sendMessage, isSending } = useChat(notebookId || '')
  const { documents } = useDocuments(notebookId || '')
  const { isDocsModalOpen, openDocsModal, closeDocsModal } = useUIStore()
  
  // Use persistent store for notebook content
  const content = useNotebookContentStore((state) => state.getContent(notebookId || ''))
  const setNotebookContent = useNotebookContentStore((state) => state.setContent)
  
  const [localContent, setLocalContent] = useState(content)
  const [showSettings, setShowSettings] = useState(false)
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  // Load content from persistent store when notebookId changes
  useEffect(() => {
    const savedContent = useNotebookContentStore.getState().getContent(notebookId || '')
    setLocalContent(savedContent)
  }, [notebookId])

  // Auto-save with debounce (2 seconds after last change)
  const handleContentChange = (newContent: string) => {
    setLocalContent(newContent)
    
    // Clear existing timeout
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current)
    }
    
    // Set new timeout for auto-save
    saveTimeoutRef.current = setTimeout(() => {
      setNotebookContent(notebookId || '', newContent)
    }, 2000)
  }

  if (isLoading) {
    return <div className="flex items-center justify-center h-full">Cargando...</div>
  }

  if (!notebook) {
    return <div className="flex items-center justify-center h-full">Notebook no encontrado</div>
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="bg-catia-dark/50 border-b border-catia-purple/20 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/')}
            className="p-2 hover:bg-catia-purple/20 rounded-lg"
          >
            <ArrowLeft className="w-5 h-5 text-catia-light/70" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-catia-light">{notebook.name}</h1>
            <p className="text-sm text-catia-light/60">
              {documents.length} documentos • {messages.length} mensajes
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={openDocsModal}
            className="flex items-center gap-2 px-4 py-2 bg-catia-purple/20 hover:bg-catia-purple/30 rounded-lg text-catia-light/70 transition-colors"
          >
            <FileCode className="w-4 h-4" />
            <span className="text-sm">{documents.length} docs</span>
          </button>
          <button 
            onClick={() => setShowSettings(!showSettings)}
            className={`p-2 hover:bg-catia-purple/20 rounded-lg transition-colors ${
              showSettings ? 'bg-catia-purple/30 text-catia-purple' : 'text-catia-light/70'
            }`}
            title="Configuración LLM"
          >
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden gap-4 p-4">
        {/* Canvas */}
        <NotebookCanvas content={localContent} onChange={handleContentChange} />

        {/* Chat Sidebar or Settings */}
        {showSettings ? (
          <ChatSettings />
        ) : (
          <ChatSidebar
            messages={messages}
            onSendMessage={sendMessage}
            isSending={isSending}
            contextDocs={documents.length}
          />
        )}
      </div>

      {/* Documents Modal */}
      {isDocsModalOpen && <DocumentsModal notebook={notebook} onClose={closeDocsModal} />}
    </div>
  )
}
