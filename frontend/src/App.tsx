import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './store/auth'
import { SettingsProvider } from './store/settings'
import { PhrasesProvider } from './store/phrases'
import AppLayout from './components/layout/AppLayout'

import Landing from './pages/Landing'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Communicate from './pages/Communicate'
import Phrases from './pages/Phrases'
import Vocabulary from './pages/Vocabulary'
import Partners from './pages/Partners'
import Settings from './pages/Settings'

export default function App() {
  return (
    <AuthProvider>
      <SettingsProvider>
        <PhrasesProvider>
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
        </PhrasesProvider>
      </SettingsProvider>
    </AuthProvider>
  )
}
