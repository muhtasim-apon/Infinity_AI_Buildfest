/**
 * Per-device UI preferences: language, theme, reduced motion, text size (spec 15.6 F7).
 *
 * This is the ONLY module allowed to touch web storage (check_forbidden: "UI preference allow-list").
 * Nothing sensitive, nothing identifying and nothing server-trusted is stored. Reads are validated
 * field by field: a tampered, truncated or foreign value falls back to the safe default instead of
 * throwing, and storage being unavailable (private mode, quota, blocked) never breaks the app.
 */

import { useSyncExternalStore } from 'react'
import { DEFAULT_LOCALE, SUPPORTED_LOCALES, type Locale } from '../i18n'

export const THEME_PREFS = ['system', 'light', 'dark'] as const
export type ThemePref = (typeof THEME_PREFS)[number]
export const TEXT_SCALES = [100, 115, 130] as const
export type TextScale = (typeof TEXT_SCALES)[number]

export interface UiPrefs {
  locale: Locale
  theme: ThemePref
  reducedMotion: boolean
  textScale: TextScale
}

export const DEFAULT_PREFS: UiPrefs = {
  locale: DEFAULT_LOCALE,
  // Light by default: the farmer app is used outdoors in sunlight (cropguardian-ui section 1).
  // Dark stays one tap away (header toggle) and 'system' remains a valid stored choice.
  theme: 'light',
  reducedMotion: false,
  textScale: 100,
}
export const PREFS_KEY = 'cg.ui.prefs'

/** Validate untrusted JSON into preferences; unknown or invalid fields take their default. */
export function parsePrefs(raw: string | null): UiPrefs {
  if (!raw || raw.length > 512) return { ...DEFAULT_PREFS }
  let data: unknown
  try {
    data = JSON.parse(raw)
  } catch {
    return { ...DEFAULT_PREFS }
  }
  if (typeof data !== 'object' || data === null) return { ...DEFAULT_PREFS }
  const o = data as Record<string, unknown>
  return {
    locale: SUPPORTED_LOCALES.find((l) => l === o.locale) ?? DEFAULT_PREFS.locale,
    theme: THEME_PREFS.find((t) => t === o.theme) ?? DEFAULT_PREFS.theme,
    reducedMotion: o.reducedMotion === true,
    textScale: TEXT_SCALES.find((s) => s === o.textScale) ?? DEFAULT_PREFS.textScale,
  }
}

export function loadPrefs(): UiPrefs {
  try {
    return parsePrefs(window.localStorage.getItem(PREFS_KEY)) // forbidden-ok: UI preference allow-list
  } catch {
    return { ...DEFAULT_PREFS }
  }
}

function persist(prefs: UiPrefs): void {
  try {
    window.localStorage.setItem(PREFS_KEY, JSON.stringify(prefs)) // forbidden-ok: UI preference allow-list
  } catch {
    // storage unavailable: the preference lasts for this page view only
  }
}

/** Reflect preferences on <html> so CSS (tokens.css, index.css, the `motion-ok:` variant) reacts. */
export function applyPrefs(prefs: UiPrefs, doc: Document = document): void {
  const root = doc.documentElement
  root.setAttribute('lang', prefs.locale)
  if (prefs.theme === 'system') root.removeAttribute('data-theme')
  else root.setAttribute('data-theme', prefs.theme)
  root.setAttribute('data-reduced-motion', String(prefs.reducedMotion))
  if (prefs.textScale === 100) root.removeAttribute('data-text-scale')
  else root.setAttribute('data-text-scale', String(prefs.textScale))
}

let current: UiPrefs = DEFAULT_PREFS
let started = false
const listeners = new Set<() => void>()

function ensureStarted(): void {
  if (started || typeof window === 'undefined') return
  started = true
  current = loadPrefs()
  applyPrefs(current)
}

export function getPrefs(): UiPrefs {
  ensureStarted()
  return current
}

export function setPrefs(patch: Partial<UiPrefs>): UiPrefs {
  ensureStarted()
  current = parsePrefs(JSON.stringify({ ...current, ...patch }))
  persist(current)
  applyPrefs(current)
  listeners.forEach((l) => l())
  return current
}

/** Test helper: forget the in-memory copy so the next read goes back to storage. */
export function resetPrefsForTests(): void {
  started = false
  current = DEFAULT_PREFS
  listeners.clear()
}

function subscribe(listener: () => void): () => void {
  listeners.add(listener)
  return () => listeners.delete(listener)
}

export function useUiPrefs(): [UiPrefs, (patch: Partial<UiPrefs>) => void] {
  const prefs = useSyncExternalStore(subscribe, getPrefs, () => DEFAULT_PREFS)
  return [prefs, setPrefs]
}
