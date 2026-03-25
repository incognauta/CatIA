import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import { useAuthStore } from '@stores/authStore'
import { QueryClientProvider, QueryClient } from '@tanstack/react-query'

// Pages
import LoginPage from '@pages/LoginPage'
import RegisterPage from '@pages/RegisterPage'
import DashboardPage from '@pages/DashboardPage'
import NotebookPage from '@pages/NotebookPage'
import ComingSoonPage from '@pages/ComingSoonPage'

// Layout
import RootLayout from '@components/layout/RootLayout'

const queryClient = new QueryClient()

// Componente para manejar la lógica de autenticación
function AppRoutes() {
  const { token } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    // Si el usuario acaba de loguearse y está en /login, redirige a /
    if (token && (location.pathname === '/login' || location.pathname === '/register')) {
      navigate('/', { replace: true })
    }
    // Si no hay token y no está en una ruta pública, redirige a /login
    if (!token && location.pathname !== '/login' && location.pathname !== '/register') {
      navigate('/login', { replace: true })
    }
  }, [token, location.pathname, navigate])

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      
      {/* Protected routes */}
      {token && (
        <Route element={<RootLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/notebook/:notebookId" element={<NotebookPage />} />
          <Route path="/coming-soon" element={<ComingSoonPage />} />
          <Route path="/documents" element={<ComingSoonPage />} />
          <Route path="/settings" element={<ComingSoonPage />} />
          <Route path="/help" element={<ComingSoonPage />} />
        </Route>
      )}
      
      {/* Fallback */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <AppRoutes />
      </Router>
    </QueryClientProvider>
  )
}

export default App
