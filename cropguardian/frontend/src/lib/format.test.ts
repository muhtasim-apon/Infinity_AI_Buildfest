import { describe, expect, it } from 'vitest'
import {
  dayPart,
  formatCompact,
  formatDate,
  formatDays,
  formatExact,
  formatNumber,
  formatPercent,
  formatRelative,
  formatTime,
  fromBanglaDigits,
  toBanglaDigits,
} from './format'

// 2026-10-16 09:30 UTC = 15:30 in Dhaka (UTC+6, no DST).
const NOW = '2026-10-16T09:30:00Z'

describe('Bangla digits', () => {
  it('converts every ASCII digit and leaves other characters alone', () => {
    expect(toBanglaDigits('0123456789')).toBe('০১২৩৪৫৬৭৮৯')
    expect(toBanglaDigits('+880 1712-345678')).toBe('+৮৮০ ১৭১২-৩৪৫৬৭৮')
    expect(toBanglaDigits('')).toBe('')
  })

  it('round-trips, so Bangla-digit phone and OTP input is accepted', () => {
    expect(fromBanglaDigits('০১৭১২৩৪৫৬৭৮')).toBe('01712345678')
    expect(fromBanglaDigits(toBanglaDigits('2026'))).toBe('2026')
    expect(fromBanglaDigits('abc')).toBe('abc')
  })
})

describe('numbers', () => {
  it('uses Bangla digits and grouping in bn, Latin in en', () => {
    expect(formatNumber(4100, 'bn')).toBe('৪,১০০')
    expect(formatNumber(4100, 'en')).toBe('4,100')
  })

  it('handles zero, negatives, fractions and very large values', () => {
    expect(formatNumber(0, 'en')).toBe('0')
    expect(formatNumber(-12.345, 'en')).toBe('-12.35')
    expect(formatNumber(1e15, 'en')).toBe('1,000,000,000,000,000')
    expect(formatNumber(0.5, 'bn', 0)).toBe('১') // rounds half to even-away as Intl does; never throws
  })

  it('rejects NaN and infinities instead of rendering them to a farmer', () => {
    for (const bad of [Number.NaN, Infinity, -Infinity]) {
      expect(() => formatNumber(bad, 'bn')).toThrow(RangeError)
      expect(() => formatCompact(bad, 'bn')).toThrow(RangeError)
      expect(() => formatPercent(bad, 'bn')).toThrow(RangeError)
    }
  })

  it('abbreviates big counts and caps percentages at one decimal', () => {
    expect(formatCompact(12500, 'en')).toBe('12.5K')
    expect(formatCompact(999, 'en')).toBe('999')
    expect(formatPercent(0.8765, 'en')).toBe('87.7%')
    expect(formatPercent(0, 'en')).toBe('0%')
  })
})

describe('dates in Asia/Dhaka', () => {
  it('formats a Bangla date with Bangla numerals and month name', () => {
    expect(formatDate(NOW, 'bn')).toBe('১৬ অক্টোবর ২০২৬')
    expect(formatDate(NOW, 'en')).toBe('16 Oct 2026')
  })

  it('moves to the next day when UTC is still the previous evening (UTC+6 boundary)', () => {
    // 18:30 UTC on 15 Oct is already 00:30 on 16 Oct in Dhaka.
    expect(formatDate('2026-10-15T18:30:00Z', 'en')).toBe('16 Oct 2026')
    expect(formatDate('2026-10-15T17:59:59Z', 'en')).toBe('15 Oct 2026')
  })

  it('accepts Date objects and epoch milliseconds', () => {
    const ms = Date.parse(NOW)
    expect(formatDate(new Date(ms), 'en')).toBe(formatDate(ms, 'en'))
  })

  it('formats clock time and an exact timestamp for tooltips', () => {
    expect(formatTime(NOW, 'en').toLowerCase()).toBe('3:30 pm')
    expect(formatExact(NOW, 'en').toLowerCase()).toBe('16 oct 2026, 3:30 pm')
    expect(formatExact(NOW, 'bn')).toContain('১৬ অক্টোবর ২০২৬')
  })

  it('rejects invalid dates with a RangeError', () => {
    for (const bad of ['not a date', '', Number.NaN, new Date('x')]) {
      expect(() => formatDate(bad, 'bn')).toThrow(RangeError)
    }
    expect(() => formatRelative(NOW, 'nope', 'bn')).toThrow(RangeError)
  })
})

describe('relative time', () => {
  const at = (iso: string, locale: 'bn' | 'en' = 'en') => formatRelative(iso, NOW, locale)

  it('picks the largest sensible unit, past and future', () => {
    expect(at('2026-10-16T06:30:00Z')).toBe('3 hours ago')
    expect(at('2026-10-14T09:30:00Z')).toBe('2 days ago')
    expect(at('2026-10-16T09:25:00Z')).toBe('5 minutes ago')
    expect(at('2026-10-17T09:30:00Z')).toBe('tomorrow')
  })

  it('says "now" under a minute rather than "0 seconds ago"', () => {
    expect(at('2026-10-16T09:29:45Z')).toBe('now')
    expect(at(NOW)).toBe('now')
  })

  it('renders Bangla digits in bn', () => {
    expect(at('2026-10-16T06:30:00Z', 'bn')).toContain('৩')
  })
})

describe('durations', () => {
  it('formats whole days in both locales', () => {
    expect(formatDays(4, 'en')).toBe('4 days')
    expect(formatDays(4, 'bn')).toContain('৪')
    expect(formatDays(0, 'en')).toBe('0 days')
  })

  it('rejects negative and non-finite spans', () => {
    expect(() => formatDays(-1, 'bn')).toThrow(RangeError)
    expect(() => formatDays(Number.NaN, 'bn')).toThrow(RangeError)
  })
})

describe('dayPart (greeting period in Asia/Dhaka)', () => {
  // Dhaka is UTC+6: 00:00 UTC is 06:00 there
  const at = (utc: string) => dayPart(`2026-10-16T${utc}:00Z`)

  it('maps Dhaka hours to the four periods', () => {
    expect(at('00:00')).toBe('morning') // 06:00
    expect(at('05:59')).toBe('morning') // 11:59
    expect(at('06:00')).toBe('noon') // 12:00
    expect(at('09:59')).toBe('noon') // 15:59
    expect(at('10:00')).toBe('evening') // 16:00
    expect(at('13:59')).toBe('evening') // 19:59
    expect(at('14:00')).toBe('night') // 20:00
    expect(at('22:59')).toBe('night') // 04:59 next day
    expect(at('23:00')).toBe('morning') // 05:00 next day
  })

  it('ignores the device time zone: only the instant matters', () => {
    expect(dayPart(Date.parse('2026-10-16T00:00:00Z'))).toBe('morning')
    expect(dayPart(new Date('2026-10-16T14:00:00Z'))).toBe('night')
  })

  it('rejects an invalid instant', () => {
    expect(() => dayPart('nope')).toThrow(RangeError)
  })
})
