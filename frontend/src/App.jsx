import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import Dashboard from './pages/Dashboard'
import ClientsPage from './pages/ClientsPage'
import ClientDetail from './pages/ClientDetail'
import SessionDetail from './pages/SessionDetail'
import BillingPage from './pages/BillingPage'

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="loading-screen">Loading...</div>
  if (!user) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="clients" element={<ClientsPage />} />
        <Route path="clients/:clientId" element={<ClientDetail />} />
        <Route path="sessions/:sessionId" element={<SessionDetail />} />
        <Route path="settings/billing" element={<BillingPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}