import { describe, expect, it } from 'vitest'
import bn from './bn.json'
import en from './en.json'
import { DEFAULT_LOCALE, isLocale, setDocumentLocale } from './index'

function flatten(obj: unknown, prefix = ''): Record<string, string> {
  const out: Record<string, string> = {}
  for (const [k, v] of Object.entries(obj as Record<string, unknown>)) {
    const key = prefix ? `${prefix}.${k}` : k
    if (typeof v === 'string') out[key] = v
    else Object.assign(out, flatten(v, key))
  }
  return out
}

const bnFlat = flatten(bn)
const enFlat = flatten(en)

describe('i18n completeness (check_i18n.py equivalent, spec 15.9)', () => {
  it('bn and en have exactly the same keys', () => {
    expect(Object.keys(bnFlat).sort()).toEqual(Object.keys(enFlat).sort())
  })

  it('no empty strings', () => {
    for (const [k, v] of [...Object.entries(bnFlat), ...Object.entries(enFlat)]) {
      expect(v.trim(), k).not.toBe('')
    }
  })

  it('Bangla strings contain Bengali script (not copied English) except allowed Latin tokens', () => {
    const allowedLatin = new Set(['advice.basedOn'])
    for (const [k, v] of Object.entries(bnFlat)) {
      if (allowedLatin.has(k)) continue
      expect(/[ঀ-৿]/.test(v), `${k} has no Bengali characters`).toBe(true)
    }
  })

  it('Bangla uses the danda (।) not a Latin full stop at sentence ends', () => {
    for (const [k, v] of Object.entries(bnFlat)) {
      if (k === 'advice.basedOn') continue
      expect(/[ঀ-৿]\.$/.test(v), `${k} ends with a Latin full stop`).toBe(false)
    }
  })

  it('Bangla sentences stay within 15 words (style guide)', () => {
    for (const [k, v] of Object.entries(bnFlat)) {
      for (const sentence of v.split(/[।?!]/)) {
        const words = sentence.trim().split(/\s+/).filter(Boolean).length
        expect(words, `${k}: "${sentence.trim()}"`).toBeLessThanOrEqual(15)
      }
    }
  })

  it('placeholders match between locales', () => {
    const ph = (s: string) => (s.match(/{{\s*\w+\s*}}/g) ?? []).sort().join(',')
    for (const k of Object.keys(bnFlat)) expect(ph(bnFlat[k]!), k).toBe(ph(enFlat[k]!))
  })

  it('the spec hero headline is used verbatim (15.11)', () => {
    expect(bnFlat['landing.hero.headline']).toBe('একটি পাতার ছবি। পুরো এলাকার সুরক্ষা।')
    expect(enFlat['landing.hero.headline']).toBe('One leaf photo. A whole area protected.')
  })

  it('farmer-facing copy never shows raw percentages (15.5.5)', () => {
    for (const [k, v] of Object.entries(bnFlat)) expect(v, k).not.toMatch(/%|[০-৯]+\s?শতাংশ/)
  })
})

describe('locale helpers', () => {
  it('Bangla is the default locale', () => {
    expect(DEFAULT_LOCALE).toBe('bn')
  })

  it('isLocale accepts only supported locales', () => {
    expect(isLocale('bn')).toBe(true)
    expect(isLocale('en')).toBe(true)
    for (const bad of ['fr', '', 'BN', null, undefined, 3, {}]) expect(isLocale(bad)).toBe(false)
  })

  it('setDocumentLocale sets the lang attribute', () => {
    setDocumentLocale('en')
    expect(document.documentElement.lang).toBe('en')
    setDocumentLocale('bn')
    expect(document.documentElement.lang).toBe('bn')
  })
})
