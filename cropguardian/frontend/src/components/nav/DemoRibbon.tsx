import { FlaskConical } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../../app/auth'
import { isDemo } from '../../lib/authApi'
import { formatNumber } from '../../lib/format'
import { useNow } from '../../lib/useOnline'

const TICK_MS = 30_000

/**
 * Persistent purple ribbon while a demo role is active (spec 2.2, 15.4): the data is fake, nothing
 * is real, and the visitor can leave at any time. The time left is read from the SERVER's session
 * expiry (never a client-side guess), so it is exactly when the demo ends.
 */
export function DemoRibbon() {
  const { t, i18n } = useTranslation()
  const { state, signOut } = useAuth()
  const now = useNow(TICK_MS)
  if (!state?.authenticated || !isDemo(state.role)) return null

  const locale = i18n.language === 'en' ? 'en' : 'bn'
  const endsAt = state.session_expires_at ? Date.parse(state.session_expires_at) : Number.NaN
  const minutes = Number.isFinite(endsAt) ? Math.max(0, Math.ceil((endsAt - now) / 60_000)) : null

  return (
    <div
      role="status"
      className="flex flex-wrap items-center justify-center gap-x-4 gap-y-1 bg-simulated-bg px-4 py-1.5 text-sm font-semibold text-simulated"
    >
      <span className="inline-flex items-center gap-1.5">
        <FlaskConical className="h-4 w-4" aria-hidden="true" />
        {t('demo.ribbon')}
      </span>
      {minutes !== null ? (
        <span className="font-medium">
          {t('demoPicker.timeLeft', { minutes: formatNumber(minutes, locale, 0) })}
        </span>
      ) : null}
      <button
        type="button"
        className="min-h-[44px] rounded-md px-2 underline underline-offset-4"
        onClick={() => void signOut()}
      >
        {t('demo.exit')}
      </button>
    </div>
  )
}
