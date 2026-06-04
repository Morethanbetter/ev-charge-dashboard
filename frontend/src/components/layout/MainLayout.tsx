import { Outlet, NavLink } from 'react-router-dom'
import AppHeader from './AppHeader'
import { LayoutDashboard, Upload, History } from 'lucide-react'
import { cn } from '../../lib/utils'

const navItems = [
  { to: '/dashboard', label: '仪表盘', icon: LayoutDashboard },
  { to: '/upload', label: '数据上传', icon: Upload },
  { to: '/history', label: '上传历史', icon: History },
]

export default function MainLayout() {
  return (
    <div className="min-h-screen bg-gray-50">
      <AppHeader />
      <div className="flex">
        <aside className="w-56 bg-white border-r border-gray-200 min-h-[calc(100vh-4rem)]">
          <nav className="p-4 space-y-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-indigo-50 text-indigo-700'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  )
                }
              >
                <item.icon className="w-5 h-5" />
                {item.label}
              </NavLink>
            ))}
          </nav>
        </aside>
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
