import { useAuth } from '../../features/auth/useAuth'
import { useNavigate } from 'react-router-dom'
import { LogOut, User } from 'lucide-react'

export default function AppHeader() {
  const user = useAuth((s) => s.user)
  const logout = useAuth((s) => s.logout)
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 shadow-sm">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #667eea, #764ba2)' }}>
          <span className="text-white font-bold text-sm">D</span>
        </div>
        <h1 className="text-lg font-semibold text-gray-800">数据监控看板</h1>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <User className="w-4 h-4" />
          <span>{user?.username || '用户'}</span>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-1 text-sm text-gray-500 hover:text-red-500 transition-colors"
        >
          <LogOut className="w-4 h-4" />
          退出
        </button>
      </div>
    </header>
  )
}
