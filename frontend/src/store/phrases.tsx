import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'
import { api } from '../lib/api'

export interface Phrase {
  id: string
  text: string
  label?: string
  language?: string
  source?: string
  is_favorite: boolean
  created_at?: string
}

interface PhrasesContextType {
  phrases: Phrase[]
  loading: boolean
  load: () => Promise<void>
  create: (text: string, label?: string) => Promise<Phrase>
  update: (id: string, patch: Partial<Phrase>) => Promise<void>
  remove: (id: string) => Promise<void>
  toggleFavorite: (id: string) => void
}

const PhrasesContext = createContext<PhrasesContextType>(null!)

export const usePhrases = () => useContext(PhrasesContext)

export function PhrasesProvider({ children }: { children: ReactNode }) {
  const [phrases, setPhrases] = useState<Phrase[]>([])
  const [loading, setLoading] = useState(false)

  const getFavoriteIds = (): string[] => {
    try {
      return JSON.parse(localStorage.getItem('samaan_fav_phrases') || '[]')
    } catch {
      return []
    }
  }

  const setFavoriteIds = (ids: string[]) => {
    localStorage.setItem('samaan_fav_phrases', JSON.stringify(ids))
  }

  const load = useCallback(async () => {
    if (!api.getToken()) {
      setPhrases([])
      return
    }
    setLoading(true)
    const favIds = new Set(getFavoriteIds())

    try {
      const data = await api.get<any[]>('/phrases')
      if (Array.isArray(data)) {
        const mapped: Phrase[] = data.map((item) => {
          const id = String(item.id || item._id)
          return {
            id,
            text: item.text,
            label: item.label,
            language: item.language || 'en',
            source: item.source || 'manual',
            is_favorite: favIds.has(id),
            created_at: item.created_at,
          }
        })
        setPhrases(mapped)
      } else {
        setPhrases([])
      }
    } catch {
      setPhrases([])
    } finally {
      setLoading(false)
    }
  }, [])

  const create = useCallback(
    async (text: string, label?: string): Promise<Phrase> => {
      const res = await api.post<any>('/phrases', {
        text,
        label: label || undefined,
        language: 'en',
        source: 'manual',
      })
      const createdPhrase: Phrase = {
        id: String(res.id || res._id),
        text: res.text,
        label: res.label,
        language: res.language || 'en',
        source: res.source || 'manual',
        is_favorite: false,
        created_at: res.created_at,
      }
      setPhrases((prev) => [createdPhrase, ...prev])
      return createdPhrase
    },
    []
  )

  const update = useCallback(async (id: string, patch: Partial<Phrase>) => {
    setPhrases((prev) => prev.map((p) => (p.id === id ? { ...p, ...patch } : p)))
    try {
      await api.patch(`/phrases/${id}`, {
        text: patch.text,
        label: patch.label,
        language: patch.language,
      })
    } catch (err) {
      console.error('Failed to update phrase:', err)
    }
  }, [])

  const remove = useCallback(async (id: string) => {
    setPhrases((prev) => prev.filter((p) => p.id !== id))
    const favIds = getFavoriteIds().filter((fId) => fId !== id)
    setFavoriteIds(favIds)
    try {
      await api.delete(`/phrases/${id}`)
    } catch (err) {
      console.error('Failed to delete phrase:', err)
    }
  }, [])

  const toggleFavorite = useCallback((id: string) => {
    let currentFavs = getFavoriteIds()
    const isFav = currentFavs.includes(id)
    if (isFav) {
      currentFavs = currentFavs.filter((fId) => fId !== id)
    } else {
      currentFavs = [...currentFavs, id]
    }
    setFavoriteIds(currentFavs)

    setPhrases((prev) =>
      prev.map((p) => (p.id === id ? { ...p, is_favorite: !isFav } : p))
    )
  }, [])

  return (
    <PhrasesContext.Provider
      value={{ phrases, loading, load, create, update, remove, toggleFavorite }}
    >
      {children}
    </PhrasesContext.Provider>
  )
}
