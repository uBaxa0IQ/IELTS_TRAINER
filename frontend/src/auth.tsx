import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type PropsWithChildren,
} from 'react'

import { me } from './api'
import type { AuthResponse, User } from './types'

type AuthContextValue = {
  user: User | null
  token: string | null
  ready: boolean
  setSession: (response: AuthResponse) => void
  logout: () => void
  refreshUser: () => Promise<void>
  setUser: (user: User | null) => void
}

const SESSION_KEY = 'ielts-trainer-session'

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    const raw = localStorage.getItem(SESSION_KEY)
    if (!raw) {
      setReady(true)
      return
    }

    const session = JSON.parse(raw) as { token: string }
    me(session.token)
      .then((nextUser) => {
        setToken(session.token)
        setUser(nextUser)
      })
      .catch(() => {
        localStorage.removeItem(SESSION_KEY)
      })
      .finally(() => setReady(true))
  }, [])

  const setSession = useCallback((response: AuthResponse) => {
    setUser(response.user)
    setToken(response.access_token)
    localStorage.setItem(SESSION_KEY, JSON.stringify({ token: response.access_token }))
  }, [])

  const refreshUser = useCallback(async () => {
    const raw = localStorage.getItem(SESSION_KEY)
    if (!raw) return
    const session = JSON.parse(raw) as { token: string }
    const nextUser = await me(session.token)
    setUser(nextUser)
  }, [])

  const setUserDirect = useCallback((next: User | null) => {
    setUser(next)
  }, [])

  const logout = useCallback(() => {
    setUser(null)
    setToken(null)
    localStorage.removeItem(SESSION_KEY)
  }, [])

  const value = useMemo(
    () => ({
      user,
      token,
      ready,
      setSession,
      logout,
      refreshUser,
      setUser: setUserDirect,
    }),
    [logout, ready, refreshUser, setSession, setUserDirect, token, user],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
