import { useTranslation } from 'react-i18next'
import { i18n, isLocale, setDocumentLocale, SUPPORTED_LOCALES, type Locale } from '../../i18n'
import { cn } from '../../lib/cn'
import { setPrefs } from '../../lib/uiPrefs'

/** Switch the interface language and remember it on this device (prefs allow-list). */
export function changeLocale(locale: Locale): void {
  if (!isLocale(locale)) return
  void i18n.changeLanguage(locale)
  setDocumentLocale(locale)
  setPrefs({ locale })
}

/**
 * বাংলা / EN segmented switch. Each button is written in its own language and carries `lang`, so a
 * screen reader pronounces it correctly whatever the page language is.
 */
export function LanguageSwitch({ className }: { className?: string }) {
  const { t } = useTranslation()
  const current = i18n.language
  return (
    <div
      role="group"
      aria-label={t('common.language')}
      className={cn('inline-flex rounded-full border border-border bg-surface-2 p-0.5', className)}
    >
      {SUPPORTED_LOCALES.map((locale) => (
        <button
          key={locale}
          type="button"
          lang={locale}
          aria-pressed={current === locale}
          className={cn(
            'min-h-[44px] min-w-[44px] rounded-full px-3 text-sm font-semibold text-muted',
            'transition-colors duration-fast ease-standard',
            'aria-pressed:bg-primary aria-pressed:text-primary-on',
          )}
          onClick={() => changeLocale(locale)}
        >
          {locale === 'bn' ? 'বাংলা' : 'EN'}
        </button>
      ))}
    </div>
  )
}
