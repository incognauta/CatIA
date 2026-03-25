import { Menu, LogOut, Settings, User } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@stores/authStore'
import { useUIStore } from '@stores/uiStore'

export default function Header() {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const { toggleSidebar } = useUIStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="bg-gradient-to-r from-catia-dark to-catia-dark/95 border-b border-catia-purple/20 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <button
          onClick={toggleSidebar}
          className="p-2 hover:bg-catia-purple/20 rounded-lg transition-colors"
        >
          <Menu className="w-5 h-5 text-catia-gold" />
        </button>
        <h1 className="text-xl font-bold bg-gradient-to-r from-catia-purple to-catia-pink bg-clip-text text-transparent">
          🐱 CatIA
        </h1>
      </div>

      <div className="flex items-center gap-4">
        <span className="text-sm text-catia-light/70">{user?.email}</span>
        <div className="flex gap-2">
          <button className="p-2 hover:bg-catia-purple/20 rounded-lg text-catia-light/70">
            <Settings className="w-5 h-5" />
          </button>
          <button className="p-2 hover:bg-catia-purple/20 rounded-lg text-catia-light/70">
            <User className="w-5 h-5" />
          </button>
          <button
            onClick={handleLogout}
            className="p-2 hover:bg-red-500/20 rounded-lg text-catia-light/70 hover:text-red-400"
          >
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </div>
    </header>
  )
}
