import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type PropsWithChildren,
} from 'react'

import { me, refreshSession, SESSION_KEY, SESSION_REFRESHED_EVENT } from './api'
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

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

type StoredSession = {
  access_token?: string
  refresh_token?: string
  /** legacy */
  token?: string
}

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    const onSessionRefreshed = (e: Event) => {
      const d = (e as CustomEvent<{ access_token?: string }>).detail
      if (d?.access_token) setToken(d.access_token)
    }
    window.addEventListener(SESSION_REFRESHED_EVENT, onSessionRefreshed)
    return () => window.removeEventListener(SESSION_REFRESHED_EVENT, onSessionRefreshed)
  }, [])

  useEffect(() => {
    const raw = localStorage.getItem(SESSION_KEY)
    if (!raw) {
      setReady(true)
      return
    }

    let session: StoredSession
    try {
      session = JSON.parse(raw) as StoredSession
    } catch {
      setReady(true)
      return
    }

    const access = session.access_token ?? session.token
    const refreshTok = session.refresh_token ?? ''

    if (!access) {
      setReady(true)
      return
    }

    const persist = (access_token: string, refresh_token: string) => {
      localStorage.setItem(SESSION_KEY, JSON.stringify({ access_token, refresh_token }))
    }

    void me(access)
      .then((nextUser) => {
        setToken(access)
        setUser(nextUser)
        persist(access, refreshTok)
      })
      .catch(async () => {
        if (!refreshTok) {
          localStorage.removeItem(SESSION_KEY)
          return
        }
        try {
          const auth = await refreshSession(refreshTok)
          setToken(auth.access_token)
          setUser(auth.user)
        } catch {
          localStorage.removeItem(SESSION_KEY)
        }
      })
      .finally(() => setReady(true))
  }, [])

  const setSession = useCallback((response: AuthResponse) => {
    setUser(response.user)
    setToken(response.access_token)
    localStorage.setItem(
      SESSION_KEY,
      JSON.stringify({
        access_token: response.access_token,
        refresh_token: response.refresh_token,
      }),
    )
  }, [])

  const refreshUser = useCallback(async () => {
    const raw = localStorage.getItem(SESSION_KEY)
    if (!raw) return
    let session: StoredSession
    try {
      session = JSON.parse(raw) as StoredSession
    } catch {
      return
    }
    const access = session.access_token ?? session.token
    if (!access) return
    const nextUser = await me(access)
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
