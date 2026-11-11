import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { ArrowRight, Mail, Lock, Globe, Sparkles, CheckCircle2 } from 'lucide-react'
import Logo from '../components/Logo'
import { useAuth } from '../store/auth'

export default function Login() {
  const { login, register } = useAuth()
  const navigate = useNavigate()

  const [isRegister, setIsRegister] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [language, setLanguage] = useState('en')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const trimmedEmail = email.trim()
    const trimmedPass = password.trim()

    if (!trimmedEmail || !trimmedPass) {
      setError('Please provide both email and password.')
      return
    }

    if (isRegister) {
      if (trimmedPass.length < 8) {
        setError('Password must be at least 8 characters long.')
        return
      }
      if (!/\d/.test(trimmedPass)) {
        setError('Password must contain at least one number.')
        return
      }
    }

    setLoading(true)
    setError(null)

    try {
      if (isRegister) {
        await register(trimmedEmail, trimmedPass, language)
      } else {
        await login(trimmedEmail, trimmedPass)
      }
      navigate('/dashboard', { replace: true })
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please verify your credentials.')
    } finally {
      setLoading(false)
    }
  }

  // Pre-fill demo credentials for instant testing
  const handleUseDemoAccount = () => {
    setEmail('demo@samaan.ai')
    setPassword('DemoUser123')
    setIsRegister(false)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-bg flex flex-col justify-between p-4 sm:p-6 lg:p-8">
      {/* Top Bar with Logo */}
      <header className="max-w-6xl w-full mx-auto flex items-center justify-between py-2">
        <Link to="/" className="inline-block">
          <Logo size="md" />
        </Link>
        <Link
          to="/"
          className="text-xs sm:text-sm font-semibold text-text-secondary hover:text-navy transition-colors"
        >
          ← Back to home
        </Link>
      </header>

      {/* Main Centered Authentication Card */}
      <main className="flex-1 flex items-center justify-center my-6">
        <div className="w-full max-w-md bg-surface p-7 sm:p-9 rounded-3xl shadow-xl border border-border space-y-6">
          {/* Header Title */}
          <div className="text-center space-y-1.5">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-navy tracking-tight">
              {isRegister ? 'Create an Account' : 'Welcome Back'}
            </h1>
            <p className="text-xs sm:text-sm text-text-secondary">
              {isRegister
                ? 'Set up your personal SAMAAN communicator profile'
                : 'Sign in to access your customized AAC boards & history'}
            </p>
          </div>

          {/* Segmented Switcher */}
          <div className="grid grid-cols-2 p-1 bg-bg rounded-xl border border-border text-xs font-bold text-center">
            <button
              type="button"
              onClick={() => {
                setIsRegister(false)
                setError(null)
              }}
              className={`py-2 rounded-lg transition-all ${!isRegister
                  ? 'bg-surface text-navy shadow-xs border border-border/50'
                  : 'text-text-secondary hover:text-navy'
                }`}
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={() => {
                setIsRegister(true)
                setError(null)
              }}
              className={`py-2 rounded-lg transition-all ${isRegister
                  ? 'bg-surface text-navy shadow-xs border border-border/50'
                  : 'text-text-secondary hover:text-navy'
                }`}
            >
              Create Account
            </button>
          </div>

          {/* Error Banner */}
          {error && (
            <div className="p-3.5 rounded-xl bg-red-50 border border-red-200 text-xs text-red-600 font-medium animate-in fade-in">
              {error}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-navy uppercase tracking-wider mb-1.5">
                Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-text-secondary absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  required
                  autoFocus
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  className="input pl-10 text-sm"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-navy uppercase tracking-wider mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-text-secondary absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="input pl-10 text-sm"
                />
              </div>
              {isRegister && (
                <p className="text-[11px] text-text-secondary mt-1.5 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3 text-teal shrink-0" />
                  Must be 8+ characters with at least one number.
                </p>
              )}
            </div>

            {isRegister && (
              <div>
                <label className="block text-xs font-bold text-navy uppercase tracking-wider mb-1.5">
                  Default Spoken Language
                </label>
                <div className="relative">
                  <Globe className="w-4 h-4 text-text-secondary absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="input pl-10 text-sm"
                  >
                    <option value="en">English (Indian Accent)</option>
                    <option value="hi">Hindi (हिंदी)</option>
                    <option value="kn">Kannada (ಕನ್ನಡ)</option>
                    <option value="ta">Tamil (தமிழ்)</option>
                    <option value="te">Telugu (తెలుగు)</option>
                  </select>
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full justify-center py-3 text-sm shadow-md shadow-purple/20 mt-2 font-bold"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Processing...
                </span>
              ) : isRegister ? (
                <span className="flex items-center gap-1.5">
                  Create Account <ArrowRight className="w-4 h-4" />
                </span>
              ) : (
                <span className="flex items-center gap-1.5">
                  Sign In <ArrowRight className="w-4 h-4" />
                </span>
              )}
            </button>
          </form>

        </div>
      </main>

      {/* Footer */}
      <footer className="text-center text-xs text-text-secondary py-3">
        © {new Date().getFullYear()} SAMAAN AI. Assistive & Augmentative Communication Platform.
      </footer>
    </div>
  )
}
