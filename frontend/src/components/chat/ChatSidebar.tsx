import { Send, Loader } from 'lucide-react'
import ChatMessage from './ChatMessage'
import type { ChatMessage as ChatMessageType } from '@types/index'
import { useRef, useEffect, useState } from 'react'

interface ChatSidebarProps {
  messages: ChatMessageType[]
  onSendMessage: (data: { message: string; systemPrompt?: string }) => void
  isSending: boolean
  contextDocs: number
}

export default function ChatSidebar({
  messages,
  onSendMessage,
  isSending,
  contextDocs,
}: ChatSidebarProps) {
  const [input, setInput] = useState('')
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = () => {
    if (!input.trim()) return
    onSendMessage({ message: input })
    setInput('')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="w-96 bg-catia-dark/50 border border-catia-purple/20 rounded-xl overflow-hidden flex flex-col">
      {/* Header */}
      <div className="border-b border-catia-purple/20 px-4 py-3 bg-catia-dark/30">
        <h2 className="font-semibold text-catia-light flex items-center gap-2">
          💬 Chat
          {contextDocs > 0 && (
            <span className="text-xs bg-catia-gold/20 text-catia-gold px-2 py-1 rounded">
              {contextDocs} docs
            </span>
          )}
        </h2>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 p-4">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <p className="text-center text-catia-light/50 text-sm">
              Haz tu primera pregunta 👋
            </p>
          </div>
        ) : (
          messages.map((msg) => <ChatMessage key={msg.id} message={msg} />)
        )}
        {isSending && (
          <div className="flex justify-center py-2">
            <Loader className="w-4 h-4 animate-spin text-catia-purple" />
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      {/* Input */}
      <div className="border-t border-catia-purple/20 p-4 bg-catia-dark/30 space-y-2">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Escribe una pregunta..."
          className="w-full bg-catia-dark/50 border border-catia-purple/30 rounded-lg px-3 py-2 text-catia-light placeholder:text-catia-light/40 resize-none focus:outline-none focus:border-catia-purple text-sm max-h-24"
          rows={3}
        />
        <button
          onClick={handleSend}
          disabled={isSending || !input.trim()}
          className="w-full bg-catia-purple hover:bg-catia-purple/80 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-2 rounded-lg flex items-center justify-center gap-2 transition-colors"
        >
          {isSending ? (
            <>
              <Loader className="w-4 h-4 animate-spin" />
              Enviando...
            </>
          ) : (
            <>
              <Send className="w-4 h-4" />
              Enviar
            </>
          )}
        </button>
      </div>
    </div>
  )
}
