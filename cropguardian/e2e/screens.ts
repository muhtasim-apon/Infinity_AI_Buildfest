/**
 * Every built screen that the accessibility, layout and visual specs walk (spec 19.6 steps 15-17).
 * A screen is added here in the same change that builds it: the gate's "every built screen" claim is
 * only as true as this list. Signed-in screens join it once the specs can sign in (Phase 2 Block 2).
 */
export interface Screen {
  /** Stable id used in test names and snapshot file names. */
  id: string
  path: string
}

export const PUBLIC_SCREENS: Screen[] = [
  { id: 'landing', path: '/' },
  { id: 'demo', path: '/demo' },
  { id: 'login', path: '/login' },
  { id: 'register', path: '/register' },
  { id: 'forgot', path: '/forgot-password' },
  { id: 'forbidden', path: '/403' },
  { id: 'not-found', path: '/this-page-does-not-exist' },
]

export const THEMES = ['light', 'dark'] as const
export const LOCALES = ['bn', 'en'] as const
export type Theme = (typeof THEMES)[number]
export type LocaleId = (typeof LOCALES)[number]
