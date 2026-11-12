import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import {
  ArrowRight,
  Mail,
  Lock,
  Globe,
  Sparkles,
  CheckCircle2,
  Eye,
  EyeOff,
  ShieldCheck,
  UserCheck,
} from 'lucide-react'
import Logo from '../components/Logo'
import { useAuth } from '../store/auth'

export default function Login() {
  const { login, register } = useAuth()
  const navigate = useNavigate()

  const [isRegister, setIsRegister] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [language, setLanguage] = useState('en')
  const [showPassword, setShowPassword] = useState(false)
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
      setError(err.message || 'Authentication failed. Please check your credentials and try again.')
    } finally {
      setLoading(false)
    }
  }

  // Pre-fill demo credentials for instant 1-tap testing
  const handleUseDemoAccount = () => {
    setEmail('demo@samaan.ai')
    setPassword('DemoUser123')
    setIsRegister(false)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-bg via-white to-purple-light/20 flex flex-col justify-between p-4 sm:p-6 lg:p-8 font-sans text-navy">
      {/* Top Header */}
      <header className="max-w-5xl w-full mx-auto flex items-center justify-between py-2">
        <Link to="/" className="inline-flex items-center gap-2 group">
          <Logo size="md" />
        </Link>
        <Link
          to="/"
          className="text-xs sm:text-sm font-semibold text-text-secondary hover:text-navy transition-colors flex items-center gap-1.5 py-2 px-3 rounded-lg hover:bg-surface"
        >
          <span>←</span> Back to home
        </Link>
      </header>

      {/* Main Authentication Box */}
      <main className="flex-1 flex items-center justify-center my-6">
        <div className="w-full max-w-md bg-surface/95 backdrop-blur-sm p-6 sm:p-9 rounded-3xl shadow-xl shadow-purple/5 border border-border/80 transition-all">
          {/* Card Header */}
          <div className="text-center space-y-2 mb-6">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-purple-light text-purple mb-1 shadow-xs">
              <Sparkles className="w-6 h-6" />
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-navy tracking-tight">
              {isRegister ? 'Join SAMAAN AI' : 'Sign In'}
            </h1>
            <p className="text-xs sm:text-sm text-text-secondary max-w-xs mx-auto">
              {isRegister
                ? 'Create an account to personalize vocabulary boards and voice settings'
                : 'Access your saved phrases, custom communication boards, and history'}
            </p>
          </div>

          {/* Simple Tab Switcher */}
          <div className="grid grid-cols-2 p-1 bg-bg rounded-2xl border border-border text-xs font-bold text-center mb-6">
            <button
              type="button"
              onClick={() => {
                setIsRegister(false)
                setError(null)
              }}
              className={`py-2.5 rounded-xl transition-all ${!isRegister
                  ? 'bg-surface text-navy shadow-sm border border-border/60'
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
              className={`py-2.5 rounded-xl transition-all ${isRegister
                  ? 'bg-surface text-navy shadow-sm border border-border/60'
                  : 'text-text-secondary hover:text-navy'
                }`}
            >
              New Account
            </button>
          </div>

          {/* Error Banner */}
          {error && (
            <div className="mb-5 p-3.5 rounded-2xl bg-red-50 border border-red-200 text-xs text-red-600 font-medium flex items-start justify-between gap-2 animate-in fade-in">
              <span>{error}</span>
              <button
                type="button"
                onClick={() => setError(null)}
                className="text-red-400 hover:text-red-700 font-bold text-sm leading-none"
              >
                ×
              </button>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-navy uppercase tracking-wider mb-1.5">
                Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-text-secondary absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  type="email"
                  required
                  autoFocus={!isRegister}
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  className="input pl-10 text-sm h-11 w-full rounded-xl"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-bold text-navy uppercase tracking-wider">
                  Password
                </label>
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 text-text-secondary absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  autoComplete={isRegister ? 'new-password' : 'current-password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="input pl-10 pr-10 text-sm h-11 w-full rounded-xl"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((prev) => !prev)}
                  tabIndex={-1}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-text-secondary hover:text-navy p-1"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {isRegister && (
                <p className="text-[11px] text-text-secondary mt-1.5 flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-teal shrink-0" />
                  Must be at least 8 characters with 1 number.
                </p>
              )}
            </div>

            {isRegister && (
              <div>
                <label className="block text-xs font-bold text-navy uppercase tracking-wider mb-1.5">
                  Preferred Voice Language
                </label>
                <div className="relative">
                  <Globe className="w-4 h-4 text-text-secondary absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                  <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="input pl-10 text-sm h-11 w-full rounded-xl bg-white"
                  >
                    <option value="en">English (Indian Accent - Aditi)</option>
                    <option value="hi">Hindi (हिंदी - Neel)</option>
                    <option value="kn">Kannada (ಕನ್ನಡ - Kavya)</option>
                    <option value="ta">Tamil (தமிழ் - Murugan)</option>
                    <option value="te">Telugu (తెలుగు - Ananya)</option>
                  </select>
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full justify-center h-12 text-sm shadow-md shadow-purple/20 font-bold rounded-xl mt-3"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Please wait...
                </span>
              ) : isRegister ? (
                <span className="flex items-center gap-1.5">
                  Create My Account <ArrowRight className="w-4 h-4" />
                </span>
              ) : (
                <span className="flex items-center gap-1.5">
                  Sign In <ArrowRight className="w-4 h-4" />
                </span>
              )}
            </button>
          </form>

          {/* Quick Guest Communicator Access */}
          <div className="pt-4 border-t border-border/80 text-center">
            <p className="text-xs text-text-secondary mb-2">Want to try the speech communicator without an account?</p>
            <button
              type="button"
              onClick={() => navigate('/communicate')}
              className="text-xs font-bold text-purple hover:text-purple-dark inline-flex items-center gap-1 hover:underline"
            >
              Launch Guest Communicator <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </main>

      {/* Trust & Guarantee Banner */}
      <footer className="max-w-md w-full mx-auto text-center space-y-2 py-4">
        <div className="flex items-center justify-center gap-4 text-[11px] text-text-secondary">
          <span className="flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-teal" /> AES-256 Encrypted
          </span>
          <span>•</span>
          <span>Strict Human-Approval Invariant</span>
        </div>
        <p className="text-[11px] text-text-secondary/80">
          © {new Date().getFullYear()} SAMAAN AI. Assistive & Augmentative Communication Platform.
        </p>
      </footer>
    </div>
  )
}
