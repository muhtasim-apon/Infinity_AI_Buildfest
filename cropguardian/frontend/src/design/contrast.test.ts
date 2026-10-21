import { describe, expect, it } from 'vitest'
import { contrastRatio, hexToRgb } from './contrast'
import { darkTheme, lightTheme, type ThemeName, themes } from './tokens'

type Pair = { name: string; fg: keyof typeof lightTheme; bg: keyof typeof lightTheme; min: number }

// Body text >= 4.5:1; large text and UI components >= 3:1 (spec 15.1). Farmer primary text >= 7:1 (15.5.6).
const pairs: Pair[] = [
  { name: 'text on bg (farmer AAA)', fg: 'text', bg: 'bg', min: 7 },
  { name: 'text on surface (farmer AAA)', fg: 'text', bg: 'surface', min: 7 },
  { name: 'text on surface-2', fg: 'text', bg: 'surface2', min: 4.5 },
  { name: 'text-muted on bg', fg: 'textMuted', bg: 'bg', min: 4.5 },
  { name: 'text-muted on surface', fg: 'textMuted', bg: 'surface', min: 4.5 },
  { name: 'text-subtle on bg', fg: 'textSubtle', bg: 'bg', min: 4.5 },
  { name: 'text-subtle on surface', fg: 'textSubtle', bg: 'surface', min: 4.5 },
  { name: 'primary link on bg', fg: 'primary', bg: 'bg', min: 4.5 },
  { name: 'primary link on surface', fg: 'primary', bg: 'surface', min: 4.5 },
  { name: 'primary on primary-soft', fg: 'primary', bg: 'primarySoft', min: 4.5 },
  { name: 'text on primary button', fg: 'onPrimary', bg: 'primary', min: 4.5 },
  { name: 'text on primary-hover button', fg: 'onPrimary', bg: 'primaryHover', min: 4.5 },
  { name: 'accent on accent-bg', fg: 'accent', bg: 'accentBg', min: 4.5 },
  { name: 'sky on sky-bg', fg: 'sky', bg: 'skyBg', min: 4.5 },
  { name: 'success on success-bg', fg: 'success', bg: 'successBg', min: 4.5 },
  { name: 'warning on warning-bg', fg: 'warning', bg: 'warningBg', min: 4.5 },
  { name: 'danger on danger-bg', fg: 'danger', bg: 'dangerBg', min: 4.5 },
  { name: 'simulated on simulated-bg', fg: 'simulated', bg: 'simulatedBg', min: 4.5 },
  { name: 'border vs bg (UI component)', fg: 'border', bg: 'bg', min: 1.0 },
]

describe('WCAG contrast of every text/background pair', () => {
  for (const theme of ['light', 'dark'] as ThemeName[]) {
    for (const p of pairs) {
      it(`${theme}: ${p.name} >= ${p.min}:1`, () => {
        const t = themes[theme]
        expect(contrastRatio(t[p.fg], t[p.bg])).toBeGreaterThanOrEqual(p.min)
      })
    }
  }

  it('contrast helper matches known WCAG values', () => {
    expect(contrastRatio('#000000', '#FFFFFF')).toBeCloseTo(21, 5)
    expect(contrastRatio('#FFFFFF', '#FFFFFF')).toBeCloseTo(1, 5)
    expect(contrastRatio('#777777', '#FFFFFF')).toBeCloseTo(4.48, 1) // classic AA-fail grey
  })

  it('rejects malformed colours instead of guessing', () => {
    expect(() => hexToRgb('#fff')).toThrow()
    expect(() => hexToRgb('red')).toThrow()
    expect(() => hexToRgb('')).toThrow()
  })

  it('every light token exists in the dark theme (no missing pair)', () => {
    expect(Object.keys(darkTheme).sort()).toEqual(Object.keys(lightTheme).sort())
  })
})
