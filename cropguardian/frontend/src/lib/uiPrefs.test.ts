import { act, renderHook } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import {
  DEFAULT_PREFS,
  PREFS_KEY,
  applyPrefs,
  getPrefs,
  parsePrefs,
  resetPrefsForTests,
  setPrefs,
  useUiPrefs,
} from './uiPrefs'

beforeEach(() => {
  window.localStorage.clear()
  document.documentElement.removeAttribute('data-theme')
  document.documentElement.removeAttribute('data-text-scale')
  document.documentElement.removeAttribute('data-reduced-motion')
  resetPrefsForTests()
})
afterEach(() => vi.restoreAllMocks())

describe('parsePrefs (storage is untrusted input)', () => {
  it('accepts a valid value', () => {
    expect(
      parsePrefs('{"locale":"en","theme":"dark","reducedMotion":true,"textScale":130}'),
    ).toEqual({
      locale: 'en',
      theme: 'dark',
      reducedMotion: true,
      textScale: 130,
    })
  })

  it('falls back to defaults for null, empty, malformed and non-object JSON', () => {
    for (const raw of [null, '', '{', 'null', '42', '"dark"', '[]']) {
      expect(parsePrefs(raw)).toEqual(DEFAULT_PREFS)
    }
  })

  it('rejects out-of-range values field by field and keeps the valid ones', () => {
    expect(parsePrefs('{"theme":"neon","reducedMotion":"yes","textScale":999}')).toEqual(
      DEFAULT_PREFS,
    )
    expect(parsePrefs('{"theme":"light","textScale":"130"}')).toEqual({
      ...DEFAULT_PREFS,
      theme: 'light',
    })
  })

  it('refuses an oversized value instead of parsing it', () => {
    const big = JSON.stringify({ theme: 'dark', junk: 'x'.repeat(2000) })
    expect(parsePrefs(big)).toEqual(DEFAULT_PREFS)
  })

  it('ignores unknown keys (a stored role or token is never read back)', () => {
    const out = parsePrefs('{"theme":"dark","role":"ADMIN","token":"abc"}')
    expect(out).toEqual({ ...DEFAULT_PREFS, theme: 'dark' })
    expect(Object.keys(out).sort()).toEqual(['locale', 'reducedMotion', 'textScale', 'theme'])
  })
})

describe('applyPrefs', () => {
  it('reflects preferences on <html>', () => {
    applyPrefs({ locale: 'en', theme: 'dark', reducedMotion: true, textScale: 115 })
    const root = document.documentElement
    expect(root.getAttribute('lang')).toBe('en')
    expect(root.getAttribute('data-theme')).toBe('dark')
    expect(root.getAttribute('data-reduced-motion')).toBe('true')
    expect(root.getAttribute('data-text-scale')).toBe('115')
  })

  it('removes theme and text-scale attributes for the defaults', () => {
    applyPrefs({ locale: 'bn', theme: 'dark', reducedMotion: false, textScale: 130 })
    applyPrefs(DEFAULT_PREFS)
    const root = document.documentElement
    expect(root.hasAttribute('data-theme')).toBe(false)
    expect(root.hasAttribute('data-text-scale')).toBe(false)
    expect(root.getAttribute('data-reduced-motion')).toBe('false')
  })
})

describe('setPrefs', () => {
  it('persists, applies and notifies subscribers', () => {
    const { result } = renderHook(() => useUiPrefs())
    act(() => result.current[1]({ textScale: 130 }))
    expect(result.current[0].textScale).toBe(130)
    expect(document.documentElement.getAttribute('data-text-scale')).toBe('130')
    expect(JSON.parse(window.localStorage.getItem(PREFS_KEY) ?? '{}').textScale).toBe(130)
  })

  it('sanitises a bad patch through the same validator', () => {
    const out = setPrefs({ theme: 'neon' as never, textScale: 7 as never })
    expect(out).toEqual(DEFAULT_PREFS)
  })

  it('still works when storage throws (private mode / blocked)', () => {
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new DOMException('quota', 'QuotaExceededError')
    })
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new DOMException('blocked', 'SecurityError')
    })
    expect(getPrefs()).toEqual(DEFAULT_PREFS)
    expect(() => setPrefs({ reducedMotion: true })).not.toThrow()
    expect(getPrefs().reducedMotion).toBe(true)
  })

  it('loads a previously stored value on first read', () => {
    window.localStorage.setItem(PREFS_KEY, '{"theme":"light","textScale":115}')
    resetPrefsForTests()
    expect(getPrefs()).toMatchObject({ theme: 'light', textScale: 115 })
    expect(document.documentElement.getAttribute('data-theme')).toBe('light')
  })
})
