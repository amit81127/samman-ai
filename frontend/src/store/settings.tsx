import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'
import { api } from '../lib/api'
import { useAuth } from './auth'

export interface AccessibilitySettings {
  language: string
  voicePreference: string
  gnaniApiKey?: string
  speechRate: number
  tileSize: 'small' | 'medium' | 'large'
  textSize: 'normal' | 'large' | 'extra'
  highContrast: boolean
  reducedMotion: boolean
}

const defaultSettings: AccessibilitySettings = {
  language: 'en-IN',
  voicePreference: 'Shivani',
  gnaniApiKey: '',
  speechRate: 1,
  tileSize: 'medium',
  textSize: 'normal',
  highContrast: false,
  reducedMotion: false,
}

interface SettingsContextType {
  settings: AccessibilitySettings
  updateSettings: (patch: Partial<AccessibilitySettings>) => Promise<void>
  lastSaved: boolean
}

const SettingsContext = createContext<SettingsContextType>(null!)

export const useSettings = () => useContext(SettingsContext)

export function SettingsProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth()
  const [settings, setSettings] = useState<AccessibilitySettings>(() => {
    try {
      const saved = localStorage.getItem('samaan_accessibility_settings')
      return saved ? { ...defaultSettings, ...JSON.parse(saved) } : defaultSettings
    } catch {
      return defaultSettings
    }
  })
  const [lastSaved, setLastSaved] = useState(false)

  // Sync settings from backend profile when user logs in
  useEffect(() => {
    if (!user) return

    async function loadBackendProfile() {
      try {
        const profile = await api.get<any>('/profile')
        if (profile) {
          setSettings((prev) => {
            const next: AccessibilitySettings = {
              ...prev,
              language: profile.language || prev.language,
              voicePreference: profile.voice_preference || prev.voicePreference,
              gnaniApiKey: profile.gnani_api_key ?? prev.gnaniApiKey,
              tileSize: (profile.tile_size as any) || prev.tileSize,
              textSize: profile.text_size === 'xlarge' ? 'extra' : (profile.text_size as any) || prev.textSize,
              highContrast: Boolean(profile.contrast_mode ?? prev.highContrast),
              reducedMotion: Boolean(profile.reduced_motion ?? prev.reducedMotion),
            }
            localStorage.setItem('samaan_accessibility_settings', JSON.stringify(next))
            return next
          })
        }
      } catch {
        // Backend profile optional / fallback to localStorage
      }
    }

    loadBackendProfile()
  }, [user])

  // Apply visual comfort classes to document root
  useEffect(() => {
    const root = document.documentElement

    // High contrast
    root.classList.toggle('high-contrast', settings.highContrast)

    // Reduced motion
    root.classList.toggle('reduced-motion', settings.reducedMotion)

    // Text size
    root.classList.remove('text-size-normal', 'text-size-large', 'text-size-extra')
    root.classList.add(`text-size-${settings.textSize}`)

    // Tile size
    root.classList.remove('tile-size-small', 'tile-size-medium', 'tile-size-large')
    root.classList.add(`tile-size-${settings.tileSize}`)
  }, [settings])

  async function updateSettings(patch: Partial<AccessibilitySettings>): Promise<void> {
    const updated = { ...settings, ...patch }
    setSettings(updated)
    localStorage.setItem('samaan_accessibility_settings', JSON.stringify(updated))
    setLastSaved(true)

    setTimeout(() => setLastSaved(false), 2500)

    if (user) {
      try {
        await api.patch('/profile', {
          language: patch.language,
          voice_preference: patch.voicePreference || undefined,
          gnani_api_key: patch.gnaniApiKey !== undefined ? patch.gnaniApiKey : undefined,
          tile_size: patch.tileSize,
          text_size: patch.textSize === 'extra' ? 'xlarge' : patch.textSize,
          contrast_mode: patch.highContrast,
          reduced_motion: patch.reducedMotion,
        })
      } catch {
        // Backend sync failure will not break client preference persistence
      }
    }
  }

  return (
    <SettingsContext.Provider value={{ settings, updateSettings, lastSaved }}>
      {children}
    </SettingsContext.Provider>
  )
}
