/**
 * SAMAAN AI — API Client
 * Coordinates all REST calls to the FastAPI backend at /api/v1
 * Supports both Cross-Origin Bearer Token Authentication and HttpOnly Cookies
 */

import { telemetry } from './telemetry'

const TOKEN_KEY = 'samaan_access_token'

let inMemoryToken: string | null = null

export function setAuthToken(token: string | null) {
  inMemoryToken = token
  if (token) {
    try {
      localStorage.setItem(TOKEN_KEY, token)
    } catch {}
  } else {
    try {
      localStorage.removeItem(TOKEN_KEY)
    } catch {}
  }
}

export function getAuthToken(): string | null {
  if (inMemoryToken) return inMemoryToken
  try {
    const saved = localStorage.getItem(TOKEN_KEY)
    if (saved) {
      inMemoryToken = saved
      return saved
    }
  } catch {}
  return null
}

const BACKEND_URL = (import.meta.env.VITE_BACKEND_URL || '').replace(/\/+$/, '')
const BASE_URL = BACKEND_URL ? `${BACKEND_URL}/api/v1` : '/api/v1'

interface RequestOptions {
  method?: string
  body?: unknown
  headers?: Record<string, string>
  signal?: AbortSignal
  skipCache?: boolean
}

// Client-side query cache (5 min staleTime, 30 min gcTime)
interface CacheEntry<T> {
  data: T
  expiresAt: number
}

const queryCache = new Map<string, CacheEntry<any>>()
const inFlightRequests = new Map<string, Promise<any>>()

export function invalidateCache(prefix?: string) {
  if (!prefix) {
    queryCache.clear()
    return
  }
  for (const key of queryCache.keys()) {
    if (key.includes(prefix)) {
      queryCache.delete(key)
    }
  }
}

function resolveUrl(path: string): string {
  const cleanPath = path.startsWith('/') ? path : `/${path}`
  return `${BASE_URL}${cleanPath}`
}

function formatErrorMessage(status: number, data: any): string {
  if (!data) return `Request failed with status ${status}`
  if (typeof data === 'string') return data

  // Handle FastAPI 422 validation errors array
  if (Array.isArray(data.detail)) {
    return data.detail
      .map((item: any) => {
        const loc = Array.isArray(item.loc) ? item.loc.slice(1).join('.') : ''
        return loc ? `${loc}: ${item.msg}` : item.msg || 'Invalid input'
      })
      .join(', ')
  }

  // Handle structured detail object { code, message }
  if (typeof data.detail === 'object' && data.detail?.message) {
    return data.detail.message
  }

  // Handle plain string detail
  if (typeof data.detail === 'string') {
    return data.detail
  }

  // Handle message field
  if (typeof data.message === 'string') {
    return data.message
  }

  return `Request failed with status ${status}`
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, headers = {}, signal, skipCache = false } = options
  const upperMethod = method.toUpperCase()
  const cacheKey = `${upperMethod}:${path}`

  // 1. Client-Side Read Cache for GET requests (5-minute TTL)
  if (upperMethod === 'GET' && !skipCache) {
    const cached = queryCache.get(cacheKey)
    if (cached && Date.now() < cached.expiresAt) {
      return cached.data as T
    }

    // Single-Flight Deduplication for identical in-flight GET requests
    const inFlight = inFlightRequests.get(cacheKey)
    if (inFlight) {
      return (await inFlight) as T
    }
  }

  const isFormData = typeof FormData !== 'undefined' && body instanceof FormData
  const requestHeaders: Record<string, string> = { ...headers }
  if (!isFormData) {
    requestHeaders['Content-Type'] = 'application/json'
  }

  // Inject Bearer token if available
  const token = getAuthToken()
  if (token && !requestHeaders['Authorization']) {
    requestHeaders['Authorization'] = `Bearer ${token}`
  }

  const fetchPromise = (async () => {
    const startMs = performance.now()
    try {
      const response = await fetch(resolveUrl(path), {
        method: upperMethod,
        credentials: 'include',
        headers: requestHeaders,
        signal,
        body: body ? (isFormData ? (body as FormData) : JSON.stringify(body)) : undefined,
      })

      if (response.status === 204) {
        telemetry.recordApiRequest(performance.now() - startMs, true)
        return undefined as unknown as T
      }

      let data: any
      const contentType = response.headers.get('content-type') || ''
      if (contentType.includes('application/json')) {
        data = await response.json().catch(() => null)
      } else {
        data = await response.text().catch(() => null)
      }

      // Handle 401 Unauthorized by clearing stale token (except on login/register endpoints)
      if (response.status === 401 && !path.includes('/auth/login') && !path.includes('/auth/register')) {
        setAuthToken(null)
      }

      if (!response.ok) {
        telemetry.recordApiRequest(performance.now() - startMs, false)
        const errorMsg = formatErrorMessage(response.status, data)
        const error = new Error(errorMsg)
        ;(error as any).status = response.status
        ;(error as any).data = data
        throw error
      }

      telemetry.recordApiRequest(performance.now() - startMs, true)

      // Cache successful GET responses for 5 minutes
      if (upperMethod === 'GET' && !skipCache) {
        queryCache.set(cacheKey, {
          data,
          expiresAt: Date.now() + 5 * 60 * 1000,
        })
      } else if (upperMethod !== 'GET') {
        // Invalidate relevant query cache on mutations
        if (path.includes('/boards')) invalidateCache('/boards')
        if (path.includes('/phrases')) invalidateCache('/phrases')
        if (path.includes('/vocabulary')) {
          invalidateCache('/vocabulary')
          invalidateCache('/boards')
        }
        if (path.includes('/users') || path.includes('/profile')) invalidateCache('/users')
        if (path.includes('/partners')) invalidateCache('/partners')
      }

      return data as T
    } catch (err) {
      telemetry.recordApiRequest(performance.now() - startMs, false)
      throw err
    }
  })()

  if (upperMethod === 'GET' && !skipCache) {
    inFlightRequests.set(cacheKey, fetchPromise)
    try {
      return await fetchPromise
    } finally {
      inFlightRequests.delete(cacheKey)
    }
  }

  return await fetchPromise
}

export const api = {
  get: <T>(path: string, options?: { signal?: AbortSignal; skipCache?: boolean }) =>
    request<T>(path, { method: 'GET', ...options }),
  post: <T>(path: string, body?: unknown, options?: { signal?: AbortSignal }) =>
    request<T>(path, { method: 'POST', body, ...options }),
  patch: <T>(path: string, body?: unknown, options?: { signal?: AbortSignal }) =>
    request<T>(path, { method: 'PATCH', body, ...options }),
  delete: <T>(path: string, options?: { signal?: AbortSignal }) =>
    request<T>(path, { method: 'DELETE', ...options }),

  setToken: setAuthToken,
  getToken: getAuthToken,
  invalidate: invalidateCache,

  /** For speech synthesis endpoint which returns audio/wav */
  getAudioBlob: async (path: string, body?: unknown): Promise<Blob> => {
    const token = getAuthToken()
    const headers: Record<string, string> = body ? { 'Content-Type': 'application/json' } : {}
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const res = await fetch(resolveUrl(path), {
      method: 'POST',
      credentials: 'include',
      headers,
      body: body ? JSON.stringify(body) : undefined,
    })

    if (!res.ok) {
      let errText = 'Speech synthesis failed'
      try {
        const json = await res.json()
        errText = formatErrorMessage(res.status, json)
      } catch {}
      throw new Error(errText)
    }
    return await res.blob()
  },
}
