import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  ArrowRight,
  Shield,
  Sparkles,
  Lock,
  Waves,
  User,
  HelpCircle,
  Volume2,
  Heart,
  Layers,
  Zap,
  CheckCircle2,
  Globe2,
  Users2,
  ChevronDown,
  ChevronUp,
  Smile,
  Activity,
  Award,
} from 'lucide-react'
import Logo from '../components/Logo'

interface DemoTile {
  id: string
  label: string
  icon: string
  category: string
  color: string
}

const DEMO_TILES: DemoTile[] = [
  { id: '1', label: 'I want', icon: '🙋', category: 'Needs', color: 'bg-purple-light border-purple text-purple' },
  { id: '2', label: 'water', icon: '💧', category: 'Needs', color: 'bg-teal-light border-teal text-teal' },
  { id: '3', label: 'food', icon: '🍎', category: 'Needs', color: 'bg-amber-50 border-amber-400 text-amber-600' },
  { id: '4', label: 'help', icon: '🆘', category: 'Needs', color: 'bg-red-50 border-red-400 text-red-600' },
  { id: '5', label: 'happy', icon: '😊', category: 'Feelings', color: 'bg-emerald-50 border-emerald-400 text-emerald-600' },
  { id: '6', label: 'pain', icon: '🤕', category: 'Health', color: 'bg-rose-50 border-rose-400 text-rose-600' },
  { id: '7', label: 'rest', icon: '🛌', category: 'Comfort', color: 'bg-blue-50 border-blue-400 text-blue-600' },
  { id: '8', label: 'thank you', icon: '🙏', category: 'Social', color: 'bg-indigo-50 border-indigo-400 text-indigo-600' },
]

export default function Landing() {
  const navigate = useNavigate()
  const [selectedDemoTiles, setSelectedDemoTiles] = useState<DemoTile[]>([DEMO_TILES[0], DEMO_TILES[1]])
  const [openFaq, setOpenFaq] = useState<number | null>(0)

  const toggleDemoTile = (tile: DemoTile) => {
    if (selectedDemoTiles.some((t) => t.id === tile.id)) {
      setSelectedDemoTiles((prev) => prev.filter((t) => t.id !== tile.id))
    } else {
      setSelectedDemoTiles((prev) => [...prev, tile])
    }
  }

  const composedSentence =
    selectedDemoTiles.length > 0
      ? selectedDemoTiles.map((t) => t.label).join(' ')
      : 'Select symbols below to build a sentence...'

  const faqs = [
    {
      q: 'What is SAMAAN AI and who is it designed for?',
      a: 'SAMAAN AI is an Augmentative and Alternative Communication (AAC) platform created for non-verbal individuals, people with speech motor difficulties, stroke survivors, individuals on the autism spectrum, and those recovering in hospital care settings.',
    },
    {
      q: 'How does the AI assistance work without changing what I want to say?',
      a: 'SAMAAN AI strictly preserves the AAC Invariant: AI never speaks on your behalf. Gemini AI analyzes your selected symbol sequence and generates polished sentence options. You review, edit, or approve the sentence, and only user-approved messages are synthesized into speech.',
    },
    {
      q: 'What languages and regional voices are supported?',
      a: 'We integrate with Gnani AI Timbre v3.0, providing natural neural text-to-speech for English (Indian accent), Hindi, Kannada, Tamil, and Telugu, with customizable voice personas and speed settings.',
    },
    {
      q: 'How fast is speech generation and communication?',
      a: 'With multi-tier caching (in-memory LRU + client-side audio blob caching), replayed sentences and common phrases synthesize in under 0.1 milliseconds, ensuring conversations remain fluid and responsive.',
    },
    {
      q: 'Can family members or speech therapists customize the boards?',
      a: 'Yes! The platform includes a full Vocabulary Board Management system and Delegated Partner permissions, allowing caregivers and therapists to add custom vocabulary symbols, configure categories, and review communication history remotely.',
    },
  ]

  return (
    <div className="min-h-screen bg-bg flex flex-col text-navy font-sans antialiased selection:bg-purple-light selection:text-purple">
      {/* Navigation Header */}
      <header className="bg-surface/90 backdrop-blur-md border-b border-border px-6 md:px-12 h-20 flex items-center justify-between sticky top-0 z-30 transition-all">
        <Logo size="md" />
        <nav className="flex items-center gap-6 text-sm font-semibold">
          <a href="#features" className="hidden md:inline text-text-secondary hover:text-navy transition-colors">
            Features
          </a>
          <a href="#interactive-demo" className="hidden sm:inline text-text-secondary hover:text-navy transition-colors">
            Interactive Demo
          </a>
          <a href="#how-it-works" className="hidden lg:inline text-text-secondary hover:text-navy transition-colors">
            How It Works
          </a>
          <a href="#faq" className="hidden sm:inline text-text-secondary hover:text-navy transition-colors">
            FAQ
          </a>
          <Link
            to="/login"
            className="btn-primary text-xs sm:text-sm px-4 py-2 sm:px-5 sm:py-2.5 shadow-sm shadow-purple/20 flex items-center gap-1.5"
          >
            Sign In <ArrowRight className="w-4 h-4" />
          </Link>
        </nav>
      </header>

      {/* Main Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-16 md:pt-20 md:pb-24 border-b border-border bg-gradient-to-b from-white to-bg">
        <div className="max-w-7xl mx-auto px-6 md:px-12 flex flex-col lg:flex-row items-center justify-between gap-12 lg:gap-16">
          {/* Left Hero Content */}
          <div className="flex-1 max-w-2xl">
            {/* Top Pill Badge */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-teal-light/60 border border-teal/20 text-teal text-xs font-bold tracking-wider uppercase mb-6 shadow-xs">
              <span className="w-2 h-2 rounded-full bg-teal animate-pulse" />
              <span>Next-Gen Assistive Communication (AAC)</span>
            </div>

            {/* Headline */}
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold text-navy tracking-tight leading-[1.12] mb-6">
              Giving every voice the <span className="text-purple underline decoration-purple-light underline-offset-8">freedom</span> to be heard.
            </h1>

            {/* Subtitle */}
            <p className="text-base sm:text-lg text-text-secondary leading-relaxed mb-8 max-w-xl">
              SAMAAN AI empowers individuals with speech and motor challenges to express thoughts, needs, and emotions through visual symbols, intelligent grammar synthesis, and natural multilingual voices.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-wrap items-center gap-4 mb-8">
              <button
                onClick={() => navigate('/communicate')}
                className="btn-primary text-base px-7 py-3.5 shadow-lg shadow-purple/25 hover:shadow-xl transition-all flex items-center gap-2 group"
              >
                Open Communicator <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>
              <button
                onClick={() => navigate('/login')}
                className="btn-secondary text-base px-6 py-3.5 hover:bg-surface transition-all border border-border"
              >
                Caregiver & User Portal
              </button>
            </div>

            {/* Invariant & Trust Guarantee */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-4 border-t border-border/80">
              <div className="flex items-center gap-2 text-xs font-medium text-text-secondary">
                <Shield className="w-4 h-4 text-teal shrink-0" />
                <span>Zero Hallucination Guardrails</span>
              </div>
              <div className="flex items-center gap-2 text-xs font-medium text-text-secondary">
                <Lock className="w-4 h-4 text-purple shrink-0" />
                <span>Strict Human Approval Invariant</span>
              </div>
            </div>
          </div>

          {/* Right Hero Visual Card */}
          <div className="flex-1 w-full max-w-lg">
            <div className="bg-surface rounded-3xl p-6 sm:p-8 shadow-2xl border border-border relative">
              <div className="absolute -top-3 -right-3 px-3 py-1 bg-purple text-white text-[11px] font-bold uppercase rounded-full shadow-md">
                Live Simulator
              </div>

              <div className="flex items-center justify-between pb-4 border-b border-border mb-5">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-xl bg-purple-light text-purple flex items-center justify-center font-bold text-xs">
                    AAC
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-navy uppercase tracking-wider">Current Utterance</h3>
                    <p className="text-[11px] text-text-secondary">Selected Symbol Tokens</p>
                  </div>
                </div>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-teal-light text-teal uppercase">
                  Ready to Speak
                </span>
              </div>

              {/* Display Strip */}
              <div className="p-4 rounded-2xl bg-bg border border-border/80 min-h-[70px] flex items-center mb-5">
                <p className="text-xl sm:text-2xl font-bold text-navy tracking-tight">
                  {selectedDemoTiles.length > 0 ? (
                    selectedDemoTiles.map((t, i) => (
                      <span key={t.id}>
                        <span className="text-purple font-extrabold">{t.label}</span>
                        {i < selectedDemoTiles.length - 1 ? ' ' : ''}
                      </span>
                    ))
                  ) : (
                    <span className="text-sm font-normal text-text-secondary italic">Tap symbols below to add words...</span>
                  )}
                </p>
              </div>

              {/* Mini Symbol Grid */}
              <div className="grid grid-cols-4 gap-2.5 mb-5">
                {DEMO_TILES.slice(0, 4).map((tile) => {
                  const isSelected = selectedDemoTiles.some((t) => t.id === tile.id)
                  return (
                    <button
                      key={tile.id}
                      onClick={() => toggleDemoTile(tile)}
                      className={`p-2.5 rounded-xl border flex flex-col items-center justify-center text-center transition-all ${
                        isSelected
                          ? `${tile.color} shadow-sm scale-95 border-2`
                          : 'bg-white border-border hover:border-purple/40 text-navy'
                      }`}
                    >
                      <span className="text-xl mb-1">{tile.icon}</span>
                      <span className="text-[11px] font-bold truncate max-w-full">{tile.label}</span>
                    </button>
                  )
                })}
              </div>

              {/* Status and Action Buttons */}
              <div className="flex items-center justify-between pt-4 border-t border-border text-xs">
                <span className="text-text-secondary flex items-center gap-1.5 font-medium">
                  <Sparkles className="w-3.5 h-3.5 text-purple" /> AI Sentence Composer Active
                </span>
                <button
                  onClick={() => navigate('/communicate')}
                  className="text-purple font-bold hover:underline flex items-center gap-1"
                >
                  Full Board <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Core Features Breakdown */}
      <section id="features" className="py-20 bg-white border-b border-border">
        <div className="max-w-7xl mx-auto px-6 md:px-12">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <p className="text-xs font-bold tracking-widest text-teal uppercase mb-2">CLINICAL & TECHNICAL EXCELLENCE</p>
            <h2 className="text-3xl md:text-4xl font-extrabold text-navy tracking-tight">
              Engineered for Independence, Dignity, and Speed.
            </h2>
            <p className="text-sm md:text-base text-text-secondary mt-3">
              Combining evidence-based AAC methodology with modern edge-cached neural speech synthesis and Google Gemini generative intelligence.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="card p-7 hover:shadow-card-hover transition-all border border-border group bg-surface">
              <div className="w-12 h-12 rounded-2xl bg-purple-light text-purple flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
                <Sparkles className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-navy mb-2">Gemini AI Sentence Composer</h3>
              <p className="text-xs text-text-secondary leading-relaxed mb-4">
                Transforms disjointed concept selections into grammatically fluent, contextual sentences without changing original intent or hallucinating unselected ideas.
              </p>
              <div className="text-[11px] font-semibold text-purple flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Instant literal fallback resilient
              </div>
            </div>

            {/* Feature 2 */}
            <div className="card p-7 hover:shadow-card-hover transition-all border border-border group bg-surface">
              <div className="w-12 h-12 rounded-2xl bg-teal-light text-teal flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
                <Volume2 className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-navy mb-2">Gnani Timbre Neural Voices</h3>
              <p className="text-xs text-text-secondary leading-relaxed mb-4">
                State-of-the-art text-to-speech built specifically for Indian accents and regional languages including Hindi, Kannada, Tamil, Telugu, and English.
              </p>
              <div className="text-[11px] font-semibold text-teal flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Authentic accents and customizable speed
              </div>
            </div>

            {/* Feature 3 */}
            <div className="card p-7 hover:shadow-card-hover transition-all border border-border group bg-surface">
              <div className="w-12 h-12 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
                <Zap className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-navy mb-2">Sub-Millisecond Replay Caching</h3>
              <p className="text-xs text-text-secondary leading-relaxed mb-4">
                Multi-tier memory and client-side binary audio blob caching ensures approved sentences and frequent phrases speak in less than 0.1ms without network latency.
              </p>
              <div className="text-[11px] font-semibold text-amber-600 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> 600,000x faster than raw API calls
              </div>
            </div>

            {/* Feature 4 */}
            <div className="card p-7 hover:shadow-card-hover transition-all border border-border group bg-surface">
              <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
                <Layers className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-navy mb-2">Tailored Vocabulary Boards</h3>
              <p className="text-xs text-text-secondary leading-relaxed mb-4">
                Organize symbols tailored to hospital settings, school routines, home needs, or dining. Add custom words, icons, and colors with a single tap.
              </p>
              <div className="text-[11px] font-semibold text-emerald-600 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Categorized symbol grids & custom tiles
              </div>
            </div>

            {/* Feature 5 */}
            <div className="card p-7 hover:shadow-card-hover transition-all border border-border group bg-surface">
              <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
                <Users2 className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-navy mb-2">Caregiver & SLP Partner Network</h3>
              <p className="text-xs text-text-secondary leading-relaxed mb-4">
                Invite family members and speech therapists with fine-grained delegated permissions (view history, edit boards, assist composition) safely and securely.
              </p>
              <div className="text-[11px] font-semibold text-blue-600 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Role-based revocable delegation
              </div>
            </div>

            {/* Feature 6 */}
            <div className="card p-7 hover:shadow-card-hover transition-all border border-border group bg-surface">
              <div className="w-12 h-12 rounded-2xl bg-rose-50 text-rose-600 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
                <Activity className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-navy mb-2">Accessibility-First Design</h3>
              <p className="text-xs text-text-secondary leading-relaxed mb-4">
                Designed for diverse motor and visual needs. Includes customizable tile sizing (small, medium, large), high-contrast modes, and reduced-motion options.
              </p>
              <div className="text-[11px] font-semibold text-rose-600 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> WCAG 2.1 AAA accessible UI standards
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Sandbox Section */}
      <section id="interactive-demo" className="py-20 bg-bg border-b border-border">
        <div className="max-w-5xl mx-auto px-6 md:px-12 text-center">
          <p className="text-xs font-bold tracking-widest text-teal uppercase mb-2">EXPERIENCE THE FLOW</p>
          <h2 className="text-3xl md:text-4xl font-extrabold text-navy tracking-tight mb-4">
            Try SAMAAN Symbol Builder Right Now
          </h2>
          <p className="text-sm text-text-secondary max-w-xl mx-auto mb-10">
            Click any symbol below to compose an assistive sentence in real-time. Experience how simple and intuitive AAC communication can be.
          </p>

          <div className="card p-6 md:p-8 bg-surface shadow-xl border border-border text-left">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-border mb-6">
              <div>
                <span className="text-[11px] font-bold text-teal uppercase tracking-wider">Live Composed Phrase</span>
                <p className="text-2xl font-bold text-navy mt-0.5">{composedSentence}</p>
              </div>
              {selectedDemoTiles.length > 0 && (
                <button
                  onClick={() => setSelectedDemoTiles([])}
                  className="btn-secondary text-xs py-1.5 px-3 self-start sm:self-auto"
                >
                  Clear all
                </button>
              )}
            </div>

            {/* Interactive Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
              {DEMO_TILES.map((tile) => {
                const isSelected = selectedDemoTiles.some((t) => t.id === tile.id)
                return (
                  <button
                    key={tile.id}
                    onClick={() => toggleDemoTile(tile)}
                    className={`p-4 rounded-2xl border text-center transition-all flex flex-col items-center justify-center ${
                      isSelected
                        ? `${tile.color} shadow-md scale-95 border-2`
                        : 'bg-white border-border hover:border-purple/50 text-navy'
                    }`}
                  >
                    <span className="text-3xl mb-2">{tile.icon}</span>
                    <span className="text-sm font-bold">{tile.label}</span>
                    <span className="text-[10px] text-text-secondary mt-0.5">{tile.category}</span>
                  </button>
                )
              })}
            </div>

            {/* Action Bar */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-4 border-t border-border">
              <div className="flex items-center gap-2 text-xs text-text-secondary">
                <Shield className="w-4 h-4 text-teal" />
                <span>Selected concepts are never altered without user confirmation</span>
              </div>
              <button
                onClick={() => navigate('/communicate')}
                className="btn-primary text-xs py-2.5 px-5 shadow-sm shadow-purple/20 flex items-center justify-center gap-2"
              >
                Go to Full Communicator <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20 bg-white border-b border-border">
        <div className="max-w-7xl mx-auto px-6 md:px-12">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <p className="text-xs font-bold tracking-widest text-teal uppercase mb-2">SIMPLE 3-STEP PROCESS</p>
            <h2 className="text-3xl md:text-4xl font-extrabold text-navy tracking-tight">How SAMAAN AI Works</h2>
            <p className="text-sm text-text-secondary mt-2">
              Every message is composed with ease, validated with care, and vocalized with pride.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 relative">
            {/* Step 1 */}
            <div className="card p-8 bg-surface border border-border text-center relative">
              <div className="w-12 h-12 rounded-2xl bg-purple-light text-purple flex items-center justify-center mx-auto mb-5 font-extrabold text-lg">
                1
              </div>
              <h3 className="text-lg font-bold text-navy mb-2">Pick Concepts & Symbols</h3>
              <p className="text-xs text-text-secondary leading-relaxed">
                Browse through organized boards or high-priority words. Tap symbols like "I want", "water", "blanket", or "tired".
              </p>
            </div>

            {/* Step 2 */}
            <div className="card p-8 bg-surface border border-border text-center relative">
              <div className="w-12 h-12 rounded-2xl bg-teal-light text-teal flex items-center justify-center mx-auto mb-5 font-extrabold text-lg">
                2
              </div>
              <h3 className="text-lg font-bold text-navy mb-2">AI Synthesizes & You Approve</h3>
              <p className="text-xs text-text-secondary leading-relaxed">
                Gemini constructs proper natural phrasing. You review the candidate sentences and tap the one that fits your exact meaning.
              </p>
            </div>

            {/* Step 3 */}
            <div className="card p-8 bg-surface border border-border text-center relative">
              <div className="w-12 h-12 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center mx-auto mb-5 font-extrabold text-lg">
                3
              </div>
              <h3 className="text-lg font-bold text-navy mb-2">Speak Naturally in Any Language</h3>
              <p className="text-xs text-text-secondary leading-relaxed">
                Gnani Timbre speaks the approved sentence in high-fidelity neural audio. Save phrases for 1-tap instant replay anytime.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Target Audiences & Use Cases */}
      <section className="py-20 bg-bg border-b border-border">
        <div className="max-w-7xl mx-auto px-6 md:px-12">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <p className="text-xs font-bold tracking-widest text-teal uppercase mb-2">UNIVERSAL IMPACT</p>
            <h2 className="text-3xl md:text-4xl font-extrabold text-navy tracking-tight">Built for Diverse Needs</h2>
            <p className="text-sm text-text-secondary mt-2">
              Empowering communication in homes, schools, rehabilitation centers, and critical care units.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="card p-6 bg-surface border border-border">
              <div className="text-3xl mb-3">🧩</div>
              <h4 className="text-base font-bold text-navy mb-1.5">Autism & Neurodiversity</h4>
              <p className="text-xs text-text-secondary leading-relaxed">
                Structured visual symbols and predictable layouts reduce communication anxiety and support natural language acquisition.
              </p>
            </div>
            <div className="card p-6 bg-surface border border-border">
              <div className="text-3xl mb-3">🏥</div>
              <h4 className="text-base font-bold text-navy mb-1.5">Hospital & Post-Operative</h4>
              <p className="text-xs text-text-secondary leading-relaxed">
                For patients on ventilators, tracheostomies, or intensive care who need to express pain and urgent comfort requests quickly.
              </p>
            </div>
            <div className="card p-6 bg-surface border border-border">
              <div className="text-3xl mb-3">🧠</div>
              <h4 className="text-base font-bold text-navy mb-1.5">Stroke & Aphasia</h4>
              <p className="text-xs text-text-secondary leading-relaxed">
                Aids word-finding difficulties with smart suggestions and semantic associations while retaining communicative autonomy.
              </p>
            </div>
            <div className="card p-6 bg-surface border border-border">
              <div className="text-3xl mb-3">♿</div>
              <h4 className="text-base font-bold text-navy mb-1.5">Cerebral Palsy & Motor Needs</h4>
              <p className="text-xs text-text-secondary leading-relaxed">
                Large high-contrast touch targets with customizable tile sizes support various input devices and accessibility switches.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Frequently Asked Questions */}
      <section id="faq" className="py-20 bg-white border-b border-border">
        <div className="max-w-4xl mx-auto px-6 md:px-12">
          <div className="text-center mb-14">
            <p className="text-xs font-bold tracking-widest text-teal uppercase mb-2">COMMON QUESTIONS</p>
            <h2 className="text-3xl font-extrabold text-navy tracking-tight">Frequently Asked Questions</h2>
          </div>

          <div className="space-y-4">
            {faqs.map((faq, idx) => {
              const isOpen = openFaq === idx
              return (
                <div key={idx} className="card p-5 border border-border bg-surface overflow-hidden transition-all">
                  <button
                    onClick={() => setOpenFaq(isOpen ? null : idx)}
                    className="w-full flex items-center justify-between text-left gap-4 font-bold text-sm text-navy"
                  >
                    <span>{faq.q}</span>
                    {isOpen ? (
                      <ChevronUp className="w-4 h-4 text-purple shrink-0" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-text-secondary shrink-0" />
                    )}
                  </button>
                  {isOpen && <p className="text-xs text-text-secondary mt-3 pt-3 border-t border-border leading-relaxed">{faq.a}</p>}
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Bottom CTA Banner */}
      <section className="py-16 bg-gradient-to-r from-purple via-indigo-600 to-[#5145E9] text-white">
        <div className="max-w-5xl mx-auto px-6 md:px-12 text-center">
          <h2 className="text-3xl sm:text-4xl font-extrabold mb-4">Start Communicating Without Barriers</h2>
          <p className="text-sm sm:text-base text-white/85 max-w-xl mx-auto mb-8">
            Experience the calm, dignified, and expressive power of SAMAAN AI. Free and accessible to everyone.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4">
            <button
              onClick={() => navigate('/communicate')}
              className="bg-white text-navy font-bold text-sm px-7 py-3.5 rounded-xl shadow-lg hover:bg-white/95 transition-all flex items-center gap-2"
            >
              Open Communicator Now <ArrowRight className="w-4 h-4 text-purple" />
            </button>
            <button
              onClick={() => navigate('/login')}
              className="bg-white/15 backdrop-blur-sm border border-white/30 text-white font-bold text-sm px-6 py-3.5 rounded-xl hover:bg-white/25 transition-all"
            >
              Sign In to Your Account
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-surface py-10 px-6 md:px-12 border-t border-border text-xs text-text-secondary">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <Logo size="sm" />
            <span className="text-[11px] text-text-secondary">
              © {new Date().getFullYear()} SAMAAN AI. Assistive & Augmentative Communication.
            </span>
          </div>
          <div className="flex items-center gap-6 font-medium">
            <Link to="/communicate" className="hover:text-navy transition-colors">
              Board
            </Link>
            <Link to="/login" className="hover:text-navy transition-colors">
              Portal
            </Link>
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-600 font-bold border border-emerald-200">
              System Online
            </span>
          </div>
        </div>
      </footer>
    </div>
  )
}
