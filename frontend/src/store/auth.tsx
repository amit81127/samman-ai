import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'
import { api } from '../lib/api'

export interface User {
  id: string
  email: string
  language: string
  name?: string
  access_token?: string
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, language?: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType>(null!)

export const useAuth = () => useContext(AuthContext)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function checkAuth() {
      // Check if access token exists in localStorage or memory
      const token = api.getToken()
      if (!token) {
        setUser(null)
        setLoading(false)
        return
      }

      try {
        const u = await api.get<User>('/auth/me')
        setUser({
          ...u,
          name: u.email.split('@')[0].replace(/[._]/g, ' '),
        })
      } catch {
        // Token invalid or expired — clear it safely
        api.setToken(null)
        setUser(null)
      } finally {
        setLoading(false)
      }
    }

    checkAuth()
  }, [])

  async function login(email: string, password: string) {
    const res = await api.post<any>('/auth/login', { email, password })
    if (res?.access_token) {
      api.setToken(res.access_token)
    }
    const userObj: User = {
      id: String(res.id || res._id),
      email: res.email,
      language: res.language || 'en',
      name: res.email.split('@')[0].replace(/[._]/g, ' '),
      access_token: res.access_token,
    }
    setUser(userObj)
  }

  async function register(email: string, password: string, language = 'en') {
    const res = await api.post<any>('/auth/register', { email, password, language })
    if (res?.access_token) {
      api.setToken(res.access_token)
    }
    const userObj: User = {
      id: String(res.id || res._id),
      email: res.email,
      language: res.language || language,
      name: res.email.split('@')[0].replace(/[._]/g, ' '),
      access_token: res.access_token,
    }
    setUser(userObj)
  }

  async function logout() {
    try {
      await api.post('/auth/logout')
    } catch {}
    api.setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}
