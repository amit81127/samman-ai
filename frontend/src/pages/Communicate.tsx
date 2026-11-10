import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import {
  Undo2,
  Trash2,
  Volume2,
  Sparkles,
  CheckCircle2,
  Bookmark,
  RefreshCw,
  Edit2,
  ShieldCheck,
  ChevronDown,
} from 'lucide-react'
import { DEFAULT_VOCAB, CATEGORIES, type VocabItem } from '../data/vocabulary'
import { api } from '../lib/api'
import { speakMessage } from '../lib/speech'
import { useSettings } from '../store/settings'
import { usePhrases } from '../store/phrases'

type Step = 'compose' | 'review' | 'speak'
const STEPS: Step[] = ['compose', 'review', 'speak']

interface Candidate {
  candidate_id: string
  text: string
  validation_status: string
  model?: string
}

interface BoardOption {
  id: string
  name: string
}

export default function Communicate() {
  const location = useLocation()
  const { settings } = useSettings()
  const { create: savePhrase } = usePhrases()

  // Boards and categories
  const [boards, setBoards] = useState<BoardOption[]>([
    { id: 'default', name: 'Default AAC Board' },
  ])
  const [selectedBoardId, setSelectedBoardId] = useState('default')
  const [activeCategory, setActiveCategory] = useState('Basic needs')
  const [vocabTiles, setVocabTiles] = useState<VocabItem[]>(DEFAULT_VOCAB)

  // Message builder state
  const [selectedWords, setSelectedWords] = useState<VocabItem[]>([])
  const [history, setHistory] = useState<VocabItem[][]>([])
  const [step, setStep] = useState<Step>('compose')

  // Server message data
  const [serverMessageId, setServerMessageId] = useState<string | null>(null)
  const [literalText, setLiteralText] = useState('')
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [selectedCandidateId, setSelectedCandidateId] = useState<string | null>(null)
  const [approvedText, setApprovedText] = useState('')
  const [isEditingApproved, setIsEditingApproved] = useState(false)
  const [manualEditText, setManualEditText] = useState('')

  // UI state
  const [isComposing, setIsComposing] = useState(false)
  const [isApproving, setIsApproving] = useState(false)
  const [isPlayingAudio, setIsPlayingAudio] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [phraseSaved, setPhraseSaved] = useState(false)

  // 1. Load boards from backend
  useEffect(() => {
    async function fetchBoards() {
      try {
        const data = await api.get<any[]>('/boards')
        if (Array.isArray(data) && data.length > 0) {
          const list = data.map((b) => ({ id: b.id, name: b.name }))
          setBoards([{ id: 'default', name: 'Default AAC Board' }, ...list])
        }
      } catch {}
    }
    fetchBoards()
  }, [])

  // 2. Load board vocabulary if custom board selected
  useEffect(() => {
    if (selectedBoardId === 'default') {
      setVocabTiles(DEFAULT_VOCAB)
      return
    }

    async function fetchBoardVocab() {
      try {
        const tiles = await api.get<any[]>(`/boards/${selectedBoardId}/vocabulary`)
        if (Array.isArray(tiles) && tiles.length > 0) {
          const mapped: VocabItem[] = tiles.map((t) => ({
            id: t.id,
            concept: t.label,
            label: t.label,
            category: t.category || 'Everyday',
            icon: '💬',
            color: t.color || '#EEF2FF',
          }))
          setVocabTiles([...DEFAULT_VOCAB, ...mapped])
        }
      } catch {
        setVocabTiles(DEFAULT_VOCAB)
      }
    }
    fetchBoardVocab()
  }, [selectedBoardId])

  // 3. Check preset from router state (e.g. Try an example from Dashboard or Open Board from Vocabulary)
  useEffect(() => {
    const navBoardId = (location.state as any)?.boardId as string | undefined
    if (navBoardId) {
      setSelectedBoardId(navBoardId)
    }

    const preset = (location.state as any)?.presetConcepts as string[] | undefined
    if (preset && preset.length > 0) {
      const items: VocabItem[] = preset.map((word) => {
        const match = DEFAULT_VOCAB.find(
          (v) => v.concept.toLowerCase() === word.toLowerCase() || v.label.toLowerCase() === word.toLowerCase()
        )
        return match || {
          id: `custom-${word}`,
          concept: word,
          label: word,
          category: 'Basic needs',
          icon: '💬',
          color: '#EEF2FF',
        }
      })
      setSelectedWords(items)
    }
  }, [location.state])

  // Tile Selection Interactions
  const pushSelection = (next: VocabItem[]) => {
    setHistory((prev) => [...prev.slice(-20), selectedWords])
    setSelectedWords(next)
  }

  const handleTileClick = (tile: VocabItem) => {
    const exists = selectedWords.find((w) => w.id === tile.id)
    if (exists) {
      // Toggle off if already selected
      pushSelection(selectedWords.filter((w) => w.id !== tile.id))
    } else {
      pushSelection([...selectedWords, tile])
    }
  }

  const handleRemoveWord = (index: number) => {
    pushSelection(selectedWords.filter((_, i) => i !== index))
  }

  const handleUndo = () => {
    if (history.length === 0) return
    const prev = history[history.length - 1]
    setSelectedWords(prev)
    setHistory((h) => h.slice(0, -1))
  }

  const handleClearAll = () => {
    pushSelection([])
    setStep('compose')
    setServerMessageId(null)
    setLiteralText('')
    setCandidates([])
    setApprovedText('')
    setErrorMessage(null)
  }

  // Phase 1 -> Phase 2: Compose Message with Backend
  const handleComposeReview = async () => {
    if (selectedWords.length === 0) return

    setIsComposing(true)
    setErrorMessage(null)

    const conceptsPayload = selectedWords.map((word, idx) => ({
      id: String(word.id),
      label: word.concept || word.label,
      position: idx,
    }))

    const fallbackLiteral = selectedWords.map((w) => w.concept || w.label).join(' ')
    setLiteralText(fallbackLiteral)

    try {
      const res = await api.post<any>('/messages/compose', {
        selected_concepts: conceptsPayload,
        request_ai_suggestions: true,
      })

      if (res) {
        setServerMessageId(res.id)
        setLiteralText(res.literal_text || fallbackLiteral)
        if (Array.isArray(res.candidates) && res.candidates.length > 0) {
          setCandidates(res.candidates)
          setSelectedCandidateId(res.candidates[0].candidate_id)
        } else {
          setCandidates([])
          setSelectedCandidateId(null)
        }
      }
    } catch (err: any) {
      setErrorMessage(
        err.message || 'AI service currently busy. You can use the literal message directly.'
      )
      setCandidates([])
      setSelectedCandidateId(null)
    } finally {
      setIsComposing(false)
      setStep('review')
    }
  }

  // Phase 2 -> Phase 3: Explicit Human Approval Invariant
  const handleApprove = async (text: string, candidateId?: string | null) => {
    setIsApproving(true)
    setErrorMessage(null)

    const finalApprovedText = text.trim()

    try {
      if (serverMessageId) {
        await api.post(`/messages/${serverMessageId}/approve`, {
          candidate_id: candidateId || null,
          approved_text: finalApprovedText,
        })
      }
      setApprovedText(finalApprovedText)
      setStep('speak')
    } catch (err: any) {
      setApprovedText(finalApprovedText)
      setStep('speak')
    } finally {
      setIsApproving(false)
    }
  }

  // Phase 3: Speak Approved Message
  const handleSpeak = async () => {
    if (!approvedText) return
    setIsPlayingAudio(true)
    try {
      await speakMessage(
        approvedText,
        serverMessageId || undefined,
        settings.speechRate,
        settings.voicePreference,
        settings.language,
        settings.gnaniApiKey
      )
    } finally {
      setIsPlayingAudio(false)
    }
  }

  // Re-edit: Invalidate approval invariant on server
  const handleReEdit = async () => {
    if (serverMessageId) {
      try {
        await api.delete(`/messages/${serverMessageId}/approval`)
      } catch {}
    }
    setStep('compose')
    setApprovedText('')
  }

  // Save to Phrases
  const handleSaveToPhrases = async () => {
    if (!approvedText) return
    try {
      await savePhrase(approvedText, 'Approved message')
      setPhraseSaved(true)
      setTimeout(() => setPhraseSaved(false), 2500)
    } catch {}
  }

  const currentCategoryTiles = vocabTiles.filter((v) => v.category === activeCategory)
  const stepIndex = STEPS.indexOf(step)

  return (
    <div className="p-6 md:p-10 max-w-6xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <p className="text-xs font-bold tracking-widest text-teal uppercase mb-1">
            COMMUNICATION BOARD
          </p>
          <h1 className="text-3xl font-extrabold text-navy tracking-tight">Build your message</h1>
          <p className="text-sm text-text-secondary mt-1">
            Select symbols to construct your sentence, review AI improvements, and approve before speaking.
          </p>
        </div>

        {/* Board & Language Selectors */}
        <div className="flex items-center gap-3 self-start md:self-auto">
          <div className="relative">
            <select
              value={selectedBoardId}
              onChange={(e) => setSelectedBoardId(e.target.value)}
              className="bg-surface border border-border rounded-btn text-xs font-semibold text-navy pl-3 pr-8 py-2 appearance-none focus:outline-none focus:ring-2 focus:ring-purple/30"
              aria-label="Select vocabulary board"
            >
              {boards.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
            <ChevronDown className="w-3.5 h-3.5 text-text-secondary absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>

          <div className="relative">
            <select
              value={settings.language}
              className="bg-surface border border-border rounded-btn text-xs font-semibold text-navy pl-3 pr-8 py-2 appearance-none focus:outline-none focus:ring-2 focus:ring-purple/30"
              aria-label="Select language"
              disabled
            >
              <option value="en">English (US)</option>
              <option value="hi">Hindi (IN)</option>
              <option value="ta">Tamil (IN)</option>
            </select>
            <ChevronDown className="w-3.5 h-3.5 text-text-secondary absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>
        </div>
      </div>

      {/* Progress Stepper (1. Compose -> 2. Review -> 3. Approve & Speak) */}
      <div className="bg-surface p-4 rounded-card border border-border shadow-xs flex items-center justify-between gap-4">
        {STEPS.map((s, idx) => {
          const isActive = step === s
          const isCompleted = idx < stepIndex
          const label =
            s === 'compose'
              ? '1. Compose'
              : s === 'review'
              ? '2. Review'
              : '3. Approve & Speak'

          return (
            <div key={s} className="flex-1 flex items-center">
              <div
                className={`flex items-center gap-2.5 text-sm font-semibold transition-colors ${
                  isActive
                    ? 'text-purple'
                    : isCompleted
                    ? 'text-success'
                    : 'text-text-secondary opacity-60'
                }`}
              >
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                    isActive
                      ? 'bg-purple text-white shadow-xs'
                      : isCompleted
                      ? 'bg-success text-white'
                      : 'bg-bg border border-border text-text-secondary'
                  }`}
                >
                  {isCompleted ? '✓' : idx + 1}
                </div>
                <span className="hidden sm:inline">{label}</span>
              </div>
              {idx < 2 && <div className="flex-1 h-0.5 bg-border mx-3 hidden sm:block" />}
            </div>
          )
        })}
      </div>

      {/* Error alert */}
      {errorMessage && (
        <div className="p-4 rounded-card bg-red-50 border border-red-200 text-sm text-red-600">
          {errorMessage}
        </div>
      )}

      {/* Main Workspace Layout */}
      <div className="grid lg:grid-cols-5 gap-8 items-start">
        {/* Left Panel: Category Tabs & Symbol Grid (3 cols) */}
        <div className="lg:col-span-3 card p-6 space-y-6">
          {/* Category Tabs */}
          <div className="flex flex-wrap gap-2 pb-2 border-b border-border">
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`px-4 py-2 rounded-full text-xs font-semibold transition-all ${
                  activeCategory === cat
                    ? 'bg-purple text-white shadow-xs'
                    : 'bg-bg text-text-secondary hover:text-navy hover:bg-purple-light/40'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Symbol Grid */}
          <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
            {currentCategoryTiles.map((tile) => {
              const isSelected = selectedWords.some((w) => w.id === tile.id)

              return (
                <button
                  key={tile.id}
                  onClick={() => handleTileClick(tile)}
                  aria-pressed={isSelected}
                  className={`aspect-square rounded-2xl flex flex-col items-center justify-center p-2 text-center transition-all select-none focus:outline-none focus:ring-2 focus:ring-purple/50 ${
                    isSelected
                      ? 'bg-purple-light border-2 border-purple shadow-xs scale-102 font-bold'
                      : 'bg-surface border border-border hover:border-purple/40 hover:bg-purple-light/20 shadow-xs'
                  }`}
                >
                  <span className="text-3xl mb-1.5">{tile.icon}</span>
                  <span
                    className={`text-xs capitalize tracking-tight ${
                      isSelected ? 'text-purple font-bold' : 'text-navy font-medium'
                    }`}
                  >
                    {tile.label}
                  </span>
                </button>
              )
            })}
          </div>
        </div>

        {/* Right Panel: Message Builder & Workflow Controller (2 cols) */}
        <div className="lg:col-span-2 space-y-5">
          {/* Active Message Card */}
          <div className="card p-6 space-y-5">
            {/* Header */}
            <div className="flex items-center justify-between pb-3 border-b border-border">
              <span className="text-xs font-bold tracking-widest text-text-secondary uppercase">
                YOUR MESSAGE
              </span>
              <span className="text-xs font-semibold px-2 py-0.5 bg-bg rounded-md text-text-secondary">
                {selectedWords.length} {selectedWords.length === 1 ? 'word' : 'words'}
              </span>
            </div>

            {/* Selected Word Chips */}
            <div className="min-h-24 p-3 rounded-xl bg-bg border border-border/80 flex flex-wrap items-center gap-2 content-start">
              {selectedWords.length === 0 ? (
                <p className="text-xs text-text-secondary text-center w-full my-auto py-4">
                  Tap symbols on the left to add words to your message.
                </p>
              ) : (
                selectedWords.map((word, i) => (
                  <span
                    key={`${word.id}-${i}`}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-purple-light text-purple text-xs font-semibold shadow-xs animate-in zoom-in-95 duration-100"
                  >
                    <span>{word.icon}</span>
                    <span>{word.label}</span>
                    <button
                      onClick={() => handleRemoveWord(i)}
                      className="ml-1 w-4 h-4 rounded-full flex items-center justify-center hover:bg-purple/20 text-purple"
                      aria-label={`Remove ${word.label}`}
                    >
                      ×
                    </button>
                  </span>
                ))
              )}
            </div>

            {/* Edit / Undo / Clear Controls */}
            <div className="flex items-center gap-2">
              <button
                onClick={handleUndo}
                disabled={history.length === 0}
                className="btn-secondary text-xs py-2 flex-1 justify-center disabled:opacity-40"
              >
                <Undo2 className="w-3.5 h-3.5" /> Undo
              </button>
              <button
                onClick={handleClearAll}
                disabled={selectedWords.length === 0}
                className="btn-secondary text-xs py-2 flex-1 justify-center disabled:opacity-40"
              >
                <Trash2 className="w-3.5 h-3.5" /> Clear all
              </button>
            </div>

            {/* STEP 1: COMPOSE STATE */}
            {step === 'compose' && (
              <div className="pt-2">
                <button
                  onClick={handleComposeReview}
                  disabled={selectedWords.length === 0 || isComposing}
                  className="btn-primary w-full justify-center py-3 text-sm shadow-md shadow-purple/20"
                >
                  {isComposing ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" /> Preparing review...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" /> Review message
                    </>
                  )}
                </button>
              </div>
            )}

            {/* STEP 2: REVIEW STATE */}
            {step === 'review' && (
              <div className="space-y-4 pt-2">
                {/* Literal Sentence Preview */}
                <div className="p-4 rounded-xl border border-border bg-surface shadow-xs space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-text-secondary uppercase">
                      Literal message
                    </span>
                    <span className="text-xs text-text-secondary">Direct sequence</span>
                  </div>
                  <p className="text-sm font-semibold text-navy">"{literalText}"</p>
                  <button
                    onClick={() => handleApprove(literalText, null)}
                    disabled={isApproving}
                    className="btn-secondary w-full justify-center text-xs py-2 mt-1"
                  >
                    Use literal message
                  </button>
                </div>

                {/* AI Improved Suggestions */}
                {candidates.length > 0 && (
                  <div className="p-4 rounded-xl border-2 border-teal/40 bg-teal-light/40 shadow-xs space-y-3">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xs font-bold text-teal uppercase flex items-center gap-1.5">
                        <Sparkles className="w-3.5 h-3.5" /> Improved with AI
                      </span>
                      {candidates[0]?.model ? (
                        <span className="text-[10px] font-semibold tracking-wide px-2 py-0.5 rounded-md bg-teal/20 text-teal border border-teal/30">
                          {candidates[0].model}
                        </span>
                      ) : (
                        <span className="text-xs text-teal font-medium">Grammar polished</span>
                      )}
                    </div>

                    {candidates.map((cand) => (
                      <div key={cand.candidate_id} className="space-y-2">
                        <p className="text-sm font-bold text-navy">"{cand.text}"</p>
                        <button
                          onClick={() => handleApprove(cand.text, cand.candidate_id)}
                          disabled={isApproving}
                          className="btn-primary w-full justify-center text-xs py-2.5 bg-teal hover:bg-[#008782] shadow-sm"
                        >
                          ✓ Approve this AI sentence
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                {/* Custom Manual Edit Option */}
                {isEditingApproved ? (
                  <div className="space-y-2">
                    <input
                      type="text"
                      value={manualEditText}
                      onChange={(e) => setManualEditText(e.target.value)}
                      className="input text-sm"
                      placeholder="Type custom exact sentence..."
                    />
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleApprove(manualEditText, null)}
                        disabled={!manualEditText.trim()}
                        className="btn-primary flex-1 text-xs py-2"
                      >
                        Approve custom
                      </button>
                      <button
                        onClick={() => setIsEditingApproved(false)}
                        className="btn-secondary text-xs py-2"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <button
                    onClick={() => {
                      setManualEditText(literalText)
                      setIsEditingApproved(true)
                    }}
                    className="w-full text-center text-xs text-text-secondary hover:text-navy flex items-center justify-center gap-1 py-1"
                  >
                    <Edit2 className="w-3 h-3" /> Or edit custom wording before approving
                  </button>
                )}

                <button
                  onClick={() => setStep('compose')}
                  className="w-full text-center text-xs text-text-secondary hover:text-navy py-1"
                >
                  ← Back to tile selection
                </button>
              </div>
            )}

            {/* STEP 3: APPROVE & SPEAK STATE */}
            {step === 'speak' && (
              <div className="space-y-4 pt-2">
                <div className="p-4 rounded-xl border-2 border-success/40 bg-success/10 space-y-2 text-center">
                  <div className="flex items-center justify-center gap-1.5 text-xs font-bold text-success uppercase">
                    <ShieldCheck className="w-4 h-4" /> APPROVED MESSAGE
                  </div>
                  <p className="text-lg font-extrabold text-navy tracking-tight py-2">
                    "{approvedText}"
                  </p>
                  <p className="text-xs text-text-secondary">
                    Verified by you. Ready for clear speech synthesis.
                  </p>
                </div>

                <div className="flex items-center justify-between px-1 text-xs text-text-secondary">
                  <span className="flex items-center gap-1 font-medium">
                    <Volume2 className="w-3.5 h-3.5 text-purple" /> Voice persona:{' '}
                    <strong className="text-navy">{settings.voicePreference || 'Shivani'}</strong> ({settings.language || 'en-IN'})
                  </span>
                  {settings.gnaniApiKey ? (
                    <span className="text-[10px] text-teal font-semibold bg-teal-light/50 px-2 py-0.5 rounded-full">Personal Key</span>
                  ) : (
                    <span className="text-[10px] text-text-secondary font-medium">Gnani AI Voice</span>
                  )}
                </div>

                {/* Play Speech CTA */}
                <button
                  onClick={handleSpeak}
                  disabled={isPlayingAudio}
                  className="btn-primary w-full justify-center py-4 text-base shadow-lg shadow-purple/25"
                >
                  <Volume2 className={`w-5 h-5 mr-1 ${isPlayingAudio ? 'animate-bounce' : ''}`} />
                  {isPlayingAudio ? 'Speaking message...' : 'Speak approved message'}
                </button>

                {/* Additional Actions */}
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={handleSaveToPhrases}
                    className="btn-secondary text-xs py-2 justify-center"
                  >
                    <Bookmark className="w-3.5 h-3.5 text-purple" />
                    {phraseSaved ? 'Saved! ✓' : 'Save to phrases'}
                  </button>
                  <button
                    onClick={handleReEdit}
                    className="btn-secondary text-xs py-2 justify-center"
                  >
                    <Edit2 className="w-3.5 h-3.5" /> Edit message
                  </button>
                </div>

                <button
                  onClick={handleClearAll}
                  className="w-full text-center text-xs text-text-secondary hover:text-navy py-1"
                >
                  Start a new message
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
