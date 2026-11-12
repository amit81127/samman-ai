import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './store/auth'
import { SettingsProvider } from './store/settings'
import { PhrasesProvider } from './store/phrases'
import AppLayout from './components/layout/AppLayout'

// Lazy-loaded route components for code-splitting & fast initial paint
const Landing = lazy(() => import('./pages/Landing'))
const Login = lazy(() => import('./pages/Login'))
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Communicate = lazy(() => import('./pages/Communicate'))
const Phrases = lazy(() => import('./pages/Phrases'))
const Vocabulary = lazy(() => import('./pages/Vocabulary'))
const Partners = lazy(() => import('./pages/Partners'))
const Settings = lazy(() => import('./pages/Settings'))

function PageLoadingFallback() {
  return (
    <div
      role="status"
      aria-live="polite"
      className="min-h-screen bg-bg flex flex-col items-center justify-center p-6 text-center"
    >
      <div className="w-10 h-10 border-4 border-purple-light border-t-purple rounded-full animate-spin mb-3" />
      <p className="text-xs font-semibold text-navy">Loading SAMAAN AI...</p>
      <span className="sr-only">Please wait while the page loads</span>
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <SettingsProvider>
        <PhrasesProvider>
          <Suspense fallback={<PageLoadingFallback />}>
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<Landing />} />
              <Route path="/login" element={<Login />} />

              {/* Authenticated Dashboard Layout */}
              <Route element={<AppLayout />}>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/communicate" element={<Communicate />} />
                <Route path="/phrases" element={<Phrases />} />
                <Route path="/vocabulary" element={<Vocabulary />} />
                <Route path="/partners" element={<Partners />} />
                <Route path="/settings" element={<Settings />} />
              </Route>

              {/* Catch-all redirect */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Suspense>
        </PhrasesProvider>
      </SettingsProvider>
    </AuthProvider>
  )
}
