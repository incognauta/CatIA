import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@hooks/useAuth'
import { Mail, Lock, Loader, User } from 'lucide-react'

export default function RegisterPage() {
  const navigate = useNavigate()
  const { register, isLoading, error } = useAuth()
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    passwordConfirm: '',
    username: '',
    firstName: '',
    lastName: '',
  })
  const [formError, setFormError] = useState('')

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setFormError('')

    // Validar que las contraseñas coincidan
    if (formData.password !== formData.passwordConfirm) {
      setFormError('Las contraseñas no coinciden')
      return
    }

    // Validar que todos los campos obligatorios estén llenos
    if (!formData.email || !formData.password || !formData.username) {
      setFormError('Por favor completa todos los campos obligatorios')
      return
    }

    register({
      email: formData.email,
      password: formData.password,
      password_confirm: formData.passwordConfirm,
      username: formData.username,
      first_name: formData.firstName,
      last_name: formData.lastName,
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-catia-dark via-catia-dark to-catia-purple/10 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2">
            <span className="bg-gradient-to-r from-catia-purple via-catia-pink to-catia-gold bg-clip-text text-transparent">
              🐱 CatIA
            </span>
          </h1>
          <p className="text-catia-light/60">Crea tu cuenta</p>
        </div>

        {/* Form */}
        <form
          onSubmit={handleSubmit}
          className="bg-catia-dark/50 border border-catia-purple/30 rounded-xl p-8 space-y-4 backdrop-blur-sm max-h-[80vh] overflow-y-auto"
        >
          {(error || formError) && (
            <div className="bg-red-500/20 border border-red-500/30 text-red-300 px-4 py-2 rounded-lg text-sm">
              {error || formError}
            </div>
          )}

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-catia-light mb-2">
              Email *
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 w-5 h-5 text-catia-gold/50" />
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full bg-catia-dark/50 border border-catia-purple/30 rounded-lg pl-10 pr-4 py-2.5 text-catia-light placeholder:text-catia-light/40 focus:outline-none focus:border-catia-purple focus:ring-1 focus:ring-catia-purple"
                placeholder="tu@email.com"
                required
              />
            </div>
          </div>

          {/* Username */}
          <div>
            <label className="block text-sm font-medium text-catia-light mb-2">
              Usuario *
            </label>
            <div className="relative">
              <User className="absolute left-3 top-3 w-5 h-5 text-catia-gold/50" />
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                className="w-full bg-catia-dark/50 border border-catia-purple/30 rounded-lg pl-10 pr-4 py-2.5 text-catia-light placeholder:text-catia-light/40 focus:outline-none focus:border-catia-purple focus:ring-1 focus:ring-catia-purple"
                placeholder="tunombre"
                required
              />
            </div>
          </div>

          {/* Nombre */}
          <div>
            <label className="block text-sm font-medium text-catia-light mb-2">
              Nombre
            </label>
            <input
              type="text"
              name="firstName"
              value={formData.firstName}
              onChange={handleChange}
              className="w-full bg-catia-dark/50 border border-catia-purple/30 rounded-lg px-4 py-2.5 text-catia-light placeholder:text-catia-light/40 focus:outline-none focus:border-catia-purple focus:ring-1 focus:ring-catia-purple"
              placeholder="Tu nombre"
            />
          </div>

          {/* Apellido */}
          <div>
            <label className="block text-sm font-medium text-catia-light mb-2">
              Apellido
            </label>
            <input
              type="text"
              name="lastName"
              value={formData.lastName}
              onChange={handleChange}
              className="w-full bg-catia-dark/50 border border-catia-purple/30 rounded-lg px-4 py-2.5 text-catia-light placeholder:text-catia-light/40 focus:outline-none focus:border-catia-purple focus:ring-1 focus:ring-catia-purple"
              placeholder="Tu apellido"
            />
          </div>

          {/* Password */}
          <div>
            <label className="block text-sm font-medium text-catia-light mb-2">
              Contraseña *
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 w-5 h-5 text-catia-gold/50" />
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="w-full bg-catia-dark/50 border border-catia-purple/30 rounded-lg pl-10 pr-4 py-2.5 text-catia-light placeholder:text-catia-light/40 focus:outline-none focus:border-catia-purple focus:ring-1 focus:ring-catia-purple"
                placeholder="••••••••"
                required
              />
            </div>
          </div>

          {/* Confirm Password */}
          <div>
            <label className="block text-sm font-medium text-catia-light mb-2">
              Confirmar contraseña *
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 w-5 h-5 text-catia-gold/50" />
              <input
                type="password"
                name="passwordConfirm"
                value={formData.passwordConfirm}
                onChange={handleChange}
                className="w-full bg-catia-dark/50 border border-catia-purple/30 rounded-lg pl-10 pr-4 py-2.5 text-catia-light placeholder:text-catia-light/40 focus:outline-none focus:border-catia-purple focus:ring-1 focus:ring-catia-purple"
                placeholder="••••••••"
                required
              />
            </div>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-catia-purple to-catia-pink hover:from-catia-purple/80 hover:to-catia-pink/80 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-2.5 rounded-lg transition-all flex items-center justify-center gap-2 mt-6"
          >
            {isLoading && <Loader className="w-4 h-4 animate-spin" />}
            {isLoading ? 'Creando cuenta...' : 'Registrarse'}
          </button>

          {/* Footer */}
          <p className="text-center text-sm text-catia-light/50">
            ¿Ya tienes cuenta?{' '}
            <button
              type="button"
              onClick={() => navigate('/login')}
              className="text-catia-purple hover:text-catia-pink transition-colors"
            >
              Inicia sesión
            </button>
          </p>
        </form>
      </div>
    </div>
  )
}
