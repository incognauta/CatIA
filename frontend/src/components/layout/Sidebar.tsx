import { Link, useLocation } from 'react-router-dom'
import { BookOpen, FileText, Settings, HelpCircle } from 'lucide-react'
import { useUIStore } from '@stores/uiStore'

export default function Sidebar() {
  const location = useLocation()
  const { toggleSidebar } = useUIStore()
  
  const isActive = (path: string) => location.pathname === path

  const menuItems = [
    { icon: BookOpen, label: 'Notebooks', path: '/' },
    { icon: FileText, label: 'Documentos', path: '/documents' },
    { icon: Settings, label: 'Configuración', path: '/settings' },
    { icon: HelpCircle, label: 'Ayuda', path: '/help' },
  ]

  return (
    <aside className="w-64 bg-catia-dark/50 border-r border-catia-purple/20 p-6 flex flex-col">
      <div className="mb-8">
        <h2 className="text-lg font-bold text-catia-light">Menú</h2>
      </div>

      <nav className="flex-1 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          const active = isActive(item.path)
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                active
                  ? 'bg-catia-purple/30 text-catia-gold'
                  : 'text-catia-light/70 hover:bg-catia-purple/10'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>

      <div className="pt-4 border-t border-catia-purple/20">
        <p className="text-xs text-catia-light/50">v0.0.1</p>
      </div>
    </aside>
  )
}
