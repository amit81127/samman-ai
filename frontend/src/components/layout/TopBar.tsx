import { useLocation, Link } from 'react-router-dom'
import { Bell, Menu } from 'lucide-react'
import { useAuth } from '../../store/auth'

interface TopBarProps {
  onToggleMobileMenu?: () => void
}

const ROUTE_TITLES: Record<string, string> = {
  '/dashboard': 'Overview',
  '/communicate': 'Communicate',
  '/phrases': 'Saved phrases',
  '/vocabulary': 'Vocabulary',
  '/partners': 'Partners',
  '/settings': 'Settings',
}

export default function TopBar({ onToggleMobileMenu }: TopBarProps) {
  const { user } = useAuth()
  const location = useLocation()

  const currentTitle = ROUTE_TITLES[location.pathname] || 'Dashboard'
  const displayName = user?.name || user?.email?.split('@')[0] || 'Alex Morgan'
  const initial = displayName.charAt(0).toUpperCase() || 'A'

  return (
    <header className="h-16 bg-surface border-b border-border sticky top-0 z-20 px-6 flex items-center justify-between">
      {/* Left: Mobile Toggle & Breadcrumbs */}
      <div className="flex items-center gap-3">
        {onToggleMobileMenu && (
          <button
            onClick={onToggleMobileMenu}
            className="md:hidden p-2 rounded-lg text-text-secondary hover:text-navy hover:bg-bg transition-colors"
            aria-label="Open navigation drawer"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}

        {/* Reference screenshot breadcrumbs: SAMAAN AI > CurrentPage */}
        <nav className="flex items-center gap-2 text-xs md:text-sm font-medium tracking-wide">
          <Link to="/dashboard" className="text-text-secondary hover:text-navy transition-colors">
            SAMAAN AI
          </Link>
          <span className="text-text-secondary">›</span>
          <span className="text-navy font-semibold">{currentTitle}</span>
        </nav>
      </div>

      {/* Right: Notification, User avatar */}
      <div className="flex items-center gap-3">

        <button
          className="w-9 h-9 rounded-xl border border-border flex items-center justify-center text-text-secondary hover:text-navy hover:bg-bg transition-colors"
          aria-label="Notifications"
        >
          <Bell className="w-4 h-4" />
        </button>

        <Link
          to="/settings"
          className="w-9 h-9 rounded-full bg-purple-light text-purple flex items-center justify-center font-bold text-sm hover:ring-2 hover:ring-purple/40 transition-all select-none"
          title={displayName}
        >
          {initial}
        </Link>
      </div>
    </header>
  )
}
