import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@hooks/useAuth'
import { Mail, Lock, Loader } from 'lucide-react'

export default function LoginPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { login, isLoading, error } = useAuth()
  const [email, setEmail] = useState('testuser@example.com')
  const [password, setPassword] = useState('testpass123')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    login({ email, password })
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
          <p className="text-catia-light/60">{t('auth.subtitle')}</p>
        </div>

        {/* Form */}
        <form
          onSubmit={handleSubmit}
          className="bg-catia-dark/50 border border-catia-purple/30 rounded-xl p-8 space-y-6 backdrop-blur-sm"
        >
          {error && (
            <div className="bg-red-500/20 border border-red-500/30 text-red-300 px-4 py-2 rounded-lg text-sm">
              {t('auth.loginError')}
            </div>
          )}

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-catia-light mb-2">
              {t('auth.email')}
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 w-5 h-5 text-catia-gold/50" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-catia-dark/50 border border-catia-purple/30 rounded-lg pl-10 pr-4 py-2.5 text-catia-light placeholder:text-catia-light/40 focus:outline-none focus:border-catia-purple focus:ring-1 focus:ring-catia-purple"
                placeholder="tu@email.com"
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label className="block text-sm font-medium text-catia-light mb-2">
              {t('auth.password')}
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 w-5 h-5 text-catia-gold/50" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-catia-dark/50 border border-catia-purple/30 rounded-lg pl-10 pr-4 py-2.5 text-catia-light placeholder:text-catia-light/40 focus:outline-none focus:border-catia-purple focus:ring-1 focus:ring-catia-purple"
                placeholder="••••••••"
              />
            </div>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-catia-purple to-catia-pink hover:from-catia-purple/80 hover:to-catia-pink/80 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-2.5 rounded-lg transition-all flex items-center justify-center gap-2"
          >
            {isLoading && <Loader className="w-4 h-4 animate-spin" />}
            {isLoading ? t('auth.loggingIn') : t('auth.login')}
          </button>

          {/* Footer */}
          <p className="text-center text-sm text-catia-light/50">
            {t('auth.noAccount')}{' '}
            <button
              type="button"
              onClick={() => navigate('/register')}
              className="text-catia-purple hover:text-catia-pink transition-colors"
            >
              {t('auth.register')}
            </button>
          </p>
        </form>
      </div>
    </div>
  )
}
