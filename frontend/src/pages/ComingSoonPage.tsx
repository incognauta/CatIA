import { useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'

export default function ComingSoonPage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gradient-to-br from-catia-dark via-catia-dark to-catia-purple/10 flex items-center justify-center p-4">
      <div className="max-w-md w-full text-center space-y-8">
        {/* Gato animado */}
        <div className="flex justify-center">
          <div className="text-8xl animate-bounce">
            🐱
          </div>
        </div>

        {/* Contenido */}
        <div className="space-y-4">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-catia-purple via-catia-pink to-catia-gold bg-clip-text text-transparent">
            Área en construcción
          </h1>
          
          <p className="text-catia-light/70 text-lg">
            Estamos trabajando duro para traerte nuevas funcionalidades increíbles. Por favor, vuelve más tarde.
          </p>

          <div className="pt-4 space-y-3">
            <div className="text-6xl opacity-50">🔨⚙️🔧</div>
            <p className="text-sm text-catia-light/50">
              Los mejores desarrolladores están en ello
            </p>
          </div>
        </div>

        {/* Botón para volver */}
        <button
          onClick={() => navigate('/')}
          className="w-full bg-gradient-to-r from-catia-purple to-catia-pink hover:from-catia-purple/80 hover:to-catia-pink/80 text-white font-semibold py-3 rounded-lg transition-all flex items-center justify-center gap-2 group"
        >
          <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
          Volver al inicio
        </button>

        {/* Footer */}
        <p className="text-xs text-catia-light/40">
          Mientras tanto, explora tus notebooks 📓
        </p>
      </div>
    </div>
  )
}
