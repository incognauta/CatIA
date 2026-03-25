import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useNotebooks } from '@hooks/useNotebooks'
import { Plus, Loader } from 'lucide-react'

export default function DashboardPage() {
  const navigate = useNavigate()
  const { notebooks, isLoading, createNotebook, isCreating } = useNotebooks()
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [title, setTitle] = useState('')

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim()) return

    createNotebook(
      { name: title },
      {
        onSuccess: () => {
          setTitle('')
          setShowCreateForm(false)
        },
      }
    )
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-catia-light mb-2">Mis Notebooks</h1>
        <p className="text-catia-light/60">Organiza y gestiona tus documentos</p>
      </div>

      {/* Create Form */}
      {showCreateForm && (
        <div className="bg-catia-dark/50 border border-catia-purple/30 rounded-xl p-6 mb-8">
          <form onSubmit={handleCreate} className="flex gap-4">
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Nombre del notebook..."
              className="flex-1 bg-catia-dark/50 border border-catia-purple/30 rounded-lg px-4 py-2 text-catia-light placeholder:text-catia-light/40 focus:outline-none focus:border-catia-purple"
            />
            <button
              type="submit"
              disabled={isCreating}
              className="bg-catia-purple hover:bg-catia-purple/80 text-white px-6 py-2 rounded-lg font-semibold disabled:opacity-50 flex items-center gap-2"
            >
              {isCreating && <Loader className="w-4 h-4 animate-spin" />}
              Crear
            </button>
            <button
              type="button"
              onClick={() => setShowCreateForm(false)}
              className="bg-catia-dark/50 border border-catia-purple/30 text-catia-light px-6 py-2 rounded-lg hover:bg-catia-dark transition-colors"
            >
              Cancelar
            </button>
          </form>
        </div>
      )}

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Create Card */}
        {!showCreateForm && (
          <button
            onClick={() => setShowCreateForm(true)}
            className="bg-catia-dark/30 border-2 border-dashed border-catia-purple/30 rounded-xl p-8 hover:border-catia-purple/60 hover:bg-catia-dark/50 transition-all group cursor-pointer"
          >
            <div className="flex flex-col items-center gap-4">
              <Plus className="w-12 h-12 text-catia-gold group-hover:scale-110 transition-transform" />
              <p className="text-catia-light/70 font-semibold">Crear Notebook</p>
            </div>
          </button>
        )}

        {/* Notebook Cards */}
        {isLoading ? (
          <div className="col-span-full flex justify-center py-12">
            <Loader className="w-8 h-8 animate-spin text-catia-purple" />
          </div>
        ) : notebooks.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <p className="text-catia-light/60">No tienes notebooks aún</p>
          </div>
        ) : (
          notebooks.map((notebook) => (
            <button
              key={notebook.id}
              onClick={() => navigate(`/notebook/${notebook.id}`)}
              className="bg-catia-dark/50 border border-catia-purple/30 rounded-xl p-6 hover:border-catia-purple hover:bg-catia-dark/70 transition-all text-left group"
            >
              <h3 className="text-lg font-semibold text-catia-light group-hover:text-catia-gold transition-colors">
                {notebook.name}
              </h3>
              <p className="text-sm text-catia-light/60 mt-2">
                {notebook.documents_count || 0} documentos
              </p>
              <p className="text-xs text-catia-light/40 mt-1">
                {notebook.messages_count || 0} mensajes
              </p>
            </button>
          ))
        )}
      </div>
    </div>
  )
}
