/**
 * Design tokens (spec 15.1) - TypeScript mirror of tokens.css for 3D/maps and tests.
 * tokens.css is what styles the app; tokens.test.ts fails if the two ever drift.
 * This is one of only two places hex colours may appear (the other is tokens.css).
 */

export const lightTheme = {
  bg: '#F6F8F3',
  surface: '#FFFFFF',
  surface2: '#EEF3E8',
  border: '#D9E2D2',
  text: '#12201A',
  textMuted: '#4A5A50',
  textSubtle: '#657569',
  primary: '#166534',
  primaryHover: '#14532D',
  primarySoft: '#E6F2E8',
  onPrimary: '#FFFFFF',
  accent: '#A16207',
  accentBg: '#FEF7E0',
  sky: '#0E7490',
  skyBg: '#ECFEFF',
  success: '#15803D',
  successBg: '#F0FDF4',
  warning: '#B45309',
  warningBg: '#FFFBEB',
  danger: '#B91C1C',
  dangerBg: '#FEF2F2',
  simulated: '#6D28D9',
  simulatedBg: '#F5F3FF',
} as const

/**
 * Dark theme. The spec fixes bg/surface/surface-2/border/text/text-muted/primary/primary-soft and
 * says status colours are "lightened to keep >= 4.5:1"; the status pairs below are our derived
 * values (DECISIONS.md D-007) and are verified by contrast.test.ts.
 */
export const darkTheme: Record<keyof typeof lightTheme, string> = {
  bg: '#0A110D',
  surface: '#101A14',
  surface2: '#17241C',
  border: '#26382C',
  text: '#E7EFE9',
  textMuted: '#A3B5A9',
  textSubtle: '#8FA397',
  primary: '#4ADE80',
  primaryHover: '#86EFAC',
  primarySoft: '#12301D',
  onPrimary: '#052E16',
  accent: '#FCD34D',
  accentBg: '#2A2206',
  sky: '#67E8F9',
  skyBg: '#082A33',
  success: '#86EFAC',
  successBg: '#0F2A1A',
  warning: '#FBBF24',
  warningBg: '#2A1E05',
  danger: '#FCA5A5',
  dangerBg: '#2D0F0F',
  simulated: '#C4B5FD',
  simulatedBg: '#1E1537',
}

/** Okabe-Ito colour-blind-safe palette; always paired with a name or icon, never colour alone. */
export const diseaseColours = [
  '#E69F00',
  '#56B4E9',
  '#009E73',
  '#D55E00',
  '#0072B2',
  '#CC79A7',
  '#8C7B00',
] as const

export const risk = { low: '#15803D', medium: '#B45309', high: '#B91C1C' } as const

/** Spacing on a 4 px grid, in px. */
export const space = [4, 8, 12, 16, 20, 24, 32, 40, 48, 64] as const
export const radius = { sm: 6, md: 10, lg: 14, xl: 20 } as const

/** Type scale [size px, line-height px] for Latin; Bangla adds +2 px and x1.15 line-height. */
export const typeScale = [
  [12, 16],
  [14, 20],
  [16, 24],
  [18, 28],
  [20, 28],
  [24, 32],
  [30, 38],
  [36, 44],
] as const

export const banglaScale = typeScale.map(([size, line]) => [
  size + 2,
  Math.round(line * 1.15),
]) as ReadonlyArray<readonly [number, number]>

export const FARMER_MIN_BODY_PX_BN = 18
export const TOUCH_TARGET_FARMER_PX = 48
export const TOUCH_TARGET_STAFF_PX = 44

export type ThemeName = 'light' | 'dark'
export const themes = { light: lightTheme, dark: darkTheme } as const
