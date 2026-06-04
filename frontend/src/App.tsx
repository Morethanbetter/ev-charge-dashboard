import { Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './features/auth/LoginPage'
import DashboardPage from './features/dashboard/DashboardPage'
import UploadPage from './features/upload/UploadPage'
import HistoryPage from './features/history/HistoryPage'
import DedupStatus from './features/dedup/DedupStatus'
import MainLayout from './components/layout/MainLayout'
import { useAuth } from './features/auth/useAuth'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = useAuth((s) => s.token)
  if (!token) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="upload" element={<UploadPage />} />
        <Route path="history" element={<HistoryPage />} />
        <Route path="history/:fileId/dedup" element={<DedupStatus />} />
      </Route>
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}
