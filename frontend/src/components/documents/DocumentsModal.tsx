import { Upload, X, Loader, Check } from 'lucide-react'
import { useDocuments } from '@hooks/useDocuments'
import type { Notebook } from '@types/index'
import { useRef, useState } from 'react'

interface DocumentsModalProps {
  notebook: Notebook
  onClose: () => void
}

export default function DocumentsModal({ notebook, onClose }: DocumentsModalProps) {
  const { documents, uploadDocument, isUploading, deleteDocument } = useDocuments(notebook.id)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
    }
  }

  const handleUpload = () => {
    if (selectedFile) {
      uploadDocument(selectedFile, {
        onSuccess: () => {
          setSelectedFile(null)
          if (fileInputRef.current) {
            fileInputRef.current.value = ''
          }
        },
      })
    }
  }

  const handleCancel = () => {
    setSelectedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-catia-dark border border-catia-purple/30 rounded-xl max-w-md w-full max-h-96 overflow-hidden flex flex-col">
        {/* Header */}
        <div className="border-b border-catia-purple/20 px-6 py-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-catia-light">Documentos</h2>
          <button onClick={onClose} className="text-catia-light/70 hover:text-catia-light">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {/* Upload Area */}
          {!selectedFile ? (
            <label className="border-2 border-dashed border-catia-purple/30 rounded-lg p-6 hover:border-catia-purple/60 cursor-pointer transition-colors block text-center">
              <Upload className="w-8 h-8 text-catia-gold/50 mx-auto mb-2" />
              <p className="text-sm text-catia-light/70">Arrastra archivos aquí o haz click</p>
              <input
                ref={fileInputRef}
                type="file"
                onChange={handleFileSelect}
                disabled={isUploading}
                className="hidden"
                accept=".pdf,.doc,.docx,.txt,.png,.jpg,.jpeg"
              />
              {isUploading && <Loader className="w-4 h-4 animate-spin mx-auto mt-2" />}
            </label>
          ) : (
            <div className="space-y-4">
              {/* Selected File Preview */}
              <div className="bg-catia-purple/20 border border-catia-purple/50 rounded-lg p-4">
                <div className="flex items-center gap-3 mb-3">
                  <Check className="w-5 h-5 text-catia-gold" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-catia-light truncate">
                      {selectedFile.name}
                    </p>
                    <p className="text-xs text-catia-light/70">
                      {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="space-y-2">
                  <button
                    onClick={handleUpload}
                    disabled={isUploading}
                    className="w-full bg-gradient-to-r from-catia-purple to-catia-pink hover:from-catia-purple/80 hover:to-catia-pink/80 disabled:opacity-50 text-white font-semibold py-2 rounded-lg transition-all flex items-center justify-center gap-2"
                  >
                    {isUploading ? (
                      <>
                        <Loader className="w-4 h-4 animate-spin" />
                        Subiendo...
                      </>
                    ) : (
                      <>
                        <Upload className="w-4 h-4" />
                        Confirmar subida
                      </>
                    )}
                  </button>
                  <button
                    onClick={handleCancel}
                    disabled={isUploading}
                    className="w-full bg-catia-dark/50 border border-catia-purple/30 hover:border-catia-purple/60 disabled:opacity-50 text-catia-light font-semibold py-2 rounded-lg transition-all"
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Documents List */}
          {documents.length > 0 && (
            <div className="space-y-2 border-t border-catia-purple/20 pt-4">
              <p className="text-xs text-catia-light/50 font-semibold">DOCUMENTOS CARGADOS</p>
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  className="bg-catia-dark/50 border border-catia-purple/20 rounded-lg p-3 flex items-center justify-between"
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-catia-light truncate">{doc.original_filename}</p>
                    <p className="text-xs text-catia-light/50">{doc.pages} páginas</p>
                  </div>
                  <button
                    onClick={() => deleteDocument(doc.id)}
                    className="ml-2 p-1 hover:bg-red-500/20 rounded text-red-400/70 hover:text-red-400"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
