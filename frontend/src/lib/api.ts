/**
 * SAMAAN AI — API Client
 * Coordinates all REST calls to the FastAPI backend at /api/v1
 */

const BASE_URL = '/api/v1'

interface RequestOptions {
  method?: string
  body?: unknown
  headers?: Record<string, string>
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, headers = {} } = options

  const isFormData = typeof FormData !== 'undefined' && body instanceof FormData
  const requestHeaders: Record<string, string> = { ...headers }
  if (!isFormData) {
    requestHeaders['Content-Type'] = 'application/json'
  }

  const response = await fetch(`${BASE_URL}${path}`, {
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

  if (!response.ok) {
    const errorMsg =
      (data && typeof data === 'object' && (data.detail?.message || data.detail || data.message)) ||
      (typeof data === 'string' && data) ||
      `Request failed with status ${response.status}`
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

  /** For speech synthesis endpoint which returns audio/wav */
  getAudioBlob: async (path: string, body?: unknown): Promise<Blob> => {
    const res = await fetch(`${BASE_URL}${path}`, {
      method: 'POST',
      credentials: 'include',
      headers: body ? { 'Content-Type': 'application/json' } : {},
      body: body ? JSON.stringify(body) : undefined,
    })
    if (!res.ok) {
      let errText = 'Speech synthesis failed'
      try {
        const json = await res.json()
        errText = json.detail?.message || json.detail || errText
      } catch {}
      throw new Error(errText)
    }
    return await res.blob()
  },
}
