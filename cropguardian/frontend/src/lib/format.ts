/**
 * Locale-aware formatting (spec 15.1, 0.2.9): Bangla numerals and month names in the `bn` locale,
 * every date shown in Asia/Dhaka (times are stored in UTC), tabular-friendly numbers.
 *
 * Pure functions: the current time is always a parameter, so nothing here reads the wall clock
 * implicitly and every function is deterministic under test. Invalid input throws a RangeError
 * instead of rendering "NaN" or "Invalid Date" to a farmer.
 */

import type { Locale } from '../i18n'

export const DHAKA_TZ = 'Asia/Dhaka'

/** BCP 47 tag per supported locale (a ternary, not a lookup table: no dynamic indexing). */
const tag = (locale: Locale): string => (locale === 'bn' ? 'bn-BD' : 'en-GB')
const BN_DIGITS = '০১২৩৪৫৬৭৮৯'

export type DateInput = Date | string | number

/** Convert ASCII digits to Bangla digits (display only). */
export function toBanglaDigits(value: string): string {
  return value.replace(/[0-9]/g, (d) => BN_DIGITS.charAt(Number(d)))
}

/** Forgiving input: Bangla digits become ASCII (phone numbers, OTP boxes; spec 15.5.7). */
export function fromBanglaDigits(value: string): string {
  return value.replace(/[০-৯]/g, (d) => String(BN_DIGITS.indexOf(d)))
}

function assertFinite(n: number): void {
  if (!Number.isFinite(n)) throw new RangeError('number must be finite')
}

function toDate(input: DateInput): Date {
  const d = input instanceof Date ? input : new Date(input)
  if (Number.isNaN(d.getTime())) throw new RangeError('invalid date')
  return d
}

/** Plain number with locale digits and grouping, e.g. 4100 -> "৪,১০০" / "4,100". */
export function formatNumber(n: number, locale: Locale, maximumFractionDigits = 2): string {
  assertFinite(n)
  return new Intl.NumberFormat(tag(locale), { maximumFractionDigits }).format(n)
}

/** Big counts abbreviated (spec 15.13.4): 12500 -> "12.5K" / "১২.৫ হা". */
export function formatCompact(n: number, locale: Locale): string {
  assertFinite(n)
  if (locale === 'en') {
    // Explicit K/M/B: ICU/CLDR versions disagree on English compact forms ("12.5K" vs "12.5k" vs
    // "13K"), and the spec fixes "12.5K"; the grouping/decimals still come from formatNumber.
    const abs = Math.abs(n)
    for (const [size, suffix] of [
      [1e9, 'B'],
      [1e6, 'M'],
      [1e3, 'K'],
    ] as const) {
      if (abs >= size) return formatNumber(n / size, 'en', 1) + suffix
    }
    return formatNumber(n, 'en', 1)
  }
  return new Intl.NumberFormat(tag(locale), {
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(n)
}

/** A fraction 0..1 as a percentage with at most one decimal (spec 15.13.4). Staff views only: farmers get bands. */
export function formatPercent(fraction: number, locale: Locale): string {
  assertFinite(fraction)
  return new Intl.NumberFormat(tag(locale), {
    style: 'percent',
    maximumFractionDigits: 1,
  }).format(fraction)
}

/**
 * "১৬ অক্টোবর ২০২৬" / "16 Oct 2026" in Asia/Dhaka (spec 15.1). Built from the parts because ICU
 * inserts a comma in the Bangla pattern ("১৬ অক্টোবর, ২০২৬") that the spec format does not have.
 */
export function formatDate(input: DateInput, locale: Locale): string {
  const parts = new Intl.DateTimeFormat(tag(locale), {
    day: 'numeric',
    month: locale === 'bn' ? 'long' : 'short',
    year: 'numeric',
    timeZone: DHAKA_TZ,
  }).formatToParts(toDate(input))
  const pick = (type: string) => parts.find((p) => p.type === type)?.value ?? ''
  return `${pick('day')} ${pick('month')} ${pick('year')}`
}

/** Clock time in Asia/Dhaka, 12-hour with Bangla/Latin digits. */
export function formatTime(input: DateInput, locale: Locale): string {
  return new Intl.DateTimeFormat(tag(locale), {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
    timeZone: DHAKA_TZ,
  }).format(toDate(input))
}

/** Exact date and time, used as the tooltip text behind every relative time. */
export function formatExact(input: DateInput, locale: Locale): string {
  return `${formatDate(input, locale)}, ${formatTime(input, locale)}`
}

const UNITS: ReadonlyArray<readonly [Intl.RelativeTimeFormatUnit, number]> = [
  ['year', 365 * 24 * 3600],
  ['month', 30 * 24 * 3600],
  ['day', 24 * 3600],
  ['hour', 3600],
  ['minute', 60],
]

/**
 * Relative time ("৩ ঘণ্টা আগে" / "3 hours ago"). `now` is explicit; future dates read "in ...".
 * Anything under a minute is "now" (numeric:auto), so a freshly saved item never says "0 seconds ago".
 */
export function formatRelative(input: DateInput, now: DateInput, locale: Locale): string {
  const diffSeconds = Math.round((toDate(input).getTime() - toDate(now).getTime()) / 1000)
  const rtf = new Intl.RelativeTimeFormat(tag(locale), { numeric: 'auto' })
  const abs = Math.abs(diffSeconds)
  for (const [unit, size] of UNITS) {
    if (abs >= size) return rtf.format(Math.trunc(diffSeconds / size), unit)
  }
  return rtf.format(0, 'second')
}

/** A span of whole days as "৪ দিন" / "4 days" (growth stage age, alert window). */
export function formatDays(days: number, locale: Locale): string {
  assertFinite(days)
  if (days < 0) throw new RangeError('days must be non-negative')
  return new Intl.NumberFormat(tag(locale), {
    style: 'unit',
    unit: 'day',
    unitDisplay: 'long',
    maximumFractionDigits: 0,
  }).format(Math.round(days))
}

export type DayPart = 'morning' | 'noon' | 'evening' | 'night'

/**
 * Greeting period in Asia/Dhaka, whatever the device clock zone is: morning 05-11, noon 12-15,
 * evening 16-19, night otherwise. Pure: the instant is a parameter.
 */
export function dayPart(input: DateInput): DayPart {
  const hour = Number(
    new Intl.DateTimeFormat('en-GB', {
      hour: 'numeric',
      hourCycle: 'h23',
      timeZone: DHAKA_TZ,
    }).format(toDate(input)),
  )
  if (hour >= 5 && hour < 12) return 'morning'
  if (hour >= 12 && hour < 16) return 'noon'
  if (hour >= 16 && hour < 20) return 'evening'
  return 'night'
}
