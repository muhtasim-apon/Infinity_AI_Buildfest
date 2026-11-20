import { useTranslation } from 'react-i18next'
import { LogoMark } from '../illustrations'

/** Public footer: who it is for, and the honesty line (nothing here is a measured result). */
export function SiteFooter() {
  const { t } = useTranslation()
  return (
    <footer className="border-t border-border bg-surface-2">
      <div className="mx-auto flex max-w-6xl flex-col gap-2 px-4 py-8 sm:flex-row sm:items-center sm:justify-between">
        <p className="flex items-center gap-2 font-medium">
          <LogoMark className="h-7 w-7" />
          {t('footer.tagline')}
        </p>
        <p className="text-sm text-muted">{t('footer.honesty')}</p>
      </div>
    </footer>
  )
}
