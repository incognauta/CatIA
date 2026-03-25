import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'
import { useUIStore } from '@stores/uiStore'

export default function RootLayout() {
  const { isSidebarOpen } = useUIStore()

  return (
    <div className="flex h-screen bg-catia-dark">
      {/* Sidebar */}
      {isSidebarOpen && <Sidebar />}
      
      {/* Main content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
