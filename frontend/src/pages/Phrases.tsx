import React, { useEffect, useState, useDeferredValue, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Search,
  Heart,
  Volume2,
  Trash2,
  Plus,
  ArrowRight,
  Edit3,
  Bookmark,
  MessageSquare,
  Sparkles,
} from 'lucide-react'
import { usePhrases, type Phrase } from '../store/phrases'
import { speakMessage } from '../lib/speech'
import { useSettings } from '../store/settings'

export default function Phrases() {
  const { phrases, loading, load, create, update, remove, toggleFavorite } = usePhrases()
  const { settings } = useSettings()
  const navigate = useNavigate()

  const [searchQuery, setSearchQuery] = useState('')
  const deferredSearch = useDeferredValue(searchQuery)
  const [activeFilter, setActiveFilter] = useState<'all' | 'favorites'>('all')

  // Form states
  const [isAdding, setIsAdding] = useState(false)
  const [newText, setNewText] = useState('')
  const [newLabel, setNewLabel] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Edit states
  const [editingPhrase, setEditingPhrase] = useState<Phrase | null>(null)
  const [editText, setEditText] = useState('')
  const [editLabel, setEditLabel] = useState('')

  // Speech playing indicator
  const [playingId, setPlayingId] = useState<string | null>(null)

  useEffect(() => {
    load()
  }, [load])

  const filteredPhrases = useMemo(() => {
    return phrases.filter((p) => {
      if (activeFilter === 'favorites' && !p.is_favorite) return false
      if (deferredSearch.trim()) {
        const q = deferredSearch.toLowerCase()
        const textMatch = p.text.toLowerCase().includes(q)
        const labelMatch = p.label ? p.label.toLowerCase().includes(q) : false
        if (!textMatch && !labelMatch) return false
      }
      return true
    })
  }, [phrases, activeFilter, deferredSearch])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newText.trim()) return

    setIsSubmitting(true)
    try {
      await create(newText.trim(), newLabel.trim() || undefined)
      setNewText('')
      setNewLabel('')
      setIsAdding(false)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleStartEdit = (p: Phrase) => {
    setEditingPhrase(p)
    setEditText(p.text)
    setEditLabel(p.label || '')
  }

  const handleSaveEdit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingPhrase || !editText.trim()) return

    try {
      await update(editingPhrase.id, {
        text: editText.trim(),
        label: editLabel.trim() || undefined,
      })
      setEditingPhrase(null)
    } catch {}
  }

  const handlePlaySpeech = async (phrase: Phrase) => {
    setPlayingId(phrase.id)
    try {
      await speakMessage(
        phrase.text,
        undefined,
        settings.speechRate,
        settings.voicePreference,
        settings.language,
        settings.gnaniApiKey
      )
    } finally {
      setPlayingId(null)
    }
  }

  const handleLoadToBoard = (phrase: Phrase) => {
    // Splits phrase into words/concepts for the communication board
    const words = phrase.text.replace(/[.,?!]/g, '').split(/\s+/).filter(Boolean)
    navigate('/communicate', { state: { presetConcepts: words } })
  }

  return (
    <div className="p-6 md:p-10 max-w-5xl mx-auto space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <p className="text-xs font-bold tracking-widest text-teal uppercase mb-1">
            YOUR LIBRARY
          </p>
          <h1 className="text-3xl font-extrabold text-navy tracking-tight">Saved phrases</h1>
          <p className="text-sm text-text-secondary mt-1">
            Keep your most important sentences ready to speak or load onto your board in one tap.
          </p>
        </div>
        <button
          onClick={() => setIsAdding(true)}
          className="btn-primary shadow-md shadow-purple/20 self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" /> Add phrase
        </button>
      </div>

      {/* Add New Phrase Card */}
      {isAdding && (
        <div className="card p-6 border-2 border-purple/30 bg-purple-light/20 shadow-card animate-in fade-in">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-bold text-navy flex items-center gap-2">
              <Bookmark className="w-4 h-4 text-purple" /> Add new phrase to library
            </h3>
            <button
              onClick={() => setIsAdding(false)}
              className="text-xs text-text-secondary hover:text-navy"
            >
              Cancel
            </button>
          </div>
          <form onSubmit={handleCreate} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-navy uppercase tracking-wider mb-1">
                Phrase sentence
              </label>
              <input
                autoFocus
                type="text"
                required
                value={newText}
                onChange={(e) => setNewText(e.target.value)}
                placeholder="e.g. Please bring me a glass of warm water"
                className="input"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-navy uppercase tracking-wider mb-1">
                Category label (optional)
              </label>
              <input
                type="text"
                value={newLabel}
                onChange={(e) => setNewLabel(e.target.value)}
                placeholder="e.g. Basic needs, Health, Comfort"
                className="input"
              />
            </div>
            <div className="flex items-center gap-3 pt-2">
              <button
                type="submit"
                disabled={isSubmitting || !newText.trim()}
                className="btn-primary"
              >
                {isSubmitting ? 'Saving...' : 'Save phrase'}
              </button>
              <button
                type="button"
                onClick={() => setIsAdding(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Edit Phrase Modal/Card */}
      {editingPhrase && (
        <div className="card p-6 border-2 border-teal/40 bg-teal-light/20 shadow-card animate-in fade-in">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-bold text-navy flex items-center gap-2">
              <Edit3 className="w-4 h-4 text-teal" /> Edit phrase
            </h3>
            <button
              onClick={() => setEditingPhrase(null)}
              className="text-xs text-text-secondary hover:text-navy"
            >
              Cancel
            </button>
          </div>
          <form onSubmit={handleSaveEdit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-navy uppercase tracking-wider mb-1">
                Phrase sentence
              </label>
              <input
                autoFocus
                type="text"
                required
                value={editText}
                onChange={(e) => setEditText(e.target.value)}
                className="input"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-navy uppercase tracking-wider mb-1">
                Category label
              </label>
              <input
                type="text"
                value={editLabel}
                onChange={(e) => setEditLabel(e.target.value)}
                className="input"
              />
            </div>
            <div className="flex items-center gap-3 pt-2">
              <button
                type="submit"
                disabled={!editText.trim()}
                className="btn-primary bg-teal hover:bg-[#008782]"
              >
                Update phrase
              </button>
              <button
                type="button"
                onClick={() => setEditingPhrase(null)}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Search and Filters Controls */}
      <div className="flex flex-col sm:flex-row gap-3">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-text-secondary" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search saved phrases..."
            className="input pl-10"
          />
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveFilter('all')}
            className={`px-4 py-2 rounded-btn text-xs font-semibold transition-all ${
              activeFilter === 'all'
                ? 'bg-purple text-white shadow-xs'
                : 'bg-surface border border-border text-text-secondary hover:bg-bg hover:text-navy'
            }`}
          >
            All phrases
          </button>
          <button
            onClick={() => setActiveFilter('favorites')}
            className={`px-4 py-2 rounded-btn text-xs font-semibold flex items-center gap-1.5 transition-all ${
              activeFilter === 'favorites'
                ? 'bg-purple text-white shadow-xs'
                : 'bg-surface border border-border text-text-secondary hover:bg-bg hover:text-navy'
            }`}
          >
            <Heart className="w-3.5 h-3.5" fill={activeFilter === 'favorites' ? 'white' : 'none'} />
            Favorites
          </button>
        </div>
      </div>

      {/* Phrases List */}
      {loading ? (
        <div className="text-center py-16 text-text-secondary">
          <div className="w-8 h-8 border-2 border-purple border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm font-medium">Loading saved phrases...</p>
        </div>
      ) : filteredPhrases.length === 0 ? (
        <div className="card p-12 text-center space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-purple-light text-purple flex items-center justify-center mx-auto text-2xl">
            💬
          </div>
          <div>
            <h3 className="text-base font-bold text-navy">
              {searchQuery ? 'No matching phrases found' : 'No saved phrases yet'}
            </h3>
            <p className="text-xs text-text-secondary mt-1 max-w-sm mx-auto">
              {searchQuery
                ? 'Try a different search query or clear the filter.'
                : 'Save frequently used sentences to quickly speak them anytime.'}
            </p>
          </div>
          {!searchQuery && (
            <button onClick={() => setIsAdding(true)} className="btn-primary text-xs">
              <Plus className="w-3.5 h-3.5" /> Create your first phrase
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {filteredPhrases.map((phrase) => {
            const isPlaying = playingId === phrase.id

            return (
              <div
                key={phrase.id}
                className="card p-4 md:p-5 flex items-center justify-between gap-4 hover:border-purple/30 transition-all group"
              >
                {/* Left: Symbol Icon & Text */}
                <div className="flex items-center gap-4 min-w-0 flex-1">
                  <div className="w-10 h-10 rounded-xl bg-purple-light flex items-center justify-center text-xl flex-shrink-0 group-hover:scale-105 transition-transform">
                    💬
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm md:text-base font-bold text-navy tracking-tight truncate">
                      {phrase.text}
                    </p>
                    <div className="flex items-center gap-2 mt-0.5">
                      {phrase.label ? (
                        <span className="text-xs font-semibold px-2 py-0.5 bg-bg rounded-md text-teal">
                          {phrase.label}
                        </span>
                      ) : (
                        <span className="text-xs text-text-secondary">Phrase</span>
                      )}
                      {phrase.source === 'approved_message' && (
                        <span className="text-xs text-purple font-medium flex items-center gap-1">
                          <Sparkles className="w-3 h-3" /> from board
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Right: Actions */}
                <div className="flex items-center gap-2 flex-shrink-0">
                  {/* Favorite toggle */}
                  <button
                    onClick={() => toggleFavorite(phrase.id)}
                    className={`w-9 h-9 rounded-xl flex items-center justify-center transition-colors ${
                      phrase.is_favorite
                        ? 'text-pink-500 bg-pink-50 hover:bg-pink-100'
                        : 'text-text-secondary hover:text-pink-500 hover:bg-pink-50'
                    }`}
                    title={phrase.is_favorite ? 'Remove favorite' : 'Add to favorites'}
                    aria-label="Toggle favorite"
                  >
                    <Heart
                      className="w-4 h-4"
                      fill={phrase.is_favorite ? 'currentColor' : 'none'}
                    />
                  </button>

                  {/* Play audio */}
                  <button
                    onClick={() => handlePlaySpeech(phrase)}
                    disabled={isPlaying}
                    className="w-9 h-9 rounded-xl border border-border flex items-center justify-center text-teal hover:bg-teal-light hover:border-teal/40 transition-colors"
                    title="Speak phrase"
                    aria-label="Speak phrase"
                  >
                    <Volume2 className={`w-4 h-4 ${isPlaying ? 'animate-bounce' : ''}`} />
                  </button>

                  {/* Load to communication board */}
                  <button
                    onClick={() => handleLoadToBoard(phrase)}
                    className="w-9 h-9 rounded-xl border border-border flex items-center justify-center text-purple hover:bg-purple-light hover:border-purple/40 transition-colors"
                    title="Load to communication board"
                    aria-label="Load to board"
                  >
                    <ArrowRight className="w-4 h-4" />
                  </button>

                  {/* Edit */}
                  <button
                    onClick={() => handleStartEdit(phrase)}
                    className="w-9 h-9 rounded-xl border border-border flex items-center justify-center text-text-secondary hover:text-navy hover:bg-bg transition-colors"
                    title="Edit phrase"
                    aria-label="Edit phrase"
                  >
                    <Edit3 className="w-4 h-4" />
                  </button>

                  {/* Delete */}
                  <button
                    onClick={() => remove(phrase.id)}
                    className="w-9 h-9 rounded-xl flex items-center justify-center text-text-secondary hover:text-red-500 hover:bg-red-50 transition-colors"
                    title="Delete phrase"
                    aria-label="Delete phrase"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
