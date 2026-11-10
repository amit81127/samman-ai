/**
 * SAMAAN AI — Speech Utility Module
 * Supports Gnani AI Timbre v3.0 (multilingual, multi-persona, custom user API keys)
 * with graceful browser Web Speech API fallback.
 */

import { api } from './api'

export const GNANI_LANGUAGES = [
  { code: 'en-IN', name: 'English (India)', native: 'English' },
  { code: 'hi-IN', name: 'Hindi (हिंदी)', native: 'हिंदी' },
  { code: 'kn-IN', name: 'Kannada (ಕನ್ನಡ)', native: 'ಕನ್ನಡ' },
  { code: 'ta-IN', name: 'Tamil (தமிழ்)', native: 'தமிழ்' },
  { code: 'te-IN', name: 'Telugu (తెలుగు)', native: 'తెలుగు' },
  { code: 'ml-IN', name: 'Malayalam (മലയാളം)', native: 'മലയാളം' },
  { code: 'mr-IN', name: 'Marathi (मराठी)', native: 'मराठी' },
  { code: 'bn-IN', name: 'Bengali (বাংলা)', native: 'বাংলা' },
  { code: 'gu-IN', name: 'Gujarati (ગુજરાતી)', native: 'ગુજરાતી' },
  { code: 'pa-IN', name: 'Punjabi (ਪੰਜਾਬੀ)', native: 'ਪੰਜਾਬੀ' },
]

export const GNANI_VOICE_PERSONAS = [
  // Female personas
  { id: 'Shivani', name: 'Shivani', gender: 'Female', description: 'Warm & Expressive (Default Female)' },
  { id: 'Lakshmi', name: 'Lakshmi', gender: 'Female', description: 'Gentle & Calm' },
  { id: 'Kalpana', name: 'Kalpana', gender: 'Female', description: 'Clear & Professional' },
  { id: 'Chetana', name: 'Chetana', gender: 'Female', description: 'Lively & Cheerful' },
  { id: 'Vasudha', name: 'Vasudha', gender: 'Female', description: 'Comforting & Reassuring' },
  { id: 'Riyaa', name: 'Riyaa', gender: 'Female', description: 'Youthful & Bright' },
  { id: 'Tarika', name: 'Tarika', gender: 'Female', description: 'Dynamic & Articulate' },
  // Male personas
  { id: 'Prakash', name: 'Prakash', gender: 'Male', description: 'Natural & Friendly (Default Male)' },
  { id: 'Avinash', name: 'Avinash', gender: 'Male', description: 'Deep & Resonant' },
  { id: 'Shubham', name: 'Shubham', gender: 'Male', description: 'Warm & Conversational' },
  { id: 'Devansh', name: 'Devansh', gender: 'Male', description: 'Soft & Articulate' },
  { id: 'Yashraj', name: 'Yashraj', gender: 'Male', description: 'Energetic & Confident' },
  { id: 'Harshad', name: 'Harshad', gender: 'Male', description: 'Authoritative & Strong' },
]

export function getVoices(): SpeechSynthesisVoice[] {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) return []
  return window.speechSynthesis.getVoices()
}

// In-memory client-side audio blob cache for instantaneous replay (0ms latency)
const clientAudioCache = new Map<string, Blob>()

export function speakWithBrowser(
  text: string,
  rate = 1,
  voiceName?: string,
  lang = 'en-US'
): Promise<void> {
  return new Promise((resolve) => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      console.warn('Speech synthesis not supported in this browser')
      resolve()
      return
    }

    window.speechSynthesis.cancel()

    const utterance = new SpeechSynthesisUtterance(text)
    utterance.rate = rate
    utterance.lang = lang

    if (voiceName) {
      const voices = window.speechSynthesis.getVoices()
      const match = voices.find((v) => v.name === voiceName || v.voiceURI === voiceName)
      if (match) utterance.voice = match
    }

    utterance.onend = () => resolve()
    utterance.onerror = (e) => {
      console.warn('Browser speech synthesis error:', e)
      resolve()
    }

    window.speechSynthesis.speak(utterance)
  })
}

export async function playAudioBlob(blob: Blob): Promise<void> {
  return new Promise((resolve, reject) => {
    const audioUrl = URL.createObjectURL(blob)
    const audio = new Audio(audioUrl)

    audio.onended = () => {
      URL.revokeObjectURL(audioUrl)
      resolve()
    }
    audio.onerror = (err) => {
      URL.revokeObjectURL(audioUrl)
      reject(err)
    }

    audio.play().catch(reject)
  })
}

/**
 * Synthesizes speech:
 * 1. Attempts backend Gnani AI Timbre TTS using the chosen voice persona, language, and custom API key.
 * 2. If the backend or Gnani AI is unavailable, gracefully falls back to browser Web Speech API.
 */
export async function speakMessage(
  text: string,
  messageId?: string,
  rate = 1,
  voiceName?: string,
  language?: string,
  customApiKey?: string
): Promise<{ source: 'backend' | 'browser' }> {
  const normText = text.trim()
  const normLang = language || 'en-IN'
  const normVoice = voiceName || 'Shivani'
  const cacheKey = `${normText.toLowerCase()}:${normLang}:${normVoice}:${customApiKey || ''}`

  // 0. Check client-side memory cache for instantaneous 0ms playback
  const cachedBlob = clientAudioCache.get(cacheKey)
  if (cachedBlob) {
    try {
      await playAudioBlob(cachedBlob)
      return { source: 'backend' }
    } catch {
      clientAudioCache.delete(cacheKey)
    }
  }

  const payload = {
    language: language || undefined,
    voice: voiceName || undefined,
    api_key: customApiKey?.trim() || undefined,
  }

  // 1. Try approved message endpoint if messageId provided
  if (messageId) {
    try {
      const audioBlob = await api.getAudioBlob(`/messages/${messageId}/speech`, payload)
      // Cache in client memory (bounded to 150 entries)
      if (clientAudioCache.size >= 150) {
        const oldest = clientAudioCache.keys().next().value
        if (oldest) clientAudioCache.delete(oldest)
      }
      clientAudioCache.set(cacheKey, audioBlob)

      await playAudioBlob(audioBlob)
      return { source: 'backend' }
    } catch (err) {
      console.info('Backend message TTS failed, trying direct endpoint:', err)
    }
  }

  // 2. Direct synthesis via Gnani AI for phrases or quick text
  if (normText) {
    try {
      const audioBlob = await api.getAudioBlob('/speech/synthesize', {
        text: normText,
        ...payload,
      })
      if (clientAudioCache.size >= 150) {
        const oldest = clientAudioCache.keys().next().value
        if (oldest) clientAudioCache.delete(oldest)
      }
      clientAudioCache.set(cacheKey, audioBlob)

      await playAudioBlob(audioBlob)
      return { source: 'backend' }
    } catch (err) {
      console.info('Backend direct synthesis failed, falling back to browser:', err)
    }
  }

  // 3. Fallback to browser Web Speech API
  await speakWithBrowser(text, rate, voiceName, language)
  return { source: 'browser' }
}
