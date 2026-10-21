import { useTranslation } from 'react-i18next'

/** Phase 0 placeholder: proves fonts, tokens, i18n and the CSP-safe build. Real screens: Phase 2. */
export function App() {
  const { t } = useTranslation()
  return (
    <main className="mx-auto max-w-md p-6">
      <h1 className="text-2xl font-semibold text-primary">{t('app.name')}</h1>
      <p className="mt-2 text-muted">{t('app.tagline')}</p>
      <p className="mt-6 rounded-lg border border-border bg-surface p-4 shadow-xs">
        {t('landing.demoNotice')}
      </p>
    </main>
  )
}
