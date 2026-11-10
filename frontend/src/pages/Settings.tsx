import { useEffect, useState } from 'react'
import {
  Check,
  Languages,
  Volume2,
  Zap,
  HelpCircle,
  MessageSquare,
  Shield,
  Heart,
  ChevronDown,
  Key,
  Play,
  Loader2,
  Sparkles,
} from 'lucide-react'
import { useSettings } from '../store/settings'
import {
  GNANI_LANGUAGES,
  GNANI_VOICE_PERSONAS,
  speakMessage,
} from '../lib/speech'

export default function Settings() {
  const { settings, updateSettings, lastSaved } = useSettings()
  const [isTestingVoice, setIsTestingVoice] = useState(false)
  const [personalApiKey, setPersonalApiKey] = useState(settings.gnaniApiKey || '')

  useEffect(() => {
    setPersonalApiKey(settings.gnaniApiKey || '')
  }, [settings.gnaniApiKey])

  const handleTestVoice = async () => {
    if (isTestingVoice) return
    setIsTestingVoice(true)
    try {
      const lang = settings.language || 'en-IN'
      let greeting = 'Hello! This is your voice persona in Samaan AI.'
      if (lang.startsWith('hi')) {
        greeting = 'नमस्ते! यह आपकी चुनी हुई आवाज़ है।'
      } else if (lang.startsWith('kn')) {
        greeting = 'ನಮಸ್ಕಾರ! ಇದು ನಿಮ್ಮ ಧ್ವನಿ ವ್ಯಕ್ತಿತ್ವ.'
      } else if (lang.startsWith('ta')) {
        greeting = 'வணக்கம்! இது உங்கள் குரல் வடிவம்.'
      } else if (lang.startsWith('te')) {
        greeting = 'నమస్కారం! ఇది మీ ఎంచుకున్న స్వరం.'
      } else if (lang.startsWith('mr')) {
        greeting = 'नमस्कार! हा तुमचा निवडलेला आवाज आहे.'
      } else if (lang.startsWith('bn')) {
        greeting = 'নমস্কার! এটি আপনার নির্বাচিত কণ্ঠস্বর।'
      } else if (lang.startsWith('gu')) {
        greeting = 'નમસ્તે! આ તમારો પસંદ કરેલો અવાજ છે.'
      } else if (lang.startsWith('ml')) {
        greeting = 'നമസ്കാരം! ഇത് നിങ്ങളുടെ ശബ്ദമാണ്.'
      } else if (lang.startsWith('pa')) {
        greeting = 'ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ! ਇਹ ਤੁਹਾਡੀ ਚੁਣੀ ਹੋਈ ਆਵਾਜ਼ ਹੈ।'
      }

      await speakMessage(
        greeting,
        undefined,
        settings.speechRate,
        settings.voicePreference || 'Shivani',
        lang,
        settings.gnaniApiKey
      )
    } finally {
      setIsTestingVoice(false)
    }
  }

  const handleSaveApiKey = () => {
    updateSettings({ gnaniApiKey: personalApiKey.trim() })
  }

  return (
    <div className="p-6 md:p-10 max-w-4xl mx-auto space-y-8">
      {/* Header matching exact UI */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <p className="text-xs font-bold tracking-widest text-teal uppercase mb-1">
            MAKE IT YOURS
          </p>
          <h1 className="text-3xl font-extrabold text-navy tracking-tight">
            Accessibility settings
          </h1>
          <p className="text-sm text-text-secondary mt-1">
            Multilingual speech synthesis, voice personas, and accessibility preferences.
          </p>
        </div>

        {/* Saved automatically indicator */}
        <div
          className={`flex items-center gap-1.5 text-xs font-semibold text-teal transition-opacity duration-300 ${
            lastSaved ? 'opacity-100' : 'opacity-80'
          }`}
        >
          <Check className="w-4 h-4 text-teal" />
          <span>Saved automatically</span>
        </div>
      </div>

      {/* 1. Communication & Gnani AI Voice Personas */}
      <div className="card p-6 md:p-8 space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-navy tracking-tight flex items-center gap-2">
            <Volume2 className="w-4 h-4 text-purple" /> Multilingual Speech & Personas
          </h2>
          <span className="text-xs font-semibold text-purple bg-purple-light px-2.5 py-1 rounded-full">
            Gnani AI Timbre v3.0
          </span>
        </div>

        <div className="divide-y divide-border space-y-6">
          {/* Row 1: Multilingual Language */}
          <div className="pt-2 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-purple-light text-purple flex items-center justify-center flex-shrink-0">
                <Languages className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-navy">Speech Language</h3>
                <p className="text-xs text-text-secondary mt-0.5">
                  Select your primary language for speech output and vocabulary
                </p>
              </div>
            </div>

            <div className="relative self-start sm:self-auto min-w-44">
              <select
                value={settings.language}
                onChange={(e) => updateSettings({ language: e.target.value })}
                className="input text-xs font-semibold pr-8 py-2 appearance-none cursor-pointer w-full"
                aria-label="Speech language"
              >
                {GNANI_LANGUAGES.map((l) => (
                  <option key={l.code} value={l.code}>
                    {l.name} ({l.native})
                  </option>
                ))}
              </select>
              <ChevronDown className="w-3.5 h-3.5 text-text-secondary absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>
          </div>

          {/* Row 2: Voice Persona (Different Persons) */}
          <div className="pt-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-purple-light text-purple flex items-center justify-center flex-shrink-0">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-navy">Voice Persona</h3>
                <p className="text-xs text-text-secondary mt-0.5">
                  Choose from 13 distinct natural voices (female and male)
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 self-start sm:self-auto">
              <div className="relative">
                <select
                  value={settings.voicePreference || 'Shivani'}
                  onChange={(e) => updateSettings({ voicePreference: e.target.value })}
                  className="input text-xs font-semibold pr-8 py-2 max-w-64 truncate appearance-none"
                  aria-label="Select voice persona"
                >
                  <optgroup label="Female Voice Personas">
                    {GNANI_VOICE_PERSONAS.filter((p) => p.gender === 'Female').map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name} — {p.description}
                      </option>
                    ))}
                  </optgroup>
                  <optgroup label="Male Voice Personas">
                    {GNANI_VOICE_PERSONAS.filter((p) => p.gender === 'Male').map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name} — {p.description}
                      </option>
                    ))}
                  </optgroup>
                </select>
                <ChevronDown className="w-3.5 h-3.5 text-text-secondary absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
              </div>

              {/* Test Voice Button */}
              <button
                type="button"
                onClick={handleTestVoice}
                disabled={isTestingVoice}
                className="btn-secondary text-xs px-3 py-2 flex items-center gap-1.5"
                title="Play test phrase with this voice"
              >
                {isTestingVoice ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-purple" />
                ) : (
                  <Play className="w-3.5 h-3.5 text-purple fill-purple" />
                )}
                <span>Test</span>
              </button>
            </div>
          </div>

          {/* Row 3: Speech rate */}
          <div className="pt-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-purple-light text-purple flex items-center justify-center flex-shrink-0">
                <Zap className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-navy">Speech rate</h3>
                <p className="text-xs text-text-secondary mt-0.5">
                  Adjust how quickly messages are spoken ({settings.speechRate}x)
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3 self-start sm:self-auto w-48">
              <input
                type="range"
                min="0.6"
                max="1.6"
                step="0.1"
                value={settings.speechRate}
                onChange={(e) => updateSettings({ speechRate: parseFloat(e.target.value) })}
                className="w-full accent-purple cursor-pointer"
                aria-label="Speech playback rate slider"
              />
            </div>
          </div>
        </div>
      </div>

      {/* 2. Personal Gnani AI Key for Different Persons */}
      <div className="card p-6 md:p-8 space-y-5 border-2 border-teal/20 bg-teal-light/10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-teal-light text-teal flex items-center justify-center flex-shrink-0">
              <Key className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-navy tracking-tight">
                Personal Gnani AI API Key
              </h2>
              <p className="text-xs text-text-secondary mt-0.5">
                Support for different persons, clinicians, or family accounts
              </p>
            </div>
          </div>
          <span className="text-[11px] font-semibold text-teal bg-teal-light/40 px-2.5 py-1 rounded-full">
            {settings.gnaniApiKey ? 'Personal Key Active' : 'System Default Key'}
          </span>
        </div>

        <p className="text-xs text-text-secondary leading-relaxed">
          Each person or care partner can optionally supply their own Gnani AI / Vachana API key
          (e.g. for individual billing or custom quotas). If left blank, Samaan AI automatically uses
          the shared system key.
        </p>

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 pt-1">
          <input
            type="password"
            value={personalApiKey}
            onChange={(e) => setPersonalApiKey(e.target.value)}
            placeholder="vach_... (leave empty to use default system key)"
            className="input flex-1 text-xs font-mono"
            aria-label="Personal Gnani AI Key"
          />
          <button
            type="button"
            onClick={handleSaveApiKey}
            className="btn-primary text-xs whitespace-nowrap"
          >
            Update Key
          </button>
          {settings.gnaniApiKey && (
            <button
              type="button"
              onClick={() => {
                setPersonalApiKey('')
                updateSettings({ gnaniApiKey: '' })
              }}
              className="btn-secondary text-xs text-red-600 hover:bg-red-50"
            >
              Reset to Default
            </button>
          )}
        </div>
      </div>

      {/* 3. Visual Comfort Section */}
      <div className="card p-6 md:p-8 space-y-6">
        <h2 className="text-base font-bold text-navy tracking-tight">Visual comfort</h2>

        <div className="divide-y divide-border space-y-6">
          {/* Row 1: Tile size */}
          <div className="pt-2 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-purple-light text-purple flex items-center justify-center flex-shrink-0">
                <HelpCircle className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-navy">Tile size</h3>
                <p className="text-xs text-text-secondary mt-0.5">Customize vocabulary tile dimensions</p>
              </div>
            </div>

            {/* Segmented Button Control */}
            <div className="inline-flex rounded-lg border border-border p-1 bg-surface self-start sm:self-auto">
              {(['small', 'medium', 'large'] as const).map((size) => (
                <button
                  key={size}
                  onClick={() => updateSettings({ tileSize: size })}
                  className={`px-3.5 py-1.5 rounded-md text-xs font-semibold capitalize transition-all ${
                    settings.tileSize === size
                      ? 'bg-purple-light text-purple font-bold shadow-xs'
                      : 'text-text-secondary hover:text-navy'
                  }`}
                >
                  {size}
                </button>
              ))}
            </div>
          </div>

          {/* Row 2: Text size */}
          <div className="pt-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-purple-light text-purple flex items-center justify-center flex-shrink-0">
                <MessageSquare className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-navy">Text size</h3>
                <p className="text-xs text-text-secondary mt-0.5">Increase text throughout SAMAAN</p>
              </div>
            </div>

            {/* Segmented Button Control */}
            <div className="inline-flex rounded-lg border border-border p-1 bg-surface self-start sm:self-auto">
              {(['normal', 'large', 'extra'] as const).map((size) => (
                <button
                  key={size}
                  onClick={() => updateSettings({ textSize: size })}
                  className={`px-3.5 py-1.5 rounded-md text-xs font-semibold capitalize transition-all ${
                    settings.textSize === size
                      ? 'bg-purple-light text-purple font-bold shadow-xs'
                      : 'text-text-secondary hover:text-navy'
                  }`}
                >
                  {size}
                </button>
              ))}
            </div>
          </div>

          {/* Row 3: High contrast */}
          <div className="pt-6 flex items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-purple-light text-purple flex items-center justify-center flex-shrink-0">
                <Shield className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-navy">High contrast</h3>
                <p className="text-xs text-text-secondary mt-0.5">
                  Increase contrast for clearer reading
                </p>
              </div>
            </div>

            {/* Toggle switch */}
            <button
              role="switch"
              aria-checked={settings.highContrast}
              onClick={() => updateSettings({ highContrast: !settings.highContrast })}
              className={`w-12 h-6 rounded-full transition-colors relative focus:outline-none focus:ring-2 focus:ring-purple/40 ${
                settings.highContrast ? 'bg-purple' : 'bg-border'
              }`}
            >
              <span
                className={`w-5 h-5 rounded-full bg-white shadow-xs absolute top-0.5 transition-transform ${
                  settings.highContrast ? 'translate-x-6' : 'translate-x-0.5'
                }`}
              />
            </button>
          </div>

          {/* Row 4: Reduced motion */}
          <div className="pt-6 flex items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-purple-light text-purple flex items-center justify-center flex-shrink-0">
                <Heart className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-navy">Reduced motion</h3>
                <p className="text-xs text-text-secondary mt-0.5">
                  Use fewer animations across the app
                </p>
              </div>
            </div>

            {/* Toggle switch */}
            <button
              role="switch"
              aria-checked={settings.reducedMotion}
              onClick={() => updateSettings({ reducedMotion: !settings.reducedMotion })}
              className={`w-12 h-6 rounded-full transition-colors relative focus:outline-none focus:ring-2 focus:ring-purple/40 ${
                settings.reducedMotion ? 'bg-purple' : 'bg-border'
              }`}
            >
              <span
                className={`w-5 h-5 rounded-full bg-white shadow-xs absolute top-0.5 transition-transform ${
                  settings.reducedMotion ? 'translate-x-6' : 'translate-x-0.5'
                }`}
              />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
