import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ArrowRight,
  MessageSquare,
  Volume2,
  Settings as SettingsIcon,
  ChevronRight,
  Sparkles,
  Bookmark,
  CheckCircle2,
} from 'lucide-react'
import { useAuth } from '../store/auth'
import { api } from '../lib/api'
import { speakMessage } from '../lib/speech'
import { useSettings } from '../store/settings'

interface ApprovedMessage {
  id: string
  literal_text: string
  approved_text?: string
  created_at: string
  approval_status?: string
}

const EXAMPLES = [
  {
    icon: '💧',
    title: 'Ask for water',
    phrase: 'I want water',
    concepts: ['I', 'want', 'water'],
  },
  {
    icon: '🤝',
    title: 'Ask for help',
    phrase: 'I need help please',
    concepts: ['I', 'need', 'help'],
  },
  {
    icon: '💊',
    title: 'Refuse medicine',
    phrase: 'No medicine right now',
    concepts: ['no', 'medicine'],
  },
]

function formatRelativeTime(dateString: string): string {
  try {
    const diff = Date.now() - new Date(dateString).getTime()
    const minutes = Math.floor(diff / 60000)
    if (minutes < 1) return 'Just now'
    if (minutes < 60) return `${minutes}m ago`
    const hours = Math.floor(minutes / 60)
    if (hours < 24) return `${hours}h ago`
    const days = Math.floor(hours / 24)
    return `${days}d ago`
  } catch {
    return 'Recently'
  }
}

export default function Dashboard() {
  const { user } = useAuth()
  const { settings } = useSettings()
  const navigate = useNavigate()

  const [messages, setMessages] = useState<ApprovedMessage[]>([])
  const [playingId, setPlayingId] = useState<string | null>(null)

  // Dynamic greeting
  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening'
  const userName = user?.name || user?.email?.split('@')[0] || 'Alex'
  const currentDate = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  })

  useEffect(() => {
    async function loadRecentMessages() {
      try {
        const data = await api.get<ApprovedMessage[]>('/messages')
        if (Array.isArray(data)) {
          setMessages(data)
        } else {
          setMessages([])
        }
      } catch {
        setMessages([])
      }
    }

    loadRecentMessages()
  }, [])

  const handlePlaySpeech = async (msg: ApprovedMessage) => {
    const textToSpeak = msg.approved_text || msg.literal_text
    setPlayingId(msg.id)
    try {
      await speakMessage(
        textToSpeak,
        msg.id,
        settings.speechRate,
        settings.voicePreference,
        settings.language,
        settings.gnaniApiKey
      )
    } finally {
      setPlayingId(null)
    }
  }

  const handleTryExample = (concepts: string[]) => {
    navigate('/communicate', { state: { presetConcepts: concepts } })
  }

  return (
    <div className="p-6 md:p-10 max-w-6xl mx-auto space-y-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-navy tracking-tight">
            {greeting}, {userName}.
          </h1>
          <p className="text-text-secondary text-sm mt-1">
            {currentDate} · Ready to help you communicate clearly and comfortably.
          </p>
        </div>
        <button
          onClick={() => navigate('/communicate')}
          className="btn-primary shadow-md shadow-purple/20 self-start sm:self-auto"
        >
          Start communicating <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Main Grid: 2 columns on desktop */}
      <div className="grid lg:grid-cols-3 gap-8">
        {/* Left Column (Span 2) */}
        <div className="lg:col-span-2 space-y-6">
          {/* 1. Communication Hero Card */}
          <div className="bg-navy rounded-card p-8 md:p-10 text-white relative overflow-hidden shadow-card">
            <div className="relative z-10 max-w-md">
              <span className="text-xs font-bold tracking-widest text-teal uppercase mb-2 block">
                COMMUNICATION BOARD
              </span>
              <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight mb-3">
                What would you like <br />
                to say today?
              </h2>
              <p className="text-[#94A3B8] text-sm md:text-base leading-relaxed mb-6">
                Choose visual symbols, let AI assist with smooth sentence construction, and review
                before speaking.
              </p>
              <button
                onClick={() => navigate('/communicate')}
                className="bg-white text-navy font-semibold px-6 py-3 rounded-btn text-sm hover:bg-[#F1F5F9] transition-all inline-flex items-center gap-2 shadow-sm"
              >
                Open communication board <ArrowRight className="w-4 h-4 text-purple" />
              </button>
            </div>

            {/* Illustration Watermark */}
            <div className="absolute right-4 -bottom-6 text-9xl opacity-10 select-none pointer-events-none">
              💬
            </div>
          </div>

          {/* 2. Try an Example Card */}
          <div className="card p-6 md:p-8">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-lg font-bold text-navy">Try an example</h3>
              <span className="text-xs text-text-secondary font-medium">Quick start templates</span>
            </div>
            <div className="space-y-3">
              {EXAMPLES.map((ex) => (
                <div
                  key={ex.title}
                  onClick={() => handleTryExample(ex.concepts)}
                  className="w-full flex items-center justify-between p-4 rounded-xl border border-border/80 hover:border-purple/40 hover:bg-purple-light/20 transition-all cursor-pointer group"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-11 h-11 rounded-xl bg-purple-light flex items-center justify-center text-2xl flex-shrink-0 group-hover:scale-105 transition-transform">
                      {ex.icon}
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-navy group-hover:text-purple transition-colors">
                        {ex.title}
                      </h4>
                      <p className="text-xs text-text-secondary mt-0.5 font-medium">
                        "{ex.phrase}"
                      </p>
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-text-secondary group-hover:text-purple group-hover:translate-x-0.5 transition-all" />
                </div>
              ))}
            </div>
          </div>

          {/* 3. Recently Approved Messages */}
          <div className="card p-6 md:p-8">
            <div className="flex items-center justify-between mb-5">
              <div>
                <h3 className="text-lg font-bold text-navy">Recently approved</h3>
                <p className="text-xs text-text-secondary mt-0.5">
                  Messages you verified and approved for speech playback
                </p>
              </div>
              <button
                onClick={() => navigate('/phrases')}
                className="text-xs font-semibold text-purple hover:underline"
              >
                View library →
              </button>
            </div>

            {messages.length === 0 ? (
              <div className="text-center py-10 text-text-secondary">
                <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-40" />
                <p className="text-sm font-medium">No approved messages yet</p>
                <p className="text-xs mt-1">Start by composing your first message</p>
              </div>
            ) : (
              <div className="space-y-3">
                {messages.slice(0, 5).map((m) => {
                  const displayText = m.approved_text || m.literal_text
                  const isPlaying = playingId === m.id

                  return (
                    <div
                      key={m.id}
                      className="flex items-center justify-between p-3.5 rounded-xl border border-border/60 hover:bg-bg/60 transition-colors"
                    >
                      <div className="flex items-center gap-3.5 min-w-0 flex-1 pr-3">
                        <div className="w-9 h-9 rounded-xl bg-teal-light text-teal flex items-center justify-center flex-shrink-0">
                          <CheckCircle2 className="w-4 h-4" />
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="text-sm font-semibold text-navy truncate">{displayText}</p>
                          <div className="flex items-center gap-2 mt-0.5 text-xs text-text-secondary">
                            <span>{formatRelativeTime(m.created_at)}</span>
                            {m.approved_text && m.approved_text !== m.literal_text && (
                              <span className="text-teal font-medium flex items-center gap-1">
                                <Sparkles className="w-3 h-3" /> AI enhanced
                              </span>
                            )}
                          </div>
                        </div>
                      </div>

                      <button
                        onClick={() => handlePlaySpeech(m)}
                        disabled={isPlaying}
                        className="w-9 h-9 rounded-xl border border-border flex items-center justify-center text-teal hover:bg-teal-light hover:border-teal/40 transition-all flex-shrink-0"
                        title="Replay message"
                        aria-label="Replay audio"
                      >
                        <Volume2 className={`w-4 h-4 ${isPlaying ? 'animate-pulse' : ''}`} />
                      </button>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Preferences & Quick Actions */}
        <div className="space-y-6">
          {/* 4. Your Preferences Card */}
          <div className="card p-6">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-base font-bold text-navy">Your preferences</h3>
              <button
                onClick={() => navigate('/settings')}
                className="text-text-secondary hover:text-navy p-1"
                aria-label="Settings"
              >
                <SettingsIcon className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3.5">
              <div
                onClick={() => navigate('/settings')}
                className="flex items-center justify-between p-3 rounded-xl bg-bg/70 hover:bg-bg cursor-pointer transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="text-lg">🌐</span>
                  <div>
                    <p className="text-xs font-semibold text-navy">Interface language</p>
                    <p className="text-xs text-text-secondary capitalize">
                      {settings.language === 'en'
                        ? 'English'
                        : settings.language === 'hi'
                        ? 'Hindi'
                        : 'Tamil'}
                    </p>
                  </div>
                </div>
                <ChevronRight className="w-4 h-4 text-text-secondary" />
              </div>

              <div
                onClick={() => navigate('/settings')}
                className="flex items-center justify-between p-3 rounded-xl bg-bg/70 hover:bg-bg cursor-pointer transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="text-lg">♿</span>
                  <div>
                    <p className="text-xs font-semibold text-navy">Visual comfort</p>
                    <p className="text-xs text-text-secondary capitalize">
                      {settings.tileSize} tiles · {settings.textSize} text
                    </p>
                  </div>
                </div>
                <ChevronRight className="w-4 h-4 text-text-secondary" />
              </div>

              <div
                onClick={() => navigate('/settings')}
                className="flex items-center justify-between p-3 rounded-xl bg-bg/70 hover:bg-bg cursor-pointer transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="text-lg">🔊</span>
                  <div>
                    <p className="text-xs font-semibold text-navy">Speech rate</p>
                    <p className="text-xs text-text-secondary">
                      {settings.speechRate}x playback speed
                    </p>
                  </div>
                </div>
                <ChevronRight className="w-4 h-4 text-text-secondary" />
              </div>
            </div>
          </div>

          {/* Quick Shortcuts */}
          <div className="card p-6">
            <h3 className="text-base font-bold text-navy mb-4">Quick actions</h3>
            <div className="space-y-2.5">
              <button
                onClick={() => navigate('/phrases')}
                className="btn-secondary w-full justify-start text-xs font-semibold"
              >
                <Bookmark className="w-4 h-4 text-purple" /> Saved phrases library
              </button>
              <button
                onClick={() => navigate('/vocabulary')}
                className="btn-secondary w-full justify-start text-xs font-semibold"
              >
                <MessageSquare className="w-4 h-4 text-teal" /> Personalize vocabulary boards
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
