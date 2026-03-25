import { FileText } from 'lucide-react'
import type { ChatMessage as ChatMessageType } from '@types/index'

interface ChatMessageProps {
  message: ChatMessageType
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isAssistant = message.role === 'assistant'

  return (
    <div className={`flex ${isAssistant ? 'justify-start' : 'justify-end'}`}>
      <div
        className={`max-w-xs px-4 py-3 rounded-lg ${
          isAssistant
            ? 'bg-catia-purple/30 text-catia-light'
            : 'bg-catia-pink/30 text-catia-light'
        }`}
      >
        {/* Content */}
        <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>

        {/* Context badge */}
        {isAssistant && message.tokens_used > 0 && (
          <div className="flex items-center gap-1 mt-2 text-xs text-catia-gold/70">
            <FileText className="w-3 h-3" />
            <span>{message.tokens_used} tokens</span>
          </div>
        )}

        {/* Timestamp */}
        <p className="text-xs opacity-50 mt-1">
          {new Date(message.created_at).toLocaleTimeString()}
        </p>
      </div>
    </div>
  )
}
