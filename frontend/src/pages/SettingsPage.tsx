import { useState } from 'react'
import { useAuthStore } from '@stores/authStore'
import { useLLMSettings } from '@hooks/useLLMSettings'
import { Save, Mail, User, Lock, Zap } from 'lucide-react'

export default function SettingsPage() {
  const { user } = useAuthStore()
  const { settings, defaults, loading, error, saving, updateSettings } = useLLMSettings()
  
  // Profile state
  const [profileChanged, setProfileChanged] = useState(false)
  const [profileForm, setProfileForm] = useState({
    username: user?.username || '',
    email: user?.email || '',
    bio: '',
  })

  // LLM state
  const [llmForm, setLlmForm] = useState({
    model: settings?.model || '',
    temperature: settings?.temperature || 0.7,
    maxTokens: settings?.maxTokens || 1024,
  })

  const handleProfileChange = (field: string, value: string) => {
    setProfileForm(prev => ({ ...prev, [field]: value }))
    setProfileChanged(true)
  }

  const handleLLMChange = (field: string, value: any) => {
    setLlmForm(prev => ({ ...prev, [field]: value }))
  }

  const handleSaveProfile = () => {
    // TODO: Implement profile update API call
    console.log('Saving profile:', profileForm)
    setProfileChanged(false)
  }

  const handleSaveLLM = async () => {
    try {
      await updateSettings({
        model: llmForm.model,
        temperature: llmForm.temperature,
        maxTokens: llmForm.maxTokens,
      })
    } catch (err) {
      console.error('Error updating LLM settings:', err)
    }
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-catia-light mb-2">Configuración</h1>
        <p className="text-catia-light/60">Personaliza tu perfil y preferencias de IA</p>
      </div>

      {/* Profile Section */}
      <div className="bg-catia-dark/40 border border-catia-purple/20 rounded-xl p-6 mb-8">
        <div className="flex items-center gap-3 mb-6">
          <User className="w-6 h-6 text-catia-purple" />
          <h2 className="text-2xl font-bold text-catia-light">Perfil</h2>
        </div>

        <div className="space-y-4">
          {/* Username */}
          <div>
            <label className="block text-catia-light text-sm font-semibold mb-2">Usuario</label>
            <input
              type="text"
              value={profileForm.username}
              onChange={(e) => handleProfileChange('username', e.target.value)}
              className="w-full bg-catia-dark/50 border border-catia-purple/30 rounded-lg px-4 py-2 text-catia-light placeholder:text-catia-light/40 focus:outline-none focus:border-catia-purple"
            />
          </div>

          {/* Email */}
          <div>
            <label className="block text-catia-light text-sm font-semibold mb-2 flex items-center gap-2">
              <Mail className="w-4 h-4" />
              Email
            </label>
            <input
              type="email"
              value={profileForm.email}
              onChange={(e) => handleProfileChange('email', e.target.value)}
              className="w-full bg-catia-dark/50 border border-catia-purple/30 rounded-lg px-4 py-2 text-catia-light placeholder:text-catia-light/40 focus:outline-none focus:border-catia-purple"
            />
            <p className="text-catia-light/50 text-sm mt-2">Tu email verificado</p>
          </div>

          {/* Bio */}
          <div>
            <label className="block text-catia-light text-sm font-semibold mb-2">Biografía</label>
            <textarea
              value={profileForm.bio}
              onChange={(e) => handleProfileChange('bio', e.target.value)}
              placeholder="Cuéntanos sobre ti..."
              rows={3}
              className="w-full bg-catia-dark/50 border border-catia-purple/30 rounded-lg px-4 py-2 text-catia-light placeholder:text-catia-light/40 focus:outline-none focus:border-catia-purple resize-none"
            />
          </div>

          {/* Subscription */}
          <div>
            <label className="block text-catia-light text-sm font-semibold mb-2">Plan de Suscripción</label>
            <div className="bg-catia-dark/50 border border-catia-purple/20 rounded-lg px-4 py-2">
              <p className="text-catia-light capitalize">{user?.subscription_tier || 'free'}</p>
              <p className="text-catia-light/50 text-sm mt-1">Acceso completo a todas las funciones</p>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex justify-end pt-4">
            <button
              onClick={handleSaveProfile}
              disabled={!profileChanged}
              className="bg-catia-purple hover:bg-catia-purple/80 disabled:bg-catia-purple/40 disabled:cursor-not-allowed text-white px-6 py-2 rounded-lg font-semibold flex items-center gap-2 transition-colors"
            >
              <Save className="w-4 h-4" />
              Guardar Cambios
            </button>
          </div>
        </div>
      </div>

      {/* LLM Settings Section */}
      <div className="bg-catia-dark/40 border border-catia-purple/20 rounded-xl p-6">
        <div className="flex items-center gap-3 mb-6">
          <Zap className="w-6 h-6 text-catia-gold" />
          <h2 className="text-2xl font-bold text-catia-light">Configuración de IA</h2>
        </div>

        {loading ? (
          <p className="text-catia-light/60">Cargando configuración...</p>
        ) : error ? (
          <p className="text-red-400">Error: {error}</p>
        ) : (
          <div className="space-y-6">
            {/* Model Selection */}
            <div>
              <label className="block text-catia-light text-sm font-semibold mb-2">Modelo de IA</label>
              <select
                value={llmForm.model}
                onChange={(e) => handleLLMChange('model', e.target.value)}
                className="w-full bg-catia-dark/50 border border-catia-purple/30 rounded-lg px-4 py-2 text-catia-light focus:outline-none focus:border-catia-purple"
              >
                <option value="">Seleccionar modelo...</option>
                {defaults?.available_models?.map(m => (
                  <option key={m.value} value={m.value}>{m.label}</option>
                ))}
              </select>
              <p className="text-catia-light/50 text-sm mt-2">Modelo utilizado para generar respuestas</p>
            </div>

            {/* Temperature Slider */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-catia-light text-sm font-semibold">Creatividad (Temperatura)</label>
                <span className="bg-catia-purple/30 text-catia-light px-3 py-1 rounded text-sm">{llmForm.temperature.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min={defaults?.temperature_range?.min || 0}
                max={defaults?.temperature_range?.max || 1}
                step={defaults?.temperature_range?.step || 0.1}
                value={llmForm.temperature}
                onChange={(e) => handleLLMChange('temperature', parseFloat(e.target.value))}
                className="w-full h-2 bg-catia-dark/50 rounded-lg appearance-none cursor-pointer accent-catia-purple"
              />
              <div className="flex justify-between text-catia-light/40 text-xs mt-2">
                <span>Determinístico (preciso)</span>
                <span>Creativo (variado)</span>
              </div>
              <p className="text-catia-light/50 text-sm mt-2">Valores más altos = respuestas más creativas</p>
            </div>

            {/* Max Tokens Slider */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-catia-light text-sm font-semibold">Máximo de Tokens</label>
                <span className="bg-catia-purple/30 text-catia-light px-3 py-1 rounded text-sm">{llmForm.maxTokens}</span>
              </div>
              <input
                type="range"
                min={defaults?.max_tokens_range?.min || 512}
                max={defaults?.max_tokens_range?.max || 4096}
                step={defaults?.max_tokens_range?.step || 256}
                value={llmForm.maxTokens}
                onChange={(e) => handleLLMChange('maxTokens', parseInt(e.target.value))}
                className="w-full h-2 bg-catia-dark/50 rounded-lg appearance-none cursor-pointer accent-catia-gold"
              />
              <p className="text-catia-light/50 text-sm mt-2">Longitud máxima de las respuestas generadas</p>
            </div>

            {/* Preview */}
            <div className="bg-catia-dark/50 border border-catia-purple/20 rounded-lg p-4">
              <p className="text-catia-light/70 text-sm mb-3 font-semibold">Vista Previa de Configuración:</p>
              <div className="space-y-2 text-sm text-catia-light/60">
                <p>• Modelo: <span className="text-catia-light">{llmForm.model || 'No seleccionado'}</span></p>
                <p>• Temperatura: <span className="text-catia-light">{llmForm.temperature.toFixed(2)}</span></p>
                <p>• Máx Tokens: <span className="text-catia-light">{llmForm.maxTokens}</span></p>
              </div>
            </div>

            {/* Save Button */}
            <div className="flex justify-end">
              <button
                onClick={handleSaveLLM}
                disabled={saving}
                className="bg-catia-gold hover:bg-catia-gold/80 disabled:bg-catia-gold/40 disabled:cursor-not-allowed text-catia-dark px-6 py-2 rounded-lg font-semibold flex items-center gap-2 transition-colors"
              >
                <Save className="w-4 h-4" />
                {saving ? 'Guardando...' : 'Guardar Configuración'}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Security Section */}
      <div className="bg-catia-dark/40 border border-catia-purple/20 rounded-xl p-6 mt-8">
        <div className="flex items-center gap-3 mb-6">
          <Lock className="w-6 h-6 text-red-500" />
          <h2 className="text-2xl font-bold text-catia-light">Seguridad</h2>
        </div>

        <div className="space-y-4">
          <button className="w-full bg-catia-dark/50 border border-catia-purple/30 hover:bg-catia-dark/70 text-catia-light px-4 py-3 rounded-lg font-semibold transition-colors">
            Cambiar Contraseña
          </button>
          <button className="w-full bg-red-500/20 border border-red-500/30 hover:bg-red-500/30 text-red-400 px-4 py-3 rounded-lg font-semibold transition-colors">
            Eliminar Cuenta
          </button>
        </div>
      </div>
    </div>
  )
}
