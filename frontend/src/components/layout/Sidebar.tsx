import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  MessageSquare,
  Bookmark,
  BookOpen,
  Users,
  Settings,
  ChevronRight,
  LogOut,
  X,
} from 'lucide-react'
import { useAuth } from '../../store/auth'
import Logo from '../Logo'

interface SidebarProps {
  isOpen?: boolean
  onClose?: () => void
}

const NAV_ITEMS = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Overview' },
  { to: '/communicate', icon: MessageSquare, label: 'Communicate' },
  { to: '/phrases', icon: Bookmark, label: 'Saved phrases' },
  { to: '/vocabulary', icon: BookOpen, label: 'Vocabulary' },
]

const BOTTOM_NAV_ITEMS = [
  { to: '/partners', icon: Users, label: 'Partners' },
  { to: '/settings', icon: Settings, label: 'Settings' },
]

export default function Sidebar({ isOpen = false, onClose }: SidebarProps) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const displayName = user?.name || user?.email?.split('@')[0] || 'Alex Morgan'
  const initial = displayName.charAt(0).toUpperCase() || 'A'

  const content = (
    <div className="flex flex-col h-full bg-surface border-r border-border select-none">
      {/* Brand Header */}
      <div className="h-16 px-6 flex items-center justify-between border-b border-border">
        <Logo size="sm" />
        {onClose && (
          <button
            onClick={onClose}
            className="md:hidden p-1.5 rounded-lg text-text-secondary hover:bg-bg hover:text-navy transition-colors"
            aria-label="Close sidebar"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Main Navigation */}
      <div className="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            onClick={onClose}
            className={({ isActive }) =>
              `flex items-center gap-3.5 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                isActive
                  ? 'bg-purple-light text-purple font-semibold shadow-xs'
                  : 'text-text-secondary hover:text-navy hover:bg-bg'
              }`
            }
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            <span>{label}</span>
          </NavLink>
        ))}

        <div className="pt-6 pb-2">
          <div className="h-px bg-border/60 mx-1 mb-4" />
          <div className="space-y-1">
            {BOTTOM_NAV_ITEMS.map(({ to, icon: Icon, label }) => (
              <NavLink
                key={to}
                to={to}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center gap-3.5 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-purple-light text-purple font-semibold shadow-xs'
                      : 'text-text-secondary hover:text-navy hover:bg-bg'
                  }`
                }
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                <span>{label}</span>
              </NavLink>
            ))}
          </div>
        </div>
      </div>

      {/* User Footer Card */}
      <div className="p-4 border-t border-border">
        <div className="flex items-center justify-between p-2 rounded-xl hover:bg-bg transition-colors group">
          <button
            onClick={() => {
              navigate('/settings')
              if (onClose) onClose()
            }}
            className="flex items-center gap-3 flex-1 min-w-0 text-left"
          >
            <div className="w-9 h-9 rounded-full bg-purple-light text-purple flex items-center justify-center font-bold text-sm flex-shrink-0">
              {initial}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-navy truncate leading-tight">
                {displayName}
              </p>
              <p className="text-xs text-text-secondary truncate mt-0.5">
                {user?.email || 'Communicator'}
              </p>
            </div>
            <ChevronRight className="w-4 h-4 text-text-secondary group-hover:text-navy transition-colors flex-shrink-0" />
          </button>
          <button
            onClick={logout}
            className="p-1.5 rounded-lg text-text-secondary hover:text-red-500 hover:bg-red-50 transition-colors ml-1"
            title="Log out"
            aria-label="Log out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )

  return (
    <>
      {/* Desktop Static Sidebar */}
      <aside className="hidden md:flex w-64 h-screen fixed left-0 top-0 z-30 flex-col">
        {content}
      </aside>

      {/* Mobile Drawer */}
      {isOpen && (
        <div className="md:hidden fixed inset-0 z-50 flex">
          <div
            className="fixed inset-0 bg-navy/40 backdrop-blur-xs transition-opacity"
            onClick={onClose}
          />
          <div className="relative w-72 max-w-xs h-full shadow-2xl z-10 animate-in slide-in-from-left duration-200">
            {content}
          </div>
        </div>
      )}
    </>
  )
}
