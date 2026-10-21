import { useQuery, useQueryClient } from '@tanstack/react-query'
import { createContext, useCallback, useContext, useEffect, useMemo, type ReactNode } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { ApiError, onUnauthenticated, setCsrfToken } from '../lib/api'
import { authApi, type AuthState } from '../lib/authApi'

interface AuthContextValue {
  state: AuthState | undefined
  loading: boolean
  /** Set when the API cannot be reached or is still starting. */
  unavailable: boolean
  refresh: () => Promise<void>
  signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)
export const AUTH_QUERY_KEY = ['auth-state'] as const

export function AuthProvider({ children }: { children: ReactNode }) {
  const client = useQueryClient()
  const navigate = useNavigate()
  const location = useLocation()
  const query = useQuery({
    queryKey: AUTH_QUERY_KEY,
    queryFn: async () => {
      const state = await authApi.state()
      if (state.csrf_token) setCsrfToken(state.csrf_token)
      return state
    },
    retry: (count, error) => error instanceof ApiError && error.isUnavailable && count < 3,
    retryDelay: (attempt) => Math.min(1000 * (attempt + 1), 4000),
    staleTime: 60_000,
  })

  const refresh = useCallback(async () => {
    await client.invalidateQueries({ queryKey: AUTH_QUERY_KEY })
  }, [client])

  const signOut = useCallback(async () => {
    try {
      await authApi.logout()
    } finally {
      client.clear()
      await client.invalidateQueries({ queryKey: AUTH_QUERY_KEY })
      navigate('/', { replace: true })
    }
  }, [client, navigate])

  // A 401 on any authenticated call means the session is gone: go to sign-in and come back after.
  useEffect(
    () =>
      onUnauthenticated(() => {
        client.setQueryData(AUTH_QUERY_KEY, { authenticated: false } satisfies AuthState)
        const here = `${location.pathname}${location.search}`
        navigate(`/login?return_to=${encodeURIComponent(here)}`, { replace: true })
      }),
    [client, navigate, location.pathname, location.search],
  )

  const value = useMemo<AuthContextValue>(
    () => ({
      state: query.data,
      loading: query.isPending,
      unavailable: query.isError && query.error instanceof ApiError && query.error.isUnavailable,
      refresh,
      signOut,
    }),
    [query.data, query.isPending, query.isError, query.error, refresh, signOut],
  )
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}
