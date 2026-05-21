import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useNotebooks } from '@hooks/useNotebooks'
import { apiClient } from '@api/client'
import { File, Calendar, HardDrive, Download, Trash2, Search, ChevronDown, Folder } from 'lucide-react'
import type { Document, Notebook } from '@types/index'

interface DocumentsByNotebook {
  notebook: Notebook
  documents: Document[]
}

export default function DocsPage() {
  const { t, i18n } = useTranslation()
  const { notebooks, isLoading: notebooksLoading } = useNotebooks()
  const [allDocuments, setAllDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [expandedNotebooks, setExpandedNotebooks] = useState<Set<string>>(new Set())
  const [sortBy, setSortBy] = useState<'date' | 'name' | 'size'>('date')

  // Fetch all documents
  useEffect(() => {
    const fetchAllDocuments = async () => {
      try {
        setLoading(true)
        const response = await apiClient.get('/documents/')
        const docs = response.data.results || []
        console.log('Fetched documents:', docs)
        console.log('Notebooks available:', notebooks)
        setAllDocuments(docs)
      } catch (error) {
        console.error('Error fetching documents:', error)
        setAllDocuments([])
      } finally {
        setLoading(false)
      }
    }

    if (notebooks.length > 0 || !notebooksLoading) {
      fetchAllDocuments()
    }
  }, [notebooksLoading])

  // Group documents by notebook
  const documentsByNotebook: DocumentsByNotebook[] = notebooks
    .map(notebook => ({
      notebook,
      documents: allDocuments.filter(doc => String(doc.notebook) === String(notebook.id)),
    }))
    .filter(item => item.documents.length > 0)

  // Find ungrouped documents (those not in any notebook)
  const groupedNotebookIds = new Set(documentsByNotebook.flatMap(item => 
    item.documents.map(doc => String(doc.notebook))
  ))
  const ungroupedDocuments = allDocuments.filter(doc => 
    !groupedNotebookIds.has(String(doc.notebook))
  )

  // Filter documents by search term
  const filteredByNotebook = documentsByNotebook.map(item => ({
    ...item,
    documents: item.documents.filter(doc =>
      doc?.original_filename?.toLowerCase?.().includes(searchTerm.toLowerCase()) ?? true
    ),
  })).filter(item => item.documents.length > 0)

  const filteredUngroupedDocuments = ungroupedDocuments.filter(doc =>
    doc?.original_filename?.toLowerCase?.().includes(searchTerm.toLowerCase()) ?? true
  )

  // Sort documents
  const sortedDocuments = (docs: Document[]) => {
    const sorted = [...docs]
    if (sortBy === 'date') {
      sorted.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    } else if (sortBy === 'name') {
      sorted.sort((a, b) => a.original_filename.localeCompare(b.original_filename))
    } else if (sortBy === 'size') {
      sorted.sort((a, b) => b.file_size - a.file_size)
    }
    return sorted
  }

  const toggleNotebook = (notebookId: string) => {
    const newExpanded = new Set(expandedNotebooks)
    if (newExpanded.has(notebookId)) {
      newExpanded.delete(notebookId)
    } else {
      newExpanded.add(notebookId)
    }
    setExpandedNotebooks(newExpanded)
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
  }

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString)
    const lang = i18n?.language || 'es'
    return new Intl.DateTimeFormat(lang === 'en' ? 'en-US' : 'es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date)
  }

  const getFileIcon = (fileType: string) => {
    const iconProps = 'w-4 h-4'
    switch (fileType) {
      case 'pdf':
        return <File className={`${iconProps} text-red-500`} />
      case 'docx':
        return <File className={`${iconProps} text-blue-500`} />
      case 'txt':
        return <File className={`${iconProps} text-gray-500`} />
      case 'image':
        return <File className={`${iconProps} text-green-500`} />
      default:
        return <File className={`${iconProps} text-catia-light/50`} />
    }
  }

  const totalDocuments = allDocuments.length
  const totalSize = allDocuments.reduce((sum, doc) => sum + doc.file_size, 0)

  if (notebooksLoading && loading) {
    return (
      <div className="p-8 max-w-7xl mx-auto">
        <div className="flex items-center justify-center h-96">
          <p className="text-catia-light/60">{t('docs.loading')}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-catia-light mb-2">{t('docs.title')}</h1>
        <p className="text-catia-light/60">{t('docs.subtitle')}</p>
      </div>

      {/* Statistics */}
      {totalDocuments > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          <div className="bg-catia-dark/40 border border-catia-purple/20 rounded-xl p-6">
            <div className="flex items-center gap-3">
              <File className="w-8 h-8 text-catia-purple" />
              <div>
                <p className="text-catia-light/60 text-sm">{t('docs.totalDocuments')}</p>
                <p className="text-2xl font-bold text-catia-light">{totalDocuments}</p>
              </div>
            </div>
          </div>
          <div className="bg-catia-dark/40 border border-catia-purple/20 rounded-xl p-6">
            <div className="flex items-center gap-3">
              <HardDrive className="w-8 h-8 text-catia-gold" />
              <div>
                <p className="text-catia-light/60 text-sm">{t('docs.totalSpace')}</p>
                <p className="text-2xl font-bold text-catia-light">{formatFileSize(totalSize)}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Search and Sort */}
      <div className="flex flex-col md:flex-row gap-4 mb-8">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-3 w-5 h-5 text-catia-light/40" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder={t('docs.search')}
            className="w-full bg-catia-dark/50 border border-catia-purple/30 rounded-lg pl-10 pr-4 py-2 text-catia-light placeholder:text-catia-light/40 focus:outline-none focus:border-catia-purple"
          />
        </div>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as any)}
          className="bg-catia-dark/50 border border-catia-purple/30 rounded-lg px-4 py-2 text-catia-light focus:outline-none focus:border-catia-purple"
        >
          <option value="date">{t('docs.sortByDate')}</option>
          <option value="name">{t('docs.sortByName')}</option>
          <option value="size">{t('docs.sortBySize')}</option>
        </select>
      </div>

      {/* Documents by Notebook */}
      {allDocuments.length === 0 ? (
        <div className="bg-catia-dark/40 border border-catia-purple/20 rounded-xl p-12 text-center">
          <File className="w-16 h-16 text-catia-purple/30 mx-auto mb-4" />
          <h3 className="text-catia-light font-semibold mb-2">
            {searchTerm ? t('docs.notFound') : t('docs.noDocuments')}
          </h3>
          <p className="text-catia-light/60">
            {searchTerm
              ? t('docs.notFoundDesc')
              : t('docs.noDocumentsDesc')}
          </p>
        </div>
      ) : (
        <>
          {/* Grouped Documents */}
          {filteredByNotebook.length > 0 && (
            <div className="space-y-4 mb-8">
              {filteredByNotebook.map(({ notebook, documents }) => (
            <div key={notebook.id} className="bg-catia-dark/40 border border-catia-purple/20 rounded-xl overflow-hidden">
              {/* Notebook Header */}
              <button
                onClick={() => toggleNotebook(notebook.id)}
                className="w-full flex items-center gap-3 p-6 hover:bg-catia-dark/60 transition-colors"
              >
                <ChevronDown
                  className={`w-5 h-5 text-catia-purple transition-transform ${
                    expandedNotebooks.has(notebook.id) ? 'rotate-180' : ''
                  }`}
                />
                <Folder className="w-5 h-5 text-catia-gold" />
                <div className="flex-1 text-left">
                  <h3 className="text-catia-light font-semibold">{notebook.name}</h3>
                  <p className="text-catia-light/50 text-sm">{documents.length} {t('docs.documents')}</p>
                </div>
                {notebook.description && (
                  <p className="text-catia-light/60 text-sm hidden md:block">{notebook.description}</p>
                )}
              </button>

              {/* Documents List */}
              {expandedNotebooks.has(notebook.id) && (
                <div className="border-t border-catia-purple/10">
                  <div className="divide-y divide-catia-purple/10">
                    {sortedDocuments(documents).map(doc => (
                      <div key={doc.id} className="p-6 hover:bg-catia-dark/50 transition-colors">
                        <div className="flex items-start gap-4">
                          {/* File Icon */}
                          <div className="flex-shrink-0 mt-1">
                            {getFileIcon(doc.file_type)}
                          </div>

                          {/* File Info */}
                          <div className="flex-1 min-w-0">
                            <h4 className="text-catia-light font-semibold truncate">
                              {doc.original_filename}
                            </h4>
                            <div className="flex flex-wrap gap-4 mt-2 text-sm text-catia-light/60">
                              <div className="flex items-center gap-1">
                                <HardDrive className="w-4 h-4" />
                                {formatFileSize(doc.file_size)}
                              </div>
                              <div className="flex items-center gap-1">
                                <Calendar className="w-4 h-4" />
                                {formatDate(doc.created_at)}
                              </div>
                              {doc.pages > 0 && (
                                <div className="flex items-center gap-1">
                                  <File className="w-4 h-4" />
                                  {doc.pages} {t('docs.documents')}
                                </div>
                              )}
                              {doc.is_scanned && (
                                <span className="px-2 py-1 bg-catia-purple/20 text-catia-light/80 rounded text-xs">
                                  Escaneado (OCR)
                                </span>
                              )}
                            </div>
                          </div>

                          {/* Actions */}
                          <div className="flex gap-2 flex-shrink-0">
                            <button
                              className="p-2 hover:bg-catia-dark/50 rounded-lg transition-colors text-catia-light/60 hover:text-catia-gold"
                              title="Descargar"
                            >
                              <Download className="w-4 h-4" />
                            </button>
                            <button
                              className="p-2 hover:bg-catia-dark/50 rounded-lg transition-colors text-catia-light/60 hover:text-red-500"
                              title="Eliminar"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>

                        {/* Content Preview */}
                        {doc.content && doc.content.length > 0 && (
                          <div className="mt-4 pt-4 border-t border-catia-purple/10">
                            <p className="text-catia-light/50 text-xs font-semibold mb-2">Preview:</p>
                            <p className="text-catia-light/60 text-sm line-clamp-2">
                              {doc.content.substring(0, 150)}...
                            </p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
            </div>
          )}

          {/* Ungrouped Documents Section */}
          {filteredUngroupedDocuments.length > 0 && (
            <div className="bg-catia-dark/40 border border-catia-purple/20 rounded-xl overflow-hidden">
              {/* Header */}
              <div className="p-6 bg-catia-dark/60">
                <h3 className="text-catia-light font-semibold flex items-center gap-2">
                  <Folder className="w-5 h-5 text-yellow-500" />
                  {t('docs.title')}
                </h3>
                <p className="text-catia-light/50 text-sm mt-1">
                  {filteredUngroupedDocuments.length} {t('docs.documents')}
                </p>
              </div>

              {/* Documents */}
              <div className="divide-y divide-catia-purple/10">
                {sortedDocuments(filteredUngroupedDocuments).map(doc => (
                  <div key={doc.id} className="p-6 hover:bg-catia-dark/50 transition-colors">
                    <div className="flex items-start gap-4">
                      {/* File Icon */}
                      <div className="flex-shrink-0 mt-1">
                        {getFileIcon(doc.file_type)}
                      </div>

                      {/* File Info */}
                      <div className="flex-1 min-w-0">
                        <h4 className="text-catia-light font-semibold truncate">
                          {doc.original_filename}
                        </h4>
                        <div className="flex flex-wrap gap-4 mt-2 text-sm text-catia-light/60">
                          <div className="flex items-center gap-1">
                            <HardDrive className="w-4 h-4" />
                            {formatFileSize(doc.file_size)}
                          </div>
                          <div className="flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            {formatDate(doc.created_at)}
                          </div>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex gap-2 flex-shrink-0">
                        <button
                          className="p-2 hover:bg-catia-dark/50 rounded-lg transition-colors text-catia-light/60 hover:text-catia-gold"
                          title="Descargar"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                        <button
                          className="p-2 hover:bg-catia-dark/50 rounded-lg transition-colors text-catia-light/60 hover:text-red-500"
                          title="Eliminar"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Show message if search filtered everything */}
          {filteredByNotebook.length === 0 && filteredUngroupedDocuments.length === 0 && searchTerm && (
            <div className="bg-catia-dark/40 border border-catia-purple/20 rounded-xl p-12 text-center">
              <File className="w-16 h-16 text-catia-purple/30 mx-auto mb-4" />
              <h3 className="text-catia-light font-semibold mb-2">{t('docs.notFound')}</h3>
              <p className="text-catia-light/60">{t('docs.notFoundDesc')}</p>
            </div>
          )}
        </>
      )}

    </div>
  )
}
