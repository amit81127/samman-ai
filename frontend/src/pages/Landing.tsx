import { Link, useNavigate } from 'react-router-dom'
import { ArrowRight, Shield, Sparkles, Lock, Waves, User, HelpCircle } from 'lucide-react'
import Logo from '../components/Logo'
import { useAuth } from '../store/auth'

export default function Landing() {
  const navigate = useNavigate()

  const handleStartCommunicating = () => {
    navigate('/communicate')
  }

  const handleSignIn = () => {
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-bg flex flex-col">
      {/* Navigation Header */}
      <header className="bg-surface border-b border-border px-6 md:px-12 h-20 flex items-center justify-between sticky top-0 z-20">
        <Logo size="md" />
        <nav className="flex items-center gap-6 text-sm font-medium">
          <a
            href="#how-it-works"
            className="hidden sm:inline text-text-secondary hover:text-navy transition-colors"
          >
            How it works
          </a>
          <Link
            to="/login"
            className="hidden sm:inline text-text-secondary hover:text-navy transition-colors"
          >
            Accessibility
          </Link>
          <Link
            to="/login"
            className="text-navy font-semibold hover:text-purple flex items-center gap-1.5 transition-colors"
          >
            Sign in <ArrowRight className="w-4 h-4" />
          </Link>
        </nav>
      </header>

      {/* Main Hero Section */}
      <main className="flex-1 max-w-7xl mx-auto px-6 md:px-12 py-12 md:py-20 flex flex-col lg:flex-row items-center justify-between gap-12 lg:gap-16">
        {/* Left Hero Content */}
        <div className="flex-1 max-w-xl">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 mb-6">
            <span className="w-2 h-2 rounded-full bg-teal" />
            <span className="text-xs font-bold tracking-widest text-teal uppercase">
              A CALMER WAY TO COMMUNICATE
            </span>
          </div>

          {/* Main Headline */}
          <h1 className="text-5xl md:text-6xl font-extrabold text-navy tracking-tight leading-[1.15] mb-6">
            Every voice <br />
            <span className="text-purple">deserves</span> to be <br />
            heard.
          </h1>

          {/* Subtitle */}
          <p className="text-lg text-text-secondary leading-relaxed mb-8">
            SAMAAN helps people express what they need, feel, and want — with symbols, thoughtful AI
            assistance, and complete human control.
          </p>

          {/* Call to Actions */}
          <div className="flex flex-wrap items-center gap-4 mb-8">
            <button
              onClick={handleStartCommunicating}
              className="btn-primary text-base px-6 py-3.5 shadow-md shadow-purple/20"
            >
              Start communicating <ArrowRight className="w-5 h-5" />
            </button>
            <button
              onClick={handleSignIn}
              className="btn-secondary text-base px-6 py-3.5"
            >
              Sign In
            </button>
          </div>

          {/* Privacy & Human Invariant Guarantee */}
          <div className="flex items-center gap-2.5 text-xs text-text-secondary">
            <Shield className="w-4 h-4 text-teal flex-shrink-0" />
            <span>AI suggests. You approve. Only approved messages are spoken.</span>
          </div>
        </div>

        {/* Right Preview Card from Reference Screenshot */}
        <div className="flex-1 w-full max-w-lg flex justify-center lg:justify-end">
          <div className="w-full bg-[#EAF5F3] p-5 sm:p-7 rounded-3xl shadow-card border border-[#D5EAE4]">
            {/* Inner White Surface */}
            <div className="bg-surface rounded-2xl p-6 shadow-sm border border-border">
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <span className="text-xs font-bold tracking-wider text-text-secondary uppercase">
                  COMMUNICATION BOARD
                </span>
                <div className="flex items-center gap-1.5 px-2.5 py-1 bg-teal-light rounded-full text-xs font-semibold text-teal">
                  <span className="w-1.5 h-1.5 rounded-full bg-teal" />
                  <span>READY</span>
                </div>
              </div>

              {/* Selected Words Display */}
              <div className="mb-6">
                <p className="text-xs font-medium text-text-secondary mb-1">Selected words</p>
                <p className="text-3xl font-extrabold text-navy tracking-tight">
                  I want <span className="text-teal font-extrabold">water</span>
                </p>
              </div>

              {/* Symbol Tiles Grid Preview */}
              <div className="grid grid-cols-4 gap-3 mb-6">
                {/* Tile 1: I */}
                <div className="aspect-square rounded-xl bg-purple-light/70 border-2 border-purple flex flex-col items-center justify-center p-2 text-center transition-all">
                  <div className="w-7 h-7 rounded-full border-2 border-purple flex items-center justify-center mb-1">
                    <User className="w-3.5 h-3.5 text-purple" />
                  </div>
                  <span className="text-xs font-medium text-navy">I</span>
                </div>

                {/* Tile 2: want */}
                <div className="aspect-square rounded-xl bg-purple-light/70 border-2 border-purple flex flex-col items-center justify-center p-2 text-center transition-all">
                  <Sparkles className="w-6 h-6 text-purple mb-1" />
                  <span className="text-xs font-medium text-navy">want</span>
                </div>

                {/* Tile 3: water */}
                <div className="aspect-square rounded-xl bg-teal-light border-2 border-teal flex flex-col items-center justify-center p-2 text-center transition-all">
                  <Waves className="w-6 h-6 text-teal mb-1" />
                  <span className="text-xs font-semibold text-teal">water</span>
                </div>

                {/* Tile 4: help */}
                <div className="aspect-square rounded-xl bg-purple-light/40 border border-border flex flex-col items-center justify-center p-2 text-center transition-all">
                  <HelpCircle className="w-6 h-6 text-purple/70 mb-1" />
                  <span className="text-xs font-medium text-navy">help</span>
                </div>
              </div>

              {/* Card Footer Indicators */}
              <div className="pt-4 border-t border-border flex items-center justify-between text-xs text-text-secondary">
                <div className="flex items-center gap-1.5 font-medium">
                  <Sparkles className="w-3.5 h-3.5 text-purple" />
                  <span>AI assistance available</span>
                </div>
                <div className="flex items-center gap-1.5 font-medium">
                  <Lock className="w-3.5 h-3.5 text-text-secondary" />
                  <span>You approve first</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-surface py-6 px-6 md:px-12 text-center text-xs text-text-secondary">
        <p>© {new Date().getFullYear()} SAMAAN AI. Assistive & Augmentative Communication (AAC).</p>
      </footer>
    </div>
  )
}
