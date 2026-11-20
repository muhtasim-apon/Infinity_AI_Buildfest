import { forwardRef, useId, type InputHTMLAttributes, type ReactNode } from 'react'
import { useTranslation } from 'react-i18next'
import { Moon, Sun } from 'lucide-react'
import { Link } from 'react-router-dom'
import { AnimatedOutlet } from '../components/app/PageTransition'
import { useUiPrefs } from '../lib/uiPrefs'
import { messageFor } from '../lib/errors'
import { isDemo } from '../lib/authApi'
import { ApiError } from '../lib/api'
import { i18n, isLocale, setDocumentLocale, SUPPORTED_LOCALES } from '../i18n'
import { useAuth } from './auth'

/** Minimal form elements the Phase 1 screens need; the full design system is Phase 2. */
interface FieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string
  hint?: string
  error?: string
}

export const Field = forwardRef<HTMLInputElement, FieldProps>(function Field(
  { label, hint, error, id, className, ...rest },
  ref,
) {
  const auto = useId()
  const inputId = id ?? auto
  const hintId = `${inputId}-hint`
  const errorId = `${inputId}-error`
  const describedBy =
    [hint ? hintId : '', error ? errorId : ''].filter(Boolean).join(' ') || undefined
  return (
    <div className="mt-4">
      <label htmlFor={inputId} className="block text-sm font-medium">
        {label}
      </label>
      <input
        ref={ref}
        id={inputId}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy}
        className={`mt-1 block w-full min-h-[48px] rounded-md border border-border bg-surface px-3 text-text ${className ?? ''}`}
        {...rest}
      />
      {hint ? (
        <p id={hintId} className="mt-1 text-sm text-muted">
          {hint}
        </p>
      ) : null}
      {error ? (
        <p id={errorId} role="alert" className="mt-1 text-sm text-danger">
          {error}
        </p>
      ) : null}
    </div>
  )
})

export function Button({
  children,
  variant = 'primary',
  ...rest
}: {
  children: ReactNode
  variant?: 'primary' | 'secondary'
} & React.ButtonHTMLAttributes<HTMLButtonElement>) {
  const base =
    'mt-6 inline-flex min-h-[48px] w-full items-center justify-center rounded-md px-4 font-semibold disabled:opacity-60'
  const tone =
    variant === 'primary'
      ? 'bg-primary text-primary-on hover:bg-primary-hover'
      : 'border border-border bg-surface text-text'
  return (
    <button className={`${base} ${tone}`} {...rest}>
      {children}
    </button>
  )
}

/** Server/problem errors for a form, announced to screen readers. */
export function FormError({ error }: { error: unknown }) {
  const { t } = useTranslation()
  if (!error) return null
  const ref = messageFor(error)
  const requestId = error instanceof ApiError ? error.requestId : undefined
  return (
    <div role="alert" className="mt-4 rounded-md border border-danger bg-danger-bg p-3 text-danger">
      <p>{t(ref.key, ref.values)}</p>
      {requestId ? (
        <p className="mt-1 text-xs">{t('errors.requestId', { id: requestId })}</p>
      ) : null}
    </div>
  )
}

export function Notice({ children }: { children: ReactNode }) {
  return (
    <p role="status" className="mt-4 rounded-md border border-border bg-primary-soft p-3">
      {children}
    </p>
  )
}

export function LanguageToggle() {
  const { t } = useTranslation()
  const current = i18n.language
  return (
    <div role="group" aria-label={t('common.language')} className="flex gap-2">
      {SUPPORTED_LOCALES.map((locale) => (
        <button
          key={locale}
          type="button"
          lang={locale}
          aria-pressed={current === locale}
          className="min-h-[44px] min-w-[44px] rounded-md border border-border px-2 aria-pressed:bg-primary aria-pressed:text-primary-on"
          onClick={() => {
            if (!isLocale(locale)) return
            void i18n.changeLanguage(locale)
            setDocumentLocale(locale)
          }}
        >
          {locale === 'bn' ? 'বাংলা' : 'EN'}
        </button>
      ))}
    </div>
  )
}

/** Always-visible banner while a demo role is active (spec 2.2): data is fake, nothing is real. */
export function DemoRibbon() {
  const { t } = useTranslation()
  const { state } = useAuth()
  if (!state?.authenticated || !isDemo(state.role)) return null
  return (
    <div
      className="bg-simulated-bg px-4 py-2 text-center text-sm font-semibold text-simulated"
      role="status"
    >
      {t('demo.ribbon')}
    </div>
  )
}

/** Sun/moon toggle. Light is the default (outdoor use); the choice is a stored UI preference. */
export function ThemeToggle() {
  const { t } = useTranslation()
  const [prefs, setPrefs] = useUiPrefs()
  const dark =
    prefs.theme === 'dark' ||
    (prefs.theme === 'system' &&
      typeof window !== 'undefined' &&
      window.matchMedia?.('(prefers-color-scheme: dark)').matches)
  const label = dark ? t('cg.theme.toLight') : t('cg.theme.toDark')
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      className="inline-flex min-h-[44px] min-w-[44px] items-center justify-center rounded-md border border-border"
      onClick={() => setPrefs({ theme: dark ? 'light' : 'dark' })}
    >
      {dark ? (
        <Sun className="h-5 w-5" aria-hidden="true" />
      ) : (
        <Moon className="h-5 w-5" aria-hidden="true" />
      )}
    </button>
  )
}

export function Shell() {
  const { t } = useTranslation()
  const { state, signOut } = useAuth()
  return (
    <>
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-2 focus:top-2 focus:bg-surface focus:p-2"
      >
        {t('common.skipToContent')}
      </a>
      <DemoRibbon />
      <header className="mx-auto flex max-w-md items-center justify-between gap-1.5 p-4">
        <Link to="/" className="text-lg font-semibold text-primary">
          {t('app.name')}
        </Link>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <LanguageToggle />
          {state?.authenticated ? (
            <button
              type="button"
              className="min-h-[44px] whitespace-nowrap rounded-md border border-border px-2"
              onClick={() => void signOut()}
            >
              {t('auth.logout')}
            </button>
          ) : null}
        </div>
      </header>
      <main id="main" className="mx-auto max-w-md px-4 pb-12">
        <AnimatedOutlet depth="section" />
      </main>
    </>
  )
}
