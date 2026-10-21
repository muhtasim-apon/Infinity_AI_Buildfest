import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import bn from './bn.json'
import en from './en.json'

export const SUPPORTED_LOCALES = ['bn', 'en'] as const
export type Locale = (typeof SUPPORTED_LOCALES)[number]
/** Bangla is the source locale (spec 0.2.10) and the default. */
export const DEFAULT_LOCALE: Locale = 'bn'

export function isLocale(value: unknown): value is Locale {
  return typeof value === 'string' && (SUPPORTED_LOCALES as readonly string[]).includes(value)
}

export function initI18n(locale: Locale = DEFAULT_LOCALE) {
  void i18n.use(initReactI18next).init({
    resources: { bn: { translation: bn }, en: { translation: en } },
    lng: locale,
    fallbackLng: 'bn',
    interpolation: { escapeValue: false }, // React escapes; values are rendered as text only
    returnNull: false,
  })
  return i18n
}

/** Keep <html lang> in sync so screen readers and fonts pick the right script (spec 15.4). */
export function setDocumentLocale(locale: Locale, doc: Document = document): void {
  doc.documentElement.lang = locale
}

export { i18n }
