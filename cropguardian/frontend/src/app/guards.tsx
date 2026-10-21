import { useTranslation } from 'react-i18next'
import { Navigate, Outlet, useLocation, useSearchParams } from 'react-router-dom'
import { baseRole, homePath } from '../lib/authApi'
import { safeReturnTo } from '../lib/returnTo'
import { useAuth } from './auth'
import { ForbiddenPage, NotFoundPage } from './pages/errors'

type Area = 'farmer' | 'reviewer' | 'admin'

/**
 * Route guard (spec 15.4):
 *  unauthenticated -> /login?return_to=...   staff mid-2FA -> /login/totp or /setup-2fa
 *  wrong role -> 403 page                    admin area for a non-admin -> 404 page (hidden)
 * `allowPending` lets the 2FA screens themselves render while 2FA is incomplete.
 */
export function RequireSession({
  area,
  allowPending = false,
}: {
  area?: Area
  allowPending?: boolean
}) {
  const { t } = useTranslation()
  const { state, loading, unavailable, refresh } = useAuth()
  const location = useLocation()

  if (loading) return <p role="status">{t('common.loading')}</p>
  if (unavailable) {
    return (
      <div role="alert">
        <p>{t('errors.waking')}</p>
        <button
          type="button"
          className="mt-4 min-h-[48px] rounded-md border border-border px-4"
          onClick={() => void refresh()}
        >
          {t('common.retry')}
        </button>
      </div>
    )
  }
  if (!state?.authenticated || !state.role) {
    const here = `${location.pathname}${location.search}`
    return <Navigate to={`/login?return_to=${encodeURIComponent(here)}`} replace />
  }
  if (!allowPending) {
    if (state.next === 'totp') return <Navigate to="/login/totp" replace />
    if (state.next === 'setup_totp') return <Navigate to="/setup-2fa" replace />
  }
  if (area && baseRole(state.role) !== area) {
    return area === 'admin' ? <NotFoundPage /> : <ForbiddenPage />
  }
  return <Outlet />
}

/**
 * Pages only for signed-out visitors (login, register): a signed-in user goes to `return_to` when it
 * is a safe in-app path, else to their home. This also covers the moment right after sign-in, when
 * the session state refreshes before the page's own redirect runs.
 */
export function RedirectIfSignedIn() {
  const { state, loading } = useAuth()
  const [params] = useSearchParams()
  if (loading) return <p role="status">…</p>
  if (state?.authenticated && state.next === 'home' && state.role) {
    return <Navigate to={safeReturnTo(params.get('return_to'), homePath(state.role))} replace />
  }
  return <Outlet />
}
