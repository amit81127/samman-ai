import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'
import { api } from '../lib/api'

export interface User {
  id: string
  email: string
  language: string
  name?: string
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
      try {
        const u = await api.get<User>('/auth/me')
        setUser({
          ...u,
          name: u.email.split('@')[0].replace(/[._]/g, ' '),
        })
      } catch {
        setUser(null)
      } finally {
        setLoading(false)
      }
    }

    checkAuth()
  }, [])

  async function login(email: string, password: string) {
    const res = await api.post<User>('/auth/login', { email, password })
    const userObj = {
      ...res,
      name: res.email.split('@')[0].replace(/[._]/g, ' '),
    }
    setUser(userObj)
  }

  async function register(email: string, password: string, language = 'en') {
    const res = await api.post<User>('/auth/register', { email, password, language })
    const userObj = {
      ...res,
      name: res.email.split('@')[0].replace(/[._]/g, ' '),
    }
    setUser(userObj)
  }

  async function logout() {
    try {
      await api.post('/auth/logout')
    } catch {}
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}
