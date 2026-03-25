import { ChangeEvent, useEffect, useState, useRef } from 'react'
import { Type, CheckCircle } from 'lucide-react'

interface NotebookCanvasProps {
  content: string
  onChange: (content: string) => void
}

export default function NotebookCanvas({ content, onChange }: NotebookCanvasProps) {
  const [isSaving, setIsSaving] = useState(false)
  const [lastSaved, setLastSaved] = useState<Date | null>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    onChange(e.target.value)
    setIsSaving(true)
  }

  // Simulate save completion after onChange is called by parent
  useEffect(() => {
    if (isSaving) {
      const timer = setTimeout(() => {
        setIsSaving(false)
        setLastSaved(new Date())
      }, 2000)
      return () => clearTimeout(timer)
    }
  }, [isSaving, content])

  const formatTime = (date: Date | null) => {
    if (!date) return 'Guardando...'
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffSecs = Math.floor(diffMs / 1000)
    const diffMins = Math.floor(diffSecs / 60)

    if (diffSecs < 60) return 'Justo ahora'
    if (diffMins < 60) return `Hace ${diffMins} min`
    return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
  }

  const insertFormat = (before: string, after: string) => {
    const textarea = textareaRef.current
    if (!textarea) return

    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const selectedText = content.substring(start, end)
    const beforeText = content.substring(0, start)
    const afterText = content.substring(end)

    let newContent: string
    let newCursorPos: number

    if (selectedText.length > 0) {
      // Hay texto seleccionado - envolverlo
      newContent = beforeText + before + selectedText + after + afterText
      newCursorPos = start + before.length + selectedText.length + after.length
    } else {
      // No hay selección - crear espacio para escribir
      newContent = beforeText + before + after + afterText
      newCursorPos = start + before.length
    }

    onChange(newContent)

    // Restaurar posición del cursor después de que React actualice
    setTimeout(() => {
      textarea.selectionStart = newCursorPos
      textarea.selectionEnd = newCursorPos
      textarea.focus()
    }, 0)
  }

  return (
    <div className="flex-1 bg-catia-dark/50 border border-catia-purple/20 rounded-xl overflow-hidden flex flex-col">
      {/* Toolbar */}
      <div className="border-b border-catia-purple/20 px-4 py-3 flex items-center gap-2 bg-catia-dark/30">
        <Type className="w-4 h-4 text-catia-gold" />
        <button
          onClick={() => insertFormat('**', '**')}
          className="px-3 py-1 text-sm hover:bg-catia-purple/20 rounded text-catia-light/70 transition-colors"
          title="Negrita (o selecciona texto)"
        >
          **Bold**
        </button>
        <button
          onClick={() => insertFormat('*', '*')}
          className="px-3 py-1 text-sm hover:bg-catia-purple/20 rounded text-catia-light/70 transition-colors"
          title="Cursiva (o selecciona texto)"
        >
          *Italic*
        </button>
        <button
          onClick={() => insertFormat('`', '`')}
          className="px-3 py-1 text-sm hover:bg-catia-purple/20 rounded text-catia-light/70 transition-colors"
          title="Código (o selecciona texto)"
        >
          `Code`
        </button>
      </div>

      {/* Editor */}
      <textarea
        ref={textareaRef}
        value={content}
        onChange={handleChange}
        placeholder="Escribe aquí tus notas en Markdown. Usa las herramientas de arriba para formatear."
        className="flex-1 bg-transparent text-catia-light placeholder:text-catia-light/30 p-4 resize-none focus:outline-none font-mono text-sm"
      />

      {/* Status */}
      <div className="border-t border-catia-purple/20 px-4 py-2 bg-catia-dark/30 text-xs text-catia-light/50 flex items-center justify-between">
        <span>{content.length} caracteres</span>
        <div className="flex items-center gap-2">
          {isSaving ? (
            <span className="animate-pulse">Guardando...</span>
          ) : lastSaved ? (
            <div className="flex items-center gap-1 text-catia-gold">
              <CheckCircle className="w-3 h-3" />
              <span>Guardado {formatTime(lastSaved)}</span>
            </div>
          ) : (
            <span>Listo para guardar</span>
          )}
        </div>
      </div>
    </div>
  )
}
