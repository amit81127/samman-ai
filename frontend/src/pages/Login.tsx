import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, Mail, KeyRound } from 'lucide-react'
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

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email || !password) {
      setError('Please provide both email and password')
      return
    }

    setLoading(true)
    setError(null)
    try {
      if (isRegister) {
        await register(email, password, language)
      } else {
        await login(email, password)
      }
      navigate('/dashboard', { replace: true })
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please check credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col lg:flex-row">
      {/* Left Dark Navy Panel */}
      <div className="lg:w-1/2 bg-navy px-8 lg:px-16 py-12 flex flex-col justify-between relative overflow-hidden text-white select-none">
        {/* Top: Logo */}
        <div className="relative z-10">
          <Logo dark size="md" />
        </div>

        {/* Center: Hero Message */}
        <div className="my-16 lg:my-auto max-w-lg relative z-10">
          <p className="text-xs font-bold tracking-widest text-teal uppercase mb-4">
            A VOICE IS MORE THAN WORDS
          </p>
          <h1 className="text-5xl lg:text-6xl font-extrabold tracking-tight leading-tight mb-6">
            Say what <br />
            <span className="text-purple">matters.</span>
          </h1>
          <p className="text-lg text-[#94A3B8] leading-relaxed">
            Assistive and Augmentative Communication that meets you where you are.
          </p>
        </div>

        {/* Bottom: Inspirational Quote */}
        <div className="relative z-10">
          <p className="text-sm italic text-[#94A3B8] leading-relaxed max-w-md">
            "The most important thing is to give people a way to be heard."
          </p>
        </div>

        {/* Decorative Subtle Circles */}
        <div className="absolute -bottom-24 -right-24 w-96 h-96 rounded-full border border-white/5 pointer-events-none" />
        <div className="absolute -bottom-10 -right-10 w-72 h-72 rounded-full border border-white/5 pointer-events-none" />
      </div>

      {/* Right White Authentication Panel */}
      <div className="flex-1 bg-surface px-6 sm:px-12 lg:px-20 py-12 flex flex-col justify-center items-center">
        <div className="w-full max-w-md">
          {/* Centered SAMAAN AI Logo */}
          <div className="flex justify-center mb-8">
            <Logo size="lg" />
          </div>

          {/* Subheader */}
          <div className="text-center mb-8">
            <p className="text-xs font-bold tracking-widest text-teal uppercase mb-1">
              {isRegister ? 'GET STARTED' : 'WELCOME BACK'}
            </p>
            <h2 className="text-3xl font-bold text-navy tracking-tight mb-2">
              {isRegister ? 'Create your account' : 'Sign in to SAMAAN'}
            </h2>
            <p className="text-sm text-text-secondary">
              {isRegister
                ? 'Create your personal communicator account.'
                : 'Enter your credentials to continue.'}
            </p>
          </div>

          {/* Error Message Box */}
          {error && (
            <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-sm text-red-600 animate-in fade-in">
              {error}
            </div>
          )}

          {/* Direct Email + Password Form */}
          <form onSubmit={handleEmailSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-navy uppercase tracking-wider mb-1.5">
                Email address
              </label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-text-secondary" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="user@example.com"
                  className="input pl-10"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-navy uppercase tracking-wider mb-1.5">
                Password
              </label>
              <div className="relative">
                <KeyRound className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-text-secondary" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="input pl-10"
                />
              </div>
            </div>

            {isRegister && (
              <div>
                <label className="block text-xs font-semibold text-navy uppercase tracking-wider mb-1.5">
                  Preferred Language
                </label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="input"
                >
                  <option value="en">English</option>
                  <option value="hi">Hindi (हिंदी)</option>
                  <option value="kn">Kannada (ಕನ್ನಡ)</option>
                  <option value="ta">Tamil (தமிழ்)</option>
                  <option value="te">Telugu (తెలుగు)</option>
                </select>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full justify-center py-3.5 text-base shadow-md shadow-purple/20 mt-2"
            >
              {loading
                ? 'Processing...'
                : isRegister
                ? 'Create account'
                : 'Sign in to account'}
              {!loading && <ArrowRight className="w-5 h-5 ml-1" />}
            </button>

            <div className="pt-4 text-center">
              <button
                type="button"
                onClick={() => {
                  setIsRegister(!isRegister)
                  setError(null)
                }}
                className="text-xs font-semibold text-purple hover:underline"
              >
                {isRegister
                  ? 'Already have an account? Sign in →'
                  : "Don't have an account yet? Register here →"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
