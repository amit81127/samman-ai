/**
 * SAMAAN AI — API Client
 * Coordinates all REST calls to the FastAPI backend at /api/v1
 * Supports both Cross-Origin Bearer Token Authentication and HttpOnly Cookies
 */

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
  const { method = 'GET', body, headers = {} } = options

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

  const response = await fetch(resolveUrl(path), {
    method,
    credentials: 'include',
    headers: requestHeaders,
    body: body ? (isFormData ? (body as FormData) : JSON.stringify(body)) : undefined,
  })

  if (response.status === 204) {
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
    const errorMsg = formatErrorMessage(response.status, data)
    const error = new Error(errorMsg)
    ;(error as any).status = response.status
    ;(error as any).data = data
    throw error
  }

  return data as T
}

export const api = {
  get: <T>(path: string) => request<T>(path, { method: 'GET' }),
  post: <T>(path: string, body?: unknown) => request<T>(path, { method: 'POST', body }),
  patch: <T>(path: string, body?: unknown) => request<T>(path, { method: 'PATCH', body }),
  delete: <T>(path: string) => request<T>(path, { method: 'DELETE' }),

  setToken: setAuthToken,
  getToken: getAuthToken,

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
