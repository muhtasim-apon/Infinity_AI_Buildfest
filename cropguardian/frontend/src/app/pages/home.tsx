import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { authApi, homePath } from '../../lib/authApi'
import { useAuth } from '../auth'
import { HeroBackground } from '../../components/app/HeroBackground'
import { Button, FormError } from '../ui'
import { useCaptcha } from '../useCaptcha'

/** Minimal public entry (the real landing page is Phase 2). Signed-in users go straight home. */
export function EntryPage() {
  const { t } = useTranslation()
  const { state, loading } = useAuth()
  if (loading) return <p role="status">{t('common.loading')}</p>
  if (state?.authenticated && state.role) {
    if (state.next === 'totp') return <Navigate to="/login/totp" replace />
    if (state.next === 'setup_totp') return <Navigate to="/setup-2fa" replace />
    return <Navigate to={homePath(state.role)} replace />
  }
  return (
    <section className="-mx-4 -mt-2">
      <div className="relative h-[640px] overflow-hidden rounded-b-xl">
        <HeroBackground />
        <div
          className="absolute inset-0 bg-gradient-to-t from-primary from-38% to-transparent to-62%"
          aria-hidden="true"
        />
        <div className="absolute inset-x-0 bottom-0 p-6 text-primary-on">
          <p className="text-lg font-semibold opacity-90">{t('app.name')}</p>
          <h1 className="mt-1 text-4xl font-bold leading-tight">{t('cg.ui2.heroTitle')}</h1>
          <p className="mt-3 text-base opacity-95">{t('cg.ui2.heroBody')}</p>
          <Link
            className="mt-6 flex min-h-[56px] items-center justify-center rounded-full bg-accent px-6 text-lg font-semibold text-text shadow-md"
            to="/demo"
          >
            {t('nav.tryDemo')}
          </Link>
          <Link
            className="mt-3 flex min-h-[48px] items-center justify-center rounded-full border border-primary-on px-6 font-semibold"
            to="/login"
          >
            {t('nav.signIn')}
          </Link>
        </div>
      </div>
      <div className="mx-4 mt-4 rounded-lg border border-border bg-surface p-4 text-sm text-muted">
        {t('landing.demoNotice')}
      </div>
      <Link className="mx-4 mt-3 flex min-h-[48px] items-center text-primary underline" to="/trust">
        {t('cg.ui2.heroTrust')}
      </Link>
    </section>
  )
}

const DEMO_ROLES = [
  { role: 'DEMO_FARMER', label: 'demoPicker.farmer' },
  { role: 'DEMO_REVIEWER', label: 'demoPicker.reviewer' },
  { role: 'DEMO_ADMIN', label: 'demoPicker.admin' },
] as const

export function DemoPickerPage() {
  const { t } = useTranslation()
  const { refresh } = useAuth()
  const navigate = useNavigate()
  const captcha = useCaptcha(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<unknown>(null)

  const enter = async (role: (typeof DEMO_ROLES)[number]['role']) => {
    setError(null)
    const token = captcha.consume()
    if (!token) return
    setBusy(true)
    try {
      const reply = await authApi.demoSession({ role, captcha: token })
      await refresh()
      navigate(homePath(reply.user?.role ?? role), { replace: true })
    } catch (err) {
      setError(err)
    } finally {
      setBusy(false)
    }
  }

  let status = 'auth.captcha.verifying'
  if (captcha.status === 'failed') status = 'auth.captcha.failed'
  if (captcha.status === 'ready') status = 'demoPicker.note'

  return (
    <section>
      <h1 className="text-2xl font-semibold">{t('demoPicker.title')}</h1>
      <p className="mt-2 text-muted">{t('demoPicker.subtitle')}</p>
      <div className="mt-4">
        {DEMO_ROLES.map(({ role, label }) => (
          <Button
            key={role}
            type="button"
            disabled={busy || captcha.status !== 'ready'}
            onClick={() => void enter(role)}
          >
            {t(label)}
          </Button>
        ))}
      </div>
      <p role="status" className="mt-4 text-sm text-muted">
        {t(status)}
      </p>
      <FormError error={error} />
    </section>
  )
}

function RoleHome({ titleKey }: { titleKey: string }) {
  const { t } = useTranslation()
  const { state } = useAuth()
  return (
    <section>
      <h1 className="text-2xl font-semibold">{t(titleKey)}</h1>
      <p className="mt-2">{t('home.welcome', { name: state?.display_name ?? '' })}</p>
      <p className="mt-4 rounded-lg border border-border bg-surface p-4 text-muted">
        {t('home.placeholder')}
      </p>
      <Link
        className="mt-4 inline-flex min-h-[48px] items-center text-primary underline"
        to="/account/sessions"
      >
        {t('auth.sessions.title')}
      </Link>
    </section>
  )
}

export const FarmerHome = () => <RoleHome titleKey="home.farmer" />
export const ReviewerHome = () => <RoleHome titleKey="home.reviewer" />

export function SessionsPage() {
  const { t } = useTranslation()
  const client = useQueryClient()
  const { signOut } = useAuth()
  const list = useQuery({ queryKey: ['my-sessions'], queryFn: () => authApi.sessions() })
  const [error, setError] = useState<unknown>(null)

  const revoke = async (id: string) => {
    setError(null)
    try {
      await authApi.revokeSession(id)
      await client.invalidateQueries({ queryKey: ['my-sessions'] })
    } catch (err) {
      setError(err)
    }
  }

  return (
    <section>
      <h1 className="text-2xl font-semibold">{t('auth.sessions.title')}</h1>
      {list.isPending ? <p role="status">{t('common.loading')}</p> : null}
      {list.isError ? <FormError error={list.error} /> : null}
      {list.data && list.data.sessions.length === 0 ? <p>{t('auth.sessions.empty')}</p> : null}
      <ul className="mt-4 space-y-3">
        {list.data?.sessions.map((s) => (
          <li key={s.id} className="rounded-lg border border-border bg-surface p-3">
            <p className="font-medium">
              {s.current ? t('auth.sessions.current') : s.device || t('auth.sessions.title')}
            </p>
            <p className="text-sm text-muted">
              {t('auth.sessions.lastSeen', { time: new Date(s.last_seen_at).toLocaleString() })}
            </p>
            {!s.current ? (
              <button
                type="button"
                className="mt-2 min-h-[44px] rounded-md border border-border px-3"
                onClick={() => void revoke(s.id)}
              >
                {t('auth.sessions.revoke')}
              </button>
            ) : null}
          </li>
        ))}
      </ul>
      <FormError error={error} />
      <Button
        type="button"
        variant="secondary"
        onClick={async () => {
          await authApi.logoutAll()
          await signOut()
        }}
      >
        {t('auth.sessions.revokeAll')}
      </Button>
    </section>
  )
}
